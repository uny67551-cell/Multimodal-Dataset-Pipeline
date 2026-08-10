"""Build and export quality-control reports."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from pipeline.models.qc_record import QCRecord

PIPELINE_VERSION = "0.1.0"


def _serialize_record(record: QCRecord) -> dict[str, Any]:
    """Convert one QCRecord to a JSON-serializable dictionary."""
    return {
        "image_id": record.image_id,
        "image_path": str(record.image_path),
        "checked_at": record.checked_at.isoformat(),
        "is_corrupt": record.is_corrupt,
        "blur_score": record.blur_score,
        "is_blurry": record.is_blurry,
        "is_duplicate": record.is_duplicate,
        "duplicate_of": record.duplicate_of,
        "quality_status": record.quality_status,
        "error_message": record.error_message,
    }


def build_summary(records: list[QCRecord]) -> dict[str, int]:
    """Compute QC summary statistics."""
    return {
        "total": len(records),
        "pass": sum(1 for record in records if record.quality_status == "pass"),
        "warn": sum(1 for record in records if record.quality_status == "warn"),
        "reject": sum(1 for record in records if record.quality_status == "reject"),
        "corrupt": sum(1 for record in records if record.is_corrupt),
        "blurry": sum(1 for record in records if record.is_blurry),
        "duplicate": sum(1 for record in records if record.is_duplicate),
    }


def build_report(
    records: list[QCRecord],
    *,
    processed_dir: Path,
    blur_threshold: float,
) -> dict[str, Any]:
    """Build the full QC report dictionary."""
    return {
        "pipeline": "qc",
        "version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "processed_dir": str(processed_dir),
        "blur_threshold": blur_threshold,
        "summary": build_summary(records),
        "records": [_serialize_record(record) for record in records],
    }


def export_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write the QC report to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    logger.info("QC report saved to {}", output_path)
    return output_path