"""
WinForge - Modular Windows Customization and Utilities Suite

Inspired by Microsoft PowerToys, WinForge provides a hub for independent
"Toys" that each offer a focused Windows customization or utility feature.
"""

__version__ = "1.0.0"
__author__ = "WinForge Contributors"

from winforge.core.toy_registry import ToyRegistry
from winforge.core.config import ConfigManager
from winforge.core.logging import get_logger

__all__ = [
    "__version__",
    "ToyRegistry",
    "ConfigManager",
    "get_logger",
]
