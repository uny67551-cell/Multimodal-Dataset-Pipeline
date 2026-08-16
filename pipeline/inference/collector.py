"""Collect images that are ready for VLM inference."""

import json
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from pipeline.core.exceptions import InferenceError


@dataclass(frozen=True)
class InferenceTarget:
    """One image selected for inference."""

    image_id: str
    image_path: Path


def collect_from_report(report_path: Path) -> list[InferenceTarget]:
    """
    Collect inference targets from an ingestion report JSON.

    A record is usable when processed_path exists on disk.
    """

    report_path = Path(report_path)
    if not report_path.exists():
        raise InferenceError(f"Ingestion report not found: {report_path}")

    with report_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = data.get("records", [])
    targets: list[InferenceTarget] = []

    for record in records:
        processed = record.get("processed_path")
        image_id = record.get("id")

        if not processed or not image_id or image_id == "unknown":
            continue

        image_path = Path(processed)
        if not image_path.exists():
            logger.warning("Skip missing processed image: {}", image_path)
            continue

        targets.append(
            InferenceTarget(
                image_id=str(image_id),
                image_path=image_path,
            )
        )

    return targets


def collect_from_directory(
    processed_dir: Path,
    supported_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".bmp"),
) -> list[InferenceTarget]:
    """
    Fallback collector: scan processed directory directly.

    image_id is derived from the filename stem.
    """
    processed_dir = Path(processed_dir)
    if not processed_dir.exists():
        raise InferenceError(f"Processed directory not found: {processed_dir}")

    if not processed_dir.is_dir():
        raise InferenceError(f"Processed path is not a directory: {processed_dir}")

    normalized_exts = {ext.lower() for ext in supported_extensions}
    targets: list[InferenceTarget] = []

    for path in sorted(processed_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() not in normalized_exts:
            continue

        targets.append(
            InferenceTarget(
                image_id=path.stem,
                image_path=path,
            )
        )

    return targets


def collect_inference_targets(
    report_path: Path | None = None,
    processed_dir: Path | None = None,
) -> list[InferenceTarget]:
    """
    Collect targets with report-first strategy.

    Priority:
    1. ingestion report (if provided and exists)
    2. processed directory scan
    """
    if report_path is not None and Path(report_path).exists():
        targets = collect_from_report(report_path)
        logger.info(
            "Collected {} inference targets from report {}",
            len(targets),
            report_path,
        )
        return targets

    if processed_dir is None:
        raise InferenceError(
            "No ingestion report found and no processed_dir provided."
        )

    targets = collect_from_directory(processed_dir)
    logger.info(
        "Collected {} inference targets from directory {}",
        len(targets),
        processed_dir,
    )
    return targets