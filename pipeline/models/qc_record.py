"""Data model for image quality-control results."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


QualityStatus = Literal["pass", "warn", "reject"]


@dataclass
class QCRecord:
    """Quality-control result for one image."""

    image_id: str
    image_path: Path
    checked_at: datetime

    is_corrupt: bool = False
    blur_score: float | None = None
    is_blurry: bool = False
    is_duplicate: bool = False
    duplicate_of: str | None = None

    quality_status: QualityStatus = "pass"
    error_message: str | None = None

    @staticmethod
    def utc_now() -> datetime:
        """Return current UTC time."""
        return datetime.now(timezone.utc)