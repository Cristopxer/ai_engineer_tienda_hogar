from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

_LOGGING_CONFIGURED = False


def configure_logging(log_dir: str | Path | None = None, level: int = logging.INFO) -> Path:
    """Configure project logging to write to console and a per-run log file."""
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return _resolve_log_path(log_dir)

    log_path = _resolve_log_path(log_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.propagate = False

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Route Uvicorn logs through the same handlers
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.setLevel(level)
        uvicorn_logger.propagate = True

    _LOGGING_CONFIGURED = True
    return log_path


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _resolve_log_path(log_dir: str | Path | None = None) -> Path:
    base_dir = Path(log_dir) if log_dir is not None else Path.cwd() / "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return base_dir / f"run_{timestamp}.log"
