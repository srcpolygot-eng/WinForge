"""Configuration management for WinForge and individual Toys."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from winforge.core.logging import get_logger
from winforge.core.errors import ConfigurationError

logger = get_logger("config")


class ConfigManager:
    """Manages persistent configuration for the hub and Toys.

    Layout under ~/.winforge/:
        config/
            hub.json
            toys/
                <toy_id>.json
        backups/
            ...
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        if base_dir is None:
            base_dir = Path.home() / ".winforge"
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "config"
        self.toys_config_dir = self.config_dir / "toys"
        self.backups_dir = self.base_dir / "backups"

        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.toys_config_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Hub configuration
    # ------------------------------------------------------------------

    def load_hub_config(self) -> Dict[str, Any]:
        path = self.config_dir / "hub.json"
        return self._load_json(path, default={
            "theme": "system",
            "window_geometry": None,
            "last_toy": None,
            "check_updates": True,
        })

    def save_hub_config(self, data: Dict[str, Any]) -> None:
        path = self.config_dir / "hub.json"
        self._save_json(path, data)

    # ------------------------------------------------------------------
    # Toy configuration
    # ------------------------------------------------------------------

    def load_toy_config(self, toy_id: str) -> Dict[str, Any]:
        """Load user configuration for a Toy. Returns empty dict if none exists."""
        path = self.toys_config_dir / f"{toy_id}.json"
        return self._load_json(path, default={})

    def save_toy_config(self, toy_id: str, data: Dict[str, Any]) -> None:
        path = self.toys_config_dir / f"{toy_id}.json"
        self._save_json(path, data)

    def delete_toy_config(self, toy_id: str) -> None:
        path = self.toys_config_dir / f"{toy_id}.json"
        if path.exists():
            path.unlink()
            logger.info("Deleted config for toy %s", toy_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_json(self, path: Path, default: Optional[Dict] = None) -> Dict[str, Any]:
        if default is None:
            default = {}
        if not path.exists():
            return dict(default)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ConfigurationError(
                    f"Config file {path} does not contain a JSON object."
                )
            return data
        except json.JSONDecodeError as exc:
            logger.error("Corrupt config %s: %s", path, exc)
            # Preserve a backup of the corrupt file
            corrupt_path = path.with_suffix(".json.corrupt")
            shutil.copy2(path, corrupt_path)
            raise ConfigurationError(
                f"Failed to parse configuration file: {path.name}",
                details=str(exc),
                suggestion=f"A backup of the corrupt file was saved as {corrupt_path.name}. "
                           "You may delete the config to reset to defaults.",
            ) from exc
        except OSError as exc:
            raise ConfigurationError(
                f"Unable to read configuration: {path}",
                details=str(exc),
            ) from exc

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        try:
            # Atomic write via temp file
            tmp = path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            tmp.replace(path)
            logger.debug("Saved config: %s", path)
        except OSError as exc:
            raise ConfigurationError(
                f"Unable to save configuration: {path}",
                details=str(exc),
            ) from exc

    def get_backup_dir(self, toy_id: str) -> Path:
        """Return (and create) a backup directory for a specific Toy."""
        d = self.backups_dir / toy_id
        d.mkdir(parents=True, exist_ok=True)
        return d
