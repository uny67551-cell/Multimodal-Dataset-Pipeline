"""Shared dependencies for the API layer."""

from functools import lru_cache # function to cache the result of a function
from pathlib import Path

from pipeline.core.config import PipelineConfig, load_config

# Repo root = parent of api/
REPO_ROOT = Path(__file__).resolve().parent.parent # resolve() -> returns the absolute path of the file
                                                   # Path(__file__) -> returns the path to the current file
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "default.yaml"

@lru_cache(maxsize=1)
def get_config() -> PipelineConfig:
    """Load pipeline config once (cached)."""
    if DEFAULT_CONFIG_PATH.exists():
        return load_config(DEFAULT_CONFIG_PATH)
    return PipelineConfig()
