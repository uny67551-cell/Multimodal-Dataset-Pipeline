"""Orchestration for the VLM inference pipeline stage."""

from pathlib import Path
from loguru import logger
from tqdm import tqdm
from pipeline.core.config import PipelineConfig
from pipeline.inference.base import VLMBackend
from pipeline.inference.collector import collect_inference_targets
from pipeline.inference.reporter import build_report, export_report
from pipeline.models.inference_record import InferenceRecord

class InferenceStage:
    """Run collect -> infer -> report."""

    def __init__(self, config: PipelineConfig, backend: VLMBackend):
        self.config = config
        self.backend = backend

    @property
    def report_path(self) -> Path:
        """Default path for the inference JSON report."""
        return self.config.inference_report_path

    def run(
        self,
        report_path: Path | None = None,
        processed_dir: Path | None = None,
    ) -> list[InferenceRecord]:
        """
        Execute the inference pipeline.

        Args:
            report_path: Optional ingestion report path.
            processed_dir: Optional processed images directory.

        Returns:
            List of InferenceRecord objects.
        """
        ingestion_report = (
            Path(report_path)
            if report_path is not None
            else self.config.ingestion_report_path
        )

        images_dir = (
            Path(processed_dir)
            if processed_dir is not None
            else self.config.processed_dir
        )

        logger.info("Collecting inference targets ...")
        targets = collect_inference_targets(
            report_path=ingestion_report,
            processed_dir=images_dir,
        )
        logger.info("Found {} images for inference", len(targets))

        if not targets:
            logger.warning("No inference targets found")
            report = build_report(
                records=[],
                processed_dir=images_dir,
                backend=self.backend.name,
            )
            export_report(report, self.report_path)
            return []

        records: list[InferenceRecord] = []
        for target in tqdm(targets, desc="Running inference"):
            record = self.backend.infer(
                image_path=target.image_path,
                image_id=target.image_id,
            )
            records.append(record)

        report = build_report(
            records=records,
            processed_dir=images_dir,
            backend=self.backend.name,
        )
        export_report(report, self.report_path)

        summary = report["summary"]
        logger.info(
            "Inference complete | success: {} | failed: {} | skipped: {}",
            summary["success"],
            summary["failed"],
            summary["skipped"],
        )
        return records