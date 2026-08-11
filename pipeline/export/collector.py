"""Collect export candidates by joining metadata and QC reports."""

import json
from pathlib import Path

from loguru import logger

from pipeline.core.exceptions import ExportError
from pipeline.models.export_record import ExportRecord


def _load_json(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise ExportError(f"Report not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _index_qc_records(qc_report: dict) -> dict[str, dict]:
    """Map image_id -> qc record dict."""
    indexed: dict[str, dict] = {}
    for record in qc_report.get("records", []):
        image_id = record.get("image_id")
        if image_id:
            indexed[str(image_id)] = record
    return indexed


def collect_export_candidates(
    metadata_report_path: Path,
    qc_report_path: Path | None = None,
) -> list[ExportRecord]:
    """
    Join metadata records with optional QC records.

    Notes:
    - Every metadata row becomes one ExportRecord (status still 'included'
      at this stage; filtering happens later).
    - If QC is missing for an id, QC fields stay at defaults / None.
    - Rows without a usable processed_path are still collected; filter can
      exclude them later.
    """
    metadata_report_path = Path(metadata_report_path)
    meta = _load_json(metadata_report_path)

    qc_index: dict[str, dict] = {}
    if qc_report_path is not None:
        qc_path = Path(qc_report_path)
        if qc_path.exists():
            qc_index = _index_qc_records(_load_json(qc_path))
            logger.info("Loaded {} QC rows from {}", len(qc_index), qc_path)
        else:
            logger.warning("QC report not found, continuing without QC: {}", qc_path)

    now = ExportRecord.utc_now()
    records: list[ExportRecord] = []

    for row in meta.get("records", []):
        image_id = row.get("id")
        if not image_id or image_id == "unknown":
            continue

        processed = row.get("processed_path")
        source_path = Path(processed) if processed else None

        qc = qc_index.get(str(image_id), {})

        extension = row.get("extension") or (
            source_path.suffix if source_path is not None else ".jpg"
        )
        # Planned relative path inside the export package (copy happens later).
        export_rel = f"images/{image_id}{extension}"

        records.append(
            ExportRecord(
                id=str(image_id),
                status="included",
                generated_at=now,
                source_image_path=source_path,
                export_image_relpath=export_rel,
                caption=row.get("caption"),
                tags=list(row.get("tags") or []),
                objects=list(row.get("objects") or []),
                scene=row.get("scene"),
                metadata_status=row.get("status"),
                quality_status=qc.get("quality_status"),
                is_corrupt=bool(qc.get("is_corrupt", False)),
                is_blurry=bool(qc.get("is_blurry", False)),
                is_duplicate=bool(qc.get("is_duplicate", False)),
                duplicate_of=qc.get("duplicate_of"),
                blur_score=qc.get("blur_score"),
            )
        )

    logger.info(
        "Collected {} export candidates from {}",
        len(records),
        metadata_report_path,
    )
    return records