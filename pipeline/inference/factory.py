"""Factory for creating VLM backends."""

from pipeline.core.config import InferenceConfig
from pipeline.core.exceptions import InferenceError
from pipeline.inference.base import VLMBackend
from pipeline.inference.mock_vlm import MockVLM


def create_backend(inference: InferenceConfig) -> VLMBackend:
    """Create a VLM backend from inference config."""
    name = inference.backend.strip().lower()

    if name == "mock":
        return MockVLM()

    if name == "local":
        from pipeline.inference.qwen_local import QwenLocalVLM

        return QwenLocalVLM(inference)

    if name == "api":
        from pipeline.inference.qwen_api import QwenAPIVLM

        return QwenAPIVLM(inference)

    raise InferenceError(
        f"Unknown inference backend: {inference.backend!r}. "
        "Expected one of: mock, local, api."
    )