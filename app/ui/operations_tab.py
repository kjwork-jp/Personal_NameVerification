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
    QProgressDialog,
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

    def create_backup(self, db_path: Path, backup_path: Path, role: UserRole = "admin") -> Path: ...


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
        self, limit: int = 100, *, include_archives: bool = False
    ) -> tuple[list[object], int]: ...

    def list_archives(self) -> list[Path]: ...


class OperationsTab(QWidget):
    """Minimal operations UI for file-based operational workflows."""

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
            "NameVerification", "NameVerificationV3"
        )
        self._operation_logger = operation_logger or OperationsJsonlLogger()
        self._operation_executor = operation_executor or ThreadPoolOperationExecutor()
        self._history_models: dict[str, QStringListModel] = {}
        self._clear_history_buttons: dict[str, QPushButton] = {}
        self._log_page_index = 0
        self._is_busy = False
        self._cancel_requested = False
        self._current_action: str | None = None
        self._progress_dialog: QProgressDialog | None = None

        root = QVBoxLayout(self)
        root.addWidget(QLabel("運用系操作（export/import/backup/restore）"))

        self.csv_export_path_input = QLineEdit()
        self.csv_export_browse_button = QPushButton("参照")
        self.csv_export_browse_button.clicked.connect(
            lambda: self._select_directory(
                self.csv_export_path_input,
                "CSV出力先ディレクトリを選択",
                field_key="csv_export_dir",
            )
        )

        self.json_export_path_input = QLineEdit()
        self.json_export_browse_button = QPushButton("参照")
        self.json_export_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.json_export_path_input,
                "JSON出力先ファイルを選択",
                "JSON Files (*.json);;All Files (*)",
                field_key="json_export_file",
            )
        )

        self.sql_dump_path_input = QLineEdit()
        self.sql_dump_browse_button = QPushButton("参照")
        self.sql_dump_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.sql_dump_path_input,
                "SQL dump出力先ファイルを選択",
                "SQL Files (*.sql);;All Files (*)",
                field_key="sql_dump_file",
            )
        )

        self.db_path_input = QLineEdit()
        self.db_path_browse_button = QPushButton("参照")
        self.db_path_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.db_path_input,
                "DBファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="db_file",
            )
        )

        self.backup_output_path_input = QLineEdit()
        self.backup_output_browse_button = QPushButton("参照")
        self.backup_output_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.backup_output_path_input,
                "バックアップ出力先ファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="backup_output_file",
            )
        )

        self.restore_backup_path_input = QLineEdit()
        self.restore_backup_browse_button = QPushButton("参照")
        self.restore_backup_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.restore_backup_path_input,
                "restore用バックアップファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="restore_backup_file",
            )
        )

        self.restore_target_db_path_input = QLineEdit()
        self.restore_target_browse_button = QPushButton("参照")
        self.restore_target_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.restore_target_db_path_input,
                "restore先DBファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
                field_key="restore_target_file",
            )
        )

        self.import_csv_dir_input = QLineEdit()
        self.import_csv_dir_browse_button = QPushButton("参照")
        self.import_csv_dir_browse_button.clicked.connect(
            lambda: self._select_directory(
                self.import_csv_dir_input,
                "CSV importディレクトリを選択",
                field_key="import_csv_dir",
            )
        )

        self.import_json_path_input = QLineEdit()
        self.import_json_browse_button = QPushButton("参照")
        self.import_json_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.import_json_path_input,
                "JSON importファイルを選択",
                "JSON Files (*.json);;All Files (*)",
                field_key="import_json_file",
            )
        )

        self.export_csv_button = QPushButton("CSV出力")
        self.export_json_button = QPushButton("JSON出力")
        self.export_sql_dump_button = QPushButton("SQLダンプ出力")
        self.create_backup_button = QPushButton("バックアップ作成")
        self.restore_button = QPushButton("復元")
        self.import_csv_button = QPushButton("CSV取込")
        self.import_json_button = QPushButton("JSON取込")
        self.cancel_operation_button = QPushButton("キャンセル")
        self.clear_recent_paths_button = QPushButton("履歴クリア")
        self.export_logs_button = QPushButton("ログエクスポート")
        self.reload_logs_button = QPushButton("ログ再読込")
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
        self.cancel_operation_button.setEnabled(False)
        self.cancel_operation_button.clicked.connect(self._request_cancel)
        self.clear_recent_paths_button.clicked.connect(self._clear_recent_paths)
        self.export_logs_button.clicked.connect(self._export_visible_logs)
        self.reload_logs_button.clicked.connect(self._reset_log_page_and_reload)
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
        self.log_limit_selector.currentTextChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_message_search_input.textChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_checkbox.stateChanged.connect(lambda *_: self._reset_log_page_and_reload())
        self.log_regex_ignore_case_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_multiline_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_regex_dotall_checkbox.stateChanged.connect(
            lambda *_: self._reset_log_page_and_reload()
        )
        self.log_sort_order.currentTextChanged.connect(lambda *_: self._reset_log_page_and_reload())

        self.export_csv_button.clicked.connect(self._run_export_csv)
        self.export_json_button.clicked.connect(self._run_export_json)
        self.export_sql_dump_button.clicked.connect(self._run_export_sql_dump)
        self.create_backup_button.clicked.connect(self._run_create_backup)
        self.restore_button.clicked.connect(self._run_restore)
        self.import_csv_button.clicked.connect(self._run_import_csv)
        self.import_json_button.clicked.connect(self._run_import_json)

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
                [self.export_csv_button, self.export_json_button, self.export_sql_dump_button],
            )
        )

        root.addWidget(
            self._build_group(
                "Backup",
                [
                    ("DBファイルパス", self.db_path_input, self.db_path_browse_button, "db_file"),
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

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        root.addWidget(self.result_view)
        root.addWidget(self.cancel_operation_button)
        root.addWidget(self.clear_recent_paths_button)

        self.operation_log_view = QTextEdit()
        self.operation_log_view.setReadOnly(True)
        logs_group = QGroupBox("Operations 実行ログ（最新100件）")
        logs_box = QVBoxLayout(logs_group)
        logs_header = QHBoxLayout()
        logs_header.addWidget(self.reload_logs_button)
        logs_header.addWidget(self.export_logs_button)
        logs_header.addWidget(self.log_prev_button)
        logs_header.addWidget(self.log_next_button)
        logs_header.addWidget(self.log_page_label)
        logs_header.addWidget(QLabel("表示件数"))
        logs_header.addWidget(self.log_limit_selector)
        logs_header.addStretch(1)
        logs_box.addLayout(logs_header)
        logs_controls = QHBoxLayout()
        logs_controls.addWidget(self.include_archives_checkbox)
        logs_controls.addWidget(QLabel("ソース"))
        logs_controls.addWidget(self.log_source_selector)
        logs_controls.addWidget(QLabel("状態"))
        logs_controls.addWidget(self.log_status_filter)
        logs_controls.addWidget(QLabel("操作"))
        logs_controls.addWidget(self.log_action_filter)
        logs_controls.addWidget(self.log_regex_checkbox)
        logs_controls.addWidget(self.log_regex_ignore_case_checkbox)
        logs_controls.addWidget(self.log_regex_multiline_checkbox)
        logs_controls.addWidget(self.log_regex_dotall_checkbox)
        logs_controls.addWidget(QLabel("並び順"))
        logs_controls.addWidget(self.log_sort_order)
        logs_controls.addWidget(self.log_message_search_input)
        logs_box.addLayout(logs_controls)
        logs_box.addWidget(self.log_source_info_label)
        logs_box.addWidget(self.operation_log_view)
        root.addWidget(logs_group)

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
        box = QVBoxLayout(group)
        form = QFormLayout()
        for label, path_input, browse_button, field_key in fields:
            row = QHBoxLayout()
            row.addWidget(path_input)
            row.addWidget(browse_button)
            clear_button = QPushButton("履歴削除")
            clear_button.clicked.connect(lambda *_args, key=field_key: self._clear_recent_path(key))
            self._clear_history_buttons[field_key] = clear_button
            row.addWidget(clear_button)
            form.addRow(label, row)
        box.addLayout(form)

        actions = QHBoxLayout()
        for button in buttons:
            actions.addWidget(button)
        actions.addStretch(1)
        box.addLayout(actions)
        return group

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

    def _push_recent_path(self, field_key: str, path_value: str) -> None:
        value = path_value.strip()
        if not value:
            return

        existing = self._get_recent_paths(field_key)
        updated = self._normalize_recent_paths([value] + existing)

        self._settings.setValue(self._history_settings_key(field_key), updated)

        model = self._history_models.get(field_key)
        if model is not None:
            model.setStringList(updated)

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

        if not editor_or_admin:
            self.export_csv_button.setToolTip("このロールでは実行できません")
            self.create_backup_button.setToolTip("このロールでは実行できません")
        if not admin_only:
            self.restore_button.setToolTip("このロールでは実行できません")
            self.import_csv_button.setToolTip("このロールでは実行できません")
            self.import_json_button.setToolTip("このロールでは実行できません")
        self._apply_busy_state()

    def _show_progress(self, action_label: str) -> None:
        dialog = QProgressDialog(f"{action_label} 実行中...", "キャンセル", 0, 0, self)
        dialog.setWindowModality(Qt.WindowModality.WindowModal)
        dialog.setMinimumDuration(0)
        dialog.canceled.connect(self._request_cancel)
        dialog.setAutoClose(False)
        dialog.show()
        self._progress_dialog = dialog

    def _hide_progress(self) -> None:
        if self._progress_dialog is not None:
            self._progress_dialog.close()
            self._progress_dialog.deleteLater()
            self._progress_dialog = None

    def _apply_busy_state(self) -> None:
        execute_buttons = [
            self.export_csv_button,
            self.export_json_button,
            self.export_sql_dump_button,
            self.create_backup_button,
            self.restore_button,
            self.import_csv_button,
            self.import_json_button,
        ]
        browse_buttons = [
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
            self.log_prev_button,
            self.log_next_button,
            self.log_limit_selector,
            self.export_logs_button,
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
        ]
        browse_buttons.extend(self._clear_history_buttons.values())

        for button in execute_buttons + browse_buttons:
            button.setEnabled(not self._is_busy)
        self.cancel_operation_button.setEnabled(self._is_busy)

        if not self._is_busy:
            self._apply_role_guards_only()

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

    def _clear_recent_paths(self) -> None:
        for field_key, line_edit in self._history_field_bindings():
            key = self._history_settings_key(field_key)
            if hasattr(self._settings, "remove"):
                self._settings.remove(key)
            else:
                self._settings.setValue(key, [])
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
            self._record_operation("clear_recent_path", "success", message, path=field_key)
            return

    def _reload_operation_logs(self) -> None:
        if not hasattr(self._operation_logger, "read_latest"):
            self.operation_log_view.setPlainText("ログ読み取り未対応です。")
            return

        source = self.log_source_selector.currentText()
        include_archives = self.include_archives_checkbox.isChecked()
        archive_path: Path | None = None
        selected_mode = "current"
        if source == "current only":
            include_archives = False
            selected_mode = "current"
        elif source == "all (current + archives)":
            include_archives = True
            selected_mode = "all"
        elif source.startswith("archive:"):
            include_archives = False
            archive_path = Path(source.removeprefix("archive:").strip())
            selected_mode = "archive"

        raw_events, decode_errors = self._operation_logger.read_latest(
            self._log_page_size() * 20,
            include_archives=include_archives,
        )
        events: list[object] = list(raw_events)
        if archive_path is not None:
            events = [
                item
                for item in events
                if str(getattr(item, "source", "") or "") == str(archive_path)
            ]
        self._sync_log_source_selector()
        self._sync_log_source_info(selected_mode, archive_path)
        self._sync_action_filter_options(events)
        events, regex_error = self._filter_log_events(events)
        events = self._sort_log_events(events)
        paged_events, page_no, total_pages = self._paginate_log_events(events)
        self.log_page_label.setText(f"ページ {page_no}/{total_pages}")
        self.log_prev_button.setEnabled(page_no > 1 and not self._is_busy)
        self.log_next_button.setEnabled(page_no < total_pages and not self._is_busy)
        if not events:
            message = "ログはまだありません。"
            if regex_error:
                message = f"[WARN] regex エラー: {regex_error}"
            if decode_errors > 0:
                message += f"（読み飛ばし: {decode_errors}件）"
            self.operation_log_view.setPlainText(message)
            if regex_error:
                self._set_message(f"regex エラー: {regex_error}", is_error=True)
            return

        lines: list[str] = []
        for event in paged_events:
            timestamp = getattr(event, "timestamp", "")
            action = getattr(event, "action", "")
            role = getattr(event, "role", "")
            status = getattr(event, "status", "")
            text = getattr(event, "message", "")
            path = getattr(event, "path", None)
            path2 = getattr(event, "path2", None)
            extra = []
            if path:
                extra.append(f"path={path}")
            if path2:
                extra.append(f"path2={path2}")
            suffix = f" ({', '.join(extra)})" if extra else ""
            lines.append(f"{timestamp} | {action} | {role} | {status} | {text}{suffix}")
        if regex_error:
            lines.append(f"[WARN] regex エラー: {regex_error}")
            self._set_message(f"regex エラー: {regex_error}", is_error=True)
        if decode_errors > 0:
            lines.append(f"[WARN] 壊れたログ行を読み飛ばしました: {decode_errors}件")
        self.operation_log_view.setPlainText("\n".join(lines))

    def _sync_log_source_info(self, mode: str, archive_path: Path | None) -> None:
        archive_names: list[str] = []
        if hasattr(self._operation_logger, "list_archives"):
            archive_names = [item.name for item in self._operation_logger.list_archives()]
        if mode == "current":
            text = f"source: current（archives: {len(archive_names)}件）"
        elif mode == "all":
            text = f"source: all（current + archives {len(archive_names)}件）"
        else:
            selected_name = archive_path.name if archive_path is not None else "(unknown)"
            text = f"source: archive（{selected_name}）"
        self.log_source_info_label.setText(text)
        if archive_names:
            self.log_source_info_label.setToolTip("\n".join(archive_names))
        else:
            self.log_source_info_label.setToolTip("archive はありません。")

    def _paginate_log_events(self, events: list[object]) -> tuple[list[object], int, int]:
        if not events:
            self._log_page_index = 0
            return [], 0, 0
        page_size = self._log_page_size()
        total_pages = (len(events) + page_size - 1) // page_size
        self._log_page_index = max(0, min(self._log_page_index, total_pages - 1))
        start = self._log_page_index * page_size
        end = start + page_size
        return events[start:end], self._log_page_index + 1, total_pages

    def _log_page_size(self) -> int:
        text = self.log_limit_selector.currentText().strip()
        if text.isdigit():
            return max(1, int(text))
        return DEFAULT_LOGS_PAGE_SIZE

    def _go_prev_log_page(self) -> None:
        if self._log_page_index <= 0:
            return
        self._log_page_index -= 1
        self._reload_operation_logs()

    def _go_next_log_page(self) -> None:
        self._log_page_index += 1
        self._reload_operation_logs()

    def _reset_log_page_and_reload(self) -> None:
        self._log_page_index = 0
        self._reload_operation_logs()

    def _sync_log_source_selector(self) -> None:
        current = self.log_source_selector.currentText() or "current only"
        options = ["current only", "all (current + archives)"]
        if hasattr(self._operation_logger, "list_archives"):
            for archive in self._operation_logger.list_archives():
                options.append(f"archive:{archive}")
        self.log_source_selector.blockSignals(True)
        self.log_source_selector.clear()
        self.log_source_selector.addItems(options)
        if current in options:
            self.log_source_selector.setCurrentText(current)
        self.log_source_selector.blockSignals(False)

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

    def _sort_log_events(self, events: list[object]) -> list[object]:
        reverse = self.log_sort_order.currentText() != "古い順"
        return sorted(
            events,
            key=lambda item: str(getattr(item, "timestamp", "")),
            reverse=reverse,
        )

    def _filter_log_events(self, events: list[object]) -> tuple[list[object], str | None]:
        status_filter = self.log_status_filter.currentText()
        action_filter = self.log_action_filter.currentText()
        query = self.log_message_search_input.text().strip()
        regex_error: str | None = None
        pattern: re.Pattern[str] | None = None
        regex_flags = 0
        if self.log_regex_ignore_case_checkbox.isChecked():
            regex_flags |= re.IGNORECASE
        if self.log_regex_multiline_checkbox.isChecked():
            regex_flags |= re.MULTILINE
        if self.log_regex_dotall_checkbox.isChecked():
            regex_flags |= re.DOTALL
        if query and self.log_regex_checkbox.isChecked():
            try:
                pattern = re.compile(query, regex_flags)
            except re.error as exc:
                regex_error = str(exc)

        filtered: list[object] = []
        for event in events:
            timestamp = str(getattr(event, "timestamp", ""))
            status = str(getattr(event, "status", ""))
            action = str(getattr(event, "action", ""))
            role = str(getattr(event, "role", ""))
            message = str(getattr(event, "message", ""))
            path = str(getattr(event, "path", "") or "")
            path2 = str(getattr(event, "path2", "") or "")

            if status_filter != "all" and status != status_filter:
                continue
            if action_filter != "all" and action != action_filter:
                continue

            haystack = " ".join([timestamp, message, action, status, role, path, path2])
            if query:
                if pattern is not None:
                    if not pattern.search(haystack):
                        continue
                elif self.log_regex_checkbox.isChecked() and regex_error is not None:
                    pass
                elif query.lower() not in haystack.lower():
                    continue
            filtered.append(event)
        return filtered, regex_error

    def _request_cancel(self) -> None:
        if not self._is_busy:
            return
        self._cancel_requested = True
        self._operation_executor.request_cancel()
        message = "Cancel requested（実行中処理の停止要求を受け付けました）"
        self._set_message(message)
        self._record_operation(
            self._current_action or "unknown",
            "cancel",
            message,
        )

    def _start_async_operation(
        self,
        action: str,
        action_label: str,
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
        self._apply_busy_state()
        self._show_progress(action_label)

        def _success(result: object) -> None:
            on_success(result)

        def _error(exc: Exception) -> None:
            on_error(exc)

        def _finished() -> None:
            self._is_busy = False
            self._current_action = None
            self._hide_progress()
            self._apply_busy_state()

        self._operation_executor.submit(work, _success, _error, _finished)

    def _require_text(self, line_edit: QLineEdit, label: str) -> str | None:
        text = line_edit.text().strip()
        if not text:
            self._set_message(f"{label} は必須です", is_error=True)
            return None
        return text

    def _run_export_csv(self) -> None:
        path = self._require_text(self.csv_export_path_input, "CSV出力先ディレクトリ")
        if path is None:
            return

        def _work() -> object:
            result = self._export_backup_service.export_csv(Path(path), role=self._role)
            return len(result)

        def _on_success(result: object) -> None:
            self._push_recent_path("csv_export_dir", path)
            if self._cancel_requested:
                message = "CSV export 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation("export_csv", "cancel", message, path=path)
                return
            message = f"CSV export 成功: {result} tables"
            self._set_message(message)
            self._record_operation("export_csv", "success", message, path=path)

        def _on_error(exc: Exception) -> None:
            message = f"CSV export 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_csv", "error", message, path=path)

        self._start_async_operation("export_csv", "CSV export", _work, _on_success, _on_error)

    def _run_export_json(self) -> None:
        path = self._require_text(self.json_export_path_input, "JSON出力先ファイル")
        if path is None:
            return

        def _work() -> object:
            result = self._export_backup_service.export_json(Path(path), role=self._role)
            return result

        def _on_success(result: object) -> None:
            self._push_recent_path("json_export_file", path)
            if self._cancel_requested:
                message = "JSON export 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation("export_json", "cancel", message, path=path)
                return
            message = f"JSON export 成功: {result}"
            self._set_message(message)
            self._record_operation("export_json", "success", message, path=path)

        def _on_error(exc: Exception) -> None:
            message = f"JSON export 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_json", "error", message, path=path)

        self._start_async_operation("export_json", "JSON export", _work, _on_success, _on_error)

    def _run_export_sql_dump(self) -> None:
        path = self._require_text(self.sql_dump_path_input, "SQL dump出力先ファイル")
        if path is None:
            return

        def _work() -> object:
            result = self._export_backup_service.export_sql_dump(Path(path), role=self._role)
            return result

        def _on_success(result: object) -> None:
            self._push_recent_path("sql_dump_file", path)
            if self._cancel_requested:
                message = "SQL dump export 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation("export_sql_dump", "cancel", message, path=path)
                return
            message = f"SQL dump export 成功: {result}"
            self._set_message(message)
            self._record_operation("export_sql_dump", "success", message, path=path)

        def _on_error(exc: Exception) -> None:
            message = f"SQL dump export 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("export_sql_dump", "error", message, path=path)

        self._start_async_operation(
            "export_sql_dump",
            "SQL dump export",
            _work,
            _on_success,
            _on_error,
        )

    def _run_create_backup(self) -> None:
        db_path = self._require_text(self.db_path_input, "DBファイルパス")
        backup_path = self._require_text(self.backup_output_path_input, "バックアップ出力先")
        if db_path is None or backup_path is None:
            return

        def _work() -> object:
            result = self._export_backup_service.create_backup(
                Path(db_path), Path(backup_path), role=self._role
            )
            return result

        def _on_success(result: object) -> None:
            self._push_recent_path("db_file", db_path)
            self._push_recent_path("backup_output_file", backup_path)
            if self._cancel_requested:
                message = "Backup create 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation(
                    "create_backup",
                    "cancel",
                    message,
                    path=db_path,
                    path2=backup_path,
                )
                return
            message = f"Backup create 成功: {result}"
            self._set_message(message)
            self._record_operation(
                "create_backup",
                "success",
                message,
                path=db_path,
                path2=backup_path,
            )

        def _on_error(exc: Exception) -> None:
            message = f"Backup create 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation(
                "create_backup",
                "error",
                message,
                path=db_path,
                path2=backup_path,
            )

        self._start_async_operation(
            "create_backup",
            "Backup create",
            _work,
            _on_success,
            _on_error,
        )

    def _run_restore(self) -> None:
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
            result = self._backup_restore_service.restore_database(
                Path(backup_path), Path(target_path), role=self._role
            )
            return result

        def _on_success(result: object) -> None:
            self._push_recent_path("restore_backup_file", backup_path)
            self._push_recent_path("restore_target_file", target_path)
            if self._cancel_requested:
                message = "Restore 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation(
                    "restore",
                    "cancel",
                    message,
                    path=backup_path,
                    path2=target_path,
                )
                return
            message = f"Restore 成功: {result}"
            self._set_message(message)
            self._record_operation(
                "restore",
                "success",
                message,
                path=backup_path,
                path2=target_path,
            )

        def _on_error(exc: Exception) -> None:
            message = f"Restore 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation(
                "restore",
                "error",
                message,
                path=backup_path,
                path2=target_path,
            )

        self._start_async_operation("restore", "復元", _work, _on_success, _on_error)

    def _run_import_csv(self) -> None:
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
            result = self._import_service.import_csv(Path(csv_dir), role=self._role)
            return result

        def _on_success(result: object) -> None:
            self._push_recent_path("import_csv_dir", csv_dir)
            if self._cancel_requested:
                message = "CSV import 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation("import_csv", "cancel", message, path=csv_dir)
                return
            message = f"CSV import 成功: {result}"
            self._set_message(message)
            self._record_operation("import_csv", "success", message, path=csv_dir)

        def _on_error(exc: Exception) -> None:
            message = f"CSV import 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("import_csv", "error", message, path=csv_dir)

        self._start_async_operation("import_csv", "CSV import", _work, _on_success, _on_error)

    def _run_import_json(self) -> None:
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
            result = self._import_service.import_json(Path(json_path), role=self._role)
            return result

        def _on_success(result: object) -> None:
            self._push_recent_path("import_json_file", json_path)
            if self._cancel_requested:
                message = "JSON import 完了（cancel requested 後に完了）"
                self._set_message(message)
                self._record_operation("import_json", "cancel", message, path=json_path)
                return
            message = f"JSON import 成功: {result}"
            self._set_message(message)
            self._record_operation("import_json", "success", message, path=json_path)

        def _on_error(exc: Exception) -> None:
            message = f"JSON import 失敗: {exc}"
            self._set_message(message, is_error=True)
            self._record_operation("import_json", "error", message, path=json_path)

        self._start_async_operation("import_json", "JSON import", _work, _on_success, _on_error)

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

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        prefix = "ERROR" if is_error else "OK"
        self.result_view.append(f"[{prefix}] {message}")
