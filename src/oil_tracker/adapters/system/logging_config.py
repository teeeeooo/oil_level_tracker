from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from .app_paths import user_data_dir


def configure_logging() -> None:
    log_path = user_data_dir() / "oil_tracker.log"
    handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler], format="%(asctime)s %(levelname)s %(name)s %(message)s")
