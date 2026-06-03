"""Regression tests for 2026-05-27 editor UAT follow-up fixes."""

from __future__ import annotations

import os

import pytest

from app.application.core_services import SubtitleInput
from app.application.read_models import NameSearchRow, RelatedRow, SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import link_management_tab as link_tab_module  # noqa: E402
from app.ui.link_management_tab import LinkManagementTab  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.subtitle_management_tab import SubtitleManagementTab  # noqa: E402
from app.ui.title_management_tab import TitleManagementTab  # noqa: E402


class StubCoreService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def create_subtitle(
        self,
        payload: SubtitleInput,
        operator_id: str,
        role: str = "admin",
    ) -> int:
        self.calls.append(f"create_subtitle:{payload.title_id}:{payload.subtitle_code}")
        self.calls.append(f"operator:{operator_id}:{role}")
        return 1

    def update_subtitle(
        self,
        subtitle_id: int,
        payload: SubtitleInput,
        operator_id: str,
        role: str = "admin",
    ) -> None:
        self.calls.append(f"update_subtitle:{subtitle_id}:{payload.subtitle_code}")
        self.calls.append(f"operator:{operator_id}:{role}")

    def link_name_to_subtitle(
        self,
        name_id: int,
        subtitle_id: int,
        relation_type: str,
        operator_id: str,
        role: str = "admin",
    ) -> int:
        self.calls.append(f"link:{name_id}:{subtitle_id}:{relation_type}")
        self.calls.append(f"operator:{operator_id}:{role}")
        return 1

    def unlink_name_from_subtitle(
        self,
        link_id: int,
        operator_id: str,
        role: str = "admin",
    ) -> None:
        self.calls.append(f"unlink:{link_id}")
        self.calls.append(f"operator:{operator_id}:{role}")


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
                public_id="name-public-id-001",
            )
        ]

    def list_titles(
        self,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return [
            TitleDetail(
                id=10,
                title_name="Searchable Parent Title",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
                public_id="title-public-id-001",
            )
        ]

    def list_subtitles(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
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
                public_id="subtitle-public-id-001",
            )
        ]

    def list_names_for_title(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[object]:
        _ = (title_id, role, include_deleted)
        return []

    def list_related_rows(
        self,
        name_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
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
                title_name="Searchable Parent Title",
                link_deleted_at=None,
                link_public_id="link-public-id-001",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _role() -> RoleContext:
    return RoleContext(role="editor", operator_id="op-1")


def test_subtitle_parent_title_selector_is_searchable() -> None:
    _app()
    tab = SubtitleManagementTab(StubCoreService(), StubQueryService(), _role())

    combo = tab.editor.add_subtitle_title_combo
    assert combo.isEditable()
    assert combo.completer() is not None
    assert tab.editor.property("searchable_title_selector_for_subtitle") is True
    assert tab.editor.property("subtitle_create_state_refresh_connected") is True

    combo.setCurrentIndex(1)
    assert tab.editor.subtitle_create_button.isEnabled()


def test_subtitle_editor_can_create_and_update_as_editor() -> None:
    _app()
    core = StubCoreService()
    tab = SubtitleManagementTab(core, StubQueryService(), _role())

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.add_tab)
    tab.editor.add_subtitle_title_combo.setCurrentIndex(1)
    tab.editor.add_subtitle_code_input.setText("SNEW")
    tab.editor.add_subtitle_name_input.setText("SubNew")
    tab.editor._create_subtitle()

    tab.editor.workflow_tabs.setCurrentWidget(tab.editor.edit_tab)
    tab.editor.titles_table.selectRow(0)
    tab.editor.subtitles_table.selectRow(0)
    tab.editor.subtitle_code_input.setText("S1-U")
    tab.editor._update_subtitle()

    assert "create_subtitle:10:SNEW" in core.calls
    assert "update_subtitle:100:S1-U" in core.calls
    assert "operator:op-1:editor" in core.calls


def _always_confirm(*_args: object, **_kwargs: object) -> bool:
    return True


def test_editor_can_unlink_existing_relation(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(link_tab_module, "confirm_destructive_action", _always_confirm)
    core = StubCoreService()
    tab = LinkManagementTab(core, StubQueryService(), _role())

    assert tab.unlink_button.isEnabled()
    tab._unlink_link()

    assert "unlink:500" in core.calls
    assert "operator:op-1:editor" in core.calls


def test_title_management_guidance_labels_are_wrapped() -> None:
    _app()
    tab = TitleManagementTab(StubCoreService(), StubQueryService(), _role())

    assert tab.editor.property("title_guidance_labels_wrapped") is True
    assert tab.editor.workflow_hint_label.wordWrap()
    assert "選択カード" in tab.editor.workflow_hint_label.text()
