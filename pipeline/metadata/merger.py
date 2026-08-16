"""Merge ingestion and inference reports into MetadataRecord objects."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from pipeline.core.exceptions import MetadataError
from pipeline.models.metadata_record import MetadataRecord, MetadataStatus


def load_json_report(path: Path) -> dict[str, Any]:
    """Load a JSON report file."""
    path = Path(path)
    if not path.exists():
        raise MetadataError(f"Report not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise MetadataError(f"Invalid report format (expected object): {path}")
    return data


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime string; return None if missing/invalid."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _derive_scene(tags: list[str], caption: str | None) -> str | None:
    """
    Lightweight scene placeholder for Sprint 3.

    Prefer the first tag; otherwise None.
    """
    if tags:
        return tags[0]
    return None


def _decide_status(
    *,
    has_processed: bool,
    inference_status: str | None,
) -> MetadataStatus:
    """Decide metadata status from available sides."""
    if not has_processed:
        return "failed"

    if inference_status == "success":
        return "complete"

    if inference_status in {"failed", "skipped"}:
        return "partial"


    return "ingestion_only"


def merge_records(
    ingestion_records: list[dict[str, Any]],
    inference_records: list[dict[str, Any]],
) -> list[MetadataRecord]:
    """
    Merge ingestion/inference dict records by image id.

    Ingestion is the left side (one metadata row per ingestion record).
    Inference is joined by image_id == ingestion id.
    """
    inference_by_id: dict[str, dict[str, Any]] = {}
    for item in inference_records:
        image_id = item.get("image_id")
        if image_id and image_id != "unknown":
            inference_by_id[str(image_id)] = item

    merged: list[MetadataRecord] = []
    generated_at = MetadataRecord.utc_now()

    for ing in ingestion_records:
        image_id = str(ing.get("id") or "unknown")
        processed_raw = ing.get("processed_path")
        has_processed = bool(processed_raw)

        inf = inference_by_id.get(image_id)
        inference_status = inf.get("status") if inf else None

        tags = list(inf.get("tags") or []) if inf else []
        objects = list(inf.get("objects") or []) if inf else []
        caption = inf.get("caption") if inf else None

        status = _decide_status(
            has_processed=has_processed,
            inference_status=inference_status,
        )

        error_parts: list[str] = []
        if ing.get("error_message"):
            error_parts.append(f"ingestion: {ing['error_message']}")
        if inf and inf.get("error_message"):
            error_parts.append(f"inference: {inf['error_message']}")

        record = MetadataRecord(
            id=image_id,
            status=status,
            generated_at=generated_at,
            original_filename=ing.get("original_filename"),
            source_path=Path(ing["source_path"]) if ing.get("source_path") else None,
            processed_path=Path(processed_raw) if processed_raw else None,
            extension=ing.get("extension"),
            width=ing.get("width"),
            height=ing.get("height"),
            format=ing.get("format"),
            file_size_bytes=ing.get("file_size_bytes"),
            checksum=ing.get("checksum") or None,
            ingested_at=_parse_datetime(ing.get("ingested_at")),
            ingestion_status=ing.get("status"),
            caption=caption,
            tags=tags,
            objects=objects,
            scene=_derive_scene(tags, caption),
            inference_backend=inf.get("backend") if inf else None,
            inferred_at=_parse_datetime(inf.get("inferred_at")) if inf else None,
            inference_status=inference_status,
            error_message="; ".join(error_parts) if error_parts else None,
        )
        merged.append(record)

    logger.info(
        "Merged metadata records: total={}, complete={}, partial={}, ingestion_only={}, failed={}",
        len(merged),
        sum(1 for r in merged if r.status == "complete"),
        sum(1 for r in merged if r.status == "partial"),
        sum(1 for r in merged if r.status == "ingestion_only"),
        sum(1 for r in merged if r.status == "failed"),
    )
    return merged


def merge_from_reports(
    ingestion_report_path: Path,
    inference_report_path: Path,
) -> list[MetadataRecord]:
    """Load both reports from disk and merge them."""
    ingestion_data = load_json_report(ingestion_report_path)
    inference_data = load_json_report(inference_report_path)

    ingestion_records = ingestion_data.get("records", [])
    inference_records = inference_data.get("records", [])

    if not isinstance(ingestion_records, list) or not isinstance(inference_records, list):
        raise MetadataError("Both reports must contain a list field named 'records'.")

    return merge_records(ingestion_records, inference_records)