#!/usr/bin/env python3
"""
Logging configuration for Illuminate Media Organizer.

Copyright (C) 2025  Shiue-Lang Chin
Licensed under GPL-3.0-or-later
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and/or console handlers.

    Args:
        name: Name of the logger (usually __name__)
        log_file: Path to log file (optional, no file logging if None)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to output to console (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # If we can't create the log file, just warn and continue
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def get_default_log_path() -> str:
    """
    Get the default log file path based on the platform.

    Returns:
        Path to the default log file location
    """
    if sys.platform == 'win32':
        # Windows: Use LOCALAPPDATA
        base_path = Path(os.getenv('LOCALAPPDATA', Path.home()))
        log_dir = base_path / 'IlluminateMediaOrganizer' / 'logs'
    elif sys.platform == 'darwin':
        # macOS: Use ~/Library/Logs
        log_dir = Path.home() / 'Library' / 'Logs' / 'IlluminateMediaOrganizer'
    else:
        # Linux/Unix: Use ~/.local/share
        base_path = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        log_dir = base_path / 'illuminate-media-organizer' / 'logs'

    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir / 'media_organizer.log')


# Make os available for Windows path
import os
