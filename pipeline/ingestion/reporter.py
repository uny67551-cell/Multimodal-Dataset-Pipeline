"""Build and export ingestion reports."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from loguru import logger
from pipeline.models.image_record import ImageRecord

PIPELINE_VERSION = "0.1.0"

def _serialize_record(record: ImageRecord) -> dict[str, Any]:
    """Convert one ImageRecord to a JSON-serializable dictionary."""
    return {
        "id": record.id,
        "source_path": str(record.source_path),
        "processed_path": str(record.processed_path) if record.processed_path else None,
        "original_filename": record.original_filename,
        "extension": record.extension,
        "width": record.width,
        "height": record.height,
        "format": record.format,
        "file_size_bytes": record.file_size_bytes,
        "checksum": record.checksum,
        "status": record.status,
        "error_message": record.error_message,
        "ingested_at": record.ingested_at.isoformat(),
    }

def build_summary(records: list[ImageRecord]) -> dict[str, int]:
    """Compute summary statistics from image records."""
    return {
        "total_scanned": len(records),
        "valid": sum(1 for record in records if record.status == "valid"),
        "invalid": sum(1 for record in records if record.status == "invalid"),
        "skipped": sum(1 for record in records if record.status == "skipped"),
    }

def build_report(
    records: list[ImageRecord],
    input_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Build the full ingestion report dictionary."""
    return {
        "pipeline": "ingestion",
        "version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "summary": build_summary(records),
        "records": [_serialize_record(record) for record in records],
    }

def export_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write the ingestion report to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    logger.info("Ingestion report saved to {}", output_path)
    return output_path