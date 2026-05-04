"""Help and settings tab for desktop/EXE usage."""

from __future__ import annotations

import os
from pathlib import Path

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
from app.ui.ui_style import PageHeader


class HelpSettingsTab(QWidget):
    """Read-only guidance for local desktop operation."""

    def __init__(self, database_path: Path | None = None) -> None:
        super().__init__()
        self.database_path = database_path or Path("nameverification.db")

        self.database_path_input = QLineEdit(str(self.database_path.resolve()))
        self.database_path_input.setReadOnly(True)

        self.operator_input = QLineEdit(default_operator_id())
        self.operator_input.setReadOnly(True)

        self.operator_env_input = QLineEdit(
            os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "未設定") or "未設定"
        )
        self.operator_env_input.setReadOnly(True)

        self.backup_hint_input = QLineEdit("データ入出力タブからバックアップを作成してください")
        self.backup_hint_input.setReadOnly(True)

        self.refresh_button = QPushButton("表示を更新")
        self.refresh_button.clicked.connect(self._refresh_values)

        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.guide_text.setPlainText(_guide_text())

        form = QFormLayout()
        form.addRow("DB保存先", self.database_path_input)
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
        layout.addWidget(self.refresh_button)
        layout.addWidget(QLabel("使い方の要点"))
        layout.addWidget(self.guide_text)

    def _refresh_values(self) -> None:
        self.database_path_input.setText(str(self.database_path.resolve()))
        self.operator_input.setText(default_operator_id())
        self.operator_env_input.setText(
            os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "未設定") or "未設定"
        )


def _guide_text() -> str:
    return "\n".join(
        [
            "1. 通常は『検索』で名前・タイトル・サブタイトルを確認します。",
            "2. 名前を増やす場合は『名前を管理』を使います。",
            "3. タイトルは『タイトルを管理』で、名前を選んで登録します。",
            "4. サブタイトルは『サブタイトルを管理』で、タイトルを選んで登録します。",
            "5. 例外的な関連修正だけ『関連付け』を使います。",
            "6. 変更履歴は『操作履歴』で確認します。",
            "7. バックアップや復元は『データ入出力』で実行します。",
            "8. 操作者は起動時に自動入力されます。固定したい場合は環境変数を使います。",
            "9. サブタイトルの管理番号は未入力なら自動生成されます。",
            "10. EXE化後もDB保存先とバックアップ取得を必ず確認してください。",
        ]
    )
