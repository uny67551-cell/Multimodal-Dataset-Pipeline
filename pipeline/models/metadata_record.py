"""Data model for merged image metadata."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


MetadataStatus = Literal["complete", "partial", "ingestion_only", "failed"]


@dataclass
class MetadataRecord:
    """
    Unified metadata for one image.

    Merges Sprint 1 ingestion fields and Sprint 2 inference fields.
    """

    id: str
    status: MetadataStatus
    generated_at: datetime


    original_filename: str | None = None
    source_path: Path | None = None
    processed_path: Path | None = None
    extension: str | None = None
    width: int | None = None
    height: int | None = None
    format: str | None = None
    file_size_bytes: int | None = None
    checksum: str | None = None
    ingested_at: datetime | None = None
    ingestion_status: str | None = None


    caption: str | None = None
    tags: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    scene: str | None = None
    inference_backend: str | None = None
    inferred_at: datetime | None = None
    inference_status: str | None = None


    error_message: str | None = None

    @staticmethod
    def utc_now() -> datetime:
        """Return current UTC time."""
        return datetime.now(timezone.utc)