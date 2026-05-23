"""Main window for NameVerification v3."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QWidget,
)

from app.application.backup_restore_services import BackupRestoreService
from app.application.core_services import CoreService
from app.application.export_backup_services import ExportBackupService
from app.application.import_services import ImportService
from app.application.query_services import QueryService
from app.application.runtime_paths import resolve_package_root_from_database_path
from app.application.user_audit_services import UserAuditLogService
from app.application.user_services import UserService
from app.ui.audit_logs_tab import AuditLogsTab
from app.ui.context_helpers import apply_operator_context
from app.ui.crud_list_first import apply_crud_list_first
from app.ui.help_settings_tab import HelpSettingsTab
from app.ui.link_management_tab import LinkManagementTab
from app.ui.name_management_tab import NameManagementTab
from app.ui.operations_log import OperationsJsonlLogger
from app.ui.operations_tab import OperationLoggerLike, OperationsTab
from app.ui.operations_tab_navigation import apply_operations_subtabs
from app.ui.rbac_ui_guards import (
    apply_operations_tab_role_guards,
    apply_tab_action_visibility_guards,
)
from app.ui.restore_current_db_guard import apply_restore_current_db_guard
from app.ui.role_context import RoleContext
from app.ui.sanitized_export_ui import apply_sanitized_export_ui
from app.ui.search_tab import SearchTab
from app.ui.sql_dump_protection_warning import apply_sql_dump_protection_warning
from app.ui.tab_guides import apply_tab_guide
from app.ui.title_subtitle_unified_tab import TitleSubtitleUnifiedTab
from app.ui.trash_tab import TrashTab
from app.ui.ui_style import apply_friendly_theme, apply_searchable_comboboxes
from app.ui.user_management_tab import UserManagementTab


def _operations_fallback_base_dir() -> Path:
    return Path.home() / "tmp" / "NameVerification v3"


def _timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _looks_like_operations_package_root(package_root: Path) -> bool:
    return (
        (package_root / "10_app").is_dir()
        or (package_root / "30_prod_db").is_dir()
        or (package_root / "60_exports").is_dir()
    )


class MainWindow(QMainWindow):
    """Top-level main window with user-facing tab layout."""

    account_switch_requested = Signal()

    def __init__(
        self,
        query_service: QueryService,
        core_service: CoreService,
        role_context: RoleContext | None = None,
        export_backup_service: ExportBackupService | None = None,
        backup_restore_service: BackupRestoreService | None = None,
        import_service: ImportService | None = None,
        user_service: UserService | None = None,
        user_audit_service: UserAuditLogService | None = None,
        package_root: Path | None = None,
        database_path: Path | None = None,
        change_log_jsonl_path: Path | None = None,
        operations_log_jsonl_path: Path | None = None,
        operation_logger: OperationLoggerLike | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        super().__init__()
        self._connection = connection
        self._package_root = package_root
        self._database_path = database_path
        self._change_log_jsonl_path = change_log_jsonl_path
        self._operations_log_jsonl_path = operations_log_jsonl_path
        self._operation_logger = operation_logger
        self._role_context = role_context or RoleContext.admin()
        self._login_context_text = self._format_login_context()
        self.setWindowTitle(f"NameVerification v3 - {self._login_context_text}")
        self.resize(1180, 760)
        apply_friendly_theme(self)
        self._setup_login_status_bar()
        self._setup_account_switch_controls()

        self.tabs = QTabWidget(self)
        self._tabs_by_name: dict[str, QWidget] = {}
        self._add_tab(
            SearchTab(query_service=query_service, role_context=self._role_context),
            "検索",
        )
        self._add_tab(
            NameManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=self._role_context,
            ),
            "名前を管理",
        )
        self._add_tab(
            TitleSubtitleUnifiedTab(
                core_service=core_service,
                query_service=query_service,
                role_context=self._role_context,
            ),
            "タイトル/サブタイトル管理",
        )
        self._add_tab(
            LinkManagementTab(
                core_service=core_service,
                query_service=query_service,
                role_context=self._role_context,
            ),
            "関連付け",
        )
        self._add_tab(
            TrashTab(
                core_service=core_service,
                query_service=query_service,
                role_context=self._role_context,
            ),
            "削除データ",
        )
        if user_service is not None and self._role_context.role == "admin":
            self._add_tab(
                UserManagementTab(
                    user_service=user_service,
                    role_context=self._role_context,
                ),
                "ユーザー管理",
            )
        self._add_tab(
            AuditLogsTab(
                query_service=query_service,
                role_context=self._role_context,
                user_audit_service=user_audit_service,
            ),
            "監査ログ",
        )
        if (
            export_backup_service is not None
            and backup_restore_service is not None
            and import_service is not None
        ):
            operation_logger = self._operation_logger
            if operation_logger is None and operations_log_jsonl_path is not None:
                operation_logger = OperationsJsonlLogger(log_path=operations_log_jsonl_path)
            operations_tab = OperationsTab(
                export_backup_service=export_backup_service,
                backup_restore_service=backup_restore_service,
                import_service=import_service,
                role_context=self._role_context,
                operation_logger=operation_logger,
            )
            apply_restore_current_db_guard(operations_tab, self._database_path)
            apply_sql_dump_protection_warning(operations_tab)
            apply_sanitized_export_ui(operations_tab)
            self._prefill_operations_paths(operations_tab)
            apply_operations_subtabs(operations_tab)
            apply_operations_tab_role_guards(operations_tab, self._role_context)
            self._add_tab(operations_tab, "データ入出力")
        self._add_tab(
            HelpSettingsTab(
                package_root=self._package_root,
                database_path=database_path,
                change_log_jsonl_path=self._change_log_jsonl_path,
                operations_log_jsonl_path=self._operations_log_jsonl_path,
            ),
            "ヘルプ / 設定",
        )
        self.tabs.currentChanged.connect(self._refresh_current_tab)
        self.setCentralWidget(self.tabs)
        apply_searchable_comboboxes(self)

    @property
    def role_context(self) -> RoleContext:
        """Return the current login context used to build this window."""

        return self._role_context

    def _format_login_context(self) -> str:
        return (
            f"ログイン中: {self._role_context.operator_id}"
            f" / 権限: {self._role_context.role}"
        )

    def _setup_login_status_bar(self) -> None:
        self.login_status_label = QLabel(self._login_context_text)
        self.login_status_label.setObjectName("loginStatusLabel")
        self.login_status_label.setToolTip(
            "現在ログイン中の操作者IDと権限です。権限により利用可能な操作が変わります。"
        )
        self.login_status_label.setStyleSheet(
            "QLabel#loginStatusLabel {"
            "padding: 2px 8px;"
            "font-weight: 600;"
            "color: #dbeafe;"
            "background-color: #1e3a8a;"
            "border: 1px solid #60a5fa;"
            "border-radius: 4px;"
            "}"
        )
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("Ready")
        self.statusBar().addPermanentWidget(self.login_status_label, 0)

    def _setup_account_switch_controls(self) -> None:
        account_menu = self.menuBar().addMenu("アカウント")
        self.account_switch_action = QAction("アカウント切替", self)
        self.account_switch_action.setToolTip(
            "現在の画面を閉じ、ログイン画面に戻って別ユーザーでログインします。"
        )
        self.account_switch_action.triggered.connect(
            lambda _checked=False: self._confirm_account_switch()
        )
        account_menu.addAction(self.account_switch_action)

        self.account_switch_button = QPushButton("アカウント切替")
        self.account_switch_button.setObjectName("accountSwitchButton")
        self.account_switch_button.setToolTip(
            "現在の画面を閉じ、ログイン画面に戻って別ユーザーでログインします。"
        )
        self.account_switch_button.setStyleSheet(
            "QPushButton#accountSwitchButton {"
            "padding: 2px 8px;"
            "font-weight: 600;"
            "}"
        )
        self.account_switch_button.clicked.connect(
            lambda _checked=False: self._confirm_account_switch()
        )
        self.statusBar().addPermanentWidget(self.account_switch_button, 0)

    def _confirm_account_switch(self) -> None:
        result = QMessageBox.question(
            self,
            "アカウント切替",
            "現在の画面を閉じてログイン画面に戻ります。\n"
            "別ユーザーでログインし直しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        self.account_switch_requested.emit()

    def _add_tab(self, widget: QWidget, title: str) -> None:
        apply_operator_context(widget, self._role_context)
        apply_tab_guide(widget, title)
        apply_crud_list_first(widget, title)
        apply_tab_action_visibility_guards(widget, self._role_context)
        self.tabs.addTab(widget, title)
        self._tabs_by_name[title] = widget
        for alias in _tab_aliases(title):
            self._tabs_by_name[alias] = widget

    def _prefill_operations_paths(self, operations_tab: OperationsTab) -> None:
        timestamp = _timestamp_suffix()
        package_root = self._resolve_operations_package_root()
        if package_root is not None:
            defaults = self._portable_operations_defaults(
                package_root.resolve(strict=False),
                timestamp,
            )
        else:
            defaults = self._fallback_operations_defaults(timestamp)
        operations_tab.apply_default_paths(defaults, replace_history_prefills=True)

    def _resolve_operations_package_root(self) -> Path | None:
        if self._package_root is not None:
            return self._package_root
        if self._database_path is None:
            return None
        portable_root = resolve_package_root_from_database_path(self._database_path)
        if portable_root is not None:
            return portable_root
        return self._database_path.expanduser().resolve(strict=False).parent

    def _portable_operations_defaults(
        self,
        package_root: Path,
        timestamp: str,
    ) -> dict[str, Path | str]:
        csv_dir = package_root / "60_exports" / "csv"
        json_dir = package_root / "60_exports" / "json"
        sql_dir = package_root / "60_exports" / "sql"
        backup_dir = package_root / "50_backups" / "daily"
        for directory in (csv_dir, json_dir, sql_dir, backup_dir):
            directory.mkdir(parents=True, exist_ok=True)

        database_path = self._database_path or (
            package_root / "30_prod_db" / "nameverification.db"
        )
        if database_path.is_absolute():
            database_path = database_path.resolve(strict=False)
        else:
            database_path = (package_root / database_path).resolve(strict=False)
        json_export_file = json_dir / f"nameverification_export_{timestamp}.json"
        backup_output_file = backup_dir / f"nameverification_{timestamp}.db"
        defaults: dict[str, Path | str] = {
            "csv_export_dir": csv_dir,
            "json_export_file": json_export_file,
            "sql_dump_file": sql_dir / f"nameverification_dump_{timestamp}.sql",
            "db_file": database_path,
            "backup_output_file": backup_output_file,
            "restore_backup_file": backup_output_file,
            "restore_target_file": database_path,
            "import_csv_dir": csv_dir,
            "import_json_file": json_export_file,
        }
        return defaults

    def _relative_operations_defaults(
        self,
        timestamp: str,
        *,
        package_root: Path | None = None,
    ) -> dict[str, Path | str]:
        csv_dir = Path("60_exports") / "csv"
        json_dir = Path("60_exports") / "json"
        sql_dir = Path("60_exports") / "sql"
        backup_dir = Path("50_backups") / "daily"
        database_path = self._operation_relative_path(
            self._database_path or Path("nameverification.db"),
            package_root=package_root,
        )
        json_export_file = json_dir / f"nameverification_export_{timestamp}.json"
        backup_output_file = backup_dir / f"nameverification_{timestamp}.db"
        return {
            "csv_export_dir": csv_dir,
            "json_export_file": json_export_file,
            "sql_dump_file": sql_dir / f"nameverification_dump_{timestamp}.sql",
            "db_file": database_path,
            "backup_output_file": backup_output_file,
            "restore_backup_file": backup_output_file,
            "restore_target_file": database_path,
            "import_csv_dir": csv_dir,
            "import_json_file": json_export_file,
        }

    def _operation_relative_path(
        self,
        path: Path,
        *,
        package_root: Path | None = None,
    ) -> Path:
        root = package_root or self._package_root
        if root is None:
            return path
        try:
            return path.resolve(strict=False).relative_to(root.resolve(strict=False))
        except ValueError:
            return path

    def _fallback_operations_defaults(self, timestamp: str) -> dict[str, Path | str]:
        base_dir = _operations_fallback_base_dir()
        base_dir.mkdir(parents=True, exist_ok=True)
        csv_dir = base_dir / "60_exports" / "csv"
        json_dir = base_dir / "60_exports" / "json"
        sql_dir = base_dir / "60_exports" / "sql"
        backup_dir = base_dir / "50_backups" / "daily"
        for directory in (csv_dir, json_dir, sql_dir, backup_dir):
            directory.mkdir(parents=True, exist_ok=True)
        json_export_file = json_dir / f"nameverification_export_{timestamp}.json"
        backup_output_file = backup_dir / f"nameverification_{timestamp}.db"
        defaults: dict[str, Path | str] = {
            "csv_export_dir": csv_dir,
            "json_export_file": json_export_file,
            "sql_dump_file": sql_dir / f"nameverification_dump_{timestamp}.sql",
            "backup_output_file": backup_output_file,
            "restore_backup_file": backup_output_file,
            "restore_target_file": base_dir / "restore_target_nameverification.db",
            "import_csv_dir": csv_dir,
            "import_json_file": json_export_file,
        }
        if self._database_path is not None:
            defaults["db_file"] = self._database_path
        return defaults

    def _refresh_current_tab(self) -> None:
        widget = self.tabs.currentWidget()
        if widget is None:
            return
        for method_name in (
            "refresh",
            "_refresh_all",
            "_refresh_list",
            "_on_search_clicked",
            "_reload",
        ):
            method = getattr(widget, method_name, None)
            if callable(method):
                method()
                self._reapply_tab_role_guards(widget)
                return
        editor = getattr(widget, "editor", None)
        if editor is not None:
            method = getattr(editor, "_refresh_titles", None)
            if callable(method):
                method()
        self._reapply_tab_role_guards(widget)

    def _reapply_tab_role_guards(self, widget: QWidget) -> None:
        apply_tab_action_visibility_guards(widget, self._role_context)
        if isinstance(widget, OperationsTab):
            apply_operations_tab_role_guards(widget, self._role_context)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._connection is not None:
            self._connection.commit()
        super().closeEvent(event)


def _tab_aliases(title: str) -> tuple[str, ...]:
    if title == "タイトル/サブタイトル管理":
        return ("タイトルを管理", "サブタイトルを管理")
    if title == "監査ログ":
        return ("操作履歴", "ユーザー監査ログ")
    return ()
