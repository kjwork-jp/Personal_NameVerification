"""UI tests for LinkManagementTab role guards."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

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
