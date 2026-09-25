"""Toy discovery and registration system."""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from winforge.core.logging import get_logger

logger = get_logger("toy_registry")


@dataclass(frozen=True)
class ToyMetadata:
    """Static metadata that every Toy must expose."""

    id: str                     # unique snake_case identifier
    name: str                   # human-readable display name
    description: str
    category: str               # e.g. "Explorer", "Taskbar", "Desktop", "Utility"
    version: str
    author: str = "WinForge"
    requires_admin: bool = False
    min_windows_build: int = 0  # 0 = any
    requires_windows_11: bool = False
    tags: tuple = field(default_factory=tuple)
    icon: Optional[str] = None  # optional emoji or icon name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "author": self.author,
            "requires_admin": self.requires_admin,
            "min_windows_build": self.min_windows_build,
            "requires_windows_11": self.requires_windows_11,
            "tags": list(self.tags),
            "icon": self.icon,
        }


class ToyRegistry:
    """Discovers and holds available Toys.

    Discovery works by scanning the `winforge.toys` package for submodules
    that expose a `get_toy_class()` function returning a subclass of BaseToy.
    """

    def __init__(self) -> None:
        self._toys: Dict[str, Type] = {}          # id -> Toy class
        self._metadata: Dict[str, ToyMetadata] = {}
        self._discovered = False

    def discover(self) -> None:
        """Scan the toys package and register every valid Toy."""
        if self._discovered:
            return

        import winforge.toys as toys_pkg

        package_path = toys_pkg.__path__
        prefix = toys_pkg.__name__ + "."

        for finder, name, ispkg in pkgutil.iter_modules(package_path, prefix):
            if not ispkg:
                continue
            # Skip the base module itself
            short_name = name.rsplit(".", 1)[-1]
            if short_name in ("base", "__pycache__"):
                continue

            try:
                module = importlib.import_module(name)
                if not hasattr(module, "get_toy_class"):
                    logger.debug("Skipping %s: no get_toy_class()", name)
                    continue

                toy_cls = module.get_toy_class()
                # Validate it has required metadata
                if not hasattr(toy_cls, "metadata"):
                    logger.warning("%s.get_toy_class() returned class without metadata", name)
                    continue

                meta: ToyMetadata = toy_cls.metadata
                if meta.id in self._toys:
                    logger.warning("Duplicate toy id '%s' from %s – skipping", meta.id, name)
                    continue

                self._toys[meta.id] = toy_cls
                self._metadata[meta.id] = meta
                logger.info("Registered toy: %s (%s)", meta.name, meta.id)

            except Exception as exc:
                logger.error("Failed to load toy module %s: %s", name, exc, exc_info=True)

        self._discovered = True
        logger.info("Toy discovery complete. %d toy(s) available.", len(self._toys))

    def get_all_metadata(self) -> List[ToyMetadata]:
        self.discover()
        return list(self._metadata.values())

    def get_metadata(self, toy_id: str) -> Optional[ToyMetadata]:
        self.discover()
        return self._metadata.get(toy_id)

    def get_toy_class(self, toy_id: str) -> Optional[Type]:
        self.discover()
        return self._toys.get(toy_id)

    def create_toy(self, toy_id: str, **kwargs) -> Any:
        """Instantiate a Toy by id."""
        cls = self.get_toy_class(toy_id)
        if cls is None:
            raise KeyError(f"Unknown toy id: {toy_id}")
        return cls(**kwargs)

    def list_ids(self) -> List[str]:
        self.discover()
        return list(self._toys.keys())

    def by_category(self) -> Dict[str, List[ToyMetadata]]:
        """Group metadata by category."""
        self.discover()
        result: Dict[str, List[ToyMetadata]] = {}
        for meta in self._metadata.values():
            result.setdefault(meta.category, []).append(meta)
        # Sort toys inside each category by name
        for cat in result:
            result[cat].sort(key=lambda m: m.name)
        return result
