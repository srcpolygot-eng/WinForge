"""God Mode Toy."""

from __future__ import annotations

from typing import Any

from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy


class GodModeToy(BaseToy):
    metadata = ToyMetadata(
        id="god_mode",
        name="God Mode",
        description=(
            "Create the classic Windows 'God Mode' folder that lists virtually "
            "every Control Panel and settings page in one place."
        ),
        category="Utility",
        version="1.0.0",
        requires_admin=False,
        tags=("utility", "settings", "control-panel"),
        icon="⚡",
    )

    def create_ui(self, parent: Any) -> Any:
        from winforge.toys.god_mode.ui import GodModeUI
        self.check_compatibility()
        return GodModeUI(parent, self)

    def get_status_text(self) -> str:
        try:
            from winforge.toys.god_mode import logic
            return "Present" if logic.exists() else "Not created"
        except Exception:
            return "Unknown"
