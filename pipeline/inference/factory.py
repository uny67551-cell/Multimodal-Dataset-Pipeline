"""Factory for creating VLM backends."""

from pipeline.core.config import InferenceConfig
from pipeline.core.exceptions import InferenceError
from pipeline.inference.base import VLMBackend
from pipeline.inference.mock_vlm import MockVLM


def create_backend(
    inference: InferenceConfig,
    *,
    api_key: str | None = None,
) -> VLMBackend:
    """Create a VLM backend from inference config.

    api_key is a per-call override for backend=api. It is never written
    to YAML. Empty/None falls back to the environment variable named in
    inference.api_key_env.
    """
    name = inference.backend.strip().lower()

    if name == "mock":
        return MockVLM()

    if name == "local":
        from pipeline.inference.qwen_local import QwenLocalVLM

        return QwenLocalVLM(inference)

    if name == "api":
        from pipeline.inference.qwen_api import QwenAPIVLM

        return QwenAPIVLM(inference, api_key=api_key)

    raise InferenceError(
        f"Unknown inference backend: {inference.backend!r}. "
        "Expected one of: mock, local, api."
    )