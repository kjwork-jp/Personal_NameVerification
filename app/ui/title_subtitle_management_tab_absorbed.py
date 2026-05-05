"""Title/subtitle tab with release QA behavior absorbed locally."""

from __future__ import annotations

from typing import Any

from app.application.core_services import SubtitleInput
from app.ui.input_defaults import default_operator_id, friendly_error_message, generate_subtitle_code
from app.ui.permissions import can_create_or_update
from app.ui.title_subtitle_management_tab import (
    TitleSubtitleManagementTab as BaseTitleSubtitleManagementTab,
)


class TitleSubtitleManagementTab(BaseTitleSubtitleManagementTab):
    """TitleSubtitleManagementTab with default input behavior built in."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not self.operator_input.text().strip():
            self.operator_input.setText(default_operator_id())
        self.operator_input.setToolTip(
            "初期値は自動入力されます。必要な場合だけ変更してください。"
        )
        self.operator_input.setPlaceholderText("操作者（自動入力）")
        self.subtitle_code_input.setPlaceholderText("未入力なら自動生成")
        self.titles_table.setColumnHidden(0, True)
        self.subtitles_table.setColumnHidden(0, True)

    def _create_title(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではタイトル作成できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_title(
                self._title_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
                name_ids=self._selected_name_ids_for_create(),
            )
            self._set_message("タイトル作成しました")
            self._refresh_titles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("タイトル作成", exc), is_error=True)

    def _update_title(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではタイトル更新できません", is_error=True)
            return
        selected = self._require_selected_title()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("削除済みタイトルは更新できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.update_title(
                selected.id,
                self._title_payload(),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("タイトル更新しました")
            self._refresh_titles(selected.id)
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("タイトル更新", exc), is_error=True)

    def _create_subtitle(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではサブタイトル作成できません", is_error=True)
            return
        selected = self._require_selected_title()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("削除済みタイトルにはサブタイトル作成できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.create_subtitle(
                self._subtitle_payload(selected.id),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("サブタイトル作成しました")
            self._refresh_subtitles()
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("サブタイトル作成", exc), is_error=True)

    def _subtitle_payload(self, title_id: int) -> SubtitleInput:
        sort_order_text = self.subtitle_sort_order_input.text().strip() or "0"
        subtitle_code = self.subtitle_code_input.text().strip() or generate_subtitle_code()
        self.subtitle_code_input.setText(subtitle_code)
        return SubtitleInput(
            title_id=title_id,
            subtitle_code=subtitle_code,
            subtitle_name=self.subtitle_name_input.text(),
            sort_order=int(sort_order_text),
            note=self.subtitle_note_input.text() or None,
        )
