"""Operations tab for export/import/backup/restore entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PySide6.QtWidgets import (
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
from app.ui.role_context import RoleContext, UserRole


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


class OperationsTab(QWidget):
    """Minimal operations UI for file-based operational workflows."""

    def __init__(
        self,
        export_backup_service: ExportBackupLike,
        backup_restore_service: BackupRestoreLike,
        import_service: ImportLike,
        role_context: RoleContext | None = None,
    ) -> None:
        super().__init__()
        self._export_backup_service = export_backup_service
        self._backup_restore_service = backup_restore_service
        self._import_service = import_service
        self._role = (role_context or RoleContext.admin()).role

        root = QVBoxLayout(self)
        root.addWidget(QLabel("運用系操作（export/import/backup/restore）"))

        self.csv_export_path_input = QLineEdit()
        self.csv_export_browse_button = QPushButton("Browse")
        self.csv_export_browse_button.clicked.connect(
            lambda: self._select_directory(
                self.csv_export_path_input,
                "CSV出力先ディレクトリを選択",
            )
        )

        self.json_export_path_input = QLineEdit()
        self.json_export_browse_button = QPushButton("Browse")
        self.json_export_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.json_export_path_input,
                "JSON出力先ファイルを選択",
                "JSON Files (*.json);;All Files (*)",
            )
        )

        self.sql_dump_path_input = QLineEdit()
        self.sql_dump_browse_button = QPushButton("Browse")
        self.sql_dump_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.sql_dump_path_input,
                "SQL dump出力先ファイルを選択",
                "SQL Files (*.sql);;All Files (*)",
            )
        )

        self.db_path_input = QLineEdit()
        self.db_path_browse_button = QPushButton("Browse")
        self.db_path_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.db_path_input,
                "DBファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
            )
        )

        self.backup_output_path_input = QLineEdit()
        self.backup_output_browse_button = QPushButton("Browse")
        self.backup_output_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.backup_output_path_input,
                "バックアップ出力先ファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
            )
        )

        self.restore_backup_path_input = QLineEdit()
        self.restore_backup_browse_button = QPushButton("Browse")
        self.restore_backup_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.restore_backup_path_input,
                "restore用バックアップファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
            )
        )

        self.restore_target_db_path_input = QLineEdit()
        self.restore_target_browse_button = QPushButton("Browse")
        self.restore_target_browse_button.clicked.connect(
            lambda: self._select_save_file(
                self.restore_target_db_path_input,
                "restore先DBファイルを選択",
                "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)",
            )
        )

        self.import_csv_dir_input = QLineEdit()
        self.import_csv_dir_browse_button = QPushButton("Browse")
        self.import_csv_dir_browse_button.clicked.connect(
            lambda: self._select_directory(
                self.import_csv_dir_input,
                "CSV importディレクトリを選択",
            )
        )

        self.import_json_path_input = QLineEdit()
        self.import_json_browse_button = QPushButton("Browse")
        self.import_json_browse_button.clicked.connect(
            lambda: self._select_open_file(
                self.import_json_path_input,
                "JSON importファイルを選択",
                "JSON Files (*.json);;All Files (*)",
            )
        )

        self.export_csv_button = QPushButton("CSV Export")
        self.export_json_button = QPushButton("JSON Export")
        self.export_sql_dump_button = QPushButton("SQL Dump Export")
        self.create_backup_button = QPushButton("Backup Create")
        self.restore_button = QPushButton("Restore")
        self.import_csv_button = QPushButton("CSV Import")
        self.import_json_button = QPushButton("JSON Import")

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
                    ),
                    (
                        "JSON出力先ファイル",
                        self.json_export_path_input,
                        self.json_export_browse_button,
                    ),
                    (
                        "SQL dump出力先ファイル",
                        self.sql_dump_path_input,
                        self.sql_dump_browse_button,
                    ),
                ],
                [self.export_csv_button, self.export_json_button, self.export_sql_dump_button],
            )
        )

        root.addWidget(
            self._build_group(
                "Backup",
                [
                    ("DBファイルパス", self.db_path_input, self.db_path_browse_button),
                    (
                        "バックアップ出力先",
                        self.backup_output_path_input,
                        self.backup_output_browse_button,
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
                    ),
                    (
                        "復元先DBファイル",
                        self.restore_target_db_path_input,
                        self.restore_target_browse_button,
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
                    ),
                    (
                        "JSONファイル",
                        self.import_json_path_input,
                        self.import_json_browse_button,
                    ),
                ],
                [self.import_csv_button, self.import_json_button],
            )
        )

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        root.addWidget(self.result_view)

        self._apply_role_guards()

    def _build_group(
        self,
        title: str,
        fields: list[tuple[str, QLineEdit, QPushButton]],
        buttons: list[QPushButton],
    ) -> QGroupBox:
        group = QGroupBox(title)
        box = QVBoxLayout(group)
        form = QFormLayout()
        for label, path_input, browse_button in fields:
            row = QHBoxLayout()
            row.addWidget(path_input)
            row.addWidget(browse_button)
            form.addRow(label, row)
        box.addLayout(form)

        actions = QHBoxLayout()
        for button in buttons:
            actions.addWidget(button)
        actions.addStretch(1)
        box.addLayout(actions)
        return group

    def _select_directory(self, target: QLineEdit, title: str) -> None:
        chosen = QFileDialog.getExistingDirectory(self, title, target.text().strip())
        if chosen:
            target.setText(chosen)

    def _select_open_file(self, target: QLineEdit, title: str, filter_spec: str) -> None:
        chosen, _ = QFileDialog.getOpenFileName(
            self,
            title,
            target.text().strip(),
            filter_spec,
        )
        if chosen:
            target.setText(chosen)

    def _select_save_file(self, target: QLineEdit, title: str, filter_spec: str) -> None:
        chosen, _ = QFileDialog.getSaveFileName(
            self,
            title,
            target.text().strip(),
            filter_spec,
        )
        if chosen:
            target.setText(chosen)

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
        try:
            result = self._export_backup_service.export_csv(Path(path), role=self._role)
            self._set_message(f"CSV export 成功: {len(result)} tables")
        except Exception as exc:
            self._set_message(f"CSV export 失敗: {exc}", is_error=True)

    def _run_export_json(self) -> None:
        path = self._require_text(self.json_export_path_input, "JSON出力先ファイル")
        if path is None:
            return
        try:
            result = self._export_backup_service.export_json(Path(path), role=self._role)
            self._set_message(f"JSON export 成功: {result}")
        except Exception as exc:
            self._set_message(f"JSON export 失敗: {exc}", is_error=True)

    def _run_export_sql_dump(self) -> None:
        path = self._require_text(self.sql_dump_path_input, "SQL dump出力先ファイル")
        if path is None:
            return
        try:
            result = self._export_backup_service.export_sql_dump(Path(path), role=self._role)
            self._set_message(f"SQL dump export 成功: {result}")
        except Exception as exc:
            self._set_message(f"SQL dump export 失敗: {exc}", is_error=True)

    def _run_create_backup(self) -> None:
        db_path = self._require_text(self.db_path_input, "DBファイルパス")
        backup_path = self._require_text(self.backup_output_path_input, "バックアップ出力先")
        if db_path is None or backup_path is None:
            return
        try:
            result = self._export_backup_service.create_backup(
                Path(db_path), Path(backup_path), role=self._role
            )
            self._set_message(f"Backup create 成功: {result}")
        except Exception as exc:
            self._set_message(f"Backup create 失敗: {exc}", is_error=True)

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
            self._set_message("Restore はキャンセルされました")
            return

        try:
            result = self._backup_restore_service.restore_database(
                Path(backup_path), Path(target_path), role=self._role
            )
            self._set_message(f"Restore 成功: {result}")
        except Exception as exc:
            self._set_message(f"Restore 失敗: {exc}", is_error=True)

    def _run_import_csv(self) -> None:
        csv_dir = self._require_text(self.import_csv_dir_input, "CSVディレクトリ")
        if csv_dir is None:
            return

        if not confirm_destructive_action(
            self,
            "CSV Import確認",
            "CSV import を実行します。空DBへの初期取込のみ想定です。続行しますか？",
        ):
            self._set_message("CSV Import はキャンセルされました")
            return

        try:
            result = self._import_service.import_csv(Path(csv_dir), role=self._role)
            self._set_message(f"CSV import 成功: {result}")
        except Exception as exc:
            self._set_message(f"CSV import 失敗: {exc}", is_error=True)

    def _run_import_json(self) -> None:
        json_path = self._require_text(self.import_json_path_input, "JSONファイル")
        if json_path is None:
            return

        if not confirm_destructive_action(
            self,
            "JSON Import確認",
            "JSON import を実行します。空DBへの初期取込のみ想定です。続行しますか？",
        ):
            self._set_message("JSON Import はキャンセルされました")
            return

        try:
            result = self._import_service.import_json(Path(json_path), role=self._role)
            self._set_message(f"JSON import 成功: {result}")
        except Exception as exc:
            self._set_message(f"JSON import 失敗: {exc}", is_error=True)

    def _set_message(self, message: str, *, is_error: bool = False) -> None:
        prefix = "ERROR" if is_error else "OK"
        self.result_view.append(f"[{prefix}] {message}")
