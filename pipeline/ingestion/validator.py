"""Validate image files and build ImageRecord objects."""

import hashlib
from pathlib import Path

from loguru import logger
from PIL import Image
from tqdm import tqdm

from pipeline.models.image_record import ImageRecord

def compute_checksum(path: Path) -> str:
    """Compute SHA256 checksum for a file."""

    sha256 = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_image_id(path: Path, file_size: int, checksum: str) -> str:
    """Generate a unique image ID."""
    raw = f"{path.name}:{file_size}:{checksum}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def validate_image(path: Path) -> ImageRecord:
    """
    Validate an image file and return an ImageRecord.

    Never raise for normal file-level errors;
    invalid images are returned with status='invalid'.
    """

    path = Path(path)
    original_filename = path.name
    extension = path.suffix.lower()
    ingested_at = ImageRecord.utc_now()

    if not path.exists():
        return ImageRecord(
            id="unknown",
            source_path=path,
            original_filename=original_filename,
            extension=extension,
            file_size_bytes=0,
            checksum="",
            status="invalid",
            ingested_at=ingested_at,
            error_message="File not found",
        )

    file_size = path.stat().st_size
    if file_size == 0:
        return ImageRecord(
            id="unknown",
            source_path=path,
            original_filename=original_filename,
            extension=extension,
            file_size_bytes=0,
            checksum="",
            status="invalid",
            ingested_at=ingested_at,
            error_message="Empty file",
        )

    try:
        checksum = compute_checksum(path)

        with Image.open(path) as img:
            img.verify()

        with Image.open(path) as img:
            width, height = img.size
            image_format = img.format

        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")

        image_id = generate_image_id(path, file_size, checksum)


        return ImageRecord(
            id=image_id,
            source_path=path,
            original_filename=original_filename,
            extension=extension,
            file_size_bytes=file_size,
            checksum=checksum,
            status="valid",
            ingested_at=ingested_at,
            processed_path=None,
            width=width,
            height=height,
            format=image_format,
            error_message=None,
        )

    except Exception as exc:
        logger.warning("Validation failed for {}: {}", path, exc)
        return ImageRecord(
            id="unknown",
            source_path=path,
            original_filename=original_filename,
            extension=extension,
            file_size_bytes=file_size,
            checksum="",
            status="invalid",
            ingested_at=ingested_at,
            error_message=str(exc),
        )

def validate_batch(
    paths: list[Path],
    show_progress: bool = True,
) -> list[ImageRecord]:
    """Validate multiple images and return ImageRecord objects."""
    iterator = tqdm(paths, desc="Validating images") if show_progress else paths
    return [validate_image(path) for path in iterator]
