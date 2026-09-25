"""Base class that every WinForge Toy must inherit from."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

from winforge.core.toy_registry import ToyMetadata
from winforge.core.config import ConfigManager
from winforge.core.backup import BackupManager
from winforge.core.windows import WindowsEnvironment, get_windows_environment
from winforge.core.logging import get_logger
from winforge.core.errors import ToyError, UnsupportedVersionError

if TYPE_CHECKING:
    import tkinter as tk


class BaseToy(ABC):
    """Abstract base for all Toys.

    Subclasses must:
      - Define a class-level `metadata: ToyMetadata`
      - Implement `create_ui(parent)` 
      - Implement `get_current_state()` / `apply()` / `reset()` as needed
    """

    metadata: ToyMetadata  # must be overridden by subclass

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        backup_manager: Optional[BackupManager] = None,
    ) -> None:
        self.logger = get_logger(f"toy.{self.metadata.id}")
        self.config_manager = config_manager or ConfigManager()
        self.backup_manager = backup_manager or BackupManager(self.config_manager)
        self.env: WindowsEnvironment = get_windows_environment()
        self._user_config: Dict[str, Any] = {}
        self._load_user_config()

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def _load_user_config(self) -> None:
        self._user_config = self.config_manager.load_toy_config(self.metadata.id)

    def save_user_config(self) -> None:
        self.config_manager.save_toy_config(self.metadata.id, self._user_config)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._user_config.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self._user_config[key] = value

    # ------------------------------------------------------------------
    # Compatibility checks
    # ------------------------------------------------------------------

    def check_compatibility(self) -> None:
        """Raise UnsupportedVersionError if the current OS does not meet requirements."""
        if not self.env.is_windows:
            raise UnsupportedVersionError(
                required="Windows",
                current=self.env.product_name or "Non-Windows",
            )
        if self.metadata.requires_windows_11 and not self.env.is_windows_11:
            raise UnsupportedVersionError(
                required="Windows 11",
                current=self.env.friendly_name,
            )
        if (
            self.metadata.min_windows_build
            and self.env.build < self.metadata.min_windows_build
        ):
            raise UnsupportedVersionError(
                required=f"Windows build {self.metadata.min_windows_build}+ "
                         f"(Windows 10 version 1809 or later)",
                current=self.env.friendly_name,
            )

    def requires_admin_now(self) -> bool:
        """Return True if this Toy needs elevation for the planned operation."""
        return self.metadata.requires_admin and not self.env.is_admin

    # ------------------------------------------------------------------
    # UI contract
    # ------------------------------------------------------------------

    @abstractmethod
    def create_ui(self, parent: "tk.Misc") -> "tk.Widget":
        """Build and return the Toy's settings widget.

        The returned widget will be packed/gridded by the hub into a
        dedicated top-level window or frame. The Toy is responsible for
        creating all controls, loading current state, and wiring Apply /
        Reset buttons.
        """
        ...

    # ------------------------------------------------------------------
    # Optional lifecycle hooks (override as needed)
    # ------------------------------------------------------------------

    def on_open(self) -> None:
        """Called just before the Toy window is shown."""
        pass

    def on_close(self) -> None:
        """Called when the Toy window is closed."""
        pass

    def get_status_text(self) -> str:
        """Short status string shown in the hub card (optional)."""
        return ""

    # ------------------------------------------------------------------
    # Error helper
    # ------------------------------------------------------------------

    def raise_toy_error(
        self,
        message: str,
        *,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        raise ToyError(
            toy_name=self.metadata.name,
            message=message,
            details=details,
            suggestion=suggestion,
        )
