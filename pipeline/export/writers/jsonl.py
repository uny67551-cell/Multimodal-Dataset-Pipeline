"""Write flat JSONL annotations for training export."""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from pipeline.models.export_record import ExportRecord
from pipeline.export.filter import iter_included


def _serialize_included(record: ExportRecord) -> dict[str, Any]:
    """One training row for annotations.jsonl."""
    return {
        "id": record.id,
        "image": record.export_image_relpath,
        "caption": record.caption,
        "tags": list(record.tags),
        "objects": list(record.objects),
        "scene": record.scene,
        "quality_status": record.quality_status,
        "is_blurry": record.is_blurry,
        "blur_score": record.blur_score,
    }


def write_annotations_jsonl(
    records: list[ExportRecord],
    output_path: Path,
    *,
    included_only: bool = True,
) -> Path:
    """
    Write annotations.jsonl.

    By default only included samples are written (training set).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = iter_included(records) if included_only else records
    with output_path.open("w", encoding="utf-8") as file:
        for record in rows:
            line = json.dumps(_serialize_included(record), ensure_ascii=False)
            file.write(line + "\n")

    logger.info("Wrote {} annotation rows to {}", len(rows), output_path)
    return output_path