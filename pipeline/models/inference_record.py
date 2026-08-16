"""Data model for VLM inference results."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

InferenceStatus = Literal["success", "failed", "skipped"]

@dataclass
class InferenceRecord:
    """Represents VLM inference output for one image."""
    image_id: str
    image_path: Path
    status: InferenceStatus
    inferred_at: datetime

    caption: str | None = None
    tags: list[str] = field(default_factory=list)
    objects: list[str] = field(default_factory=list)
    backend: str = "mock"
    error_message: str | None = None

    @staticmethod
    def utc_now() -> datetime:
        """Return current UTC time."""
        return datetime.now(timezone.utc)