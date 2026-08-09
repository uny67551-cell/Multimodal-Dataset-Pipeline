"""Abstract interface for VLM backends."""

from abc import ABC, abstractmethod
from pathlib import Path
from pipeline.models.inference_record import InferenceRecord

class VLMBackend(ABC):
    """Base class for vision-language model backends."""

    @property # property is a decorator that makes a method a property
    @abstractmethod 
    def name(self) -> str:
        """Backend name, e.g. mock / local / api."""

    @abstractmethod
    def infer(self, image_path: Path, image_id: str) -> InferenceRecord:
        """
        Run inference on one image.
        Implementations should catch model-level errors and return
        InferenceRecord(status='failed') instead of crashing the batch.
        """
    