"""Operations tab execution log persistence helper."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QStandardPaths

DEFAULT_OPERATIONS_LOG_FILE_NAME = "operations_events.jsonl"


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
    source: str | None = None


class OperationsJsonlLogger:
    """Append-only JSON Lines logger for operations execution results."""

    def __init__(
        self,
        app_data_locator: AppDataLocator | None = None,
        file_name: str = DEFAULT_OPERATIONS_LOG_FILE_NAME,
        max_bytes: int = 1_000_000,
        ttl_days: int = 30,
        now_provider: Callable[[], datetime] | None = None,
        log_path: Path | None = None,
    ) -> None:
        self._explicit_log_path = log_path.expanduser() if log_path is not None else None
        self._locator = app_data_locator or QStandardPaths
        self._file_name = file_name
        self._max_bytes = max_bytes
        self._ttl_days = ttl_days
        self._now_provider = now_provider or (lambda: datetime.now(UTC))

    def _log_path(self) -> Path:
        if self._explicit_log_path is not None:
            self._explicit_log_path.parent.mkdir(parents=True, exist_ok=True)
            return self._explicit_log_path
        return default_operations_log_path(self._locator, self._file_name)

    @property
    def log_path(self) -> Path:
        """Return the concrete JSONL path used by this logger."""

        return self._log_path()

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
        log_path = self._log_path()
        event = OperationLogEvent(
            timestamp=self._now_provider().isoformat(),
            action=action,
            role=role,
            status=status,
            message=message,
            path=path,
            path2=path2,
            source=str(log_path),
        )
        payload = json.dumps(event.__dict__, ensure_ascii=False)
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

    def list_archives(self) -> list[Path]:
        log_path = self._log_path()
        pattern = f"{log_path.stem}.*{log_path.suffix}"
        archives = [p for p in log_path.parent.glob(pattern) if p.name != log_path.name]
        return sorted(archives, key=lambda p: p.stat().st_mtime, reverse=True)

    def read_latest(
        self, limit: int = 100, *, include_archives: bool = False
    ) -> tuple[list[OperationLogEvent], int]:
        if limit <= 0:
            return [], 0

        log_files: list[Path] = [self._log_path()]
        if include_archives:
            log_files.extend(self.list_archives())

        events: list[OperationLogEvent] = []
        decode_errors = 0
        for path in log_files:
            parsed, errors = self._read_events_from_file(path)
            decode_errors += errors
            events.extend(parsed)

        events.sort(key=lambda item: item.timestamp, reverse=True)
        return events[:limit], decode_errors

    def _read_events_from_file(self, path: Path) -> tuple[list[OperationLogEvent], int]:
        if not path.exists():
            return [], 0

        events: list[OperationLogEvent] = []
        decode_errors = 0
        with path.open("r", encoding="utf-8") as fp:
            for line in fp:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    decode_errors += 1
                    continue
                if not isinstance(payload, dict):
                    decode_errors += 1
                    continue
                try:
                    events.append(
                        OperationLogEvent(
                            timestamp=str(payload.get("timestamp", "")),
                            action=str(payload.get("action", "")),
                            role=str(payload.get("role", "")),
                            status=str(payload.get("status", "")),
                            message=str(payload.get("message", "")),
                            path=str(payload["path"]) if payload.get("path") is not None else None,
                            path2=(
                                str(payload["path2"]) if payload.get("path2") is not None else None
                            ),
                            source=str(path),
                        )
                    )
                except Exception:
                    decode_errors += 1
        return events, decode_errors


def default_operations_log_path(
    app_data_locator: AppDataLocator | None = None,
    file_name: str = DEFAULT_OPERATIONS_LOG_FILE_NAME,
) -> Path:
    """Resolve the historical AppDataLocation-backed Operations JSONL path."""

    locator = app_data_locator or QStandardPaths
    base_dir = locator.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base_dir.strip():
        base_dir = str(Path.home() / ".nameverification")
    target_dir = Path(base_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / file_name
