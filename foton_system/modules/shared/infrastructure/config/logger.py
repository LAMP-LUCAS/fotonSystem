"""
Logger: Centralized logging configuration for FotonSystem.

Logs are written to both console and file (in AppData).
"""

import logging
import sys
from pathlib import Path

from foton_system.modules.shared.infrastructure.services.path_manager import PathManager


def setup_logger(name: str = "foton_system", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger that writes to a file and the console.
    
    Args:
        name: Logger name (default: "foton_system")
        level: Logging level (default: INFO)
    
    Returns:
        Configured Logger instance
    """
    # Always use AppData for log file to avoid permission issues
    log_dir = PathManager.get_app_data_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = PathManager.get_log_path()

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times if logger is already configured
    if logger.handlers:
        return logger

    # Console handler
    c_handler = logging.StreamHandler(sys.stdout)

    c_handler.setLevel(level)
    c_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File handler
    try:
        f_handler = logging.FileHandler(str(log_file_path), encoding='utf-8')
        f_handler.setLevel(level)
        f_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
    except Exception as e:
        # Fallback: continue without file logging
        logger.warning(f"Could not initialize log file at {log_file_path}: {e}")

    return logger
