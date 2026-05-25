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


@dataclass(frozen=True)
class RoleCapabilitySummary:
    role: UserRole
    allowed: tuple[str, ...]
    restricted: tuple[str, ...]
    caution: str


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

_ROLE_CAPABILITIES: dict[UserRole, RoleCapabilitySummary] = {
    "viewer": RoleCapabilitySummary(
        role="viewer",
        allowed=("検索・参照", "一覧確認", "関連明細確認"),
        restricted=("登録", "更新", "削除", "export", "backup", "restore", "import"),
        caution="参照専用です。ファイルをOSから直接読める場合はアプリ内RBACの対象外です。",
    ),
    "editor": RoleCapabilitySummary(
        role="editor",
        allowed=("通常登録", "通常更新", "共有用JSON出力", "CSV/JSON/SQL出力", "backup"),
        restricted=("関連解除", "削除", "復元", "完全削除", "restore", "import", "ユーザー管理"),
        caution="通常運用向けです。export/backupの保存先アクセス権を確認してください。",
    ),
    "admin": RoleCapabilitySummary(
        role="admin",
        allowed=("全参照", "通常登録・更新", "削除/復元/完全削除", "restore/import", "ユーザー管理"),
        restricted=(),
        caution="destructive操作前にbackupとOperations Logの確認手順を固定してください。",
    ),
}


def role_visual_identity(role_context: RoleContext) -> RoleVisualIdentity:
    """Return the visual identity for a role context."""

    return _ROLE_VISUALS[role_context.role]


def role_capability_summary(role_context: RoleContext) -> RoleCapabilitySummary:
    """Return structured capability text for dashboard/help surfaces."""

    return _ROLE_CAPABILITIES[role_context.role]


def role_banner_text(role_context: RoleContext) -> str:
    """Return a concise role banner text."""

    visual = role_visual_identity(role_context)
    capability = role_capability_summary(role_context)
    allowed = " / ".join(capability.allowed[:3])
    restricted = " / ".join(capability.restricted[:3]) or "なし"
    return (
        f"{visual.label} - {role_context.operator_id} - {visual.summary} "
        f"許可: {allowed} / 制限: {restricted}"
    )


def make_role_banner(role_context: RoleContext) -> QLabel:
    """Create a role-specific banner shown outside the status bar."""

    visual = role_visual_identity(role_context)
    capability = role_capability_summary(role_context)
    label = QLabel(role_banner_text(role_context))
    label.setObjectName("roleVisualBanner")
    label.setProperty("operatorRole", role_context.role)
    label.setProperty("allowedActions", " | ".join(capability.allowed))
    label.setProperty("restrictedActions", " | ".join(capability.restricted))
    label.setWordWrap(True)
    label.setToolTip(
        "現在の権限と主な操作制限です。権限により表示/実行できる操作が変わります。\n"
        f"注意: {capability.caution}"
    )
    label.setStyleSheet(_label_style(visual, padding="6px 10px", radius="7px"))
    return label


def apply_role_status_style(label: QLabel, role_context: RoleContext) -> None:
    """Apply role-specific styling to a status label."""

    visual = role_visual_identity(role_context)
    capability = role_capability_summary(role_context)
    label.setProperty("operatorRole", role_context.role)
    label.setProperty("roleCaution", capability.caution)
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
