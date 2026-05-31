"""Regression tests for workflow navigation polish."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication
QTabWidget = qt_widgets.QTabWidget
QWidget = qt_widgets.QWidget

from app.ui.navigation_polish import apply_workflow_tab_navigation  # noqa: E402


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_apply_workflow_tab_navigation_adds_guidance_without_renaming_tabs() -> None:
    _app()
    tabs = QTabWidget()
    for label in ["一覧", "新規追加", "編集", "削除", "ガイド"]:
        tabs.addTab(QWidget(), label)

    apply_workflow_tab_navigation(tabs)

    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        "一覧",
        "新規追加",
        "編集",
        "削除",
        "ガイド",
    ]
    assert tabs.property("navigation_polish_applied") is True
    assert tabs.property("navigation_order_hint") == "一覧 -> 新規追加 -> 編集 -> 削除 -> ガイド"
    assert tabs.tabToolTip(0).startswith("登録済みデータ")
    assert "空フォーム" in tabs.tabToolTip(1)
    assert "admin" in tabs.tabToolTip(3)


def test_apply_workflow_tab_navigation_accepts_numbered_labels() -> None:
    _app()
    tabs = QTabWidget()
    for label in ["1. 一覧", "2. 新規追加", "3. 編集"]:
        tabs.addTab(QWidget(), label)

    apply_workflow_tab_navigation(tabs)

    assert tabs.tabText(0) == "1. 一覧"
    assert tabs.tabToolTip(0).startswith("登録済みデータ")
    assert "空フォーム" in tabs.tabToolTip(1)
    assert "対象を明示" in tabs.tabToolTip(2)
