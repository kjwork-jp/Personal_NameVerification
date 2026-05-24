"""Role-specific visual identity helpers for the main UI."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QLabel

from app.ui.role_context import RoleContext, UserRole


@dataclass(frozen=True)
class RoleVisualIdentity:
    role: UserRole
    label: str
    summary: str
    text_color: str
    background_color: str
    border_color: str


_ROLE_VISUALS: dict[UserRole, RoleVisualIdentity] = {
    "viewer": RoleVisualIdentity(
        role="viewer",
        label="VIEWER / 参照専用",
        summary="登録・更新・削除・データ入出力は制限されています。",
        text_color="#d7fbe8",
        background_color="#163326",
        border_color="#4ade80",
    ),
    "editor": RoleVisualIdentity(
        role="editor",
        label="EDITOR / 編集可",
        summary="通常登録・更新・共有用出力・バックアップが可能です。管理/復元系操作は制限されています。",
        text_color="#dbeafe",
        background_color="#172554",
        border_color="#60a5fa",
    ),
    "admin": RoleVisualIdentity(
        role="admin",
        label="ADMIN / 管理者",
        summary="ユーザー管理・Import/Restoreなどの管理操作が可能です。実行前にバックアップを確認してください。",
        text_color="#fff7ed",
        background_color="#431407",
        border_color="#fb923c",
    ),
}


def role_visual_identity(role_context: RoleContext) -> RoleVisualIdentity:
    """Return the visual identity for a role context."""

    return _ROLE_VISUALS[role_context.role]


def role_banner_text(role_context: RoleContext) -> str:
    """Return a concise role banner text."""

    visual = role_visual_identity(role_context)
    return f"{visual.label} - {role_context.operator_id} - {visual.summary}"


def make_role_banner(role_context: RoleContext) -> QLabel:
    """Create a role-specific banner shown outside the status bar."""

    visual = role_visual_identity(role_context)
    label = QLabel(role_banner_text(role_context))
    label.setObjectName("roleVisualBanner")
    label.setProperty("operatorRole", role_context.role)
    label.setWordWrap(True)
    label.setToolTip(
        "現在の権限と主な操作制限です。権限により表示/実行できる操作が変わります。"
    )
    label.setStyleSheet(_label_style(visual, padding="6px 10px", radius="7px"))
    return label


def apply_role_status_style(label: QLabel, role_context: RoleContext) -> None:
    """Apply role-specific styling to a status label."""

    visual = role_visual_identity(role_context)
    label.setProperty("operatorRole", role_context.role)
    label.setStyleSheet(_label_style(visual, padding="2px 8px", radius="4px"))


def _label_style(
    visual: RoleVisualIdentity,
    *,
    padding: str,
    radius: str,
) -> str:
    return (
        "QLabel {"
        f"color: {visual.text_color};"
        f"background-color: {visual.background_color};"
        f"border: 1px solid {visual.border_color};"
        f"border-radius: {radius};"
        f"padding: {padding};"
        "font-weight: 700;"
        "}"
    )
