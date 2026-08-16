"""Logging setup for the pipeline."""

import sys
from pathlib import Path
from loguru import logger

def setup_logger(level: str = "INFO", log_file: Path | None = None):
    """
    Configure loguru for CLI and pipeline usage.
    Args:
        level: Log level, e.g. INFO / DEBUG / WARNING.
        log_file: Optional path to write logs to disk.
    Returns:
        The configured loguru logger instance.
    """
    logger.remove()
    logger.add(sys.stderr, level=level)
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            level=level,
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8",
        )
    return logger