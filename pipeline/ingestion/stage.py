"""Orchestration for the image ingestion pipeline stage."""

from pathlib import Path
from loguru import logger
from pipeline.core.config import PipelineConfig # default values
from pipeline.core.stage import PipelineStage
from pipeline.ingestion.organizer import organize_batch
from pipeline.ingestion.reporter import build_report, export_report
from pipeline.ingestion.scanner import scan_directory
from pipeline.ingestion.validator import validate_batch
from pipeline.models.image_record import ImageRecord


class IngestionStage(PipelineStage):
    """Run scan -> validate -> organize -> report."""
    def __init__(self, config: PipelineConfig):
        self.config = config
    def run(self, input_dir: Path | None = None) -> list[ImageRecord]:
        """
        Execute the ingestion pipeline.
        Args:
            input_dir: Optional override for the configured raw directory.
        Returns:
            Final list of ImageRecord objects after organize step.
        """
        source_dir = Path(input_dir) if input_dir is not None else self.config.raw_dir
        processed_dir = self.config.processed_dir
        ingestion = self.config.ingestion
        logger.info("Scanning {} ...", source_dir)
        paths = scan_directory(
            input_dir=source_dir,
            supported_extensions=ingestion.supported_extensions,
            recursive=ingestion.recursive,
        )
        logger.info("Found {} candidate images", len(paths)) # delayed formatting
        if not paths:
            logger.warning("No images found in {}", source_dir)
        records = validate_batch(paths, show_progress=True)
        records = organize_batch(
            records,
            output_dir=processed_dir,
            mode=ingestion.mode,  # type: ignore[arg-type]
        )
        report = build_report(
            records=records,
            input_dir=source_dir,
            output_dir=processed_dir,
        )
        export_report(report, self.config.ingestion_report_path) #
        summary = report["summary"]
        logger.info(
            "Ingestion complete | valid: {} | invalid: {} | skipped: {}",
            summary["valid"],
            summary["invalid"],
            summary["skipped"],
        )
        return records