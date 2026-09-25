"""Windows integration for Taskbar Alignment (Windows 11)."""

from __future__ import annotations

import sys
from typing import Literal

from winforge.core.logging import get_logger
from winforge.core.errors import ToyError

logger = get_logger("toy.taskbar_alignment.logic")

_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
_VALUE_NAME = "TaskbarAl"  # 0 = left, 1 = center


Alignment = Literal["left", "center"]


def _open_key(access: int):
    if sys.platform != "win32":
        raise ToyError(
            toy_name="Taskbar Alignment",
            message="This Toy only works on Windows.",
            details=f"Current platform: {sys.platform}",
        )
    import winreg
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH, 0, access)


def get_alignment() -> Alignment:
    """Return current taskbar alignment ('left' or 'center')."""
    try:
        import winreg
        with _open_key(winreg.KEY_READ) as key:
            try:
                value, _ = winreg.QueryValueEx(key, _VALUE_NAME)
                return "center" if value == 1 else "left"
            except FileNotFoundError:
                # Default on Windows 11 is center
                return "center"
    except Exception as exc:
        logger.error("Failed to read TaskbarAl: %s", exc)
        raise ToyError(
            toy_name="Taskbar Alignment",
            message="Unable to read current taskbar alignment.",
            details=str(exc),
        ) from exc


def set_alignment(alignment: Alignment) -> None:
    """Set taskbar alignment. Requires Windows 11."""
    value = 1 if alignment == "center" else 0
    try:
        import winreg
        with _open_key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, _VALUE_NAME, 0, winreg.REG_DWORD, value)
        logger.info("Set TaskbarAl = %s (%s)", value, alignment)
        _restart_explorer()
    except Exception as exc:
        logger.error("Failed to set TaskbarAl: %s", exc)
        raise ToyError(
            toy_name="Taskbar Alignment",
            message="Unable to change taskbar alignment.",
            details=str(exc),
            suggestion=(
                "Ensure you are running Windows 11. "
                "If the change does not appear, sign out and back in."
            ),
        ) from exc


def _restart_explorer() -> None:
    """Soft-restart Explorer so the taskbar updates."""
    if sys.platform != "win32":
        return
    try:
        import subprocess
        # Kill and let Windows restart Explorer
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            capture_output=True,
            check=False,
        )
        subprocess.Popen(["explorer.exe"], shell=False)
        logger.info("Restarted explorer.exe")
    except Exception as exc:
        logger.warning("Could not restart Explorer: %s", exc)


def verify_alignment(expected: Alignment) -> bool:
    try:
        return get_alignment() == expected
    except Exception:
        return False
