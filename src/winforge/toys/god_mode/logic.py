"""Logic for creating / removing the God Mode folder."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from winforge.core.logging import get_logger
from winforge.core.errors import ToyError

logger = get_logger("toy.god_mode.logic")

# The magic CLSID that turns a folder into God Mode
GOD_MODE_NAME = "GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}"


def default_location() -> Path:
    """Default place to create the folder – user's Desktop."""
    return Path.home() / "Desktop" / GOD_MODE_NAME


def exists(path: Optional[Path] = None) -> bool:
    p = path or default_location()
    return p.is_dir()


def create(path: Optional[Path] = None) -> Path:
    """Create the God Mode folder. Returns the path created."""
    if sys.platform != "win32":
        raise ToyError(
            toy_name="God Mode",
            message="God Mode is a Windows-only feature.",
            details=f"Current platform: {sys.platform}",
        )

    target = path or default_location()
    if target.exists():
        if target.is_dir():
            logger.info("God Mode folder already exists at %s", target)
            return target
        raise ToyError(
            toy_name="God Mode",
            message="A file with the same name already exists.",
            details=str(target),
            suggestion="Rename or delete the conflicting file and try again.",
        )

    try:
        target.mkdir(parents=True, exist_ok=False)
        logger.info("Created God Mode folder at %s", target)
        return target
    except OSError as exc:
        raise ToyError(
            toy_name="God Mode",
            message="Failed to create God Mode folder.",
            details=str(exc),
            suggestion="Check that you have write permission to the target location.",
        ) from exc


def remove(path: Optional[Path] = None) -> None:
    """Remove the God Mode folder if it exists and is empty of user files."""
    target = path or default_location()
    if not target.exists():
        return
    if not target.is_dir():
        raise ToyError(
            toy_name="God Mode",
            message="Target exists but is not a directory.",
            details=str(target),
        )
    try:
        # Only remove if it looks like our God Mode folder (name match)
        if not target.name.startswith("GodMode.{ED7BA470"):
            raise ToyError(
                toy_name="God Mode",
                message="Refusing to delete a folder that does not look like God Mode.",
                details=str(target),
            )
        # God Mode folders are virtual; they appear empty to normal APIs
        target.rmdir()
        logger.info("Removed God Mode folder at %s", target)
    except OSError as exc:
        raise ToyError(
            toy_name="God Mode",
            message="Failed to remove God Mode folder.",
            details=str(exc),
            suggestion="Close any open windows inside the folder and try again.",
        ) from exc
