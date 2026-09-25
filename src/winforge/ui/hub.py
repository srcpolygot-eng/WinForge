"""WinForge Hub – central launcher for all Toys."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Type

from winforge import __version__
from winforge.core.config import ConfigManager
from winforge.core.backup import BackupManager
from winforge.core.toy_registry import ToyRegistry, ToyMetadata
from winforge.core.windows import get_windows_environment
from winforge.core.logging import get_logger, setup_logging
from winforge.core.errors import WinForgeError, ToyError
from winforge.ui.styles import apply_theme

logger = get_logger("hub")


class ToyWindow(tk.Toplevel):
    """Independent top-level window that hosts a single Toy's UI."""

    def __init__(
        self,
        master: tk.Tk,
        toy_instance,
        metadata: ToyMetadata,
    ) -> None:
        super().__init__(master)
        self.toy = toy_instance
        self.metadata = metadata
        self.title(f"{metadata.name} – WinForge")
        self.geometry("520x560")
        self.minsize(420, 400)
        self.resizable(True, True)

        # Make it look like a proper dialog relative to the hub
        self.transient(master)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        try:
            self.toy.on_open()
            ui = self.toy.create_ui(container)
            ui.pack(fill="both", expand=True)
        except Exception as exc:
            self._show_error(exc)
            return

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _show_error(self, exc: Exception) -> None:
        for child in self.winfo_children():
            child.destroy()
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, text="Unable to open this Toy", font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        if isinstance(exc, (ToyError, WinForgeError)):
            msg = exc.user_message()
        else:
            msg = str(exc)
            logger.exception("Unhandled error opening toy %s", self.metadata.id)

        text = tk.Text(frame, wrap="word", height=12, font=("Segoe UI", 10))
        text.insert("1.0", msg)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True)

        ttk.Button(frame, text="Close", command=self.destroy).pack(pady=(12, 0))

    def _on_close(self) -> None:
        try:
            self.toy.on_close()
        except Exception:
            pass
        self.destroy()


class WinForgeHub(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        setup_logging()
        apply_theme(self)

        self.title(f"WinForge {__version__}")
        self.geometry("780x620")
        self.minsize(640, 480)

        self.config_manager = ConfigManager()
        self.backup_manager = BackupManager(self.config_manager)
        self.registry = ToyRegistry()
        self.env = get_windows_environment()

        self._toy_windows: Dict[str, ToyWindow] = {}

        self._build_ui()
        self._load_geometry()
        self.protocol("WM_DELETE_WINDOW", self._on_quit)

        logger.info("WinForge Hub started (version %s)", __version__)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Top bar
        top = ttk.Frame(self, padding=(16, 12, 16, 8))
        top.pack(fill="x")

        ttk.Label(top, text="WinForge", style="Title.TLabel").pack(side="left")

        version_lbl = ttk.Label(
            top, text=f"v{__version__}", foreground="#666666"
        )
        version_lbl.pack(side="left", padx=(10, 0))

        # Environment badge
        ttk.Label(
            top, text=self.env.friendly_name, foreground="#555555"
        ).pack(side="right")

        # Subtitle
        sub = ttk.Frame(self, padding=(16, 0, 16, 8))
        sub.pack(fill="x")
        ttk.Label(
            sub,
            text="Modular Windows customization and utilities. Each feature is an independent Toy.",
            wraplength=720,
        ).pack(anchor="w")

        # Search / filter
        filter_frame = ttk.Frame(self, padding=(16, 4, 16, 8))
        filter_frame.pack(fill="x")

        ttk.Label(filter_frame, text="Filter:").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._populate_toys())
        entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=30)
        entry.pack(side="left", padx=(6, 12))

        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            state="readonly",
            width=18,
        )
        self.category_combo.pack(side="left")
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self._populate_toys())

        # Scrollable toy list
        list_container = ttk.Frame(self, padding=(12, 0, 12, 12))
        list_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(list_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.toys_frame = ttk.Frame(canvas)

        self.toys_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.toys_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.canvas = canvas

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(
            self, textvariable=self.status_var, relief="sunken", anchor="w", padding=(8, 3)
        )
        status.pack(fill="x", side="bottom")

        # Populate
        self._populate_categories()
        self._populate_toys()

    def _populate_categories(self) -> None:
        cats = sorted(self.registry.by_category().keys())
        values = ["All"] + cats
        self.category_combo["values"] = values
        self.category_var.set("All")

    def _populate_toys(self) -> None:
        for child in self.toys_frame.winfo_children():
            child.destroy()

        filter_text = self.filter_var.get().strip().lower()
        category = self.category_var.get()

        metas = self.registry.get_all_metadata()
        # Sort by category then name
        metas.sort(key=lambda m: (m.category, m.name))

        shown = 0
        for meta in metas:
            if category != "All" and meta.category != category:
                continue
            if filter_text:
                hay = f"{meta.name} {meta.description} {meta.category} {' '.join(meta.tags)}".lower()
                if filter_text not in hay:
                    continue

            self._create_toy_card(meta)
            shown += 1

        if shown == 0:
            ttk.Label(
                self.toys_frame,
                text="No Toys match the current filter.",
                foreground="#666666",
            ).pack(pady=20)

        self.status_var.set(f"{shown} Toy(s) shown  •  {len(metas)} total")

    def _create_toy_card(self, meta: ToyMetadata) -> None:
        card = ttk.Frame(self.toys_frame, style="ToyCard.TFrame", padding=12)
        card.pack(fill="x", pady=6, padx=4)

        # Left: icon + name
        left = ttk.Frame(card)
        left.pack(side="left", fill="both", expand=True)

        title_row = ttk.Frame(left)
        title_row.pack(anchor="w")

        icon = meta.icon or "🔧"
        ttk.Label(title_row, text=icon, font=("Segoe UI", 14)).pack(side="left", padx=(0, 6))
        ttk.Label(title_row, text=meta.name, font=("Segoe UI", 12, "bold")).pack(side="left")

        ttk.Label(
            left,
            text=meta.description,
            wraplength=480,
            foreground="#333333",
        ).pack(anchor="w", pady=(4, 2))

        # Meta line
        meta_parts = [meta.category, f"v{meta.version}"]
        if meta.requires_windows_11:
            meta_parts.append("Win11")
        if meta.requires_admin:
            meta_parts.append("Admin")
        ttk.Label(
            left,
            text=" · ".join(meta_parts),
            foreground="#777777",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # Right: open button + status
        right = ttk.Frame(card)
        right.pack(side="right", padx=(12, 0))

        ttk.Button(
            right,
            text="Open",
            style="Accent.TButton",
            command=lambda m=meta: self._open_toy(m),
        ).pack(pady=(0, 4))

        # Live status if possible
        try:
            toy_cls = self.registry.get_toy_class(meta.id)
            if toy_cls:
                tmp = toy_cls(
                    config_manager=self.config_manager,
                    backup_manager=self.backup_manager,
                )
                status = tmp.get_status_text()
                if status:
                    ttk.Label(
                        right, text=status, foreground="#555555", font=("Segoe UI", 9)
                    ).pack()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Toy launching
    # ------------------------------------------------------------------

    def _open_toy(self, meta: ToyMetadata) -> None:
        # Reuse existing window if already open
        if meta.id in self._toy_windows:
            win = self._toy_windows[meta.id]
            if win.winfo_exists():
                win.lift()
                win.focus_force()
                return
            else:
                del self._toy_windows[meta.id]

        try:
            toy = self.registry.create_toy(
                meta.id,
                config_manager=self.config_manager,
                backup_manager=self.backup_manager,
            )
            win = ToyWindow(self, toy, meta)
            self._toy_windows[meta.id] = win
            self.status_var.set(f"Opened: {meta.name}")
        except Exception as exc:
            logger.exception("Failed to open toy %s", meta.id)
            if isinstance(exc, (ToyError, WinForgeError)):
                messagebox.showerror("Cannot open Toy", exc.user_message(), parent=self)
            else:
                messagebox.showerror(
                    "Cannot open Toy",
                    f"An unexpected error occurred while opening {meta.name}:\n\n{exc}",
                    parent=self,
                )

    # ------------------------------------------------------------------
    # Geometry / quit
    # ------------------------------------------------------------------

    def _load_geometry(self) -> None:
        cfg = self.config_manager.load_hub_config()
        geo = cfg.get("window_geometry")
        if geo:
            try:
                self.geometry(geo)
            except Exception:
                pass

    def _save_geometry(self) -> None:
        cfg = self.config_manager.load_hub_config()
        cfg["window_geometry"] = self.geometry()
        self.config_manager.save_hub_config(cfg)

    def _on_quit(self) -> None:
        self._save_geometry()
        for win in list(self._toy_windows.values()):
            try:
                if win.winfo_exists():
                    win.destroy()
            except Exception:
                pass
        self.destroy()
        logger.info("WinForge Hub closed")
