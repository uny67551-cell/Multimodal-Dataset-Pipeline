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
    logger.remove()  # remove all existing handlers
    logger.add(sys.stderr, level=level) # diy handler to stderr; sys.stderr is a pipleline to CLI output
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True) 
        logger.add(    # add a new handler to the log file, (configs)
            log_file,
            level=level,
            rotation="10 MB",  # rotate log file every 10MB
            retention="7 days",  # keep logs for 7 days
            encoding="utf-8",
        )
    return logger  # return the logger instance for further use