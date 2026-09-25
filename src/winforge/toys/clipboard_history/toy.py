"""Clipboard History Toy."""

from __future__ import annotations

from typing import Any

from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy


class ClipboardHistoryToy(BaseToy):
    metadata = ToyMetadata(
        id="clipboard_history",
        name="Clipboard History",
        description=(
            "Enable or disable Windows Clipboard History (Win + V). "
            "Keep a history of items you copy and pin important ones. "
            "Requires Windows 10 version 1809 or later (not available on 8.1)."
        ),
        category="Utility",
        version="1.0.0",
        requires_admin=False,
        min_windows_build=17763,  # Windows 10 1809
        tags=("utility", "clipboard", "productivity"),
        icon="📋",
    )

    def create_ui(self, parent: Any) -> Any:
        from winforge.toys.clipboard_history.ui import ClipboardHistoryUI
        self.check_compatibility()
        return ClipboardHistoryUI(parent, self)

    def get_status_text(self) -> str:
        if self.env.is_windows_8_1 or (
            self.env.is_windows and self.env.build < 17763
        ):
            return "Requires Win10 1809+"
        try:
            from winforge.toys.clipboard_history import logic
            return "Enabled" if logic.is_enabled() else "Disabled"
        except Exception:
            return "Unknown"
