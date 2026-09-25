"""WinForge core infrastructure."""

from winforge.core.config import ConfigManager
from winforge.core.logging import get_logger, setup_logging
from winforge.core.windows import WindowsEnvironment, require_windows, is_admin
from winforge.core.backup import BackupManager
from winforge.core.toy_registry import ToyRegistry, ToyMetadata
from winforge.core.errors import WinForgeError, ToyError, PermissionError, UnsupportedVersionError

__all__ = [
    "ConfigManager",
    "get_logger",
    "setup_logging",
    "WindowsEnvironment",
    "require_windows",
    "is_admin",
    "BackupManager",
    "ToyRegistry",
    "ToyMetadata",
    "WinForgeError",
    "ToyError",
    "PermissionError",
    "UnsupportedVersionError",
]
