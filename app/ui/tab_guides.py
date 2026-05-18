"""Shared operation guide panels for main tabs."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

_GUIDES: dict[str, str] = {
    "検索": (
        "名前・タイトル・サブタイトルを横断検索します。"
        "条件を入力して検索し、下段で関連情報を確認します。"
    ),
    "名前を管理": (
        "名前の一覧確認、絞り込み、新規作成、更新、ゴミ箱移動を行います。"
        "復元と完全削除は削除データタブで実行します。"
    ),
    "タイトルを管理": (
        "名前を選択し、関連するタイトルを登録・更新します。"
        "復元と完全削除は削除データタブで実行します。"
    ),
    "サブタイトルを管理": (
        "タイトルを選択し、配下のサブタイトルを登録・更新します。"
        "管理番号は未入力なら自動生成されます。"
    ),
    "関連付け": (
        "名前とタイトル/サブタイトルの関連付けを作成・確認します。"
        "関連解除や削除系操作は権限に応じて制御されます。"
    ),
    "削除データ": (
        "削除済みデータを対象別に確認します。"
        "adminのみ復元または完全削除を実行できます。"
    ),
    "操作履歴": (
        "変更履歴を確認します。"
        "登録・更新・削除・復元などの操作証跡を追跡します。"
    ),
    "ユーザー管理": (
        "ユーザーの作成、ロール変更、無効化、パスワード再設定を行います。"
        "最後の有効admin保護が適用されます。"
    ),
    "ユーザー監査ログ": (
        "ログイン失敗、ユーザー管理操作などの認証・ユーザー系監査ログを確認します。"
    ),
    "データ入出力": (
        "Export / Backup / Restore / Import / Operations Log を用途別に実行します。"
        "Restore/Importはadmin専用です。"
    ),
    "ヘルプ / 設定": (
        "実行中のDB、ログ、パッケージパスを確認します。"
        "配布時やトラブル調査時の参照画面です。"
    ),
}

_GUIDE_STYLE = """
QGroupBox#tabGuidePanel {
    margin-top: 6px;
    padding-top: 6px;
}
QGroupBox#tabGuidePanel::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 3px;
}
"""


def apply_tab_guide(widget: QWidget, tab_title: str) -> None:
    """Insert a compact operation guide near the top of a tab layout."""

    if widget.property("has_tab_guide") is True:
        return

    guide_text = _GUIDES.get(tab_title)
    if guide_text is None:
        return

    root_layout = widget.layout()
    if not isinstance(root_layout, QVBoxLayout):
        return

    guide = QGroupBox("操作ガイド")
    guide.setObjectName("tabGuidePanel")
    guide.setStyleSheet(_GUIDE_STYLE)
    guide_layout = QVBoxLayout(guide)
    guide_layout.setContentsMargins(8, 8, 8, 6)
    guide_layout.setSpacing(2)

    label = QLabel(guide_text)
    label.setWordWrap(True)
    label.setTextFormat(Qt.TextFormat.PlainText)
    guide_layout.addWidget(label)

    insert_index = 1 if root_layout.count() > 0 else 0
    root_layout.insertWidget(insert_index, guide)
    widget.setProperty("has_tab_guide", True)
