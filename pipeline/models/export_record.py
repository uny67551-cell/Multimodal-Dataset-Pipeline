"""Data model for one exportable training sample."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


ExportStatus = Literal["included", "excluded"]


@dataclass
class ExportRecord:
    """
    One candidate sample for dataset export.

    Built by joining metadata + QC, then optionally filtered.
    """

    id: str
    status: ExportStatus
    generated_at: datetime


    source_image_path: Path | None = None


    export_image_relpath: str | None = None


    caption: str | None = None
    tags: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    scene: str | None = None
    metadata_status: str | None = None


    quality_status: str | None = None
    is_corrupt: bool = False
    is_blurry: bool = False
    is_duplicate: bool = False
    duplicate_of: str | None = None
    blur_score: float | None = None


    exclude_reason: str | None = None

    @staticmethod
    def utc_now() -> datetime:
        """Return current UTC time."""
        return datetime.now(timezone.utc)