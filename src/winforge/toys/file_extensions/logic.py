"""Windows integration for File Extensions Toy."""

from __future__ import annotations

import sys
from typing import Optional, Tuple

from winforge.core.logging import get_logger
from winforge.core.errors import ToyError

logger = get_logger("toy.file_extensions.logic")

# Registry path used by Explorer
_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
_VALUE_NAME = "HideFileExt"


def _open_key(access: int):
    if sys.platform != "win32":
        raise ToyError(
            toy_name="File Extensions",
            message="This Toy only works on Windows.",
            details=f"Current platform: {sys.platform}",
        )
    import winreg
    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        _REG_PATH,
        0,
        access,
    )


def get_hide_extensions() -> bool:
    """Return True if extensions are currently hidden."""
    try:
        import winreg
        with _open_key(winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, _VALUE_NAME)
            return bool(value)
    except FileNotFoundError:
        # Default on most systems is to hide
        return True
    except Exception as exc:
        logger.error("Failed to read HideFileExt: %s", exc)
        raise ToyError(
            toy_name="File Extensions",
            message="Unable to read current setting.",
            details=str(exc),
            suggestion="Ensure you have permission to read the Windows registry.",
        ) from exc


def set_hide_extensions(hide: bool) -> None:
    """Set whether to hide known file extensions.

    Args:
        hide: True to hide extensions, False to show them.
    """
    try:
        import winreg
        with _open_key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, _VALUE_NAME, 0, winreg.REG_DWORD, 1 if hide else 0)
        logger.info("Set HideFileExt = %s", 1 if hide else 0)
        # Notify Explorer to refresh
        _notify_explorer()
    except PermissionError as exc:
        raise ToyError(
            toy_name="File Extensions",
            message="Permission denied while writing registry.",
            details=str(exc),
            suggestion="Try running WinForge as a normal user (this setting is per-user).",
        ) from exc
    except Exception as exc:
        logger.error("Failed to set HideFileExt: %s", exc)
        raise ToyError(
            toy_name="File Extensions",
            message="Unable to apply the requested change.",
            details=str(exc),
        ) from exc


def _notify_explorer() -> None:
    """Broadcast a settings change so Explorer refreshes."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002

        result = ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "ShellEnvironment_Changed",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(wintypes.DWORD()),
        )
        logger.debug("SendMessageTimeout result: %s", result)
    except Exception as exc:
        logger.warning("Could not notify Explorer of settings change: %s", exc)


def verify_setting(expected_hide: bool) -> bool:
    """Return True if the live registry value matches the expected state."""
    try:
        return get_hide_extensions() == expected_hide
    except Exception:
        return False
