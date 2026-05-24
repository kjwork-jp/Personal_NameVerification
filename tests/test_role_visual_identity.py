"""Tests for role visual identity helpers."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.role_visual_identity import (  # noqa: E402
    apply_role_status_style,
    make_role_banner,
    role_banner_text,
    role_visual_identity,
)


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_role_visual_identity_texts_are_role_specific() -> None:
    viewer = role_visual_identity(
        RoleContext(role="viewer", operator_id="v", auth_provider="local")
    )
    editor = role_visual_identity(
        RoleContext(role="editor", operator_id="e", auth_provider="local")
    )
    admin = role_visual_identity(
        RoleContext(role="admin", operator_id="a", auth_provider="local")
    )

    assert viewer.label == "VIEWER / 参照専用"
    assert "登録・更新・削除" in viewer.summary
    assert editor.label == "EDITOR / 編集可"
    assert "バックアップ" in editor.summary
    assert admin.label == "ADMIN / 管理者"
    assert "Import/Restore" in admin.summary
    assert len({viewer.background_color, editor.background_color, admin.background_color}) == 3


def test_role_banner_includes_operator_and_limitations() -> None:
    role_context = RoleContext(role="viewer", operator_id="windows:pc\\naoki")

    text = role_banner_text(role_context)

    assert "VIEWER / 参照専用" in text
    assert "windows:pc\\naoki" in text
    assert "制限" in text


def test_make_role_banner_sets_properties_and_style() -> None:
    _app()
    role_context = RoleContext(role="admin", operator_id="local-admin")

    banner = make_role_banner(role_context)

    assert banner.objectName() == "roleVisualBanner"
    assert banner.property("operatorRole") == "admin"
    assert "ADMIN / 管理者" in banner.text()
    assert "background-color" in banner.styleSheet()


def test_apply_role_status_style_sets_role_property() -> None:
    _app()
    label = qt_widgets.QLabel("status")

    apply_role_status_style(label, RoleContext(role="editor", operator_id="editor1"))

    assert label.property("operatorRole") == "editor"
    assert "background-color" in label.styleSheet()
