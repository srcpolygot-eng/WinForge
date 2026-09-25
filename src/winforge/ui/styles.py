"""Shared visual styling for WinForge."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_theme(root: tk.Tk) -> None:
    """Apply a clean, Windows-friendly ttk theme and fonts."""
    style = ttk.Style(root)

    # Prefer a modern theme if available
    available = style.theme_names()
    preferred = ("vista", "winnative", "clam", "default")
    for name in preferred:
        if name in available:
            style.theme_use(name)
            break

    # Fonts – Segoe UI is the standard Windows UI font
    default_font = ("Segoe UI", 10)
    heading_font = ("Segoe UI", 14, "bold")
    title_font = ("Segoe UI", 18, "bold")

    root.option_add("*Font", default_font)

    style.configure("TLabel", font=default_font)
    style.configure("TButton", font=default_font, padding=6)
    style.configure("TCheckbutton", font=default_font)
    style.configure("TRadiobutton", font=default_font)
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
    style.configure("Heading.TLabel", font=heading_font)
    style.configure("Title.TLabel", font=title_font)

    # Card-like frames
    style.configure("Card.TFrame", relief="solid", borderwidth=1)
    style.configure("ToyCard.TFrame", relief="groove", borderwidth=1, padding=10)

    # Accent button
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
