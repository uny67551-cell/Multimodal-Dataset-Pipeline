"""Data model for a single image in the pipeline."""

from dataclasses import dataclass #dataclass is a built-in function that creates a class from a dictionary.
from datetime import datetime, timezone 
from pathlib import Path
from typing import Literal 

ImageStatus = Literal["valid", "invalid", "skipped"] # Locked type for the image status and it can be either valid, invalid or skipped.
                                                     # Autocompletion will be available for the image status.

@dataclass # This is a decorator that tells Python to create a class from the dataclass.
           # @ is the decorator syntax in Python.
class ImageRecord: # preprocessed image record
    """Represents one image in the pipeline."""

    id: str  # no default value, mandatory field that needs to be input 
    source_path: Path
    original_filename: str
    extension: str
    file_size_bytes: int
    checksum: str
    status: ImageStatus
    ingested_at: datetime

    processed_path: Path | None = None # Path | None is a type hint that says the processed_path can be either a Path object or None.
    width: int | None = None
    height: int | None = None
    format: str | None = None
    error_message: str | None = None 

    @staticmethod #static method is a method no need instantiation and to pass the self argument 
    def utc_now() -> datetime:
        """Return current UTC time."""
        return datetime.now(timezone.utc)