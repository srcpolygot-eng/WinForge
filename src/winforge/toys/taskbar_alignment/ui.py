"""UI for Taskbar Alignment Toy."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from winforge.toys.taskbar_alignment import logic

if TYPE_CHECKING:
    from winforge.toys.taskbar_alignment.toy import TaskbarAlignmentToy


class TaskbarAlignmentUI(ttk.Frame):
    def __init__(self, parent: tk.Misc, toy: "TaskbarAlignmentToy") -> None:
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self) -> None:
        ttk.Label(
            self, text="Taskbar Alignment", font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            self,
            text=(
                "Choose whether taskbar icons are aligned to the left or centered.\n"
                "This setting is available on Windows 11 only."
            ),
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        # Compatibility banner
        if not self.toy.env.is_windows_11:
            detected = self.toy.env.friendly_name
            banner = ttk.Label(
                self,
                text=(
                    f"⚠ Requires Windows 11 – not available on {detected}.\n"
                    "On Windows 10 and 8.1 the taskbar does not support this left/center toggle."
                ),
                foreground="#b45309",
                font=("Segoe UI", 10, "bold"),
                wraplength=460,
                justify="left",
            )
            banner.pack(anchor="w", pady=(0, 12))

        status_frame = ttk.LabelFrame(self, text="Current Status", padding=12)
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_var = tk.StringVar(value="Checking…")
        ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 11)).pack(
            anchor="w"
        )

        pref = ttk.LabelFrame(self, text="Alignment", padding=12)
        pref.pack(fill="x", pady=(0, 16))

        self.align_var = tk.StringVar(value="center")

        ttk.Radiobutton(
            pref, text="Left", variable=self.align_var, value="left"
        ).pack(anchor="w", pady=2)
        ttk.Radiobutton(
            pref, text="Center (Windows 11 default)", variable=self.align_var, value="center"
        ).pack(anchor="w", pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(8, 0))

        self.apply_btn = ttk.Button(btn_frame, text="Apply", command=self._on_apply)
        self.apply_btn.pack(side="left", padx=(0, 8))

        ttk.Button(btn_frame, text="Refresh", command=self.refresh_state).pack(side="left")

        if not self.toy.env.is_windows_11:
            self.apply_btn.state(["disabled"])

        ttk.Label(
            self,
            text=(
                "Note: Applying this change will briefly restart Windows Explorer.\n"
                "Open windows remain open; the taskbar and desktop will refresh."
            ),
            wraplength=460,
            foreground="#555555",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(16, 0))

    def refresh_state(self) -> None:
        if not self.toy.env.is_windows_11:
            self.status_var.set("Not available (requires Windows 11)")
            return
        try:
            current = logic.get_alignment()
            self.align_var.set(current)
            self.status_var.set(f"Currently aligned: {current.capitalize()}")
        except Exception as exc:
            self.status_var.set("Unable to read current alignment")
            self.toy.logger.error("Refresh failed: %s", exc)

    def _on_apply(self) -> None:
        if not self.toy.env.is_windows_11:
            messagebox.showerror(
                "Unsupported",
                "Taskbar alignment requires Windows 11.",
                parent=self,
            )
            return

        desired = self.align_var.get()
        if desired not in ("left", "center"):
            return

        try:
            current = logic.get_alignment()
            self.toy.backup_manager.create_backup(
                self.toy.metadata.id, "before_apply", {"alignment": current}
            )
            logic.set_alignment(desired)  # type: ignore[arg-type]

            # Small delay then verify
            self.after(1500, lambda: self._verify_and_notify(desired))
        except Exception as exc:
            from winforge.core.errors import ToyError
            msg = exc.user_message() if isinstance(exc, ToyError) else str(exc)
            messagebox.showerror("Error", msg, parent=self)

    def _verify_and_notify(self, desired: str) -> None:
        ok = logic.verify_alignment(desired)  # type: ignore[arg-type]
        if ok:
            messagebox.showinfo(
                "Success",
                f"Taskbar is now aligned to the {desired}.",
                parent=self,
            )
        else:
            messagebox.showwarning(
                "Verification",
                "The setting was written. If the taskbar did not update, "
                "try signing out and back in.",
                parent=self,
            )
        self.toy.set_setting("preferred_alignment", desired)
        self.toy.save_user_config()
        self.refresh_state()
