"""Mock VLM backend for development and tests without GPU."""

from pathlib import Path
from loguru import logger
from pipeline.inference.base import VLMBackend
from pipeline.models.inference_record import InferenceRecord

class MockVLM(VLMBackend):
    """Return deterministic fake captions/tags/objects."""

    @property
    def name(self) -> str:
        return "mock"

    def infer(self, image_path: Path, image_id: str) -> InferenceRecord:
        image_path = Path(image_path)
        inferred_at = InferenceRecord.utc_now()  # static method
        if not image_path.exists():
            logger.warning("MockVLM: image not found: {}", image_path)
            return InferenceRecord(
                image_id=image_id,
                image_path=image_path,
                status="failed",
                inferred_at=inferred_at,
                backend=self.name,
                error_message="Image not found",
            )
        stem = image_path.stem  # stem is the name of the image without the extension; property
        caption = f"A mock caption for image {stem}."
        tags = ["mock", "demo", stem[:8]]
        objects = ["object_a", "object_b"]
        logger.info("MockVLM inferred: {}", image_path.name)
        return InferenceRecord(
            image_id=image_id,
            image_path=image_path,
            status="success",
            inferred_at=inferred_at,
            caption=caption,
            tags=tags,
            objects=objects,
            backend=self.name,
            error_message=None,
        )