"""
utils.py — Logging setup and helper utilities.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import LOGS_DIR


def setup_logger(name: str = "healthcare_ai", level: int = logging.INFO) -> logging.Logger:
    """
    Create and return a logger with both console and rotating file handlers.

    Parameters
    ----------
    name : str
        Logger name (usually the module name).
    level : int
        Logging level.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler (rotating, max 5 MB, keep 3 backups)
    log_file = LOGS_DIR / "app.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


def validate_directory(path: Path, label: str = "Directory") -> None:
    """Raise FileNotFoundError if *path* does not exist or is not a directory."""
    if not path.exists():
        raise FileNotFoundError(f"{label} does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"{label} is not a directory: {path}")
