"""Orchestration for the quality-control pipeline stage."""

from pathlib import Path

from loguru import logger
from tqdm import tqdm

from pipeline.core.config import PipelineConfig
from pipeline.models.qc_record import QCRecord
from pipeline.qc.collector import collect_qc_targets
from pipeline.qc.duplicate import find_duplicates
from pipeline.qc.reporter import build_report, export_report
from pipeline.qc.scorer import build_qc_record


class QCStage:
    """Run collect -> duplicate -> per-image checks -> report."""

    def __init__(self, config: PipelineConfig, blur_threshold: float | None = None,):
        self.config = config
        self.blur_threshold = (
            blur_threshold
            if blur_threshold is not None
            else config.qc.blur_threshold
        )

    @property
    def report_path(self) -> Path:
        """Default path for the QC JSON report."""
        return self.config.qc_report_path

    def run(
        self,
        metadata_report_path: Path | None = None,
        processed_dir: Path | None = None,
    ) -> list[QCRecord]:
        """
        Execute quality control.

        Args:
            metadata_report_path: Optional metadata report override.
            processed_dir: Optional processed directory override.

        Returns:
            List of QCRecord objects.
        """
        metadata_path = (
            Path(metadata_report_path)
            if metadata_report_path is not None
            else self.config.metadata_report_path
        )
        images_dir = (
            Path(processed_dir)
            if processed_dir is not None
            else self.config.processed_dir
        )

        logger.info("Collecting QC targets ...")
        targets = collect_qc_targets(
            metadata_report_path=metadata_path,
            processed_dir=images_dir,
        )
        logger.info("Found {} images for QC", len(targets))

        logger.info("Detecting duplicates ...")
        duplicate_map = find_duplicates(targets)
        logger.info("Found {} duplicate images", len(duplicate_map))

        records: list[QCRecord] = []
        for target in tqdm(targets, desc="Running QC"):
            record = build_qc_record(
                image_id=target.image_id,
                image_path=target.image_path,
                blur_threshold=self.blur_threshold,
                duplicate_of=duplicate_map.get(target.image_id),
            )
            records.append(record)

        report = build_report(
            records,
            processed_dir=images_dir,
            blur_threshold=self.blur_threshold,
        )
        export_report(report, self.report_path)

        summary = report["summary"]
        logger.info(
            "QC complete | pass: {} | warn: {} | reject: {} | "
            "corrupt: {} | blurry: {} | duplicate: {}",
            summary["pass"],
            summary["warn"],
            summary["reject"],
            summary["corrupt"],
            summary["blurry"],
            summary["duplicate"],
        )
        return records