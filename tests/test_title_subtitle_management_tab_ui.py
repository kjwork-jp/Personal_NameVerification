"""UI tests for TitleSubtitleManagementTab."""

from __future__ import annotations

import os

import pytest

from app.application.read_models import SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui import title_subtitle_management_tab as ts_tab_module  # noqa: E402
from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab  # noqa: E402


class StubCoreService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def create_title(self, payload, operator_id: str, role: str = "admin") -> int:  # type: ignore[no-untyped-def]
        self.calls.append(f"create_title:{payload.title_name}:{operator_id}:{role}")
        return 1

    def update_title(self, title_id: int, payload, operator_id: str, role: str = "admin") -> None:  # type: ignore[no-untyped-def]
        self.calls.append(f"update_title:{title_id}:{payload.title_name}:{operator_id}:{role}")

    def delete_title(self, title_id: int, operator_id: str, role: str = "admin") -> None:
        self.calls.append(f"delete_title:{title_id}:{operator_id}:{role}")

    def restore_title(self, title_id: int, operator_id: str, role: str = "admin") -> None:
        self.calls.append(f"restore_title:{title_id}:{operator_id}:{role}")

    def hard_delete_title(self, title_id: int, operator_id: str, role: str = "admin") -> None:
        self.calls.append(f"hard_delete_title:{title_id}:{operator_id}:{role}")

    def create_subtitle(self, payload, operator_id: str, role: str = "admin") -> int:  # type: ignore[no-untyped-def]
        self.calls.append(
            f"create_subtitle:{payload.title_id}:{payload.subtitle_code}:{operator_id}:{role}"
        )
        return 1

    def update_subtitle(  # type: ignore[no-untyped-def]
        self,
        subtitle_id: int,
        payload,
        operator_id: str,
        role: str = "admin",
    ) -> None:
        self.calls.append(
            f"update_subtitle:{subtitle_id}:{payload.subtitle_code}:{operator_id}:{role}"
        )

    def delete_subtitle(self, subtitle_id: int, operator_id: str, role: str = "admin") -> None:
        self.calls.append(f"delete_subtitle:{subtitle_id}:{operator_id}:{role}")

    def restore_subtitle(self, subtitle_id: int, operator_id: str, role: str = "admin") -> None:
        self.calls.append(f"restore_subtitle:{subtitle_id}:{operator_id}:{role}")

    def hard_delete_subtitle(self, subtitle_id: int, operator_id: str, role: str = "admin") -> None:
        self.calls.append(f"hard_delete_subtitle:{subtitle_id}:{operator_id}:{role}")


class StubQueryService:
    def __init__(self) -> None:
        self.titles = [
            TitleDetail(
                id=1,
                title_name="Title1",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
            TitleDetail(
                id=2,
                title_name="Title2",
                note="memo",
                icon_path=None,
                deleted_at="2026-01-02T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-02T00:00:00Z",
            ),
        ]

    def list_titles(self, *, include_deleted: bool = False) -> list[TitleDetail]:
        _ = include_deleted
        return self.titles

    def list_subtitles(
        self, title_id: int, *, include_deleted: bool = False
    ) -> list[SubtitleDetail]:
        _ = include_deleted
        if title_id == 2:
            deleted_at = "2026-01-03T00:00:00Z"
        else:
            deleted_at = None
        return [
            SubtitleDetail(
                id=10 + title_id,
                title_id=title_id,
                subtitle_code=f"S{title_id}",
                subtitle_name=f"Sub{title_id}",
                sort_order=1,
                note=None,
                icon_path=None,
                deleted_at=deleted_at,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_title_subtitle_management_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(ts_tab_module, "confirm_destructive_action", lambda *args, **kwargs: True)
    core = StubCoreService()
    query = StubQueryService()
    tab = TitleSubtitleManagementTab(core_service=core, query_service=query)

    tab.operator_input.setText("op-1")

    tab.title_name_input.setText("NewTitle")
    tab._create_title()
    tab.titles_table.selectRow(0)
    tab.title_name_input.setText("UpdatedTitle")
    tab._update_title()
    tab._delete_title()

    tab.titles_table.selectRow(1)
    tab._restore_title()
    tab._hard_delete_title()

    tab.titles_table.selectRow(0)
    tab.subtitle_code_input.setText("SNEW")
    tab.subtitle_name_input.setText("SubNew")
    tab._create_subtitle()

    tab.subtitles_table.selectRow(0)
    tab.subtitle_code_input.setText("S1-U")
    tab._update_subtitle()
    tab._delete_subtitle()

    tab.titles_table.selectRow(0)
    tab.subtitles_table.selectRow(0)
    tab._restore_subtitle()
    tab._hard_delete_subtitle()

    assert any(call.startswith("create_title:NewTitle:op-1:admin") for call in core.calls)
    assert any(call.startswith("update_title:1:UpdatedTitle:op-1:admin") for call in core.calls)
    assert any(call.startswith("delete_title:1:op-1:admin") for call in core.calls)
    assert any(call.startswith("restore_title:2:op-1:admin") for call in core.calls)
    assert any(call.startswith("hard_delete_title:2:op-1:admin") for call in core.calls)
    assert any(call.startswith("create_subtitle:1:SNEW:op-1:admin") for call in core.calls)
    assert any(call.startswith("update_subtitle:11:S1-U:op-1:admin") for call in core.calls)
    assert any(call.startswith("delete_subtitle:11:op-1:admin") for call in core.calls)
    assert any(call.startswith("restore_subtitle:11:op-1:admin") for call in core.calls)
    assert any(call.startswith("hard_delete_subtitle:11:op-1:admin") for call in core.calls)


def test_title_subtitle_management_requires_operator_id() -> None:
    _app()
    tab = TitleSubtitleManagementTab(
        core_service=StubCoreService(), query_service=StubQueryService()
    )
    tab.operator_input.setText("")
    tab._create_title()

    assert "operator_id" in tab.message_label.text()


def test_title_subtitle_cancel_does_not_call_service(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(ts_tab_module, "confirm_destructive_action", lambda *args, **kwargs: False)
    core = StubCoreService()
    tab = TitleSubtitleManagementTab(core_service=core, query_service=StubQueryService())
    tab.operator_input.setText("op-1")

    tab.titles_table.selectRow(0)
    tab._delete_title()

    assert not any(call.startswith("delete_title:") for call in core.calls)


def test_title_subtitle_role_guards() -> None:
    _app()
    viewer = TitleSubtitleManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="viewer"),
    )
    assert not viewer.title_create_button.isEnabled()
    assert not viewer.subtitle_create_button.isEnabled()
    assert "このロールでは実行できません" in viewer.title_delete_button.toolTip()

    editor = TitleSubtitleManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="editor"),
    )
    assert editor.title_create_button.isEnabled()
    assert editor.subtitle_update_button.isEnabled()
    assert not editor.title_delete_button.isEnabled()
    assert not editor.subtitle_delete_button.isEnabled()

    admin = TitleSubtitleManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin"),
    )
    assert admin.title_delete_button.isEnabled()
    assert not admin.title_restore_button.isEnabled()
    assert admin.subtitle_delete_button.isEnabled()
    assert not admin.subtitle_hard_delete_button.isEnabled()
    assert "operator_id" in admin.operator_input.toolTip()


def test_selected_title_label_and_subtitle_form_clear_on_title_change() -> None:
    _app()
    tab = TitleSubtitleManagementTab(
        core_service=StubCoreService(), query_service=StubQueryService()
    )

    tab.titles_table.selectRow(0)
    assert "ID=1 / Title1 (有効)" in tab.selected_title_label.text()

    tab.subtitle_code_input.setText("TEMP")
    tab.titles_table.selectRow(1)

    assert "ID=2 / Title2 (削除済み)" in tab.selected_title_label.text()
    assert tab.subtitle_code_input.text() == ""
    assert "削除済みタイトル" in tab.subtitle_hint_label.text()
    assert not tab.subtitle_create_button.isEnabled()


def test_cannot_create_or_update_subtitle_under_deleted_title() -> None:
    _app()
    core = StubCoreService()
    tab = TitleSubtitleManagementTab(core_service=core, query_service=StubQueryService())
    tab.operator_input.setText("op-1")
    tab.titles_table.selectRow(1)

    tab.subtitle_code_input.setText("S2-N")
    tab.subtitle_name_input.setText("Sub2-New")
    tab._create_subtitle()
    assert "削除済みタイトルにはサブタイトル作成できません" in tab.message_label.text()
    assert not any(call.startswith("create_subtitle:") for call in core.calls)

    tab.subtitles_table.selectRow(0)
    tab.subtitle_code_input.setText("S2-U")
    tab._update_subtitle()
    assert "削除済みタイトルのサブタイトルは更新できません" in tab.message_label.text()
    assert not any(call.startswith("update_subtitle:") for call in core.calls)


def test_subtitle_buttons_disabled_without_title_selection() -> None:
    _app()
    tab = TitleSubtitleManagementTab(
        core_service=StubCoreService(), query_service=StubQueryService()
    )
    tab.titles_table.clearSelection()

    assert "タイトルを選択してください" in tab.subtitle_hint_label.text()
    assert not tab.subtitle_refresh_button.isEnabled()
    assert not tab.subtitle_create_button.isEnabled()
    assert not tab.subtitle_update_button.isEnabled()
    assert not tab.subtitle_delete_button.isEnabled()
    assert not tab.subtitle_restore_button.isEnabled()
    assert not tab.subtitle_hard_delete_button.isEnabled()


def test_title_buttons_follow_deleted_state() -> None:
    _app()
    tab = TitleSubtitleManagementTab(
        core_service=StubCoreService(), query_service=StubQueryService()
    )

    tab.titles_table.selectRow(0)
    assert tab.title_update_button.isEnabled()
    assert tab.title_delete_button.isEnabled()
    assert not tab.title_restore_button.isEnabled()
    assert not tab.title_hard_delete_button.isEnabled()

    tab.titles_table.selectRow(1)
    assert not tab.title_update_button.isEnabled()
    assert not tab.title_delete_button.isEnabled()
    assert tab.title_restore_button.isEnabled()
    assert tab.title_hard_delete_button.isEnabled()


class SubtitleDeletedOnActiveTitleQueryService(StubQueryService):
    def list_subtitles(
        self, title_id: int, *, include_deleted: bool = False
    ) -> list[SubtitleDetail]:
        _ = include_deleted
        return [
            SubtitleDetail(
                id=11,
                title_id=title_id,
                subtitle_code="S1",
                subtitle_name="Sub1",
                sort_order=1,
                note=None,
                icon_path=None,
                deleted_at="2026-01-03T00:00:00Z",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]


def test_subtitle_destructive_buttons_follow_subtitle_deleted_state() -> None:
    _app()
    tab = TitleSubtitleManagementTab(
        core_service=StubCoreService(), query_service=SubtitleDeletedOnActiveTitleQueryService()
    )
    tab.titles_table.selectRow(0)
    tab.subtitles_table.selectRow(0)

    assert not tab.subtitle_update_button.isEnabled()
    assert not tab.subtitle_delete_button.isEnabled()
    assert tab.subtitle_restore_button.isEnabled()
    assert tab.subtitle_hard_delete_button.isEnabled()
