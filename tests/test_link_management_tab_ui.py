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
        self.calls.append(
            f"link:{name_id}:{subtitle_id}:{relation_type}:{operator_id}:{role}"
        )
        return 1

    def unlink_name_from_subtitle(
        self, link_id: int, operator_id: str, role: str = "admin"
    ) -> None:
        self.calls.append(f"unlink:{link_id}:{operator_id}:{role}")


class StubQueryService:
    def __init__(self, *, include_existing_link: bool = False) -> None:
        self.include_existing_link = include_existing_link

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
                public_id="title-public-id-001",
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
                public_id="subtitle-public-id-001",
            )
        ]

    def list_related_rows(
        self, name_id: int, role: str = "admin", *, include_deleted: bool = False
    ) -> list[RelatedRow]:
        _ = (name_id, role, include_deleted)
        if not self.include_existing_link:
            return []
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
                link_public_id="link-public-id-001",
            )
        ]


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_link_management_tab_registers_primary_relation() -> None:
    _app()
    core = StubCoreService()
    query = StubQueryService(include_existing_link=False)
    tab = LinkManagementTab(
        core_service=core,
        query_service=query,
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    tab._create_link()

    assert "link:1:100:primary:op-1:admin" in core.calls
    assert not hasattr(tab, "relation_type_combo")
    assert not hasattr(tab, "operator_input")


def test_link_management_tab_unlinks_existing_relation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _app()
    monkeypatch.setattr(
        link_tab_module,
        "confirm_destructive_action",
        lambda *args, **kwargs: True,
    )
    core = StubCoreService()
    query = StubQueryService(include_existing_link=True)
    tab = LinkManagementTab(
        core_service=core,
        query_service=query,
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

    tab._unlink_link()

    assert "unlink:500:op-1:admin" in core.calls


def test_link_management_uses_login_operator_without_input_field() -> None:
    _app()
    core = StubCoreService()
    tab = LinkManagementTab(
        core_service=core,
        query_service=StubQueryService(include_existing_link=False),
        role_context=RoleContext(role="admin", operator_id="login-user"),
    )

    assert not hasattr(tab, "operator_input")
    tab._create_link()
    assert "link:1:100:primary:login-user:admin" in core.calls


def test_link_management_cancel_unlink(monkeypatch: pytest.MonkeyPatch) -> None:
    _app()
    monkeypatch.setattr(
        link_tab_module,
        "confirm_destructive_action",
        lambda *args, **kwargs: False,
    )
    core = StubCoreService()
    tab = LinkManagementTab(
        core_service=core,
        query_service=StubQueryService(include_existing_link=True),
        role_context=RoleContext(role="admin", operator_id="op-1"),
    )

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
    assert "未関連" in admin.link_button.toolTip()
    assert "既存関連" in admin.unlink_button.toolTip()


def test_link_management_propagates_editor_role_to_service() -> None:
    _app()
    core = StubCoreService()
    tab = LinkManagementTab(
        core_service=core,
        query_service=StubQueryService(include_existing_link=False),
        role_context=RoleContext(role="editor", operator_id="op-2"),
    )

    tab._create_link()

    assert "link:1:100:primary:op-2:editor" in core.calls


def test_link_management_labels_are_readable_and_full_public_id() -> None:
    _app()
    tab = LinkManagementTab(
        core_service=StubCoreService(),
        query_service=StubQueryService(include_existing_link=True),
    )

    assert tab.register_name_combo.itemText(0) == "名前: Alice（公開ID: name-public-id-001）"
    assert tab.register_title_combo.itemText(0) == "タイトル: T1（公開ID: title-public-id-001）"
    assert "公開ID=" not in tab.register_name_combo.itemText(0)
    assert "..." not in tab.register_name_combo.itemText(0)
    assert "…" not in tab.register_name_combo.itemText(0)
