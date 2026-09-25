"""Windows integration for Clipboard History."""

from __future__ import annotations

import sys
from typing import Optional

from winforge.core.logging import get_logger
from winforge.core.errors import ToyError

logger = get_logger("toy.clipboard_history.logic")

# Windows 10 1809+ / Windows 11
_REG_PATH = r"Software\Microsoft\Clipboard"
_VALUE_NAME = "EnableClipboardHistory"


def _open_key(access: int):
    if sys.platform != "win32":
        raise ToyError(
            toy_name="Clipboard History",
            message="This Toy only works on Windows.",
            details=f"Current platform: {sys.platform}",
        )
    import winreg
    # Ensure the key exists
    try:
        return winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH, 0, access)
    except FileNotFoundError:
        if access & winreg.KEY_SET_VALUE:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, _REG_PATH)
            return winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH, 0, access)
        raise


def is_enabled() -> bool:
    """Return True if Clipboard History is enabled."""
    try:
        import winreg
        with _open_key(winreg.KEY_READ) as key:
            try:
                value, _ = winreg.QueryValueEx(key, _VALUE_NAME)
                return bool(value)
            except FileNotFoundError:
                # Default is often enabled on modern Windows
                return True
    except Exception as exc:
        logger.error("Failed to read EnableClipboardHistory: %s", exc)
        raise ToyError(
            toy_name="Clipboard History",
            message="Unable to read current Clipboard History setting.",
            details=str(exc),
        ) from exc


def set_enabled(enabled: bool) -> None:
    """Enable or disable Clipboard History."""
    try:
        import winreg
        with _open_key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(
                key, _VALUE_NAME, 0, winreg.REG_DWORD, 1 if enabled else 0
            )
        logger.info("Set EnableClipboardHistory = %s", 1 if enabled else 0)
    except Exception as exc:
        logger.error("Failed to set EnableClipboardHistory: %s", exc)
        raise ToyError(
            toy_name="Clipboard History",
            message="Unable to change Clipboard History setting.",
            details=str(exc),
            suggestion=(
                "On some Windows editions this feature may be managed by policy. "
                "You can also toggle it in Settings → System → Clipboard."
            ),
        ) from exc


def verify(expected: bool) -> bool:
    try:
        return is_enabled() == expected
    except Exception:
        return False
