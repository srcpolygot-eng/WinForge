"""UI for Clipboard History Toy."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from winforge.toys.clipboard_history import logic

if TYPE_CHECKING:
    from winforge.toys.clipboard_history.toy import ClipboardHistoryToy


class ClipboardHistoryUI(ttk.Frame):
    def __init__(self, parent: tk.Misc, toy: "ClipboardHistoryToy") -> None:
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self) -> None:
        ttk.Label(
            self, text="Clipboard History", font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            self,
            text=(
                "Windows Clipboard History (Win + V) lets you access multiple items "
                "you have copied, not just the most recent one.\n\n"
                "This Toy enables or disables the feature."
            ),
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        status_frame = ttk.LabelFrame(self, text="Current Status", padding=12)
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_var = tk.StringVar(value="Checking…")
        ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 11)).pack(
            anchor="w"
        )

        pref = ttk.LabelFrame(self, text="Setting", padding=12)
        pref.pack(fill="x", pady=(0, 16))

        self.enabled_var = tk.BooleanVar(value=True)

        ttk.Radiobutton(
            pref,
            text="Enable Clipboard History (recommended)",
            variable=self.enabled_var,
            value=True,
        ).pack(anchor="w", pady=2)
        ttk.Radiobutton(
            pref,
            text="Disable Clipboard History",
            variable=self.enabled_var,
            value=False,
        ).pack(anchor="w", pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(btn_frame, text="Apply", command=self._on_apply).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_state).pack(
            side="left"
        )

        ttk.Label(
            self,
            text=(
                "After enabling, press Win + V to open the clipboard history panel.\n"
                "You can pin important items so they survive reboots."
            ),
            wraplength=460,
            foreground="#555555",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(16, 0))

    def refresh_state(self) -> None:
        try:
            enabled = logic.is_enabled()
            self.enabled_var.set(enabled)
            self.status_var.set(
                "Clipboard History is ENABLED" if enabled else "Clipboard History is DISABLED"
            )
        except Exception as exc:
            self.status_var.set("Unable to read current setting")
            self.toy.logger.error("Refresh failed: %s", exc)

    def _on_apply(self) -> None:
        desired = self.enabled_var.get()
        try:
            current = logic.is_enabled()
            self.toy.backup_manager.create_backup(
                self.toy.metadata.id, "before_apply", {"enabled": current}
            )
            logic.set_enabled(desired)

            if not logic.verify(desired):
                messagebox.showwarning(
                    "Verification",
                    "The setting was written but could not be verified.\n"
                    "Try opening Settings → System → Clipboard to confirm.",
                    parent=self,
                )
            else:
                state = "enabled" if desired else "disabled"
                messagebox.showinfo(
                    "Success",
                    f"Clipboard History has been {state}.\n\n"
                    "Press Win + V to try it.",
                    parent=self,
                )

            self.toy.set_setting("preferred_enabled", desired)
            self.toy.save_user_config()
            self.refresh_state()
        except Exception as exc:
            from winforge.core.errors import ToyError
            msg = exc.user_message() if isinstance(exc, ToyError) else str(exc)
            messagebox.showerror("Error", msg, parent=self)
