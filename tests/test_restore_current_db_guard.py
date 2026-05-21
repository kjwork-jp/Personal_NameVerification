"""Tests for the active database restore guard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ui.restore_current_db_guard import apply_restore_current_db_guard


class _TextInput:
    def __init__(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text


class _FakeOperationsTab:
    def __init__(self, backup_path: str, target_path: str) -> None:
        self.restore_backup_path_input = _TextInput(backup_path)
        self.restore_target_db_path_input = _TextInput(target_path)
        self.messages: list[tuple[str, bool]] = []
        self.operations: list[dict[str, str | None]] = []
        self.restore_called = False

    def _run_restore(self) -> None:
        self.restore_called = True

    def _ensure_not_busy(self) -> bool:
        return True

    def _require_text(self, line_edit: _TextInput, label: str) -> str | None:
        value = line_edit.text().strip()
        if value:
            return value
        self._set_message(f"{label} は必須です", is_error=True)
        return None

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        self.messages.append((message, is_error))

    def _record_operation(
        self,
        action: str,
        status: str,
        message: str,
        *,
        path: str | None = None,
        path2: str | None = None,
    ) -> None:
        self.operations.append(
            {
                "action": action,
                "status": status,
                "message": message,
                "path": path,
                "path2": path2,
            }
        )


def test_guard_blocks_restore_to_current_database_before_service_call(tmp_path: Path) -> None:
    current_db = tmp_path / "30_prod_db" / "nameverification.db"
    current_db.parent.mkdir()
    current_db.write_text("current", encoding="utf-8")
    backup_db = tmp_path / "50_backups" / "daily" / "backup.db"
    backup_db.parent.mkdir(parents=True)
    backup_db.write_text("backup", encoding="utf-8")

    tab = _FakeOperationsTab(str(backup_db), str(current_db))
    apply_restore_current_db_guard(tab, current_db)

    tab._run_restore()

    assert not tab.restore_called
    assert tab.messages
    assert tab.messages[-1][1] is True
    assert "現在利用中DB" in tab.messages[-1][0]
    assert tab.operations[-1]["action"] == "restore"
    assert tab.operations[-1]["status"] == "error"
    assert tab.operations[-1]["path"] == str(backup_db)
    assert tab.operations[-1]["path2"] == str(current_db)


def test_guard_allows_restore_to_different_database(tmp_path: Path) -> None:
    current_db = tmp_path / "30_prod_db" / "nameverification.db"
    target_db = tmp_path / "restore_target.db"
    backup_db = tmp_path / "backup.db"

    tab = _FakeOperationsTab(str(backup_db), str(target_db))
    apply_restore_current_db_guard(tab, current_db)

    tab._run_restore()

    assert tab.restore_called
    assert not tab.messages
    assert not tab.operations


def test_guard_is_noop_without_current_database_path(tmp_path: Path) -> None:
    tab = _FakeOperationsTab(str(tmp_path / "backup.db"), str(tmp_path / "target.db"))
    apply_restore_current_db_guard(tab, None)

    tab._run_restore()

    assert tab.restore_called


def test_guard_is_idempotent(tmp_path: Path) -> None:
    current_db = tmp_path / "nameverification.db"
    backup_db = tmp_path / "backup.db"
    tab: Any = _FakeOperationsTab(str(backup_db), str(current_db))

    apply_restore_current_db_guard(tab, current_db)
    first_guarded_restore = tab._run_restore
    apply_restore_current_db_guard(tab, current_db)

    assert tab._run_restore is first_guarded_restore
