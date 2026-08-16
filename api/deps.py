"""Shared dependencies for the API layer."""

from functools import lru_cache
from pathlib import Path

from pipeline.core.config import PipelineConfig, load_config


REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "default.yaml"

@lru_cache(maxsize=1)
def get_config() -> PipelineConfig:
    """Load pipeline config once (cached)."""
    if DEFAULT_CONFIG_PATH.exists():
        return load_config(DEFAULT_CONFIG_PATH)
    return PipelineConfig()
