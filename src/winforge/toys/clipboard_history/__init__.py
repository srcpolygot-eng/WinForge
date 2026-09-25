"""Clipboard History Toy – enable/disable Windows Clipboard History (Win+V)."""

from winforge.toys.clipboard_history.toy import ClipboardHistoryToy


def get_toy_class():
    return ClipboardHistoryToy
