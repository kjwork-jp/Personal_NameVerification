"""Help and settings tab for desktop/EXE usage."""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.input_defaults import default_operator_id
from app.ui.ui_style import PageHeader, set_status_message


class HelpSettingsTab(QWidget):
    """Read-only guidance for local desktop operation."""

    def __init__(self, database_path: Path | None = None) -> None:
        super().__init__()
        self.database_path = database_path or Path("nameverification.db")

        self.database_path_input = QLineEdit(str(self.database_path.resolve()))
        self.database_path_input.setReadOnly(True)
        self.database_path_input.setToolTip(
            "現在このアプリが参照しているSQLite DBファイルです。"
        )

        self.database_env_input = QLineEdit(
            os.environ.get("NAMEVERIFICATION_DB_PATH", "未設定") or "未設定"
        )
        self.database_env_input.setReadOnly(True)
        self.database_env_input.setToolTip(
            "DB保存先を固定したい場合は、起動前に NAMEVERIFICATION_DB_PATH を設定します。"
        )

        self.change_log_path_input = QLineEdit(
            os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH", "logs/change_logs.jsonl")
        )
        self.change_log_path_input.setReadOnly(True)
        self.change_log_path_input.setToolTip(
            "DB操作履歴とは別に自動出力するJSONLログです。失敗してもDB更新は継続します。"
        )

        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setReadOnly(True)

        self.operator_env_input = QLineEdit(
            os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "未設定") or "未設定"
        )
        self.operator_env_input.setReadOnly(True)

        self.backup_hint_input = QLineEdit("データ入出力タブからバックアップを作成してください")
        self.backup_hint_input.setReadOnly(True)

        self.copy_db_path_button = QPushButton("DB保存先をコピー")
        self.copy_db_path_button.clicked.connect(self._copy_database_path)
        self.copy_env_command_button = QPushButton("DB環境変数コマンドをコピー")
        self.copy_env_command_button.clicked.connect(self._copy_database_env_command)
        self.copy_change_log_command_button = QPushButton("自動ログ環境変数コマンドをコピー")
        self.copy_change_log_command_button.clicked.connect(self._copy_change_log_env_command)
        self.refresh_button = QPushButton("表示を更新")
        self.refresh_button.clicked.connect(self._refresh_values)

        self.message_label = QLabel("")

        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.guide_text.setPlainText(_guide_text())

        form = QFormLayout()
        form.addRow("DB保存先", self.database_path_input)
        form.addRow("DB保存先の環境変数", self.database_env_input)
        form.addRow("自動JSONLログ出力先", self.change_log_path_input)
        form.addRow("現在の操作者", self.operator_input)
        form.addRow("操作者の環境変数", self.operator_env_input)
        form.addRow("バックアップ", self.backup_hint_input)

        layout = QVBoxLayout(self)
        layout.addWidget(
            PageHeader(
                "ヘルプ / 設定",
                "EXE配布や通常運用を前提に、保存先・操作者・基本操作を確認します。",
            )
        )
        layout.addLayout(form)
        layout.addWidget(self.copy_db_path_button)
        layout.addWidget(self.copy_env_command_button)
        layout.addWidget(self.copy_change_log_command_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.message_label)
        layout.addWidget(QLabel("使い方の要点"))
        layout.addWidget(self.guide_text)

    def _refresh_values(self) -> None:
        self.database_path_input.setText(str(self.database_path.resolve()))
        self.database_env_input.setText(
            os.environ.get("NAMEVERIFICATION_DB_PATH", "未設定") or "未設定"
        )
        self.change_log_path_input.setText(
            os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH", "logs/change_logs.jsonl")
        )
        self.operator_input.setText(default_operator_id())
        self.operator_env_input.setText(
            os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "未設定") or "未設定"
        )
        self._set_message("表示を更新しました")

    def _copy_database_path(self) -> None:
        QGuiApplication.clipboard().setText(str(self.database_path.resolve()))
        self._set_message("DB保存先をクリップボードへコピーしました")

    def _copy_database_env_command(self) -> None:
        command = f'$env:NAMEVERIFICATION_DB_PATH = "{self.database_path.resolve()}"'
        QGuiApplication.clipboard().setText(command)
        self._set_message("DB保存先のPowerShell環境変数コマンドをコピーしました")

    def _copy_change_log_env_command(self) -> None:
        command = '$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "logs/change_logs.jsonl"'
        QGuiApplication.clipboard().setText(command)
        self._set_message("自動JSONLログ出力先のPowerShell環境変数コマンドをコピーしました")

    def _set_message(self, message: str) -> None:
        set_status_message(self.message_label, message, level="success")


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
            "9. DB操作履歴はDB内 change_logs に残ります。加えて JSONL へ自動出力されます。",
            "10. JSONL自動ログは NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH で保存先を変更できます。",
            "11. 自動ログ出力に失敗してもDB更新は継続します。ログは監査補助であり、DBが正です。",
            "12. バックアップ、復元、CSV/JSON/SQL出力、CSV/JSON取込は『データ入出力』で実行します。",
            "13. Restore と Import は destructive 操作です。事前にバックアップを取得してください。",
            "14. DB保存先は NAMEVERIFICATION_DB_PATH で変更できます。EXE起動前に指定してください。",
            "15. 検証は pytest / ruff / black / mypy / EXE build / smoke test を実行します。",
        ]
    )
