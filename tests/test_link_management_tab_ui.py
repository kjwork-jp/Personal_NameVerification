"""UI tests for LinkManagementTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameSearchRow, RelatedRow, SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import link_management_tab as link_tab_module  # noqa: E402
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
        self.calls.append(f"link:{name_id}:{subtitle_id}:{relation_type}:{operator_id}:{role}")
        return 1

    def unlink_name_from_subtitle(
        self, link_id: int, operator_id: str, role: str = "admin"
    ) -> None:
        self.calls.append(f"unlink:{link_id}:{operator_id}:{role}")


class StubQueryService:
    def search_names(self, *args: object, **kwargs: object) -> list[NameSearchRow]:
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                deleted_at=None,
                linked_count=0,
                title_ids=(),
            )
        ]

    def list_titles(
        self, role: str = "admin", *, include_deleted: bool = False
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return [
            TitleDetail(
                id=10,
                title_name="T1",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

    def list_subtitles(
        self, title_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[SubtitleDetail]:
        _ = (title_id, role, include_deleted)
        return [
            SubtitleDetail(
                id=100,
                title_id=10,
                subtitle_code="S1",
                subtitle_name="Sub1",
                sort_order=1,
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

    def list_related_rows(
        self, name_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[RelatedRow]:
        _ = (name_id, role, include_deleted)
        return [
            RelatedRow(
                link_id=500,
                name_id=1,
                subtitle_id=100,
                title_id=10,
                relation_type="primary",
                subtitle_code="S1",
                subtitle_name="Sub1",
                title_name="T1",
                link_deleted_at=None,
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_link_management_tab_link_and_unlink(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(link_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True)
    core = StubCoreService()
    query = StubQueryService()
    tab = LinkManagementTab(core_service=core, query_service=query)

    tab.operator_input.setText("op-1")
    tab.relation_type_combo.setCurrentIndex(1)
    tab._create_link()
    tab._unlink_link()

    assert "link:1:100:primary:op-1:admin" in core.calls
    assert "unlink:500:op-1:admin" in core.calls


def test_link_management_tab_requires_operator_and_relation_type() -> None:
    _app()
    tab = LinkManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    tab.operator_input.setText("")
    tab.relation_type_combo.setCurrentIndex(0)
    tab._create_link()
    assert "operator_id" in tab.message_label.text()


def test_link_management_cancel_unlink(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(
        link_tab_module, "confirm_destructive_action", lambda *args, **kwargs: False
    )
    core = StubCoreService()
    tab = LinkManagementTab(core_service=core, query_service=StubQueryService())

    tab.operator_input.setText("op-1")
    tab._unlink_link()

    assert not any(call.startswith("unlink:") for call in core.calls)


def test_link_management_role_guards() -> None:
    _app()
    viewer = LinkManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="viewer"),
    )
    assert not viewer.link_button.isEnabled()
    assert not viewer.unlink_button.isEnabled()
    assert "このロールでは実行できません" in viewer.link_button.toolTip()

    editor = LinkManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="editor"),
    )
    assert editor.link_button.isEnabled()
    assert not editor.unlink_button.isEnabled()

    admin = LinkManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin"),
    )
    assert admin.link_button.isEnabled()
    assert admin.unlink_button.isEnabled()
    assert "relation_type" in admin.relation_type_combo.toolTip()


def test_link_management_tab_requires_relation_type_selection() -> None:
    _app()
    tab = LinkManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    tab.operator_input.setText("op-1")
    tab.relation_type_combo.setCurrentIndex(0)
    tab._create_link()

    assert "relation_type" in tab.message_label.text()


def test_link_management_tab_accepts_custom_relation_type(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(link_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True)
    core = StubCoreService()
    tab = LinkManagementTab(core_service=core, query_service=StubQueryService())

    tab.operator_input.setText("op-1")
    tab.relation_type_combo.setCurrentIndex(tab.relation_type_combo.count() - 1)
    tab.custom_relation_type_input.setText("custom-tag")
    tab._create_link()

    assert "link:1:100:custom-tag:op-1:admin" in core.calls


def test_link_management_custom_relation_type_requires_text() -> None:
    _app()
    tab = LinkManagementTab(core_service=StubCoreService(), query_service=StubQueryService())

    tab.operator_input.setText("op-1")
    tab.relation_type_combo.setCurrentIndex(tab.relation_type_combo.count() - 1)
    tab.custom_relation_type_input.setText("")
    tab._create_link()

    assert "custom relation_type" in tab.message_label.text()
    assert "custom relation_type" in tab.custom_relation_type_input.toolTip()


def test_link_management_propagates_editor_role_to_service() -> None:
    _app()
    core = StubCoreService()
    tab = LinkManagementTab(
        core_service=core,
        query_service=StubQueryService(),
        role_context=RoleContext(role="editor"),
    )

    tab.operator_input.setText("op-2")
    tab.relation_type_combo.setCurrentIndex(1)
    tab._create_link()

    assert "link:1:100:primary:op-2:editor" in core.calls
