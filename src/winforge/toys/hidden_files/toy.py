"""Hidden Files Toy."""

from __future__ import annotations

from typing import Any

from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy


class HiddenFilesToy(BaseToy):
    metadata = ToyMetadata(
        id="hidden_files",
        name="Hidden & System Files",
        description=(
            "Show or hide hidden files and protected operating system files "
            "in File Explorer."
        ),
        category="Explorer",
        version="1.0.0",
        requires_admin=False,
        tags=("explorer", "files", "hidden"),
        icon="👁️",
    )

    def create_ui(self, parent: Any) -> Any:
        from winforge.toys.hidden_files.ui import HiddenFilesUI
        self.check_compatibility()
        return HiddenFilesUI(parent, self)

    def get_status_text(self) -> str:
        try:
            from winforge.toys.hidden_files import logic
            state = logic.get_state()
            if state["show_hidden"]:
                return "Showing hidden"
            return "Hiding hidden"
        except Exception:
            return "Unknown"
