"""Copy included images into the export package."""

import shutil
from pathlib import Path

from loguru import logger

from pipeline.core.exceptions import ExportError
from pipeline.export.filter import iter_included
from pipeline.models.export_record import ExportRecord


def copy_export_images(
    records: list[ExportRecord],
    export_dir: Path,
) -> int:
    """
    Copy included source images into export_dir using export_image_relpath.

    Returns:
        Number of files copied.
    """
    export_dir = Path(export_dir)
    images_root = export_dir / "images"
    images_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    for record in iter_included(records):
        if record.source_image_path is None or record.export_image_relpath is None:
            raise ExportError(f"Included record missing image paths: {record.id}")

        src = Path(record.source_image_path)
        dst = export_dir / record.export_image_relpath
        dst.parent.mkdir(parents=True, exist_ok=True)

        if not src.exists():
            raise ExportError(f"Source image missing for {record.id}: {src}")

        shutil.copy2(src, dst)
        copied += 1

    logger.info("Copied {} images into {}", copied, images_root)
    return copied