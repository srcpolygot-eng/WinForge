"""UI for the Hidden Files Toy."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from winforge.toys.hidden_files import logic

if TYPE_CHECKING:
    from winforge.toys.hidden_files.toy import HiddenFilesToy


class HiddenFilesUI(ttk.Frame):
    def __init__(self, parent: tk.Misc, toy: "HiddenFilesToy") -> None:
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self) -> None:
        ttk.Label(
            self, text="Hidden & System Files", font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            self,
            text=(
                "Control whether File Explorer displays hidden files and "
                "protected operating system files.\n"
                "Showing system files is useful for advanced users but can clutter the view."
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

        opts = ttk.LabelFrame(self, text="Options", padding=12)
        opts.pack(fill="x", pady=(0, 16))

        self.show_hidden_var = tk.BooleanVar(value=False)
        self.show_system_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            opts,
            text="Show hidden files, folders, and drives",
            variable=self.show_hidden_var,
        ).pack(anchor="w", pady=3)

        ttk.Checkbutton(
            opts,
            text="Show protected operating system files (recommended: off)",
            variable=self.show_system_var,
        ).pack(anchor="w", pady=3)

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
                "Note: These are per-user settings. No administrator rights required.\n"
                "Press F5 in an open Explorer window if the change does not appear immediately."
            ),
            wraplength=460,
            foreground="#555555",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(16, 0))

    def refresh_state(self) -> None:
        try:
            state = logic.get_state()
            self.show_hidden_var.set(state["show_hidden"])
            self.show_system_var.set(state["show_system"])
            parts = []
            parts.append("Hidden files: " + ("Shown" if state["show_hidden"] else "Hidden"))
            parts.append(
                "System files: " + ("Shown" if state["show_system"] else "Hidden")
            )
            self.status_var.set("  |  ".join(parts))
        except Exception as exc:
            self.status_var.set("Unable to read current settings")
            self.toy.logger.error("Refresh failed: %s", exc)

    def _on_apply(self) -> None:
        desired = {
            "show_hidden": self.show_hidden_var.get(),
            "show_system": self.show_system_var.get(),
        }
        try:
            current = logic.get_state()
            self.toy.backup_manager.create_backup(
                self.toy.metadata.id, "before_apply", current
            )
            logic.set_state(**desired)

            if not logic.verify_state(desired):
                messagebox.showwarning(
                    "Verification",
                    "Settings were written but could not be verified immediately.\n"
                    "Try refreshing File Explorer (F5).",
                    parent=self,
                )
            else:
                messagebox.showinfo(
                    "Success",
                    "Hidden / system file visibility has been updated.",
                    parent=self,
                )

            self.toy.set_setting("last_state", desired)
            self.toy.save_user_config()
            self.refresh_state()
        except Exception as exc:
            from winforge.core.errors import ToyError
            msg = exc.user_message() if isinstance(exc, ToyError) else str(exc)
            messagebox.showerror("Error", msg, parent=self)
