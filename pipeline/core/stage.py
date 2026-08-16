"""Base class for pipeline stages."""

from abc import ABC, abstractmethod
from pathlib import Path
from pipeline.models.image_record import ImageRecord

class PipelineStage(ABC):
    """Abstract base class for a pipeline stage."""
    @abstractmethod
    def run(self, input_dir: Path | None = None) -> list[ImageRecord]:
        """Execute the stage and return image records."""