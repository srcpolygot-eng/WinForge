"""Centralized logging for WinForge."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

_LOG_DIR: Optional[Path] = None
_CONFIGURED = False


def setup_logging(
    level: int = logging.INFO,
    log_dir: Optional[Path] = None,
    console: bool = True,
) -> None:
    """Configure application-wide logging.

    Args:
        level: Logging level (default INFO).
        log_dir: Directory for log files. Defaults to ~/.winforge/logs.
        console: Whether to also log to console.
    """
    global _LOG_DIR, _CONFIGURED

    if _CONFIGURED:
        return

    if log_dir is None:
        log_dir = Path.home() / ".winforge" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _LOG_DIR = log_dir

    root = logging.getLogger("winforge")
    root.setLevel(level)
    root.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    file_handler = logging.FileHandler(
        log_dir / "winforge.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    _CONFIGURED = True
    root.debug("Logging initialized. Log directory: %s", log_dir)


def get_logger(name: str) -> logging.Logger:
    """Return a logger namespaced under winforge.

    Args:
        name: Logger name (usually __name__ or a short module id).

    Returns:
        Configured Logger instance.
    """
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(f"winforge.{name}")
