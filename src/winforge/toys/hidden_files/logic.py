"""Windows integration for Hidden Files Toy."""

from __future__ import annotations

import sys
from typing import Dict

from winforge.core.logging import get_logger
from winforge.core.errors import ToyError

logger = get_logger("toy.hidden_files.logic")

_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
# Hidden: 1 = show, 2 = hide (historic Windows values)
# ShowSuperHidden: 0/1 for protected OS files


def _open_key(access: int):
    if sys.platform != "win32":
        raise ToyError(
            toy_name="Hidden Files",
            message="This Toy only works on Windows.",
            details=f"Current platform: {sys.platform}",
        )
    import winreg
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH, 0, access)


def get_state() -> Dict[str, bool]:
    """Return current visibility flags.

    Returns:
        dict with keys:
          - show_hidden: True if hidden files are shown
          - show_system: True if protected operating system files are shown
    """
    try:
        import winreg
        with _open_key(winreg.KEY_READ) as key:
            try:
                hidden_val, _ = winreg.QueryValueEx(key, "Hidden")
            except FileNotFoundError:
                hidden_val = 2  # default = hide
            try:
                super_val, _ = winreg.QueryValueEx(key, "ShowSuperHidden")
            except FileNotFoundError:
                super_val = 0

            return {
                "show_hidden": hidden_val == 1,
                "show_system": bool(super_val),
            }
    except Exception as exc:
        logger.error("Failed to read hidden-files settings: %s", exc)
        raise ToyError(
            toy_name="Hidden Files",
            message="Unable to read current settings.",
            details=str(exc),
        ) from exc


def set_state(show_hidden: bool, show_system: bool) -> None:
    """Apply the desired visibility settings."""
    try:
        import winreg
        with _open_key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(
                key, "Hidden", 0, winreg.REG_DWORD, 1 if show_hidden else 2
            )
            winreg.SetValueEx(
                key, "ShowSuperHidden", 0, winreg.REG_DWORD, 1 if show_system else 0
            )
        logger.info(
            "Set Hidden=%s, ShowSuperHidden=%s",
            1 if show_hidden else 2,
            1 if show_system else 0,
        )
        _notify_explorer()
    except Exception as exc:
        logger.error("Failed to set hidden-files settings: %s", exc)
        raise ToyError(
            toy_name="Hidden Files",
            message="Unable to apply the requested changes.",
            details=str(exc),
        ) from exc


def _notify_explorer() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "ShellEnvironment_Changed",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(wintypes.DWORD()),
        )
    except Exception as exc:
        logger.warning("Could not notify Explorer: %s", exc)


def verify_state(expected: Dict[str, bool]) -> bool:
    try:
        current = get_state()
        return (
            current["show_hidden"] == expected["show_hidden"]
            and current["show_system"] == expected["show_system"]
        )
    except Exception:
        return False
