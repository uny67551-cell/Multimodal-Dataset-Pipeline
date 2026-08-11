"""Orchestration for the dataset export pipeline stage."""

from pathlib import Path

from loguru import logger

from pipeline.core.config import PipelineConfig
from pipeline.export.collector import collect_export_candidates
from pipeline.export.filter import apply_export_filters, iter_included
from pipeline.export.reporter import build_report, export_report
from pipeline.export.writers.images import copy_export_images
from pipeline.export.writers.jsonl import write_annotations_jsonl
from pipeline.models.export_record import ExportRecord
from pipeline.export.writers.llava import write_llava_jsonl


class ExportStage:
    """Run collect -> filter -> copy images -> JSONL -> report."""

    def __init__(
        self,
        config: PipelineConfig,
        *,
        export_dir: Path | None = None,
        exclude_duplicates: bool | None = None,
        include_blurry: bool | None = None,
        require_caption: bool | None = None,
    ):
        self.config = config
        self.export_dir = (
            Path(export_dir)
            if export_dir is not None
            else Path(config.export.export_dir)
        )
        self.exclude_duplicates = (
            exclude_duplicates
            if exclude_duplicates is not None
            else config.export.exclude_duplicates
        )
        self.include_blurry = (
            include_blurry
            if include_blurry is not None
            else config.export.include_blurry
        )
        self.require_caption = (
            require_caption
            if require_caption is not None
            else config.export.require_caption
        )

    @property
    def report_path(self) -> Path:
        """Path for export_report.json inside the export package."""
        return self.export_dir / "export_report.json"

    @property
    def annotations_path(self) -> Path:
        """Path for annotations.jsonl inside the export package."""
        return self.export_dir / "annotations.jsonl"

    @property
    def llava_path(self) -> Path:
        return self.export_dir / "llava.jsonl"

    def run(
        self,
        metadata_report_path: Path | None = None,
        qc_report_path: Path | None = None,
    ) -> list[ExportRecord]:
        """
        Execute dataset export into a self-contained package.

        Returns:
            Full candidate list (included + excluded) for auditing.
        """
        metadata_path = (
            Path(metadata_report_path)
            if metadata_report_path is not None
            else self.config.metadata_report_path
        )
        qc_path = (
            Path(qc_report_path)
            if qc_report_path is not None
            else self.config.qc_report_path
        )

        self.export_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Collecting export candidates ...")
        records = collect_export_candidates(
            metadata_report_path=metadata_path,
            qc_report_path=qc_path,
        )

        logger.info("Applying export filters ...")
        apply_export_filters(
            records,
            exclude_duplicates=self.exclude_duplicates,
            include_blurry=self.include_blurry,
            require_caption=self.require_caption,
        )

        logger.info("Copying included images ...")
        images_copied = copy_export_images(records, self.export_dir)

        logger.info("Writing annotations.jsonl ...")
        write_annotations_jsonl(records, self.annotations_path)

        logger.info("Writing llava.jsonl ...")
        write_llava_jsonl(records, self.llava_path)

        report = build_report(
            records,
            export_dir=self.export_dir,
            metadata_report_path=metadata_path,
            qc_report_path=qc_path if qc_path.exists() else None,
            exclude_duplicates=self.exclude_duplicates,
            include_blurry=self.include_blurry,
            require_caption=self.require_caption,
            images_copied=images_copied,
            annotations_path=self.annotations_path,
            llava_path=self.llava_path,
        )
        export_report(report, self.report_path)

        included_n = len(iter_included(records))
        logger.info(
            "Export complete | included: {} | images_copied: {} | dir: {}",
            included_n,
            images_copied,
            self.export_dir,
        )
        return records