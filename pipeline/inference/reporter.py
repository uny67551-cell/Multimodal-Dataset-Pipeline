"""Build and export VLM inference reports."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from loguru import logger
from pipeline.models.inference_record import InferenceRecord


PIPELINE_VERSION = "0.1.0"

def _serialize_record(record: InferenceRecord) -> dict[str, Any]:
    """Convert one InferenceRecord to a JSON-serializable dictionary."""
    return {
        "image_id": record.image_id,
        "image_path": str(record.image_path),
        "status": record.status,
        "caption": record.caption,
        "tags": record.tags,
        "objects": record.objects,
        "backend": record.backend,
        "error_message": record.error_message,
        "inferred_at": record.inferred_at.isoformat(),
    }

def build_summary(records: list[InferenceRecord]) -> dict[str, int]:
    """Compute inference summary statistics."""
    return {
        "total": len(records),
        "success": sum(1 for record in records if record.status == "success"),
        "failed": sum(1 for record in records if record.status == "failed"),
        "skipped": sum(1 for record in records if record.status == "skipped"),
    }

def build_report(
    records: list[InferenceRecord],
    processed_dir: Path,
    backend: str,
) -> dict[str, Any]:
    """Build the full inference report dictionary."""
    return {
        "pipeline": "inference",
        "version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "processed_dir": str(processed_dir),
        "backend": backend,
        "summary": build_summary(records),
        "records": [_serialize_record(record) for record in records],
    }
    
def export_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write the inference report to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    logger.info("Inference report saved to {}", output_path)
    return output_path
