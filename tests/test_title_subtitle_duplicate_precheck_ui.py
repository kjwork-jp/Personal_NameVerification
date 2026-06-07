"""UI tests for title/subtitle duplicate input prechecks."""

from __future__ import annotations

import os
from typing import Any

import pytest

from app.application.read_models import SubtitleDetail, TitleDetail

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.role_context import RoleContext  # noqa: E402
from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab  # noqa: E402
from app.ui.title_subtitle_summary_patch import (  # noqa: E402
    install_title_subtitle_summary_counters,
)
from app.ui.title_subtitle_update_duplicate_precheck import (  # noqa: E402
    install_title_subtitle_update_duplicate_precheck,
)

install_title_subtitle_summary_counters()
install_title_subtitle_update_duplicate_precheck()


class StubCoreService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def create_title(
        self,
        payload: Any,
        operator_id: str,
        role: str = "admin",
        *,
        name_ids: list[int] | None = None,
    ) -> int:
        self.calls.append(
            f"create_title:{payload.title_name}:{operator_id}:{role}:{name_ids or []}"
        )
        return 1

    def update_title(
        self,
        title_id: int,
        payload: Any,
        operator_id: str,
        role: str = "admin",
    ) -> None:
        self.calls.append(
            f"update_title:{title_id}:{payload.title_name}:{operator_id}:{role}"
        )

    def create_subtitle(
        self,
        payload: Any,
        operator_id: str,
        role: str = "admin",
    ) -> int:
        self.calls.append(
            f"create_subtitle:{payload.title_id}:{payload.subtitle_code}:{operator_id}:{role}"
        )
        return 1

    def update_subtitle(
        self,
        subtitle_id: int,
        payload: Any,
        operator_id: str,
        role: str = "admin",
    ) -> None:
        self.calls.append(
            f"update_subtitle:{subtitle_id}:{payload.subtitle_code}:{operator_id}:{role}"
        )


class DuplicateQueryService:
    def list_titles(
        self,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[TitleDetail]:
        _ = (role, include_deleted)
        return [
            TitleDetail(
                id=1,
                title_name="Title1",
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

    def list_subtitles(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[SubtitleDetail]:
        _ = (role, include_deleted)
        if title_id != 1:
            return []
        return [
            SubtitleDetail(
                id=11,
                title_id=1,
                subtitle_code="S1",
                subtitle_name="Sub1",
                sort_order=1,
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
            SubtitleDetail(
                id=12,
                title_id=1,
                subtitle_code="S2",
                subtitle_name="Sub2",
                sort_order=2,
                note=None,
                icon_path=None,
                deleted_at=None,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            ),
        ]

    def search_names(self, *args: Any, **kwargs: Any) -> list[Any]:
        _ = (args, kwargs)
        return []

    def list_names_for_title(
        self,
        title_id: int,
        role: str = "admin",
        *,
        include_deleted: bool = False,
    ) -> list[Any]:
        _ = (title_id, role, include_deleted)
        return []


def _tab(core: StubCoreService | None = None) -> TitleSubtitleManagementTab:
    app = QApplication.instance() or QApplication([])
    _ = app
    return TitleSubtitleManagementTab(
        core_service=core or StubCoreService(),
        query_service=DuplicateQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )


def test_title_create_duplicate_is_stopped_before_service_call() -> None:
    core = StubCoreService()
    tab = _tab(core)
    tab.workflow_tabs.setCurrentWidget(tab.add_tab)
    tab.add_title_name_input.setText(" title1 ")

    tab._create_title()

    assert "登録前に重複" in tab.message_label.text()
    assert "Title1" in tab.message_label.text()
    assert not core.calls


def test_subtitle_create_duplicate_code_is_stopped_before_service_call() -> None:
    core = StubCoreService()
    tab = _tab(core)
    tab.workflow_tabs.setCurrentWidget(tab.add_tab)
    tab.add_subtitle_title_combo.setCurrentIndex(1)
    tab.add_subtitle_code_input.setText("s1")
    tab.add_subtitle_name_input.setText("NewSub")

    tab._create_subtitle()

    assert "登録前に重複" in tab.message_label.text()
    assert "管理番号" in tab.message_label.text()
    assert not core.calls


def test_subtitle_update_duplicate_name_is_stopped_before_service_call() -> None:
    core = StubCoreService()
    tab = _tab(core)
    tab.workflow_tabs.setCurrentWidget(tab.edit_tab)
    tab._select_title(tab._titles[0])
    tab._select_subtitle(tab._subtitles[0])
    tab.subtitle_code_input.setText("S1")
    tab.subtitle_name_input.setText("Sub2")
    install_title_subtitle_update_duplicate_precheck()

    tab._update_subtitle()

    assert "登録前に重複" in tab.message_label.text()
    assert "サブタイトル名" in tab.message_label.text()
    assert not core.calls
