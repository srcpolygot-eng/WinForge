"""Taskbar Alignment Toy."""

from __future__ import annotations

from typing import Any

from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy


class TaskbarAlignmentToy(BaseToy):
    metadata = ToyMetadata(
        id="taskbar_alignment",
        name="Taskbar Alignment",
        description=(
            "Align the Windows 11 taskbar icons to the left or keep them centered. "
            "Classic left alignment is preferred by many power users."
        ),
        category="Taskbar",
        version="1.0.0",
        requires_admin=False,
        requires_windows_11=True,
        min_windows_build=22000,
        tags=("taskbar", "windows11", "ui"),
        icon="📌",
    )

    def create_ui(self, parent: Any) -> Any:
        from winforge.toys.taskbar_alignment.ui import TaskbarAlignmentUI
        # Compatibility is checked inside UI for graceful messaging
        return TaskbarAlignmentUI(parent, self)

    def get_status_text(self) -> str:
        if not self.env.is_windows_11:
            if self.env.is_windows_10:
                return "Requires Win11 (you have 10)"
            if self.env.is_windows_8_1:
                return "Requires Win11 (you have 8.1)"
            return "Requires Win11"
        try:
            from winforge.toys.taskbar_alignment import logic
            return logic.get_alignment().capitalize()
        except Exception:
            return "Unknown"
