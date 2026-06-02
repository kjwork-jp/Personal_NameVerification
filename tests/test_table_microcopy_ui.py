"""UI tests for table readability and microcopy consistency."""

# ruff: noqa: E402, I001

from __future__ import annotations

import os

import pytest

from app.application.read_models import NameDetail, NameSearchRow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from app.ui.name_management_tab import NameManagementTab
from app.ui.public_id_display import public_id_detail, short_public_id
from app.ui.role_context import RoleContext


LONG_PUBLIC_ID = "12345678-1234-1234-1234-123456789abc"


class StubCoreService:
    pass


class StubQueryService:
    def search_names(self, *args, **kwargs) -> list[NameSearchRow]:  # type: ignore[no-untyped-def]
        _ = (args, kwargs)
        return [
            NameSearchRow(
                id=1,
                raw_name="Alice",
                normalized_name="alice",
                note="primary note",
                deleted_at=None,
                linked_count=3,
                title_ids=(10,),
                public_id=LONG_PUBLIC_ID,
                title_related_count=1,
                subtitle_related_count=2,
            )
        ]

    def get_name_detail(self, name_id: int, role: str = "admin") -> NameDetail:
        _ = (name_id, role)
        return NameDetail(
            id=1,
            raw_name="Alice",
            normalized_name="alice",
            note="primary note",
            icon_path=None,
            deleted_at=None,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
            public_id=LONG_PUBLIC_ID,
        )


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_public_id_table_display_keeps_full_detail() -> None:
    assert short_public_id(LONG_PUBLIC_ID) == LONG_PUBLIC_ID
    assert public_id_detail(LONG_PUBLIC_ID) == LONG_PUBLIC_ID
    assert short_public_id(None) == "未採番"
    assert public_id_detail(None) == "未採番"


def test_name_table_uses_short_public_id_with_full_tooltip() -> None:
    _app()
    tab = NameManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    public_id_item = tab.names_table.item(0, 1)
    assert public_id_item is not None
    assert public_id_item.text() == LONG_PUBLIC_ID
    assert public_id_item.toolTip() == LONG_PUBLIC_ID
