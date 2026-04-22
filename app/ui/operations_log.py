"""Operations tab execution log persistence helper."""

from __future__ import annotations

import json
from collections.abc import Callable
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
        max_bytes: int = 1_000_000,
        ttl_days: int = 30,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._locator = app_data_locator or QStandardPaths
        self._file_name = file_name
        self._max_bytes = max_bytes
        self._ttl_days = ttl_days
        self._now_provider = now_provider or (lambda: datetime.now(UTC))

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
            timestamp=self._now_provider().isoformat(),
            action=action,
            role=role,
            status=status,
            message=message,
            path=path,
            path2=path2,
        )
        payload = json.dumps(event.__dict__, ensure_ascii=False)
        log_path = self._log_path()
        self._run_housekeeping(log_path)
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(payload + "\n")

    def _run_housekeeping(self, log_path: Path) -> None:
        try:
            self._rotate_if_needed(log_path)
        except Exception:
            pass
        try:
            self._prune_archives(log_path)
        except Exception:
            pass

    def _rotate_if_needed(self, log_path: Path) -> None:
        if not log_path.exists():
            return
        if log_path.stat().st_size < self._max_bytes:
            return
        ts = self._now_provider().strftime("%Y%m%d-%H%M%S")
        archived = log_path.with_name(f"{log_path.stem}.{ts}{log_path.suffix}")
        log_path.replace(archived)

    def _prune_archives(self, log_path: Path) -> None:
        cutoff = self._now_provider().timestamp() - (self._ttl_days * 24 * 60 * 60)
        pattern = f"{log_path.stem}.*{log_path.suffix}"
        for archived in log_path.parent.glob(pattern):
            if archived.name == log_path.name:
                continue
            if archived.stat().st_mtime < cutoff:
                archived.unlink(missing_ok=True)
