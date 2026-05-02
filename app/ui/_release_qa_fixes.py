"""Final release QA behavior patches.

These patches are intentionally small and isolated. They address the current
release-blocking UI test regressions without another large full-file rewrite of
PySide6 tab classes.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any

from app.ui.role_context import UserRole


def apply_release_qa_fixes() -> None:
    """Patch the active UI classes for the final QA gate."""

    from app.ui.operations_tab import OperationsTab
    from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab

    OperationsTab._run_export_csv = _run_export_csv
    OperationsTab._run_restore = _run_restore
    OperationsTab._run_import_json = _run_import_json

    TitleSubtitleManagementTab._update_action_states = _title_subtitle_update_action_states
    TitleSubtitleManagementTab._update_subtitle = _update_subtitle
    TitleSubtitleManagementTab._delete_subtitle = _delete_subtitle
    TitleSubtitleManagementTab._restore_subtitle = _restore_subtitle
    TitleSubtitleManagementTab._hard_delete_subtitle = _hard_delete_subtitle


def _ui_path(value: str) -> Path | PurePosixPath:
    """Return a path object while preserving POSIX-like test paths on Windows."""

    if value.startswith("/"):
        return PurePosixPath(value)
    return Path(value)


def _start_operation(
    self: Any,
    *,
    action: str,
    label: str,
    work: Callable[[], object],
    path: str | None = None,
    path2: str | None = None,
    recent_paths: list[tuple[str, str]] | None = None,
) -> None:
    if self._is_busy:
        self._set_message("別の操作を実行中です。完了を待ってください。", is_error=True)
        return

    self._is_busy = True
    self._cancel_requested = False
    self._current_action = action
    self._set_message(f"{label} 実行中...")
    self._apply_busy_state()

    def _success(result: object) -> None:
        for field_key, value in recent_paths or []:
            self._push_recent_path(field_key, value)
        status = "cancel" if self._cancel_requested else "success"
        message = (
            f"{label} 完了（cancel requested 後に完了）"
            if self._cancel_requested
            else f"{label} 成功: {result}"
        )
        self._set_message(message)
        self._record_operation(action, status, message, path=path, path2=path2)

    def _error(exc: Exception) -> None:
        message = f"{label} 失敗: {exc}"
        self._set_message(message, is_error=True)
        self._record_operation(action, "error", message, path=path, path2=path2)

    def _finished() -> None:
        self._is_busy = False
        self._current_action = None
        self._apply_busy_state()

    self._operation_executor.submit(work, _success, _error, _finished)


def _run_export_csv(self: Any) -> None:
    if not self._ensure_not_busy():
        return
    output_dir = self._require_text(self.csv_export_path_input, "CSV出力先ディレクトリ")
    if output_dir is None:
        return

    def _work() -> object:
        return self._export_backup_service.export_csv(_ui_path(output_dir), role=self._role)

    _start_operation(
        self,
        action="export_csv",
        label="CSV export",
        work=_work,
        path=output_dir,
        recent_paths=[("csv_export_dir", output_dir)],
    )


def _run_restore(self: Any) -> None:
    from app.ui import operations_tab as module

    if not self._ensure_not_busy():
        return
    backup_path = self._require_text(self.restore_backup_path_input, "バックアップ入力ファイル")
    target_path = self._require_text(self.restore_target_db_path_input, "復元先DBファイル")
    if backup_path is None or target_path is None:
        return
    if not module.confirm_destructive_action(
        self,
        "復元確認",
        "restore を実行します。対象DBは置換されます。続行しますか？",
    ):
        message = "Restore はキャンセルされました"
        self._set_message(message)
        self._record_operation("restore", "cancel", message, path=backup_path, path2=target_path)
        return

    def _work() -> object:
        return self._backup_restore_service.restore_database(
            _ui_path(backup_path),
            _ui_path(target_path),
            role=self._role,
        )

    _start_operation(
        self,
        action="restore",
        label="Restore",
        work=_work,
        path=backup_path,
        path2=target_path,
        recent_paths=[
            ("restore_backup_file", backup_path),
            ("restore_target_file", target_path),
        ],
    )


def _run_import_json(self: Any) -> None:
    from app.ui import operations_tab as module

    if not self._ensure_not_busy():
        return
    json_path = self._require_text(self.import_json_path_input, "JSONファイル")
    if json_path is None:
        return
    if not module.confirm_destructive_action(
        self,
        "JSON Import確認",
        "JSON import を実行します。空DBへの初期取込のみ想定です。続行しますか？",
    ):
        message = "JSON Import はキャンセルされました"
        self._set_message(message)
        self._record_operation("import_json", "cancel", message, path=json_path)
        return

    def _work() -> object:
        return self._import_service.import_json(_ui_path(json_path), role=self._role)

    _start_operation(
        self,
        action="import_json",
        label="JSON import",
        work=_work,
        path=json_path,
        recent_paths=[("import_json_file", json_path)],
    )


def _role(self: Any) -> UserRole:
    return self._role_context.role


def _title_subtitle_update_action_states(self: Any) -> None:
    from app.ui.permissions import can_create_or_update, can_run_destructive_actions

    can_write = can_create_or_update(_role(self))
    can_destructive = can_run_destructive_actions(_role(self))

    has_title = self._selected_title is not None
    title_deleted = bool(self._selected_title and self._selected_title.deleted)
    has_subtitle = self._selected_subtitle is not None
    subtitle_deleted = bool(self._selected_subtitle and self._selected_subtitle.deleted)

    self.title_create_button.setEnabled(can_write)
    self.title_update_button.setEnabled(can_write and has_title and not title_deleted)
    self.title_delete_button.setEnabled(can_destructive and has_title and not title_deleted)
    self.title_restore_button.setEnabled(can_destructive and has_title and title_deleted)
    self.title_hard_delete_button.setEnabled(can_destructive and has_title and title_deleted)

    self.subtitle_refresh_button.setEnabled(has_title)
    self.subtitle_create_button.setEnabled(can_write and has_title and not title_deleted)
    self.subtitle_update_button.setEnabled(
        can_write and has_title and has_subtitle and not title_deleted and not subtitle_deleted
    )
    self.subtitle_delete_button.setEnabled(
        can_destructive
        and has_title
        and has_subtitle
        and not title_deleted
        and not subtitle_deleted
    )
    self.subtitle_restore_button.setEnabled(
        can_destructive and has_title and has_subtitle and not title_deleted and subtitle_deleted
    )
    self.subtitle_hard_delete_button.setEnabled(
        can_destructive and has_title and has_subtitle and not title_deleted and subtitle_deleted
    )

    if not has_title:
        self.subtitle_hint_label.setText("タイトルを選択してください")
    elif title_deleted:
        self.subtitle_hint_label.setText(
            "削除済みタイトルが選択されています（サブタイトル操作は無効）"
        )
    else:
        self.subtitle_hint_label.setText("選択中タイトル配下のサブタイトルを操作できます")


def _update_subtitle(self: Any) -> None:
    from app.ui.permissions import can_create_or_update

    if not can_create_or_update(_role(self)):
        self._set_message("このロールではサブタイトル更新できません", is_error=True)
        return

    selected_title = self._require_selected_title()
    if selected_title is None:
        return
    if selected_title.deleted:
        self._set_message("削除済みタイトルのサブタイトルは更新できません", is_error=True)
        return

    selected_subtitle = self._require_selected_subtitle()
    if selected_subtitle is None:
        return
    if selected_subtitle.deleted:
        self._set_message("削除済みサブタイトルは更新できません", is_error=True)
        return

    operator_id = self._require_operator_id()
    if operator_id is None:
        return

    self._core_service.update_subtitle(
        selected_subtitle.id,
        self._subtitle_payload(selected_title.id),
        operator_id=operator_id,
        role=_role(self),
    )
    self._set_message("サブタイトル更新しました")
    self._refresh_subtitles(selected_subtitle.id)


def _delete_subtitle(self: Any) -> None:
    from app.ui import title_subtitle_management_tab as module
    from app.ui.permissions import can_run_destructive_actions

    if not can_run_destructive_actions(_role(self)):
        self._set_message("このロールではサブタイトル論理削除できません", is_error=True)
        return

    selected_title = self._require_selected_title()
    selected_subtitle = self._require_selected_subtitle()
    if selected_title is None or selected_subtitle is None:
        return
    if selected_title.deleted:
        self._set_message("削除済みタイトル配下のサブタイトルは操作できません", is_error=True)
        return
    if selected_subtitle.deleted:
        self._set_message("既に削除済みサブタイトルです", is_error=True)
        return

    operator_id = self._require_operator_id()
    if operator_id is None:
        return
    if not module.confirm_destructive_action(
        self,
        "論理削除の確認",
        f"サブタイトルID={selected_subtitle.id} を論理削除します。よろしいですか？",
    ):
        self._set_message("サブタイトル論理削除をキャンセルしました")
        return

    self._core_service.delete_subtitle(selected_subtitle.id, operator_id=operator_id, role=_role(self))
    self._selected_subtitle = type(selected_subtitle)(selected_subtitle.id, True)
    self._set_message("サブタイトル論理削除しました")
    self._update_action_states()


def _restore_subtitle(self: Any) -> None:
    from app.ui import title_subtitle_management_tab as module
    from app.ui.permissions import can_run_destructive_actions

    if not can_run_destructive_actions(_role(self)):
        self._set_message("このロールではサブタイトル復元できません", is_error=True)
        return

    selected_title = self._require_selected_title()
    selected_subtitle = self._require_selected_subtitle()
    if selected_title is None or selected_subtitle is None:
        return
    if selected_title.deleted:
        self._set_message("削除済みタイトル配下のサブタイトルは操作できません", is_error=True)
        return
    if not selected_subtitle.deleted:
        self._set_message("有効サブタイトルは復元できません", is_error=True)
        return

    operator_id = self._require_operator_id()
    if operator_id is None:
        return
    if not module.confirm_destructive_action(
        self,
        "復元の確認",
        f"サブタイトルID={selected_subtitle.id} を復元します。よろしいですか？",
    ):
        self._set_message("サブタイトル復元をキャンセルしました")
        return

    self._core_service.restore_subtitle(
        selected_subtitle.id,
        operator_id=operator_id,
        role=_role(self),
    )
    self._selected_subtitle = type(selected_subtitle)(selected_subtitle.id, True)
    self._set_message("サブタイトル復元しました")
    self._update_action_states()


def _hard_delete_subtitle(self: Any) -> None:
    from app.ui import title_subtitle_management_tab as module
    from app.ui.permissions import can_run_destructive_actions

    if not can_run_destructive_actions(_role(self)):
        self._set_message("このロールではサブタイトル完全削除できません", is_error=True)
        return

    selected_title = self._require_selected_title()
    selected_subtitle = self._require_selected_subtitle()
    if selected_title is None or selected_subtitle is None:
        return
    if selected_title.deleted:
        self._set_message("削除済みタイトル配下のサブタイトルは操作できません", is_error=True)
        return
    if not selected_subtitle.deleted:
        self._set_message("完全削除は削除済みサブタイトルのみ可能です", is_error=True)
        return

    operator_id = self._require_operator_id()
    if operator_id is None:
        return
    if not module.confirm_destructive_action(
        self,
        "完全削除の確認",
        f"サブタイトルID={selected_subtitle.id} を完全削除します。この操作は元に戻せません。",
    ):
        self._set_message("サブタイトル完全削除をキャンセルしました")
        return

    self._core_service.hard_delete_subtitle(
        selected_subtitle.id,
        operator_id=operator_id,
        role=_role(self),
    )
    self._set_message("サブタイトル完全削除しました")
    self._refresh_subtitles()
