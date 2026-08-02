"""Validate image files and build ImageRecord objects."""

import hashlib # hashlib is a module that provides a hash function
from pathlib import Path

from loguru import logger # loguru is a module that provides a logger
from PIL import Image # PIL is a module that can process images
from tqdm import tqdm # progress bar 

from pipeline.models.image_record import ImageRecord # format: from the first subfile of root directory to module script

def compute_checksum(path: Path) -> str:  # fingerprinting algorithm
    """Compute SHA256 checksum for a file."""

    sha256 = hashlib.sha256()
    with path.open("rb") as file:  # read in binary mode "rb"
        for chunk in iter(lambda: file.read(4096), b""):  # read in chunks of 4096 bytes，Form:iter(function, endvalue(binary""))
            sha256.update(chunk)  # update or add the SHA256 checksum with the current chunk
    return sha256.hexdigest()  # return the hexadecimal representation of the SHA256 checksum

def generate_image_id(path: Path, file_size: int, checksum: str) -> str:
    """Generate a unique image ID."""
    raw = f"{path.name}:{file_size}:{checksum}"  # create a raw string
    return hashlib.sha256(raw.encode()).hexdigest()[:12] # encode raw into binary and return the first 12 characters

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

    file_size = path.stat().st_size  # get st_size by stat() method
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

        with Image.open(path) as img:  # check if the image is valid
            img.verify()  # verify() is a method form PIL to verify if the image is valid
                          # File handle has been moved to the end, so getting size is not possible
        with Image.open(path) as img:
            width, height = img.size
            image_format = img.format

        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}") # sometime broken images have invalid dimensions

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
        logger.warning("Validation failed for {}: {}", path, exc) # {} is a placeholder for the path and exc
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
    return [validate_image(path) for path in iterator] # return list[validate_image(path) = ImageRecord]
                                                       # [...] return a list