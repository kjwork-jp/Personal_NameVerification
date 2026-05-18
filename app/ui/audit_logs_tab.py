"""Unified audit log tab."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from app.application.query_services import QueryService
from app.application.user_audit_services import UserAuditLogService
from app.ui.audit_log_tab import AuditLogTab
from app.ui.role_context import RoleContext
from app.ui.ui_style import PageHeader, compact_layout
from app.ui.user_audit_log_tab import UserAuditLogTab


class AuditLogsTab(QWidget):
    """Top-level audit container that groups business and user/auth logs."""

    def __init__(
        self,
        query_service: QueryService,
        role_context: RoleContext,
        user_audit_service: UserAuditLogService | None = None,
    ) -> None:
        super().__init__()
        self.data_change_tab = AuditLogTab(
            query_service=query_service,
            role_context=role_context,
        )
        self.user_audit_tab: UserAuditLogTab | None = None

        self.tabs = QTabWidget()
        self.tabs.setObjectName("auditLogSubTabs")
        self.tabs.addTab(self.data_change_tab, "データ変更ログ")
        if user_audit_service is not None:
            self.user_audit_tab = UserAuditLogTab(
                user_audit_service=user_audit_service,
                role_context=role_context,
            )
            self.tabs.addTab(self.user_audit_tab, "ユーザー/認証ログ")
        self.tabs.addTab(_build_guide_page(), "ガイド")

        root = QVBoxLayout(self)
        compact_layout(root, margins=5, spacing=4)
        root.addWidget(
            PageHeader(
                "監査ログ",
                "データ変更ログとユーザー/認証ログを用途別に確認します。",
            )
        )
        root.addWidget(self.tabs, 1)

    def refresh(self) -> None:
        """Refresh the currently visible audit subtab."""

        widget = self.tabs.currentWidget()
        if widget is None:
            return
        for method_name in ("refresh", "_reload"):
            method = getattr(widget, method_name, None)
            if callable(method):
                method()
                return


def _build_guide_page() -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    compact_layout(layout, margins=8, spacing=6)
    text = QLabel(
        "データ変更ログ: 名前・タイトル・サブタイトル・関連付けなど、"
        "業務データの変更履歴です。\n"
        "ユーザー/認証ログ: ログイン成功/失敗、ユーザー作成、権限変更などの"
        "認証・ユーザー管理履歴です。\n"
        "入出力/起動ログ: データ入出力タブのOperations Logで確認します。"
    )
    text.setWordWrap(True)
    layout.addWidget(text)
    layout.addStretch(1)
    return page
