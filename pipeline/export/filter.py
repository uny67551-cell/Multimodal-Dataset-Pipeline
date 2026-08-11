"""Filter export candidates into included / excluded."""

from pathlib import Path

from loguru import logger

from pipeline.models.export_record import ExportRecord


def apply_export_filters(
    records: list[ExportRecord],
    *,
    exclude_duplicates: bool = True,
    include_blurry: bool = False,
    require_caption: bool = False,
) -> list[ExportRecord]:
    """
    Mutate and return records with status/exclude_reason set.

    Does not remove items from the list — keeps a full audit trail for
    export_report.json later.
    """
    for record in records:
        reason = _exclusion_reason(
            record,
            exclude_duplicates=exclude_duplicates,
            include_blurry=include_blurry,
            require_caption=require_caption,
        )
        if reason is None:
            record.status = "included"
            record.exclude_reason = None
        else:
            record.status = "excluded"
            record.exclude_reason = reason

    total = len(records)
    included = sum(1 for r in records if r.status == "included")
    excluded = total - included
    logger.info(
        "Export filter done | total: {} | included: {} | excluded: {} | "
        "exclude_duplicates={} | include_blurry={} | require_caption={}",
        total,
        included,
        excluded,
        exclude_duplicates,
        include_blurry,
        require_caption,
    )
    return records


def _exclusion_reason(
    record: ExportRecord,
    *,
    exclude_duplicates: bool,
    include_blurry: bool,
    require_caption: bool,
) -> str | None:
    """Return exclude reason, or None if the record should be included."""
    if record.metadata_status == "failed":
        return "metadata_failed"

    if record.source_image_path is None:
        return "missing_source_path"

    source = Path(record.source_image_path)
    if not source.exists() or not source.is_file():
        return "source_file_missing"

    if record.is_corrupt or record.quality_status == "reject":
        return "corrupt_or_reject"

    if exclude_duplicates and record.is_duplicate:
        return "duplicate"

    if not include_blurry and record.is_blurry:
        return "blurry"

    if require_caption and not (record.caption and str(record.caption).strip()):
        return "missing_caption"

    return None


def iter_included(records: list[ExportRecord]) -> list[ExportRecord]:
    """Return only included records (convenience for writers)."""
    return [record for record in records if record.status == "included"]