"""Backup and restore helpers for Toys that modify system state."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from winforge.core.config import ConfigManager
from winforge.core.errors import BackupError
from winforge.core.logging import get_logger

logger = get_logger("backup")


class BackupManager:
    """Simple file/registry value backup system used by Toys."""

    def __init__(self, config: ConfigManager) -> None:
        self.config = config

    def create_backup(
        self,
        toy_id: str,
        label: str,
        data: Dict[str, Any],
    ) -> Path:
        """Persist a JSON backup snapshot for a Toy.

        Args:
            toy_id: Identifier of the Toy.
            label: Human-readable label (e.g. "before_apply").
            data: Serializable dictionary of values to restore later.

        Returns:
            Path to the created backup file.
        """
        backup_dir = self.config.get_backup_dir(toy_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{label}.json"
        path = backup_dir / filename

        payload = {
            "toy_id": toy_id,
            "label": label,
            "created": datetime.now().isoformat(timespec="seconds"),
            "data": data,
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.write("\n")
            logger.info("Created backup for %s: %s", toy_id, path.name)
            return path
        except OSError as exc:
            raise BackupError(
                f"Failed to create backup for {toy_id}",
                details=str(exc),
            ) from exc

    def list_backups(self, toy_id: str) -> List[Dict[str, Any]]:
        """Return metadata for all backups of a Toy, newest first."""
        backup_dir = self.config.get_backup_dir(toy_id)
        results: List[Dict[str, Any]] = []
        for path in sorted(backup_dir.glob("*.json"), reverse=True):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                results.append({
                    "path": str(path),
                    "filename": path.name,
                    "label": payload.get("label", ""),
                    "created": payload.get("created", ""),
                    "data": payload.get("data", {}),
                })
            except Exception as exc:
                logger.warning("Skipping corrupt backup %s: %s", path, exc)
        return results

    def load_backup(self, path: Path) -> Dict[str, Any]:
        """Load a backup file and return its data dictionary."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return payload.get("data", {})
        except Exception as exc:
            raise BackupError(
                f"Failed to load backup {path.name}",
                details=str(exc),
            ) from exc

    def restore_latest(self, toy_id: str) -> Optional[Dict[str, Any]]:
        """Load the most recent backup for a Toy, or None if none exist."""
        backups = self.list_backups(toy_id)
        if not backups:
            return None
        return backups[0]["data"]

    def delete_backup(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise BackupError(
                f"Failed to delete backup {path.name}",
                details=str(exc),
            ) from exc
