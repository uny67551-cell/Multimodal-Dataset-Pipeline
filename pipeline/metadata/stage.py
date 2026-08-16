"""Orchestration for the metadata generation stage."""

from pathlib import Path

from loguru import logger

from pipeline.core.config import PipelineConfig
from pipeline.metadata.merger import merge_from_reports
from pipeline.metadata.reporter import build_report, export_report
from pipeline.models.metadata_record import MetadataRecord


class MetadataStage:
    """Run merge -> report."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    @property
    def report_path(self) -> Path:
        """Default path for the metadata JSON report."""
        return self.config.metadata_report_path

    def run(
        self,
        ingestion_report_path: Path | None = None,
        inference_report_path: Path | None = None,
    ) -> list[MetadataRecord]:
        """
        Execute metadata merge and export.

        Args:
            ingestion_report_path: Optional override for ingestion report.
            inference_report_path: Optional override for inference report.

        Returns:
            List of MetadataRecord objects.
        """
        ingestion_path = (
            Path(ingestion_report_path)
            if ingestion_report_path is not None
            else self.config.ingestion_report_path
        )
        inference_path = (
            Path(inference_report_path)
            if inference_report_path is not None
            else self.config.inference_report_path
        )

        logger.info("Merging metadata from reports ...")
        logger.info("Ingestion report: {}", ingestion_path)
        logger.info("Inference report: {}", inference_path)

        records = merge_from_reports(
            ingestion_report_path=ingestion_path,
            inference_report_path=inference_path,
        )

        report = build_report(
            records=records,
            ingestion_report_path=ingestion_path,
            inference_report_path=inference_path,
        )
        export_report(report, self.report_path)

        summary = report["summary"]
        logger.info(
            "Metadata complete | complete: {} | partial: {} | "
            "ingestion_only: {} | failed: {}",
            summary["complete"],
            summary["partial"],
            summary["ingestion_only"],
            summary["failed"],
        )
        return records