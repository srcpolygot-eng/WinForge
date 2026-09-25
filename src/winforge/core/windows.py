"""Windows environment detection and permission helpers."""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from typing import Optional

from winforge.core.logging import get_logger

logger = get_logger("windows")


@dataclass(frozen=True)
class WindowsEnvironment:
    """Immutable snapshot of the current Windows environment."""

    is_windows: bool
    version: str          # e.g. "10.0.22631" or "6.3.9600"
    major: int            # NT major (6 for 8.1, 10 for 10/11)
    minor: int
    build: int
    edition: str          # e.g. "Professional"
    is_admin: bool
    architecture: str     # "AMD64", "ARM64", etc.
    product_name: str     # "Windows 11 Pro", "Windows 8.1", etc.

    @property
    def is_windows_8_1(self) -> bool:
        """Windows 8.1 is NT 6.3."""
        return self.is_windows and self.major == 6 and self.minor == 3

    @property
    def is_windows_10(self) -> bool:
        """Windows 10 (builds below 22000)."""
        return (
            self.is_windows
            and self.major == 10
            and self.build < 22000
        )

    @property
    def is_windows_11(self) -> bool:
        """Windows 11 is reported as major 10 with build >= 22000."""
        return self.is_windows and self.major == 10 and self.build >= 22000

    @property
    def is_windows_10_or_later(self) -> bool:
        return self.is_windows and self.major >= 10

    @property
    def is_windows_8_1_or_later(self) -> bool:
        """Windows 8.1, 10, or 11."""
        if not self.is_windows:
            return False
        if self.major > 6:
            return True
        if self.major == 6 and self.minor >= 3:
            return True
        return False

    @property
    def friendly_name(self) -> str:
        """Human-readable OS name for UI badges."""
        if not self.is_windows:
            return self.product_name or "Non-Windows"
        if self.is_windows_11:
            return f"{self.product_name or 'Windows 11'} (11)"
        if self.is_windows_10:
            return f"{self.product_name or 'Windows 10'} (10)"
        if self.is_windows_8_1:
            return f"{self.product_name or 'Windows 8.1'} (8.1)"
        return self.product_name or f"Windows {self.major}.{self.minor}"

    def requires(
        self,
        min_build: int = 0,
        windows_11: bool = False,
        min_major: int = 0,
    ) -> bool:
        """Check whether the environment meets minimum requirements."""
        if not self.is_windows:
            return False
        if windows_11 and not self.is_windows_11:
            return False
        if min_major and self.major < min_major:
            return False
        if min_build and self.build < min_build:
            return False
        return True


_cached_env: Optional[WindowsEnvironment] = None


def get_windows_environment(force_refresh: bool = False) -> WindowsEnvironment:
    """Detect and cache the current Windows environment."""
    global _cached_env
    if _cached_env is not None and not force_refresh:
        return _cached_env

    is_windows = sys.platform == "win32"
    version = "0.0.0"
    major = minor = build = 0
    edition = "Unknown"
    product_name = "Unknown"
    architecture = platform.machine() or "Unknown"
    admin = False

    if is_windows:
        try:
            # platform.version() returns something like "10.0.22631"
            ver_str = platform.version()
            parts = ver_str.split(".")
            if len(parts) >= 3:
                major = int(parts[0])
                minor = int(parts[1])
                build = int(parts[2])
            version = ver_str
        except Exception as exc:
            logger.warning("Failed to parse Windows version: %s", exc)

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            )
            try:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
            except FileNotFoundError:
                pass
            try:
                edition = winreg.QueryValueEx(key, "EditionID")[0]
            except FileNotFoundError:
                pass
            # More accurate build
            try:
                build_str = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                build = int(build_str)
            except (FileNotFoundError, ValueError):
                pass
            winreg.CloseKey(key)
        except Exception as exc:
            logger.debug("Could not read Windows registry for product info: %s", exc)

        admin = _check_admin()

    _cached_env = WindowsEnvironment(
        is_windows=is_windows,
        version=version,
        major=major,
        minor=minor,
        build=build,
        edition=edition,
        is_admin=admin,
        architecture=architecture,
        product_name=product_name,
    )
    logger.info(
        "Detected environment: %s (build %s), admin=%s",
        product_name,
        build,
        admin,
    )
    return _cached_env


def _check_admin() -> bool:
    """Return True if the current process has administrator privileges."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def is_admin() -> bool:
    """Convenience wrapper."""
    return get_windows_environment().is_admin


def require_windows() -> WindowsEnvironment:
    """Raise if not running on Windows."""
    env = get_windows_environment()
    if not env.is_windows:
        from winforge.core.errors import UnsupportedVersionError
        raise UnsupportedVersionError(
            required="Windows",
            current=platform.system(),
            details="WinForge is designed exclusively for Microsoft Windows.",
        )
    return env


def require_admin() -> None:
    """Raise PermissionError if not running elevated."""
    if not is_admin():
        from winforge.core.errors import PermissionError as WFPermissionError
        raise WFPermissionError()
