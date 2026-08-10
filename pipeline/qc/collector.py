"""Collect images for quality control."""

import json
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from pipeline.core.exceptions import QCError


@dataclass(frozen=True)
class QCTarget:
    """One image selected for QC."""

    image_id: str
    image_path: Path
    checksum: str | None = None


def collect_from_metadata_report(report_path: Path) -> list[QCTarget]:
    """Collect QC targets from metadata_report.json."""
    report_path = Path(report_path)
    if not report_path.exists():
        raise QCError(f"Metadata report not found: {report_path}")

    with report_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    targets: list[QCTarget] = []
    for record in data.get("records", []):
        image_id = record.get("id")
        processed = record.get("processed_path")
        if not image_id or image_id == "unknown" or not processed:
            continue

        image_path = Path(processed)
        if not image_path.exists():
            logger.warning("Skip missing processed image: {}", image_path)
            continue

        checksum = record.get("checksum") or None
        targets.append(
            QCTarget(
                image_id=str(image_id),
                image_path=image_path,
                checksum=checksum,
            )
        )

    return targets


def collect_from_directory(
    processed_dir: Path,
    supported_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".bmp"),
) -> list[QCTarget]:
    """Fallback: scan processed directory."""
    processed_dir = Path(processed_dir)
    if not processed_dir.exists() or not processed_dir.is_dir():
        raise QCError(f"Processed directory not found: {processed_dir}")

    normalized = {ext.lower() for ext in supported_extensions}
    targets: list[QCTarget] = []

    for path in sorted(processed_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in normalized:
            continue
        targets.append(QCTarget(image_id=path.stem, image_path=path))

    return targets


def collect_qc_targets(
    metadata_report_path: Path | None = None,
    processed_dir: Path | None = None,
) -> list[QCTarget]:
    """
    Collect targets with metadata-report-first strategy.

    Priority:
    1. metadata report (if provided and exists)
    2. processed directory scan
    """
    if metadata_report_path is not None and Path(metadata_report_path).exists():
        targets = collect_from_metadata_report(metadata_report_path)
        logger.info(
            "Collected {} QC targets from metadata report {}",
            len(targets),
            metadata_report_path,
        )
        return targets

    if processed_dir is None:
        raise QCError(
            "No metadata report found and no processed_dir provided."
        )

    targets = collect_from_directory(processed_dir)
    logger.info(
        "Collected {} QC targets from directory {}",
        len(targets),
        processed_dir,
    )
    return targets