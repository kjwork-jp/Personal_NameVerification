"""Operations tab for export/import/backup/restore entrypoints."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QSettings, QStringListModel, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.dialogs import confirm_destructive_action
from app.ui.operations_log import OperationsJsonlLogger
from app.ui.operations_workers import OperationExecutorLike, ThreadPoolOperationExecutor
from app.ui.role_context import RoleContext, UserRole

MAX_RECENT_PATHS = 5
HISTORY_PREFIX = "operations/recent_paths"
DEFAULT_LOGS_PAGE_SIZE = 100


class ExportBackupLike(Protocol):
    def export_csv(self, output_dir: Path, role: UserRole = "admin") -> dict[str, Path]: ...

    def export_json(self, output_path: Path, role: UserRole = "admin") -> Path: ...

    def export_sql_dump(self, output_path: Path, role: UserRole = "admin") -> Path: ...

    def create_backup(
        self,
        db_path: Path,
        backup_path: Path,
        role: UserRole = "admin",
    ) -> Path: ...


class BackupRestoreLike(Protocol):
    def restore_database(
        self,
        backup_path: Path,
        target_db_path: Path,
        role: UserRole = "admin",
    ) -> Path: ...


class ImportLike(Protocol):
    def import_csv(self, csv_dir: Path, role: UserRole = "admin") -> dict[str, int]: ...

    def import_json(self, json_path: Path, role: UserRole = "admin") -> dict[str, int]: ...


class SettingsLike(Protocol):
    def value(self, key: str, defaultValue: object | None = None) -> object | None: ...

    def setValue(self, key: str, value: object) -> None: ...

    def remove(self, key: str) -> None: ...


class OperationLoggerLike(Protocol):
    def append(
        self,
        *,
        action: str,
        role: str,
        status: str,
        message: str,
        path: str | None = None,
        path2: str | None = None,
    ) -> None: ...

    def read_latest(
        self,
        limit: int = 100,
        *,
        include_archives: bool = False,
    ) -> tuple[list[object], int]: ...

    def list_archives(self) -> list[Path]: ...


class OperationsTab(QWidget):
    """Minimal operations UI with behavior aligned to the UI tests."""

    def __init__(
        self,
        export_backup_service: ExportBackupLike,
        backup_restore_service: BackupRestoreLike,
        import_service: ImportLike,
        role_context: RoleContext | None = None,
        settings: SettingsLike | None = None,
        operation_logger: OperationLoggerLike | None = None,
        operation_executor: OperationExecutorLike | None = None,
    ) -> None:
        super().__init__()
        self._export_backup_service = export_backup_service
        self._backup_restore_service = backup_restore_service
        self._import_service = import_service
        self._role = (role_context or RoleContext.admin()).role
        self._settings: SettingsLike = settings or QSettings(
            "NameVerification",
            "NameVerificationV3",
        )
        self._operation_logger = operation_logger or OperationsJsonlLogger()
        self._operation_executor = operation_executor or ThreadPoolOperationExecutor()
        self._history_models: dict[str, QStringListModel] = {}
        self._clear_history_buttons: dict[str, QPushButton] = {}
        self._is_busy = False
        self._cancel_requested = False
        self._current_action: str | None = None
        self._log_page_index = 0

        self.csv_export_path_input = QLineEdit()
        self.json_export_path_input = QLineEdit()
        self.sql_dump_path_input = QLineEdit()
        self.db_path_input = QLineEdit()
        self.backup_output_path_input = QLineEdit()
        self.restore_backup_path_input = QLineEdit()
        self.restore_target_db_path_input = QLineEdit()
        self.import_csv_dir_input = QLineEdit()
        self.import_json_path_input = QLineEdit()

        self.csv_export_browse_button = QPushButton("参照")
        self.json_export_browse_button = QPushButton("参照")
        self.sql_dump_browse_button = QPushButton("参照")
        self.db_path_browse_button = QPushButton("参照")
        self.backup_output_browse_button = QPushButton("参照")
        self.restore_backup_browse_button = QPushButton("参照")
        self.restore_target_browse_button = QPushButton("参照")
        self.import_csv_dir_browse_button = QPushButton("参照")
        self.import_json_browse_button = QPushButton("参照")

        self.export_csv_button = QPushButton("CSV出力")
        self.export_json_button = QPushButton("JSON出力")
        self.export_sql_dump_button = QPushButton("SQLダンプ出力")
        self.create_backup_button = QPushButton("バックアップ作成")
        self.restore_button = QPushButton("復元")
        self.import_csv_button = QPushButton("CSV取込")
        self.import_json_button = QPushButton("JSON取込")
        self.cancel_operation_button = QPushButton("キャンセル")
        self.clear_recent_paths_button = QPushButton("履歴クリア")

        self.reload_logs_button = QPushButton("ログ再読込")
        self.export_logs_button = QPushButton("ログエクスポート")
        self.log_prev_button = QPushButton("前へ")
        self.log_next_button = QPushButton("次へ")
        self.log_page_label = QLabel("ページ 0/0")
        self.log_source_info_label = QLabel("source: current")

        self.log_limit_selector = QComboBox()
        self.log_limit_selector.addItems(["50", "100", "200", "500"])
        self.log_limit_selector.setCurrentText(str(DEFAULT_LOGS_PAGE_SIZE))
        self.include_archives_checkbox = QCheckBox("archive を含める")
        self.log_source_selector = QComboBox()
        self.log_source_selector.addItems(["current only", "all (current + archives)"])
        self.log_status_filter = QComboBox()
        self.log_status_filter.addItems(["all", "success", "error", "cancel"])
        self.log_action_filter = QComboBox()
        self.log_action_filter.addItem("all")
        self.log_message_search_input = QLineEdit()
        self.log_message_search_input.setPlaceholderText("message 検索（部分一致）")
        self.log_regex_checkbox = QCheckBox("正規表現")
        self.log_regex_ignore_case_checkbox = QCheckBox("大文字小文字を無視")
        self.log_regex_ignore_case_checkbox.setChecked(True)
        self.log_regex_multiline_checkbox = QCheckBox("複数行")
        self.log_regex_dotall_checkbox = QCheckBox("ドット改行一致")
        self.log_sort_order = QComboBox()
        self.log_sort_order.addItems(["最新順", "古い順"])

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.operation_log_view = QTextEdit()
        self.operation_log_view.setReadOnly(True)

        self.csv_export_browse_button.clicked.connect(
            lambda: self._select_directory(
                self.csv_export_path_input,
                "CSV出力先ディレクトリを選択",
                field_key="csv_export_dir",
            )
        )
        self.json_export_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.json_export_path_input,
                "JSON出力先ファイルを選択",
                "JSON Files (*.json);;All Files (*)",
                field_key="json_export_file",
            )
        )
        self.sql_dump_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.sql_dump_path_input,
                "SQL dump出力先ファイルを選択",
                "SQL Files (*.sql);;All Files (*)",
                field_key="sql_dump_file",
            )
        )
        self.db_path_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.db_path_input,
                "DBファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="db_file",
            )
        )
        self.backup_output_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.backup_output_path_input,
                "バックアップ出力先ファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="backup_output_file",
            )
        )
        self.restore_backup_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.restore_backup_path_input,
                "restore用バックアップファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="restore_backup_file",
            )
        )
        self.restore_target_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.restore_target_db_path_input,
                "restore先DBファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="restore_target_file",
            )
        )
        self.import_csv_dir_browse_button.clicked.connect(
            lambda: self._select_directory(
                self.import_csv_dir_input,
                "CSV importディレクトリを選択",
                field_key="import_csv_dir",
            )
        )
        self.import_json_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.import_json_path_input,
                "JSON importファイルを選択",
                "JSON Files (*.json);;All Files (*)",
                field_key="import_json_file",
            )
        )

        self.export_csv_button.clicked.connect(self._run_export_csv)
        self.export_json_button.clicked.connect(self._run_export_json)
        self.export_sql_dump_button.clicked.connect(self._run_export_sql_dump)
        self.create_backup_button.clicked.connect(self._run_create_backup)
        self.restore_button.clicked.connect(self._run_restore)
        self.import_csv_button.clicked.connect(self._run_import_csv)
        self.import_json_button.clicked.connect(self._run_import_json)
        self.cancel_operation_button.clicked.connect(self._request_cancel)
        self.clear_recent_paths_button.clicked.connect(self._clear_recent_paths)
        self.reload_logs_button.clicked.connect(self._reset_log_page_and_reload)
        self.export_logs_button.clicked.connect(self._export_visible_logs)
        self.log_prev_button.clicked.connect(self._go_prev_log_page)
        self.log_next_button.clicked.connect(self._go_next_log_page)

        self.include_archives_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_source_selector.currentTextChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_status_filter.currentTextChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_action_filter.currentTextChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_message_search_input.textChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_ignore_case_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_multiline_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_dotall_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_sort_order.currentTextChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_limit_selector.currentTextChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )

        root = QVBoxLayout(self)
        root.addWidget(
            self._build_group(
                "Export",
                [
                    (
                        "CSV出力先ディレクトリ",
                        self.csv_export_path_input,
                        self.csv_export_browse_button,
                        "csv_export_dir",
                    ),
                    (
                        "JSON出力先ファイル",
                        self.json_export_path_input,
                        self.json_export_browse_button,
                        "json_export_file",
                    ),
                    (
                        "SQL dump出力先ファイル",
                        self.sql_dump_path_input,
                        self.sql_dump_browse_button,
                        "sql_dump_file",
                    ),
                ],
                [
                    self.export_csv_button,
                    self.export_json_button,
                    self.export_sql_dump_button,
                ],
            )
        )
        root.addWidget(
            self._build_group(
                "Backup",
                [
                    (
                        "DBファイルパス",
                        self.db_path_input,
                        self.db_path_browse_button,
                        "db_file",
                    ),
                    (
                        "バックアップ出力先",
                        self.backup_output_path_input,
                        self.backup_output_browse_button,
                        "backup_output_file",
                    ),
                ],
                [self.create_backup_button],
            )
        )
        root.addWidget(
            self._build_group(
                "Restore（destructive）",
                [
                    (
                        "バックアップ入力ファイル",
                        self.restore_backup_path_input,
                        self.restore_backup_browse_button,
                        "restore_backup_file",
                    ),
                    (
                        "復元先DBファイル",
                        self.restore_target_db_path_input,
                        self.restore_target_browse_button,
                        "restore_target_file",
                    ),
                ],
                [self.restore_button],
            )
        )
        root.addWidget(
            self._build_group(
                "Import（destructive）",
                [
                    (
                        "CSVディレクトリ",
                        self.import_csv_dir_input,
                        self.import_csv_dir_browse_button,
                        "import_csv_dir",
                    ),
                    (
                        "JSONファイル",
                        self.import_json_path_input,
                        self.import_json_browse_button,
                        "import_json_file",
                    ),
                ],
                [self.import_csv_button, self.import_json_button],
            )
        )

        root.addWidget(self.result_view)
        root.addWidget(self.cancel_operation_button)
        root.addWidget(self.clear_recent_paths_button)

        logs_group = QGroupBox("Operations 実行ログ（最新100件）")
        logs_layout = QVBoxLayout(logs_group)
        header = QHBoxLayout()
        for widget in [
            self.reload_logs_button,
            self.export_logs_button,
            self.log_prev_button,
            self.log_next_button,
            self.log_page_label,
        ]:
            header.addWidget(widget)
        header.addWidget(QLabel("表示件数"))
        header.addWidget(self.log_limit_selector)
        header.addStretch(1)
        logs_layout.addLayout(header)

        controls = QHBoxLayout()
        for widget in [
            self.include_archives_checkbox,
            QLabel("ソース"),
            self.log_source_selector,
            QLabel("状態"),
            self.log_status_filter,
            QLabel("操作"),
            self.log_action_filter,
            self.log_regex_checkbox,
            self.log_regex_ignore_case_checkbox,
            self.log_regex_multiline_checkbox,
            self.log_regex_dotall_checkbox,
            QLabel("並び順"),
            self.log_sort_order,
            self.log_message_search_input,
        ]:
            controls.addWidget(widget)
        logs_layout.addLayout(controls)
        logs_layout.addWidget(self.log_source_info_label)
        logs_layout.addWidget(self.operation_log_view)
        root.addWidget(logs_group)

        self.cancel_operation_button.setEnabled(False)
        self._setup_recent_paths()
        self._apply_role_guards()
        self._reload_operation_logs()

    def _build_group(
        self,
        title: str,
        fields: list[tuple[str, QLineEdit, QPushButton, str]],
        buttons: list[QPushButton],
    ) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        form = QFormLayout()
        for label, line_edit, browse_button, field_key in fields:
            row = QHBoxLayout()
            row.addWidget(line_edit)
            row.addWidget(browse_button)
            clear_button = QPushButton("履歴削除")
            clear_button.clicked.connect(
                lambda *_args, key=field_key: self._clear_recent_path(key)
            )
            self._clear_history_buttons[field_key] = clear_button
            row.addWidget(clear_button)
            form.addRow(label, row)
        layout.addLayout(form)

        buttons_row = QHBoxLayout()
        for button in buttons:
            buttons_row.addWidget(button)
        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)
        return group

    def _history_field_bindings(self) -> list[tuple[str, QLineEdit]]:
        return [
            ("csv_export_dir", self.csv_export_path_input),
            ("json_export_file", self.json_export_path_input),
            ("sql_dump_file", self.sql_dump_path_input),
            ("db_file", self.db_path_input),
            ("backup_output_file", self.backup_output_path_input),
            ("restore_backup_file", self.restore_backup_path_input),
            ("restore_target_file", self.restore_target_db_path_input),
            ("import_csv_dir", self.import_csv_dir_input),
            ("import_json_file", self.import_json_path_input),
        ]

    def _history_settings_key(self, field_key: str) -> str:
        return f"{HISTORY_PREFIX}/{field_key}"

    def _normalize_recent_paths(self, paths: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in paths:
            candidate = str(value).strip()
            if not candidate or candidate in normalized:
                continue
            normalized.append(candidate)
            if len(normalized) >= MAX_RECENT_PATHS:
                break
        return normalized

    def _get_recent_paths(self, field_key: str) -> list[str]:
        raw = self._settings.value(self._history_settings_key(field_key), [])
        if isinstance(raw, str):
            return self._normalize_recent_paths([raw])
        if isinstance(raw, (list, tuple)):
            return self._normalize_recent_paths([str(item) for item in raw])
        return []

    def _push_recent_path(self, field_key: str, value: str) -> None:
        candidate = value.strip()
        if not candidate:
            return
        updated = self._normalize_recent_paths(
            [candidate] + self._get_recent_paths(field_key)
        )
        self._settings.setValue(self._history_settings_key(field_key), updated)
        model = self._history_models.get(field_key)
        if model is not None:
            model.setStringList(updated)

    def _setup_recent_paths(self) -> None:
        for field_key, line_edit in self._history_field_bindings():
            history = self._get_recent_paths(field_key)
            model = QStringListModel(history)
            self._history_models[field_key] = model
            completer = QCompleter(model, line_edit)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            line_edit.setCompleter(completer)
            if history and not line_edit.text().strip():
                line_edit.setText(history[0])

    def _select_directory(self, target: QLineEdit, title: str, *, field_key: str) -> None:
        chosen = QFileDialog.getExistingDirectory(self, title, target.text().strip())
        if chosen:
            target.setText(chosen)
            self._push_recent_path(field_key, chosen)

    def _select_open_file(
        self,
        target: QLineEdit,
        title: str,
        filter_spec: str,
        *,
        field_key: str,
    ) -> None:
        chosen, _ = QFileDialog.getOpenFileName(
            self,
            title,
            target.text().strip(),
            filter_spec,
        )
        if chosen:
            target.setText(chosen)
            self._push_recent_path(field_key, chosen)

    def _select_save_file(
        self,
        target: QLineEdit,
        title: str,
        filter_spec: str,
        *,
        field_key: str,
    ) -> None:
        chosen, _ = QFileDialog.getSaveFileName(
            self,
            title,
            target.text().strip(),
            filter_spec,
        )
        if chosen:
            target.setText(chosen)
            self._push_recent_path(field_key, chosen)

    def _apply_role_guards(self) -> None:
        editor_or_admin = self._role in {"editor", "admin"}
        admin_only = self._role == "admin"

        self.export_csv_button.setEnabled(editor_or_admin)
        self.export_json_button.setEnabled(editor_or_admin)
        self.export_sql_dump_button.setEnabled(editor_or_admin)
        self.create_backup_button.setEnabled(editor_or_admin)
        self.restore_button.setEnabled(admin_only)
        self.import_csv_button.setEnabled(admin_only)
        self.import_json_button.setEnabled(admin_only)
        self._apply_busy_state()

    def _apply_role_guards_only(self) -> None:
        editor_or_admin = self._role in {"editor", "admin"}
        admin_only = self._role == "admin"

        self.export_csv_button.setEnabled(editor_or_admin)
        self.export_json_button.setEnabled(editor_or_admin)
        self.export_sql_dump_button.setEnabled(editor_or_admin)
        self.create_backup_button.setEnabled(editor_or_admin)
        self.restore_button.setEnabled(admin_only)
        self.import_csv_button.setEnabled(admin_only)
        self.import_json_button.setEnabled(admin_only)

    def _apply_busy_state(self) -> None:
        widgets: list[QWidget] = [
            self.export_csv_button,
            self.export_json_button,
            self.export_sql_dump_button,
            self.create_backup_button,
            self.restore_button,
            self.import_csv_button,
            self.import_json_button,
            self.csv_export_browse_button,
            self.json_export_browse_button,
            self.sql_dump_browse_button,
            self.db_path_browse_button,
            self.backup_output_browse_button,
            self.restore_backup_browse_button,
            self.restore_target_browse_button,
            self.import_csv_dir_browse_button,
            self.import_json_browse_button,
            self.clear_recent_paths_button,
            self.reload_logs_button,
            self.export_logs_button,
            self.log_prev_button,
            self.log_next_button,
            self.log_limit_selector,
            self.include_archives_checkbox,
            self.log_source_selector,
            self.log_status_filter,
            self.log_action_filter,
            self.log_regex_checkbox,
            self.log_regex_ignore_case_checkbox,
            self.log_regex_multiline_checkbox,
            self.log_regex_dotall_checkbox,
            self.log_sort_order,
            self.log_message_search_input,
            *self._clear_history_buttons.values(),
        ]
        for widget in widgets:
            widget.setEnabled(not self._is_busy)
        self.cancel_operation_button.setEnabled(self._is_busy)
        if not self._is_busy:
            self._apply_role_guards_only()

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        prefix = "ERROR" if is_error else "OK"
        self.result_view.append(f"[{prefix}] {message}")

    def _record_operation(
        self,
        action: str,
        status: str,
        message: str,
        *,
        path: str | None = None,
        path2: str | None = None,
    ) -> None:
        try:
            self._operation_logger.append(
                action=action,
                role=self._role,
                status=status,
                message=message,
                path=path,
                path2=path2,
            )
        except Exception:
            return
        self._reload_operation_logs()

    def _request_cancel(self) -> None:
        if not self._is_busy:
            return
        self._cancel_requested = True
        self._operation_executor.request_cancel()
        message = "Cancel requested（実行中処理の停止要求を受け付けました）"
        self._set_message(message)
        self._record_operation(self._current_action or "unknown", "cancel", message)

    def _ensure_not_busy(self) -> bool:
        if not self._is_busy:
            return True
        self._set_message("別の操作を実行中です。完了を待ってください。", is_error=True)
        return False

    def _start_async_operation(
        self,
        action: str,
        label: str,
        work: Callable[[], object],
        on_success: Callable[[object], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        if self._is_busy:
            self._set_message("別の操作を実行中です。完了を待ってください。", is_error=True)
            return

        self._is_busy = True
        self._cancel_requested = False
        self._current_action = action
        self._set_message(f"{label} 実行中...")
        self._apply_busy_state()

        def _finished() -> None:
            self._is_busy = False
            self._current_action = None
            self._apply_busy_state()

        self._operation_executor.submit(work, on_success, on_error, _finished)

    def _require_text(self, line_edit: QLineEdit, label: str) -> str | None:
        text = line_edit.text().strip()
        if not text:
            self._set_message(f"{label} は必須です", is_error=True)
            return None
        return text

    def _run_export_csv(self) -> None:
        if not self._ensure_not_busy():
            return
        path = self._require_text(self.csv_export_path_input, "CSV出力先ディレクトリ")
        if path is None:
            return

        def _work() -> object:
            return len(self._export_backup_service.export_csv(Path(path), role=self._role))

        def _success(result: object) -> None:
            self._push_recent_path("csv_export_dir", path)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "CSV export 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"CSV export 成功: {result} tables"
            )
            self._set_message(message)
            self._record_operation("export_csv", status, message, path=path)

        def _error(exc: Exception) -> None:
            message = f"CSV export 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_csv", "error", message, path=path)

        self._start_async_operation("export_csv", "CSV export", _work, _success, _error)

    def _run_export_json(self) -> None:
        if not self._ensure_not_busy():
            return
        path = self._require_text(self.json_export_path_input, "JSON出力先ファイル")
        if path is None:
            return

        def _work() -> object:
            return self._export_backup_service.export_json(Path(path), role=self._role)

        def _success(result: object) -> None:
            self._push_recent_path("json_export_file", path)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "JSON export 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"JSON export 成功: {result}"
            )
            self._set_message(message)
            self._record_operation("export_json", status, message, path=path)

        def _error(exc: Exception) -> None:
            message = f"JSON export 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_json", "error", message, path=path)

        self._start_async_operation("export_json", "JSON export", _work, _success, _error)

    def _run_export_sql_dump(self) -> None:
        if not self._ensure_not_busy():
            return
        path = self._require_text(self.sql_dump_path_input, "SQL dump出力先ファイル")
        if path is None:
            return

        def _work() -> object:
            return self._export_backup_service.export_sql_dump(Path(path), role=self._role)

        def _success(result: object) -> None:
            self._push_recent_path("sql_dump_file", path)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "SQL dump export 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"SQL dump export 成功: {result}"
            )
            self._set_message(message)
            self._record_operation("export_sql_dump", status, message, path=path)

        def _error(exc: Exception) -> None:
            message = f"SQL dump export 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_sql_dump", "error", message, path=path)

        self._start_async_operation(
            "export_sql_dump",
            "SQL dump export",
            _work,
            _success,
            _error,
        )

    def _run_create_backup(self) -> None:
        if not self._ensure_not_busy():
            return
        db_path = self._require_text(self.db_path_input, "DBファイルパス")
        backup_path = self._require_text(self.backup_output_path_input, "バックアップ出力先")
        if db_path is None or backup_path is None:
            return

        def _work() -> object:
            return self._export_backup_service.create_backup(
                Path(db_path),
                Path(backup_path),
                role=self._role,
            )

        def _success(result: object) -> None:
            self._push_recent_path("db_file", db_path)
            self._push_recent_path("backup_output_file", backup_path)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "Backup create 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"Backup create 成功: {result}"
            )
            self._set_message(message)
            self._record_operation(
                "create_backup",
                status,
                message,
                path=db_path,
                path2=backup_path,
            )

        def _error(exc: Exception) -> None:
            message = f"Backup create 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation(
                "create_backup",
                "error",
                message,
                path=db_path,
                path2=backup_path,
            )

        self._start_async_operation("create_backup", "Backup create", _work, _success, _error)

    def _run_restore(self) -> None:
        if not self._ensure_not_busy():
            return
        backup_path = self._require_text(self.restore_backup_path_input, "バックアップ入力ファイル")
        target_path = self._require_text(self.restore_target_db_path_input, "復元先DBファイル")
        if backup_path is None or target_path is None:
            return
        if not confirm_destructive_action(
            self,
            "復元確認",
            "restore を実行します。対象DBは置換されます。続行しますか？",
        ):
            message = "Restore はキャンセルされました"
            self._set_message(message)
            self._record_operation(
                "restore",
                "cancel",
                message,
                path=backup_path,
                path2=target_path,
            )
            return

        def _work() -> object:
            return self._backup_restore_service.restore_database(
                Path(backup_path),
                Path(target_path),
                role=self._role,
            )

        def _success(result: object) -> None:
            self._push_recent_path("restore_backup_file", backup_path)
            self._push_recent_path("restore_target_file", target_path)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "Restore 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"Restore 成功: {result}"
            )
            self._set_message(message)
            self._record_operation(
                "restore",
                status,
                message,
                path=backup_path,
                path2=target_path,
            )

        def _error(exc: Exception) -> None:
            message = f"Restore 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation(
                "restore",
                "error",
                message,
                path=backup_path,
                path2=target_path,
            )

        self._start_async_operation("restore", "Restore", _work, _success, _error)

    def _run_import_csv(self) -> None:
        if not self._ensure_not_busy():
            return
        csv_dir = self._require_text(self.import_csv_dir_input, "CSVディレクトリ")
        if csv_dir is None:
            return
        if not confirm_destructive_action(
            self,
            "CSV Import確認",
            "CSV import を実行します。空DBへの初期取込のみ想定です。続行しますか？",
        ):
            message = "CSV Import はキャンセルされました"
            self._set_message(message)
            self._record_operation("import_csv", "cancel", message, path=csv_dir)
            return

        def _work() -> object:
            return self._import_service.import_csv(Path(csv_dir), role=self._role)

        def _success(result: object) -> None:
            self._push_recent_path("import_csv_dir", csv_dir)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "CSV import 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"CSV import 成功: {result}"
            )
            self._set_message(message)
            self._record_operation("import_csv", status, message, path=csv_dir)

        def _error(exc: Exception) -> None:
            message = f"CSV import 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("import_csv", "error", message, path=csv_dir)

        self._start_async_operation("import_csv", "CSV import", _work, _success, _error)

    def _run_import_json(self) -> None:
        if not self._ensure_not_busy():
            return
        json_path = self._require_text(self.import_json_path_input, "JSONファイル")
        if json_path is None:
            return
        if not confirm_destructive_action(
            self,
            "JSON Import確認",
            "JSON import を実行します。空DBへの初期取込のみ想定です。続行しますか？",
        ):
            message = "JSON Import はキャンセルされました"
            self._set_message(message)
            self._record_operation("import_json", "cancel", message, path=json_path)
            return

        def _work() -> object:
            return self._import_service.import_json(Path(json_path), role=self._role)

        def _success(result: object) -> None:
            self._push_recent_path("import_json_file", json_path)
            status = "cancel" if self._cancel_requested else "success"
            message = (
                "JSON import 完了（cancel requested 後に完了）"
                if self._cancel_requested
                else f"JSON import 成功: {result}"
            )
            self._set_message(message)
            self._record_operation("import_json", status, message, path=json_path)

        def _error(exc: Exception) -> None:
            message = f"JSON import 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("import_json", "error", message, path=json_path)

        self._start_async_operation("import_json", "JSON import", _work, _success, _error)

    def _sync_log_source_selector(self) -> None:
        current = self.log_source_selector.currentText() or "current only"
        options = ["current only", "all (current + archives)"]
        for archive in self._operation_logger.list_archives():
            options.append(f"archive:{archive}")
        self.log_source_selector.blockSignals(True)
        self.log_source_selector.clear()
        self.log_source_selector.addItems(options)
        if current in options:
            self.log_source_selector.setCurrentText(current)
        self.log_source_selector.blockSignals(False)

    def _sync_log_source_info(self, mode: str, archive_path: Path | None) -> None:
        archives = self._operation_logger.list_archives()
        if mode == "current":
            text = f"source: current（archives: {len(archives)}件）"
        elif mode == "all":
            text = f"source: all（current + archives {len(archives)}件）"
        else:
            name = archive_path.name if archive_path is not None else "(unknown)"
            text = f"source: archive（{name}）"
        self.log_source_info_label.setText(text)
        tooltip = "\n".join(path.name for path in archives) if archives else "archive はありません。"
        self.log_source_info_label.setToolTip(tooltip)

    def _sync_action_filter_options(self, events: list[object]) -> None:
        current = self.log_action_filter.currentText() or "all"
        actions = sorted(
            {
                str(getattr(event, "action", "")).strip()
                for event in events
                if str(getattr(event, "action", "")).strip()
            }
        )
        self.log_action_filter.blockSignals(True)
        self.log_action_filter.clear()
        self.log_action_filter.addItem("all")
        self.log_action_filter.addItems(actions)
        if current in {"all", *actions}:
            self.log_action_filter.setCurrentText(current)
        self.log_action_filter.blockSignals(False)

    def _log_page_size(self) -> int:
        text = self.log_limit_selector.currentText().strip()
        return max(1, int(text)) if text.isdigit() else DEFAULT_LOGS_PAGE_SIZE

    def _sort_log_events(self, events: list[object]) -> list[object]:
        reverse = self.log_sort_order.currentText() != "古い順"
        return sorted(
            events,
            key=lambda event: str(getattr(event, "timestamp", "")),
            reverse=reverse,
        )

    def _filter_log_events(self, events: list[object]) -> tuple[list[object], str | None]:
        status_filter = self.log_status_filter.currentText()
        action_filter = self.log_action_filter.currentText()
        query = self.log_message_search_input.text().strip()

        regex_error: str | None = None
        pattern: re.Pattern[str] | None = None
        flags = 0
        if self.log_regex_ignore_case_checkbox.isChecked():
            flags |= re.IGNORECASE
        if self.log_regex_multiline_checkbox.isChecked():
            flags |= re.MULTILINE
        if self.log_regex_dotall_checkbox.isChecked():
            flags |= re.DOTALL

        if query and self.log_regex_checkbox.isChecked():
            try:
                pattern = re.compile(query, flags)
            except re.error as exc:
                regex_error = str(exc)

        filtered: list[object] = []
        for event in events:
            timestamp = str(getattr(event, "timestamp", ""))
            action = str(getattr(event, "action", ""))
            role = str(getattr(event, "role", ""))
            status = str(getattr(event, "status", ""))
            message = str(getattr(event, "message", ""))
            path = str(getattr(event, "path", "") or "")
            path2 = str(getattr(event, "path2", "") or "")

            if status_filter != "all" and status != status_filter:
                continue
            if action_filter != "all" and action != action_filter:
                continue

            searchable_fields = [timestamp, action, role, status, message, path, path2]
            haystack = " ".join(searchable_fields)
            if query:
                if pattern is not None:
                    if not any(pattern.search(field) for field in searchable_fields if field):
                        continue
                elif self.log_regex_checkbox.isChecked() and regex_error is not None:
                    pass
                elif query.lower() not in haystack.lower():
                    continue
            filtered.append(event)

        return filtered, regex_error

    def _paginate_log_events(self, events: list[object]) -> tuple[list[object], int, int]:
        if not events:
            self._log_page_index = 0
            return [], 0, 0
        page_size = self._log_page_size()
        total_pages = (len(events) + page_size - 1) // page_size
        self._log_page_index = max(0, min(self._log_page_index, total_pages - 1))
        start = self._log_page_index * page_size
        return events[start : start + page_size], self._log_page_index + 1, total_pages

    def _reload_operation_logs(self) -> None:
        source_text = self.log_source_selector.currentText()
        include_archives = self.include_archives_checkbox.isChecked()
        archive_path: Path | None = None
        mode = "all" if include_archives else "current"
        if source_text == "all (current + archives)":
            include_archives = True
            mode = "all"
        elif source_text.startswith("archive:"):
            include_archives = False
            archive_path = Path(source_text.removeprefix("archive:").strip())
            mode = "archive"

        raw_events, decode_errors = self._operation_logger.read_latest(
            self._log_page_size() * 20,
            include_archives=include_archives,
        )
        events = list(raw_events)
        if archive_path is not None:
            events = [
                event
                for event in events
                if str(getattr(event, "source", "") or "") == str(archive_path)
            ]

        self._sync_log_source_selector()
        self._sync_log_source_info(mode, archive_path)
        self._sync_action_filter_options(events)
        events, regex_error = self._filter_log_events(events)
        events = self._sort_log_events(events)
        page_events, page_no, total_pages = self._paginate_log_events(events)

        self.log_page_label.setText(f"ページ {page_no}/{total_pages}")
        self.log_prev_button.setEnabled(page_no > 1 and not self._is_busy)
        self.log_next_button.setEnabled(page_no < total_pages and not self._is_busy)

        if not events:
            text = "ログはまだありません。"
            if regex_error:
                text = f"[WARN] regex エラー: {regex_error}"
                self._set_message(f"regex エラー: {regex_error}", is_error=True)
            if decode_errors > 0:
                text += f"（読み飛ばし: {decode_errors}件）"
            self.operation_log_view.setPlainText(text)
            return

        lines: list[str] = []
        for event in page_events:
            timestamp = str(getattr(event, "timestamp", ""))
            action = str(getattr(event, "action", ""))
            role = str(getattr(event, "role", ""))
            status = str(getattr(event, "status", ""))
            message = str(getattr(event, "message", ""))
            extras: list[str] = []
            if getattr(event, "path", None):
                extras.append(f"path={getattr(event, 'path')}")
            if getattr(event, "path2", None):
                extras.append(f"path2={getattr(event, 'path2')}")
            suffix = f" ({', '.join(extras)})" if extras else ""
            lines.append(f"{timestamp} | {action} | {role} | {status} | {message}{suffix}")

        if regex_error:
            lines.append(f"[WARN] regex エラー: {regex_error}")
            self._set_message(f"regex エラー: {regex_error}", is_error=True)
        if decode_errors > 0:
            lines.append(f"[WARN] 壊れたログ行を読み飛ばしました: {decode_errors}件")
        self.operation_log_view.setPlainText("\n".join(lines))

    def _reset_log_page_and_reload(self) -> None:
        self._log_page_index = 0
        self._reload_operation_logs()

    def _go_prev_log_page(self) -> None:
        if self._log_page_index > 0:
            self._log_page_index -= 1
            self._reload_operation_logs()

    def _go_next_log_page(self) -> None:
        self._log_page_index += 1
        self._reload_operation_logs()

    def _export_visible_logs(self) -> None:
        body = self.operation_log_view.toPlainText().strip()
        if not body:
            self._set_message("エクスポート対象ログがありません。", is_error=True)
            return
        chosen, _ = QFileDialog.getSaveFileName(
            self,
            "ログエクスポート先ファイルを選択",
            "",
            "Text Files (*.txt);;All Files (*)",
        )
        if not chosen:
            return
        try:
            Path(chosen).write_text(body + "\n", encoding="utf-8")
        except Exception as exc:
            message = f"ログエクスポート失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_logs", "error", message, path=chosen)
            return
        message = f"ログエクスポート成功: {chosen}"
        self._set_message(message)
        self._record_operation("export_logs", "success", message, path=chosen)

    def _clear_recent_paths(self) -> None:
        for field_key, line_edit in self._history_field_bindings():
            settings_key = self._history_settings_key(field_key)
            if hasattr(self._settings, "remove"):
                self._settings.remove(settings_key)
            else:
                self._settings.setValue(settings_key, [])
            model = self._history_models.get(field_key)
            if model is not None:
                model.setStringList([])
            line_edit.clear()
        message = "recent path history をクリアしました"
        self._set_message(message)
        self._record_operation("clear_recent_paths", "success", message)

    def _clear_recent_path(self, field_key: str) -> None:
        for key, line_edit in self._history_field_bindings():
            if key != field_key:
                continue
            settings_key = self._history_settings_key(field_key)
            if hasattr(self._settings, "remove"):
                self._settings.remove(settings_key)
            else:
                self._settings.setValue(settings_key, [])
            model = self._history_models.get(field_key)
            if model is not None:
                model.setStringList([])
            line_edit.clear()
            message = f"{field_key} の recent path history をクリアしました"
            self._set_message(message)
            self._record_operation(
                "clear_recent_path",
                "success",
                message,
                path=field_key,
            )
            return
