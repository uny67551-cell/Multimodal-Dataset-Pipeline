"""Data model for a single image in the pipeline."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

ImageStatus = Literal["valid", "invalid", "skipped"]


@dataclass
class ImageRecord:
    """Represents one image in the pipeline."""

    id: str
    source_path: Path
    original_filename: str
    extension: str
    file_size_bytes: int
    checksum: str
    status: ImageStatus
    ingested_at: datetime

    processed_path: Path | None = None
    width: int | None = None
    height: int | None = None
    format: str | None = None
    error_message: str | None = None

    @staticmethod
    def utc_now() -> datetime:
        """Return current UTC time."""
        return datetime.now(timezone.utc)