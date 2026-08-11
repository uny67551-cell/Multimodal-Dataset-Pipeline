"""Build and write dataset export reports."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from pipeline.models.export_record import ExportRecord

PIPELINE_VERSION = "0.1.0"


def _serialize_record(record: ExportRecord) -> dict[str, Any]:
    """Convert one ExportRecord for the audit report."""
    return {
        "id": record.id,
        "status": record.status,
        "exclude_reason": record.exclude_reason,
        "source_image_path": (
            str(record.source_image_path) if record.source_image_path else None
        ),
        "export_image_relpath": record.export_image_relpath,
        "caption": record.caption,
        "tags": list(record.tags),
        "objects": list(record.objects),
        "scene": record.scene,
        "metadata_status": record.metadata_status,
        "quality_status": record.quality_status,
        "is_corrupt": record.is_corrupt,
        "is_blurry": record.is_blurry,
        "is_duplicate": record.is_duplicate,
        "duplicate_of": record.duplicate_of,
        "blur_score": record.blur_score,
        "generated_at": record.generated_at.isoformat(),
    }


def build_summary(records: list[ExportRecord]) -> dict[str, Any]:
    """Compute export summary statistics."""
    reasons = Counter(
        record.exclude_reason
        for record in records
        if record.status == "excluded" and record.exclude_reason
    )
    return {
        "total": len(records),
        "included": sum(1 for r in records if r.status == "included"),
        "excluded": sum(1 for r in records if r.status == "excluded"),
        "exclude_reasons": dict(reasons),
    }


def build_report(
    records: list[ExportRecord],
    *,
    export_dir: Path,
    metadata_report_path: Path,
    qc_report_path: Path | None,
    exclude_duplicates: bool,
    include_blurry: bool,
    require_caption: bool,
    images_copied: int,
    annotations_path: Path,
    llava_path: Path,
) -> dict[str, Any]:
    """Build the full export report dictionary."""
    return {
        "pipeline": "export",
        "version": PIPELINE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "export_dir": str(export_dir),
        "metadata_report": str(metadata_report_path),
        "qc_report": str(qc_report_path) if qc_report_path else None,
        "policy": {
            "exclude_duplicates": exclude_duplicates,
            "include_blurry": include_blurry,
            "require_caption": require_caption,
            "copy_images": True,
        },
        "artifacts": {
            "annotations_jsonl": str(annotations_path),
            "llava_jsonl": str(llava_path),
            "images_copied": images_copied,
        },
        "summary": build_summary(records),
        "records": [_serialize_record(record) for record in records],
    }


def export_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write export_report.json."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    logger.info("Export report saved to {}", output_path)
    return output_path