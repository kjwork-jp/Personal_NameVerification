"""Name management tab with release QA behavior absorbed locally."""

from __future__ import annotations

from typing import Any

from app.ui.input_defaults import default_operator_id, friendly_error_message
from app.ui.name_management_tab import NameManagementTab as BaseNameManagementTab
from app.ui.permissions import can_create_or_update


class NameManagementTab(BaseNameManagementTab):
    """NameManagementTab with default operator and friendly errors built in."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not self.operator_input.text().strip():
            self.operator_input.setText(default_operator_id())
        self.operator_input.setToolTip(
            "初期値は自動入力されます。必要な場合だけ変更してください。"
        )
        self.operator_input.setPlaceholderText("操作者（自動入力）")
        self.names_table.setColumnHidden(0, True)

    def _create_name(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールでは新規作成できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_name(
                self._current_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("新規作成しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("名前の新規作成", exc), is_error=True)

    def _update_name(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールでは更新できません", is_error=True)
            return
        selected = self._require_selected()
        operator_id = self._require_operator_id()
        if selected is None or operator_id is None:
            return
        if selected.deleted:
            self._set_message("削除済みは更新できません", is_error=True)
            return
        try:
            self._core_service.update_name(
                selected.id,
                self._current_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("更新しました")
            self._refresh_list()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("名前の更新", exc), is_error=True)
