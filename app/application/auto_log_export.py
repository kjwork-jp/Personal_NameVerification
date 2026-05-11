"""Best-effort automatic JSONL export for database change logs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.application.core_services import CoreService, _to_json, _utc_now

_DEFAULT_MAX_BYTES = 5 * 1024 * 1024
_DISABLED_VALUES = {"0", "false", "no", "off"}


class AutoExportingCoreService(CoreService):
    """CoreService variant that mirrors change logs to local JSONL.

    The database change_logs table remains the source of truth. The JSONL export
    is a best-effort operational aid for local troubleshooting and file-based
    audit collection. Export failures never block the database transaction.
    """

    def __init__(
        self,
        connection: Any,
        *,
        log_path: Path | None = None,
        max_bytes: int | None = None,
    ) -> None:
        super().__init__(connection)
        self._auto_log_enabled = _is_enabled()
        self._auto_log_path = log_path or _default_log_path()
        self._auto_log_max_bytes = max_bytes or _default_max_bytes()

    def _insert_change_log(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        operator_id: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> None:
        super()._insert_change_log(
            entity_type,
            entity_id,
            action,
            operator_id,
            before,
            after,
        )
        self._append_auto_log(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            operator_id=operator_id,
            before=before,
            after=after,
        )

    def _append_auto_log(
        self,
        *,
        entity_type: str,
        entity_id: int,
        action: str,
        operator_id: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> None:
        if not self._auto_log_enabled:
            return
        try:
            self._auto_log_path.parent.mkdir(parents=True, exist_ok=True)
            self._rotate_auto_log_if_needed()
            payload = {
                "timestamp": _utc_now(),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": action,
                "operator_id": operator_id,
                "before_json": _to_json(before),
                "after_json": _to_json(after),
            }
            with self._auto_log_path.open("a", encoding="utf-8") as file_obj:
                file_obj.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
                file_obj.write("\n")
        except Exception:
            return

    def _rotate_auto_log_if_needed(self) -> None:
        if not self._auto_log_path.exists():
            return
        if self._auto_log_path.stat().st_size < self._auto_log_max_bytes:
            return
        timestamp = _utc_now().replace(":", "").replace("-", "").replace("Z", "Z")
        rotated = self._auto_log_path.with_name(
            f"{self._auto_log_path.stem}.{timestamp}{self._auto_log_path.suffix}"
        )
        self._auto_log_path.replace(rotated)


def _is_enabled() -> bool:
    raw = os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_ENABLED", "1")
    return raw.strip().lower() not in _DISABLED_VALUES


def _default_log_path() -> Path:
    raw = os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH", "logs/change_logs.jsonl")
    return Path(raw)


def _default_max_bytes() -> int:
    raw = os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_MAX_BYTES", "")
    if not raw.strip():
        return _DEFAULT_MAX_BYTES
    try:
        return max(1024, int(raw))
    except ValueError:
        return _DEFAULT_MAX_BYTES
