"""UI for God Mode Toy."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import TYPE_CHECKING

from winforge.toys.god_mode import logic

if TYPE_CHECKING:
    from winforge.toys.god_mode.toy import GodModeToy


class GodModeUI(ttk.Frame):
    def __init__(self, parent: tk.Misc, toy: "GodModeToy") -> None:
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self) -> None:
        ttk.Label(
            self, text="God Mode", font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            self,
            text=(
                "God Mode is a special Windows folder that exposes a huge list of "
                "Control Panel and settings pages in one place.\n\n"
                "It is completely safe – it is just a folder with a special name. "
                "You can delete it at any time."
            ),
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        status_frame = ttk.LabelFrame(self, text="Status", padding=12)
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_var = tk.StringVar(value="Checking…")
        ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 11)).pack(
            anchor="w"
        )

        loc_frame = ttk.LabelFrame(self, text="Location", padding=12)
        loc_frame.pack(fill="x", pady=(0, 16))

        self.path_var = tk.StringVar(value=str(logic.default_location()))
        path_entry = ttk.Entry(loc_frame, textvariable=self.path_var, width=55)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Button(loc_frame, text="Browse…", command=self._browse).pack(side="left")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(btn_frame, text="Create God Mode", command=self._on_create).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Remove", command=self._on_remove).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Open Location", command=self._on_open).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_state).pack(side="left")

        ttk.Label(
            self,
            text=(
                "Tip: After creating, open the folder to browse hundreds of Windows settings.\n"
                "You can also rename the folder (keep the .{CLSID} suffix) if you prefer a different name."
            ),
            wraplength=460,
            foreground="#555555",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(16, 0))

    def refresh_state(self) -> None:
        path = Path(self.path_var.get())
        if logic.exists(path):
            self.status_var.set(f"God Mode folder exists at:\n{path}")
        else:
            self.status_var.set("God Mode folder is not present at the chosen location.")

    def _browse(self) -> None:
        directory = filedialog.askdirectory(
            title="Choose parent folder for God Mode",
            initialdir=str(Path.home() / "Desktop"),
        )
        if directory:
            target = Path(directory) / logic.GOD_MODE_NAME
            self.path_var.set(str(target))
            self.refresh_state()

    def _on_create(self) -> None:
        path = Path(self.path_var.get())
        try:
            created = logic.create(path)
            self.toy.backup_manager.create_backup(
                self.toy.metadata.id,
                "created",
                {"path": str(created)},
            )
            messagebox.showinfo(
                "Success",
                f"God Mode folder created:\n{created}\n\n"
                "Double-click it to open the settings list.",
                parent=self,
            )
            self.toy.set_setting("last_path", str(created))
            self.toy.save_user_config()
            self.refresh_state()
        except Exception as exc:
            from winforge.core.errors import ToyError
            msg = exc.user_message() if isinstance(exc, ToyError) else str(exc)
            messagebox.showerror("Error", msg, parent=self)

    def _on_remove(self) -> None:
        path = Path(self.path_var.get())
        if not logic.exists(path):
            messagebox.showinfo("Nothing to do", "God Mode folder is not present.", parent=self)
            return
        if not messagebox.askyesno(
            "Confirm",
            f"Remove the God Mode folder at:\n{path}?",
            parent=self,
        ):
            return
        try:
            logic.remove(path)
            messagebox.showinfo("Removed", "God Mode folder has been deleted.", parent=self)
            self.refresh_state()
        except Exception as exc:
            from winforge.core.errors import ToyError
            msg = exc.user_message() if isinstance(exc, ToyError) else str(exc)
            messagebox.showerror("Error", msg, parent=self)

    def _on_open(self) -> None:
        path = Path(self.path_var.get()).parent
        if not path.exists():
            path = Path.home() / "Desktop"
        try:
            import os
            os.startfile(str(path))  # type: ignore[attr-defined]
        except Exception:
            messagebox.showinfo("Location", str(path), parent=self)
