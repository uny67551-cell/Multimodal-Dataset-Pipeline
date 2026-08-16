"""Organize images into subdirectories based on the file extension."""

import shutil
from pathlib import Path
from loguru import logger
from typing import Literal
from pipeline.models.image_record import ImageRecord

OrganizeMode = Literal["copy", "move"]

def organize_image(
    record: ImageRecord,
    output_dir: Path,
    mode: OrganizeMode = "copy",
) -> ImageRecord:
    """
    copy or move one valid image into output_dir.

    Args:
        record: ImageRecord to organize.
        output_dir: Directory to organize the image into.
        mode: 'copy' keeps source file, 'move' removes source file.

    Returns:
        Updated ImageRecord.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if record.status != "valid":
        logger.debug(f"Skipping invalid image: {record.source_path}")
        return record

    destination = output_dir / f"{record.id}{record.extension}"

    if destination.exists():
        record.processed_path = destination
        record.status = "skipped"
        record.error_message = "Destination already exists"
        logger.info("Skipped existing file: {}", destination)
        return record

    if mode == "copy":
        shutil.copy(record.source_path, destination)
    elif mode == "move":
        shutil.move(record.source_path, destination)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    record.processed_path = destination
    record.status = "valid"
    record.error_message = None
    logger.info("Organized {} -> {}", record.source_path, destination)
    return record

def organize_batch(
    records: list[ImageRecord],
    output_dir: Path,
    mode: OrganizeMode = "copy",
) -> list[ImageRecord]:
    """Organize multiple ImageRecord objects."""
    return [organize_image(record, output_dir, mode=mode) for record in records]
