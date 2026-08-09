"""Build and export metadata reports."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from pipeline.models.metadata_record import MetadataRecord

PIPELINE_VERSION = "0.1.0"


def _serialize_record(record: MetadataRecord) -> dict[str, Any]:
    """Convert one MetadataRecord to a JSON-serializable dictionary."""
    return {
        "id": record.id,
        "status": record.status,
        "generated_at": record.generated_at.isoformat(),
        "original_filename": record.original_filename,
        "source_path": str(record.source_path) if record.source_path else None,
        "processed_path": str(record.processed_path) if record.processed_path else None,
        "extension": record.extension,
        "width": record.width,
        "height": record.height,
        "format": record.format,
        "file_size_bytes": record.file_size_bytes,
        "checksum": record.checksum,
        "ingested_at": record.ingested_at.isoformat() if record.ingested_at else None,
        "ingestion_status": record.ingestion_status,
        "caption": record.caption,
        "tags": record.tags,
        "objects": record.objects,
        "scene": record.scene,
        "inference_backend": record.inference_backend,
        "inferred_at": record.inferred_at.isoformat() if record.inferred_at else None,
        "inference_status": record.inference_status,
        "error_message": record.error_message,
    }


def build_summary(records: list[MetadataRecord]) -> dict[str, int]:
    """Compute metadata summary statistics."""
    return {
        "total": len(records),
        "complete": sum(1 for record in records if record.status == "complete"),
        "partial": sum(1 for record in records if record.status == "partial"),
        "ingestion_only": sum(
            1 for record in records if record.status == "ingestion_only"
        ),
        "failed": sum(1 for record in records if record.status == "failed"),
    }


def build_report(
    records: list[MetadataRecord],
    ingestion_report_path: Path,
    inference_report_path: Path,
) -> dict[str, Any]:
    """Build the full metadata report dictionary."""
    return {
        "pipeline": "metadata",
        "version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ingestion_report": str(ingestion_report_path),
        "inference_report": str(inference_report_path),
        "summary": build_summary(records),
        "records": [_serialize_record(record) for record in records],
    }


def export_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write the metadata report to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    logger.info("Metadata report saved to {}", output_path)
    return output_path