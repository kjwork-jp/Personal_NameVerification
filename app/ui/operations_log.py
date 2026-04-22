"""Operations tab execution log persistence helper."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QStandardPaths


class AppDataLocator(Protocol):
    def writableLocation(self, location: QStandardPaths.StandardLocation) -> str: ...


@dataclass(frozen=True)
class OperationLogEvent:
    timestamp: str
    action: str
    role: str
    status: str
    message: str
    path: str | None = None
    path2: str | None = None


class OperationsJsonlLogger:
    """Append-only JSON Lines logger for operations execution results."""

    def __init__(
        self,
        app_data_locator: AppDataLocator | None = None,
        file_name: str = "operations_events.jsonl",
    ) -> None:
        self._locator = app_data_locator or QStandardPaths
        self._file_name = file_name

    def _log_path(self) -> Path:
        base_dir = self._locator.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not base_dir.strip():
            base_dir = str(Path.home() / ".nameverification")
        target_dir = Path(base_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / self._file_name

    def append(
        self,
        *,
        action: str,
        role: str,
        status: str,
        message: str,
        path: str | None = None,
        path2: str | None = None,
    ) -> None:
        event = OperationLogEvent(
            timestamp=datetime.now(UTC).isoformat(),
            action=action,
            role=role,
            status=status,
            message=message,
            path=path,
            path2=path2,
        )
        payload = json.dumps(event.__dict__, ensure_ascii=False)
        log_path = self._log_path()
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(payload + "\n")
