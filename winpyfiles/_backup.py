"""Backup and restore of Windows Python file associations."""
import dataclasses
import json
import os
from datetime import datetime
from typing import Optional

from ._assoc import AssocDiagnosis, ExtensionInfo, ProgIdInfo, diagnose

_BACKUP_VERSION = 1


def _default_backup_path() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(os.getcwd(), f"winpyfiles_backup_{timestamp}.json")


def backup(path: Optional[str] = None) -> str:
    """Snapshot current associations to a JSON file. Returns the path written."""
    if path is None:
        path = _default_backup_path()

    d = diagnose()
    payload = {
        "version": _BACKUP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "extensions": [dataclasses.asdict(e) for e in d.extensions],
        "prog_ids": {k: dataclasses.asdict(v) for k, v in d.prog_ids.items()},
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return path


def load_backup(path: str) -> AssocDiagnosis:
    """Deserialize a backup file into an AssocDiagnosis."""
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)

    if payload.get("version") != _BACKUP_VERSION:
        raise ValueError(f"Unsupported backup version: {payload.get('version')}")

    extensions = [ExtensionInfo(**e) for e in payload["extensions"]]
    prog_ids = {k: ProgIdInfo(**v) for k, v in payload["prog_ids"].items()}
    return AssocDiagnosis(extensions=extensions, prog_ids=prog_ids)
