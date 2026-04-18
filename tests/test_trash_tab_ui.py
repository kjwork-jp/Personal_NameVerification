"""UI tests for TrashTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail, RelatedRow, SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import trash_tab as trash_tab_module  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.trash_tab import TrashTab  # noqa: E402


class StubCoreService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def restore_name(self, name_id: int, operator_id: str) -> None:
        self.calls.append(f"restore_name:{name_id}:{operator_id}")

    def hard_delete_name(self, name_id: int, operator_id: str) -> None:
        self.calls.append(f"hard_delete_name:{name_id}:{operator_id}")

    def restore_title(self, title_id: int, operator_id: str) -> None:
        self.calls.append(f"restore_title:{title_id}:{operator_id}")

    def hard_delete_title(self, title_id: int, operator_id: str) -> None:
        self.calls.append(f"hard_delete_title:{title_id}:{operator_id}")

    def restore_subtitle(self, subtitle_id: int, operator_id: str) -> None:
        self.calls.append(f"restore_subtitle:{subtitle_id}:{operator_id}")

    def hard_delete_subtitle(self, subtitle_id: int, operator_id: str) -> None:
        self.calls.append(f"hard_delete_subtitle:{subtitle_id}:{operator_id}")

    def restore_link(self, link_id: int, operator_id: str) -> None:
        self.calls.append(f"restore_link:{link_id}:{operator_id}")

    def hard_delete_link(self, link_id: int, operator_id: str) -> None:
        self.calls.append(f"hard_delete_link:{link_id}:{operator_id}")


class StubQueryService:
    def list_deleted_names(self) -> list[NameDetail]:
        return [
            NameDetail(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                icon_path=None,
                deleted_at="2026-01-01T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

    def list_deleted_titles(self) -> list[TitleDetail]:
        return [
            TitleDetail(
                id=10,
                title_name="T1",
                note=None,
                icon_path=None,
                deleted_at="2026-01-01T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

    def list_deleted_subtitles(self) -> list[SubtitleDetail]:
        return [
            SubtitleDetail(
                id=100,
                title_id=10,
                subtitle_code="S1",
                subtitle_name="Sub1",
                sort_order=1,
                note=None,
                icon_path=None,
                deleted_at="2026-01-01T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

    def list_deleted_links(self) -> list[RelatedRow]:
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
                link_deleted_at="2026-01-01T00:00:00Z",
            )
        ]


class ActiveOnlyQueryService(StubQueryService):
    def list_deleted_names(self) -> list[NameDetail]:
        return [
            NameDetail(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_trash_tab_restore_and_hard_delete_for_all_entities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    monkeypatch.setattr(
        trash_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True
    )
    core = StubCoreService()
    tab = TrashTab(core_service=core, query_service=StubQueryService())
    tab.operator_input.setText("op-1")

    # Name
    tab.entity_selector.setCurrentText("Name")
    tab._restore_selected()
    tab._hard_delete_selected()

    # Title
    tab.entity_selector.setCurrentText("Title")
    tab._restore_selected()
    tab._hard_delete_selected()

    # Subtitle
    tab.entity_selector.setCurrentText("Subtitle")
    tab._restore_selected()
    tab._hard_delete_selected()

    # Link
    tab.entity_selector.setCurrentText("Link")
    tab._restore_selected()
    tab._hard_delete_selected()

    assert "restore_name:1:op-1" in core.calls
    assert "hard_delete_name:1:op-1" in core.calls
    assert "restore_title:10:op-1" in core.calls
    assert "hard_delete_title:10:op-1" in core.calls
    assert "restore_subtitle:100:op-1" in core.calls
    assert "hard_delete_subtitle:100:op-1" in core.calls
    assert "restore_link:500:op-1" in core.calls
    assert "hard_delete_link:500:op-1" in core.calls


def test_trash_tab_requires_operator_id() -> None:
    _app()
    tab = TrashTab(core_service=StubCoreService(), query_service=StubQueryService())
    tab.operator_input.setText("")
    tab._restore_selected()
    assert "operator_id" in tab.message_label.text()


def test_trash_tab_guards_active_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(
        trash_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True
    )
    core = StubCoreService()
    tab = TrashTab(core_service=core, query_service=ActiveOnlyQueryService())
    tab.operator_input.setText("op-1")
    tab.entity_selector.setCurrentText("Name")
    tab._restore_selected()

    assert "active" in tab.message_label.text()
    assert not core.calls


def test_trash_tab_cancel_does_not_call_service(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(
        trash_tab_module, "confirm_destructive_action", lambda *args, **kwargs: False
    )
    core = StubCoreService()
    tab = TrashTab(core_service=core, query_service=StubQueryService())
    tab.operator_input.setText("op-1")

    tab.entity_selector.setCurrentText("Name")
    tab._restore_selected()

    assert not core.calls


def test_trash_tab_role_guards() -> None:
    _app()
    viewer = TrashTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="viewer"),
    )
    assert not viewer.restore_button.isEnabled()
    assert not viewer.hard_delete_button.isEnabled()

    editor = TrashTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="editor"),
    )
    assert not editor.restore_button.isEnabled()
    assert not editor.hard_delete_button.isEnabled()

    admin = TrashTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin"),
    )
    assert admin.restore_button.isEnabled()
    assert admin.hard_delete_button.isEnabled()
