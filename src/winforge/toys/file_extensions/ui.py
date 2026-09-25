"""UI for the File Extensions Toy."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from winforge.toys.file_extensions import logic

if TYPE_CHECKING:
    from winforge.toys.file_extensions.toy import FileExtensionsToy


class FileExtensionsUI(ttk.Frame):
    """Settings panel for showing/hiding known file extensions."""

    def __init__(self, parent: tk.Misc, toy: "FileExtensionsToy") -> None:
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self) -> None:
        # Header
        header = ttk.Label(
            self,
            text="File Extensions",
            font=("Segoe UI", 16, "bold"),
        )
        header.pack(anchor="w", pady=(0, 4))

        desc = ttk.Label(
            self,
            text=(
                "Control whether File Explorer shows the extension of known file types "
                "(e.g. .txt, .docx, .png).\n"
                "Showing extensions is recommended for security awareness."
            ),
            wraplength=460,
            justify="left",
        )
        desc.pack(anchor="w", pady=(0, 16))

        # Current status card
        status_frame = ttk.LabelFrame(self, text="Current Status", padding=12)
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_var = tk.StringVar(value="Checking…")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
        )
        self.status_label.pack(anchor="w")

        # Preference
        pref_frame = ttk.LabelFrame(self, text="Preference", padding=12)
        pref_frame.pack(fill="x", pady=(0, 16))

        self.hide_var = tk.BooleanVar(value=True)

        ttk.Radiobutton(
            pref_frame,
            text="Show file extensions (recommended)",
            variable=self.hide_var,
            value=False,
        ).pack(anchor="w", pady=2)

        ttk.Radiobutton(
            pref_frame,
            text="Hide extensions for known file types",
            variable=self.hide_var,
            value=True,
        ).pack(anchor="w", pady=2)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(8, 0))

        self.apply_btn = ttk.Button(
            btn_frame, text="Apply", command=self._on_apply
        )
        self.apply_btn.pack(side="left", padx=(0, 8))

        self.refresh_btn = ttk.Button(
            btn_frame, text="Refresh", command=self.refresh_state
        )
        self.refresh_btn.pack(side="left")

        # Notes
        note = ttk.Label(
            self,
            text=(
                "Note: This is a per-user setting. No administrator rights are required.\n"
                "Changes take effect immediately in new Explorer windows; existing ones "
                "may need a refresh (F5)."
            ),
            wraplength=460,
            foreground="#555555",
            font=("Segoe UI", 9),
        )
        note.pack(anchor="w", pady=(16, 0))

    def refresh_state(self) -> None:
        try:
            hide = logic.get_hide_extensions()
            self.hide_var.set(hide)
            if hide:
                self.status_var.set("Extensions are currently HIDDEN")
            else:
                self.status_var.set("Extensions are currently VISIBLE")
        except Exception as exc:
            self.status_var.set("Unable to read current setting")
            self.toy.logger.error("UI refresh failed: %s", exc)

    def _on_apply(self) -> None:
        desired_hide = self.hide_var.get()
        try:
            # Backup current value
            current = logic.get_hide_extensions()
            self.toy.backup_manager.create_backup(
                self.toy.metadata.id,
                "before_apply",
                {"hide_extensions": current},
            )

            logic.set_hide_extensions(desired_hide)

            # Verify
            if not logic.verify_setting(desired_hide):
                messagebox.showwarning(
                    "Verification",
                    "The setting was written but could not be verified immediately.\n"
                    "Please press Refresh or open a new File Explorer window.",
                    parent=self,
                )
            else:
                messagebox.showinfo(
                    "Success",
                    "File extension visibility has been updated.",
                    parent=self,
                )

            # Persist preference
            self.toy.set_setting("prefer_hide", desired_hide)
            self.toy.save_user_config()
            self.refresh_state()

        except Exception as exc:
            from winforge.core.errors import ToyError
            if isinstance(exc, ToyError):
                messagebox.showerror(
                    "Error",
                    exc.user_message(),
                    parent=self,
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"Unexpected error:\n{exc}",
                    parent=self,
                )
