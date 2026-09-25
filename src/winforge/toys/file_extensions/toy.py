"""File Extensions Toy implementation."""

from __future__ import annotations

from typing import Any

from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy


class FileExtensionsToy(BaseToy):
    """Toggle visibility of known file extensions in File Explorer."""

    metadata = ToyMetadata(
        id="file_extensions",
        name="File Extensions",
        description=(
            "Show or hide extensions for known file types in File Explorer. "
            "Showing extensions helps you identify file types at a glance."
        ),
        category="Explorer",
        version="1.0.0",
        author="WinForge",
        requires_admin=False,
        min_windows_build=0,
        requires_windows_11=False,
        tags=("explorer", "files", "security"),
        icon="📄",
    )

    def create_ui(self, parent: Any) -> Any:
        from winforge.toys.file_extensions.ui import FileExtensionsUI
        self.check_compatibility()
        return FileExtensionsUI(parent, self)

    def get_status_text(self) -> str:
        try:
            from winforge.toys.file_extensions import logic
            hide = logic.get_hide_extensions()
            return "Hidden" if hide else "Visible"
        except Exception:
            return "Unknown"
