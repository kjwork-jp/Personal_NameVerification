"""UI tests for LinkManagementTab role guards and normalized labels."""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
qt_core = pytest.importorskip("PySide6.QtCore", exc_type=ImportError)
QApplication = qt_widgets.QApplication
Qt = qt_core.Qt

from app.ui.link_management_tab import LinkManagementTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402


class StubCoreService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def link_name_to_subtitle(
        self,
        name_id: int,
        subtitle_id: int,
        relation_type: str,
        operator_id: str,
        role: str = "admin",
    ) -> int:
        self.calls.append(
            f"link:{name_id}:{subtitle_id}:{relation_type}:{operator_id}:{role}"
        )
        return 1

    def unlink_name_from_subtitle(
        self, link_id: int, operator_id: str, role: str = "admin"
    ) -> None:
        self.calls.append(f"unlink:{link_id}:{operator_id}:{role}")


class EmptyQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def list_titles(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def list_subtitles(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []

    def list_related_rows(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return []


class LabelQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return [
            SimpleNamespace(
                id=100,
                raw_name="Alice",
                public_id="name-public-100",
            )
        ]

    def list_titles(self, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        return [
            SimpleNamespace(
                id=200,
                title_name="Title One",
                public_id="title-public-200",
            )
        ]

    def list_subtitles(self, title_id: int, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        assert title_id == 200
        return [
            SimpleNamespace(
                id=300,
                title_id=200,
                subtitle_code="S1",
                subtitle_name="Sub One",
                public_id="subtitle-public-300",
            ),
            SimpleNamespace(
                id=301,
                title_id=200,
                subtitle_code="S2",
                subtitle_name="Sub Two",
                public_id="subtitle-public-301",
            ),
        ]

    def list_related_rows(self, name_id: int, *args: object, **kwargs: object) -> list[object]:
        _ = (args, kwargs)
        assert name_id == 100
        return [
            SimpleNamespace(
                link_id=400,
                name_id=100,
                subtitle_id=300,
                title_id=200,
                relation_type="primary",
                subtitle_code="S1",
                subtitle_name="Sub One",
                title_name="Title One",
                link_deleted_at=None,
                link_public_id="link-public-400",
                name_public_id="name-public-100",
                subtitle_public_id="subtitle-public-300",
                title_public_id="title-public-200",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _tab_for_role(role: str) -> LinkManagementTab:
    return LinkManagementTab(
        core_service=StubCoreService(),
        query_service=EmptyQueryService(),
        role_context=RoleContext(role=role),
    )


def test_link_management_role_guards() -> None:
    _app()

    viewer = _tab_for_role("viewer")
    assert not viewer.link_button.isEnabled()
    assert not viewer.unlink_button.isEnabled()

    editor = _tab_for_role("editor")
    assert editor.link_button.isEnabled()
    assert editor.unlink_button.isEnabled()

    admin = _tab_for_role("admin")
    assert admin.link_button.isEnabled()
    assert admin.unlink_button.isEnabled()


def test_link_management_propagates_editor_role_to_service() -> None:
    _app()
    core = StubCoreService()
    tab = LinkManagementTab(
        core_service=core,
        query_service=EmptyQueryService(),
        role_context=RoleContext(role="editor", operator_id="op-2"),
    )

    assert tab.link_button.isEnabled()
    assert tab.unlink_button.isEnabled()


def test_link_management_uses_display_names_and_id_tooltips() -> None:
    _app()
    tab = LinkManagementTab(
        core_service=StubCoreService(),
        query_service=LabelQueryService(),
        role_context=RoleContext(role="editor", operator_id="op-2"),
    )

    assert tab.property("link_label_normalized") is True
    assert tab.register_name_combo.itemText(0) == "Alice"
    assert tab.register_title_combo.itemText(0) == "Title One"
    assert tab.register_subtitle_combo.itemText(0) == "S2 / Sub Two"
    assert tab.unregister_link_combo.itemText(0) == "Title One / S1 / Sub One"

    name_tooltip = tab.register_name_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    title_tooltip = tab.register_title_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    subtitle_tooltip = tab.register_subtitle_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)
    link_tooltip = tab.unregister_link_combo.itemData(0, Qt.ItemDataRole.ToolTipRole)

    assert "公開ID: name-public-100" in name_tooltip
    assert "内部ID: 100" in name_tooltip
    assert "公開ID: title-public-200" in title_tooltip
    assert "内部ID: 200" in title_tooltip
    assert "公開ID: subtitle-public-301" in subtitle_tooltip
    assert "親タイトルID: 200" in subtitle_tooltip
    assert "リンク公開ID: link-public-400" in link_tooltip
    assert "名前公開ID: name-public-100" in link_tooltip
    assert "タイトル公開ID: title-public-200" in link_tooltip
    assert "サブタイトル公開ID: subtitle-public-300" in link_tooltip
    assert "内部リンクID: 400" in link_tooltip
