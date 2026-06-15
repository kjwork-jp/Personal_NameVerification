"""Help and settings tab for desktop/EXE usage."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.datetime_display import format_datetime_display
from app.ui.input_defaults import default_operator_id
from app.ui.operations_log import default_operations_log_path
from app.ui.ui_style import PageHeader, set_status_message


class HelpSettingsTab(QWidget):
    """Read-only guidance for local desktop operation."""

    def __init__(
        self,
        package_root: Path | None = None,
        database_path: Path | None = None,
        change_log_jsonl_path: Path | None = None,
        operations_log_jsonl_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.package_root = package_root
        self.database_path = database_path or Path("nameverification.db")
        self.change_log_jsonl_path = change_log_jsonl_path or Path(
            os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH", "logs/change_logs.jsonl")
        )
        self.operations_log_jsonl_path = operations_log_jsonl_path

        self.package_root_input = QLineEdit(self._package_root_text())
        self.package_root_input.setReadOnly(True)
        self.package_root_input.setToolTip("portable配布フォルダ、またはsource実行時の基準フォルダです。")

        self.database_path_input = QLineEdit(self._path_text(self.database_path))
        self.database_path_input.setReadOnly(True)
        self.database_path_input.setToolTip(
            "現在このアプリが参照しているSQLite DBファイルです。"
        )

        self.change_log_path_input = QLineEdit(self._path_text(self.change_log_jsonl_path))
        self.change_log_path_input.setReadOnly(True)
        self.change_log_path_input.setToolTip(
            "DB内 change_logs を補助的にJSONLへ出力するファイルです。正本はDBです。"
        )

        self.operations_log_path_input = QLineEdit(
            self._path_text(self._operations_log_path_for_display())
        )
        self.operations_log_path_input.setReadOnly(True)
        self.operations_log_path_input.setToolTip(
            "データ入出力タブのExport/Import/Backup/Restore実行結果を記録するJSONLログです。"
        )

        self.database_exists_input = QLineEdit()
        self.database_exists_input.setReadOnly(True)
        self.database_size_input = QLineEdit()
        self.database_size_input.setReadOnly(True)
        self.database_updated_input = QLineEdit()
        self.database_updated_input.setReadOnly(True)
        self._refresh_database_metadata()

        self.database_env_input = QLineEdit(
            os.environ.get("NAMEVERIFICATION_DB_PATH", "未設定") or "未設定"
        )
        self.database_env_input.setReadOnly(True)
        self.database_env_input.setToolTip(
            "DB保存先を固定したい場合は、起動前に NAMEVERIFICATION_DB_PATH を設定します。"
        )

        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setReadOnly(True)

        self.operator_env_input = QLineEdit(
            os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "未設定") or "未設定"
        )
        self.operator_env_input.setReadOnly(True)

        self.backup_hint_input = QLineEdit(self._backup_hint_text())
        self.backup_hint_input.setReadOnly(True)

        self.copy_db_path_button = QPushButton("DB保存先をコピー")
        self.copy_db_path_button.clicked.connect(self._copy_database_path)
        self.copy_env_command_button = QPushButton("DB環境変数コマンドをコピー")
        self.copy_env_command_button.clicked.connect(self._copy_database_env_command)
        self.copy_change_log_command_button = QPushButton("DB変更ログ環境変数コマンドをコピー")
        self.copy_change_log_command_button.clicked.connect(self._copy_change_log_env_command)
        self.copy_operations_log_command_button = QPushButton(
            "Operationsログ環境変数コマンドをコピー"
        )
        self.copy_operations_log_command_button.clicked.connect(
            self._copy_operations_log_env_command
        )
        self.refresh_button = QPushButton("表示を更新")
        self.refresh_button.clicked.connect(self._refresh_values)

        self.message_label = QLabel("")

        self.path_diagnostics_text = QTextEdit()
        self.path_diagnostics_text.setReadOnly(True)
        self.security_warning_text = QTextEdit()
        self.security_warning_text.setReadOnly(True)
        self.protection_diagnostics_text = QTextEdit()
        self.protection_diagnostics_text.setReadOnly(True)
        self.operator_protection_checklist_text = QTextEdit()
        self.operator_protection_checklist_text.setReadOnly(True)
        self.audit_safety_text = QTextEdit()
        self.audit_safety_text.setReadOnly(True)
        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.guide_text.setPlainText(_guide_text())

        self.sections = QTabWidget()
        self.sections.setObjectName("helpSettingsSubTabs")
        self.sections.addTab(self._build_basic_info_page(), "基本情報")
        self.sections.addTab(self._build_path_diagnostics_page(), "パス診断")
        self.sections.addTab(self._build_security_warning_page(), "保護警告")
        self.sections.addTab(self._build_operation_memo_page(), "操作メモ")

        layout = QVBoxLayout(self)
        layout.addWidget(
            PageHeader(
                "ヘルプ / 設定",
                "EXE配布や通常運用を前提に、保存先・操作者・基本操作を確認します。",
            )
        )
        layout.addWidget(self.sections, 1)
        layout.addWidget(self.message_label)
        self._refresh_diagnostics_texts()

    def _build_basic_info_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        form.addRow("package root", self.package_root_input)
        form.addRow("DB保存先", self.database_path_input)
        form.addRow("DBファイル存在", self.database_exists_input)
        form.addRow("DBファイルサイズ", self.database_size_input)
        form.addRow("DB更新日時", self.database_updated_input)
        form.addRow("DB変更JSONLログ出力先", self.change_log_path_input)
        form.addRow("Operations実行JSONLログ出力先", self.operations_log_path_input)
        form.addRow("現在の操作者", self.operator_input)
        form.addRow("バックアップ既定先", self.backup_hint_input)
        return page

    def _build_path_diagnostics_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()
        form.addRow("DB保存先の環境変数", self.database_env_input)
        form.addRow("操作者の環境変数", self.operator_env_input)
        layout.addLayout(form)
        layout.addWidget(self.copy_db_path_button)
        layout.addWidget(self.copy_env_command_button)
        layout.addWidget(self.copy_change_log_command_button)
        layout.addWidget(self.copy_operations_log_command_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(QLabel("診断結果"))
        layout.addWidget(self.path_diagnostics_text, 1)
        return page

    def _build_security_warning_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("DB / backup / export / log 保護警告"))
        layout.addWidget(self.security_warning_text, 1)
        layout.addWidget(QLabel("保護対象パス診断"))
        layout.addWidget(self.protection_diagnostics_text, 1)
        layout.addWidget(QLabel("operator file protection checklist"))
        layout.addWidget(self.operator_protection_checklist_text, 1)
        layout.addWidget(QLabel("passwordログ非記録確認"))
        layout.addWidget(self.audit_safety_text, 1)
        return page

    def _build_operation_memo_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("使い方の要点"))
        layout.addWidget(self.guide_text, 1)
        return page

    def _path_text(self, path: Path) -> str:
        return str(path.expanduser().resolve(strict=False))

    def _package_root_text(self) -> str:
        if self.package_root is None:
            return "未設定"
        return self._path_text(self.package_root)

    def _operations_log_path_for_display(self) -> Path:
        if self.operations_log_jsonl_path is not None:
            return self.operations_log_jsonl_path
        return default_operations_log_path()

    def _backup_hint_text(self) -> str:
        if self.package_root is None:
            return "データ入出力タブでバックアップ出力先を指定します"
        if (
            (self.package_root / "10_app").is_dir()
            or (self.package_root / "30_prod_db").is_dir()
            or (self.package_root / "50_backups").is_dir()
        ):
            return self._path_text(self.package_root / "50_backups" / "daily")
        return "データ入出力タブでバックアップ出力先を指定します"

    def _refresh_database_metadata(self) -> None:
        db_path = self.database_path.expanduser()
        try:
            exists = db_path.exists()
            if not exists:
                self.database_exists_input.setText("なし")
                self.database_size_input.setText("未作成")
                self.database_updated_input.setText("未作成")
                return
            stat = db_path.stat()
        except OSError as exc:
            self.database_exists_input.setText("確認エラー")
            self.database_size_input.setText(str(exc))
            self.database_updated_input.setText("確認エラー")
            return

        updated = format_datetime_display(
            datetime.fromtimestamp(stat.st_mtime), fallback="不明"
        )
        self.database_exists_input.setText("あり")
        self.database_size_input.setText(f"{stat.st_size:,} bytes")
        self.database_updated_input.setText(updated)

    def _refresh_values(self) -> None:
        self.package_root_input.setText(self._package_root_text())
        self.database_path_input.setText(self._path_text(self.database_path))
        self.change_log_path_input.setText(self._path_text(self.change_log_jsonl_path))
        self.operations_log_path_input.setText(
            self._path_text(self._operations_log_path_for_display())
        )
        self._refresh_database_metadata()
        self.database_env_input.setText(
            os.environ.get("NAMEVERIFICATION_DB_PATH", "未設定") or "未設定"
        )
        self.operator_input.setText(default_operator_id())
        self.operator_env_input.setText(
            os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "未設定") or "未設定"
        )
        self.backup_hint_input.setText(self._backup_hint_text())
        self._refresh_diagnostics_texts()
        self._set_message("表示を更新しました")

    def _refresh_diagnostics_texts(self) -> None:
        self.path_diagnostics_text.setPlainText(self._path_diagnostics_text())
        self.security_warning_text.setPlainText(self._security_warning_text())
        self.protection_diagnostics_text.setPlainText(self._protection_diagnostics_text())
        self.operator_protection_checklist_text.setPlainText(
            _operator_protection_checklist_text()
        )
        self.audit_safety_text.setPlainText(_audit_safety_text())

    def _copy_database_path(self) -> None:
        QGuiApplication.clipboard().setText(self._path_text(self.database_path))
        self._set_message("DB保存先をクリップボードへコピーしました")

    def _copy_database_env_command(self) -> None:
        command = f'$env:NAMEVERIFICATION_DB_PATH = "{self._path_text(self.database_path)}"'
        QGuiApplication.clipboard().setText(command)
        self._set_message("DB保存先のPowerShell環境変数コマンドをコピーしました")

    def _copy_change_log_env_command(self) -> None:
        command = (
            "$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "
            f'"{self._path_text(self.change_log_jsonl_path)}"'
        )
        QGuiApplication.clipboard().setText(command)
        self._set_message("DB変更JSONLログ出力先のPowerShell環境変数コマンドをコピーしました")

    def _copy_operations_log_env_command(self) -> None:
        command = (
            "$env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH = "
            f'"{self._path_text(self._operations_log_path_for_display())}"'
        )
        QGuiApplication.clipboard().setText(command)
        self._set_message("Operations実行JSONLログ出力先のPowerShell環境変数コマンドをコピーしました")

    def _set_message(self, message: str) -> None:
        set_status_message(self.message_label, message, level="success")

    def _path_diagnostics_text(self) -> str:
        paths = [
            ("DB", self.database_path),
            ("DB変更JSONLログ", self.change_log_jsonl_path),
            ("Operations実行JSONLログ", self._operations_log_path_for_display()),
        ]
        lines = ["保存先診断"]
        for label, path in paths:
            expanded = path.expanduser()
            parent = expanded.parent
            lines.extend(
                [
                    f"- {label}: {self._path_text(path)}",
                    f"  - exists: {expanded.exists()}",
                    f"  - parent exists: {parent.exists()}",
                    f"  - readable: {os.access(expanded, os.R_OK) if expanded.exists() else '未作成'}",
                    f"  - writable parent: {os.access(parent, os.W_OK) if parent.exists() else False}",
                ]
            )
        return "\n".join(lines)

    def _protection_diagnostics_text(self) -> str:
        lines = [
            "保護対象パス診断",
            "以下はDB/backup/export/logの配置候補です。",
            "parent writable=True はアプリが出力できることを示すだけで、閲覧制限済みとは限りません。",
            "共有・添付・外部保存前にOS ACL/BitLocker/EFS/共有権限を確認してください。",
            "Windows権限確認コマンド例:",
            "- PowerShell: Get-Acl \"<対象パス>\" | Format-List",
            "- Command Prompt: icacls \"<対象パス>\"",
            "- ACL確認では、Users / Authenticated Users / Everyone に不要な読取権限がないかを確認してください。",
            "- writable parent=True はACL hardening済みの証明ではありません。",
        ]
        for label, path, kind in self._protected_locations():
            expanded = path.expanduser()
            target = expanded if kind == "directory" else expanded.parent
            path_text = self._path_text(path)
            lines.extend(
                [
                    f"- {label}: {path_text}",
                    f"  - kind: {kind}",
                    f"  - exists: {expanded.exists()}",
                    f"  - parent exists: {target.exists()}",
                    f"  - parent writable: {os.access(target, os.W_OK) if target.exists() else False}",
                    f"  - PowerShell ACL: Get-Acl \"{path_text}\" | Format-List",
                    f"  - icacls: icacls \"{path_text}\"",
                ]
            )
        return "\n".join(lines)

    def _protected_locations(self) -> list[tuple[str, Path, str]]:
        locations = [
            ("DBファイル", self.database_path, "file"),
            ("DBフォルダ", self.database_path.parent, "directory"),
            ("DB変更JSONLログ", self.change_log_jsonl_path, "file"),
            ("Operations実行JSONLログ", self._operations_log_path_for_display(), "file"),
        ]
        if self.package_root is not None:
            locations.extend(
                [
                    ("backupフォルダ", self.package_root / "50_backups", "directory"),
                    ("daily backupフォルダ", self.package_root / "50_backups" / "daily", "directory"),
                    ("CSV exportフォルダ", self.package_root / "60_exports" / "csv", "directory"),
                    ("JSON exportフォルダ", self.package_root / "60_exports" / "json", "directory"),
                    ("SQL dumpフォルダ", self.package_root / "60_exports" / "sql", "directory"),
                ]
            )
        return locations

    def _security_warning_text(self) -> str:
        return "\n".join(
            [
                "重要: このアプリの認証/RBACはアプリ内操作を制御するものです。",
                "SQLite DB、backup、export、JSONL logファイルをOS上で読めるユーザーは、",
                "アプリを経由せずにファイルを直接閲覧・コピーできる可能性があります。",
                "",
                "exportの扱い:",
                "- SQL dumpはfull DB dumpです。認証・管理・設定系テーブルを含み得るため、",
                "  保護対象ファイルとして扱います。共有・添付・外部保存時はアクセス制御を確認してください。",
                "- 共有用JSON出力は業務データの許可リスト方式です。認証・管理・設定系テーブルは含めません。",
                "- 通常JSON/CSV exportも業務データ中心ですが、出力先フォルダのアクセス権は必ず確認してください。",
                "",
                "推奨運用:",
                "- 配布フォルダは利用者ごとに分離する。",
                "- Windowsのユーザープロファイル配下、またはACL制御されたフォルダへ配置する。",
                "- 機微情報を扱う場合はBitLocker/EFSなどのOS側保護を併用する。",
                "- backup/export/logを共有フォルダへ置く場合は、閲覧権限を明示的に制限する。",
                "- Restore/Import前にはbackupを取得し、Operations Logとchange_logsを突合する。",
            ]
        )


def _operator_protection_checklist_text() -> str:
    return "\n".join(
        [
            "operator file protection checklist:",
            "[ ] DBファイルは利用者ごと、または運用担当者だけが読めるフォルダに配置した。",
            "[ ] backupフォルダはDBと同等以上のアクセス制御にした。",
            "[ ] CSV/JSON/SQL exportフォルダは共有前に権限と保存期間を確認した。",
            "[ ] SQL dumpはfull DB dumpとして扱い、共有用JSONとは用途を分けた。",
            "[ ] 共有用JSONに認証・管理・設定・監査系テーブルが含まれないことを理解した。",
            "[ ] change_logs / operations_events JSONLの保存先と閲覧権限を確認した。",
            "[ ] Windowsでは Get-Acl または icacls でUsers/Auth Users/Everyoneの読取権限を確認した。",
            "[ ] 必要に応じてBitLocker/EFS/共有フォルダ権限を併用した。",
            "[ ] Restore/Import前にbackupとOperations Logの確認手順を決めた。",
            "[ ] 外部送付・添付・アップロード前にファイル種別と含有情報を再確認した。",
        ]
    )


def _audit_safety_text() -> str:
    return "\n".join(
        [
            "passwordログ非記録方針:",
            "- user_audit_logsのbefore_json/after_jsonは operator_id, display_name, role,",
            "  disabled_at, failed_login_count, locked_until, last_login_at を記録対象とします。",
            "- password、password_hash、password_salt、password_algorithm、",
            "  password_iterations は監査ログ表示/JSON差分に含めません。",
            "- login_failureではreasonのみを記録し、入力されたpassword値は記録しません。",
            "- 自動テストで平文passwordおよびpassword系キーが監査ログに混入しないことを確認します。",
        ]
    )


def _guide_text() -> str:
    return "\n".join(
        [
            "1. 起動時にローカルログインで操作者とロールを選択します。これは外部認証ではなく、操作記録用のローカル選択です。",
            "2. 通常確認は『検索』で名前・タイトル・サブタイトルを横断検索します。",
            "3. 名前は『名前を管理』で登録・更新し、通常タブではゴミ箱投入まで行います。",
            "4. タイトルは『タイトルを管理』で、登録時に関連付ける名前を1件だけ選びます。",
            "5. サブタイトルは『サブタイトルを管理』で、タイトルを選択して登録します。管理番号は未入力なら自動生成されます。",
            "6. 例外的な関連修正だけ『関連付け』を使います。関連種類は内部で primary 固定です。",
            "7. 復元と完全削除は『削除データ』に集約しています。通常タブでは実施しません。",
            "8. 変更履歴は『操作履歴』で確認します。変更前・変更後・差分を項目名付きで表示します。",
            "9. DB変更履歴の正本はDB内 change_logs です。change_logs.jsonl は外部確認用の補助ログです。",
            "10. operations_events.jsonl は『データ入出力』のExport/Import/Backup/Restoreや起動確認を記録します。",
            "11. DB変更ログとOperations実行ログは別系統です。必要に応じて時刻と操作者で突き合わせます。",
            "12. JSONLログ出力に失敗してもDB更新は継続します。監査上の正本はDB内 change_logs です。",
            "13. バックアップ、復元、CSV/JSON/SQL出力、共有用JSON出力、CSV/JSON取込は『データ入出力』で実行します。",
            "14. 共有用JSON出力は共有向けです。認証・管理・設定系テーブルを除外します。",
            "15. SQL dumpはfull DB dumpです。認証・管理・設定系テーブルを含み得るため、共有時は使い分けてください。",
            "16. Restore と Import は destructive 操作です。事前にバックアップを取得してください。",
            "17. DB保存先は NAMEVERIFICATION_DB_PATH で変更できます。EXE起動前に指定してください。",
            "18. DB変更JSONLログは NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH で保存先を変更できます。",
            "19. Operations実行JSONLログは NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH で保存先を変更できます。",
            "20. 検証は pytest / ruff / black / mypy / EXE build / smoke test を実行します。",
        ]
    )
