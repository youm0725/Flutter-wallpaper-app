import logging
import sys
from pathlib import Path
from app.utils.path_helper import PathHelper

def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """Configures application-wide logging system writing to console and log file."""
    logs_dir = PathHelper.get_logs_dir()
    log_file = logs_dir / "app.log"

    logger = logging.getLogger("WallpaperAssetManager")
    logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging system initialized. Log file: %s", log_file)
    return logger

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"WallpaperAssetManager.{name}")
