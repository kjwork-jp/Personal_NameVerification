"""Title/Subtitle management tab UI.

This module keeps the public import path stable while the large legacy editor is
being absorbed into the owning UI module.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QListWidgetItem

from app.application.core_services import SubtitleInput
from app.application.read_models import TitleDetail
from app.ui.dialogs import confirm_destructive_action
from app.ui.input_defaults import (
    default_operator_id,
    friendly_error_message,
    generate_subtitle_code,
)
from app.ui.old.title_subtitle_management_tab import (
    TitleSubtitleManagementTab as _BaseTitleSubtitleManagementTab,
)
from app.ui.old.title_subtitle_management_tab import (
    TitleSubtitleReadService,
    TitleSubtitleWriteService,
    _SubtitleSelection,
    _TitleSelection,
    _call_with_optional_role,
)
from app.ui.permissions import can_create_or_update, can_run_destructive_actions
from app.ui.public_id_display import short_public_id


class TitleSubtitleManagementTab(_BaseTitleSubtitleManagementTab):
    """Title/subtitle editor with release QA behavior absorbed locally."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not self.operator_input.text().strip():
            self.operator_input.setText(default_operator_id())
        self.operator_input.setPlaceholderText("操作者（自動入力）")
        self.operator_input.setToolTip(
            "初期値は自動入力されます。必要な場合だけ変更してください。"
        )
        self.subtitle_code_input.setPlaceholderText("未入力なら自動生成")
        self.titles_table.setColumnHidden(0, True)
        self.subtitles_table.setColumnHidden(0, True)
        self._update_action_states()

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

    def _update_subtitle(self) -> None:
        if not can_create_or_update(self._role_context.role):
            self._set_message("このロールではサブタイトル更新できません", is_error=True)
            return
        selected_title = self._require_selected_title()
        if selected_title is None:
            return
        if selected_title.deleted:
            self._set_message("削除済みタイトルのサブタイトルは更新できません", is_error=True)
            return
        selected_subtitle = self._require_selected_subtitle()
        if selected_subtitle is None:
            return
        if selected_subtitle.deleted:
            self._set_message("削除済みサブタイトルは更新できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        try:
            self._core_service.update_subtitle(
                selected_subtitle.id,
                self._subtitle_payload(selected_title.id),
                operator_id=operator_id,
                role=self._role_context.role,
            )
            self._set_message("サブタイトル更新しました")
            self._refresh_subtitles(selected_subtitle.id)
        except Exception as exc:  # noqa: BLE001
            self._set_message(friendly_error_message("サブタイトル更新", exc), is_error=True)

    def _delete_title(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではタイトル論理削除できません", is_error=True)
            return
        selected = self._require_selected_title()
        if selected is None:
            return
        if selected.deleted:
            self._set_message("既に削除済みタイトルです", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if not confirm_destructive_action(
            self,
            "論理削除の確認",
            f"タイトルID={selected.id} を論理削除します。よろしいですか？",
        ):
            self._set_message("タイトル論理削除をキャンセルしました")
            return
        self._core_service.delete_title(selected.id, operator_id=operator_id, role=self._role_context.role)
        self._set_message("タイトル論理削除しました")
        self._refresh_titles(selected.id)

    def _restore_title(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではタイトル復元できません", is_error=True)
            return
        selected = self._require_selected_title()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("有効タイトルは復元できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if not confirm_destructive_action(
            self,
            "復元の確認",
            f"タイトルID={selected.id} を復元します。よろしいですか？",
        ):
            self._set_message("タイトル復元をキャンセルしました")
            return
        self._core_service.restore_title(selected.id, operator_id=operator_id, role=self._role_context.role)
        self._set_message("タイトル復元しました")
        self._refresh_titles(selected.id)

    def _hard_delete_title(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではタイトル完全削除できません", is_error=True)
            return
        selected = self._require_selected_title()
        if selected is None:
            return
        if not selected.deleted:
            self._set_message("完全削除は削除済みタイトルのみ可能です", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if not confirm_destructive_action(
            self,
            "完全削除の確認",
            f"タイトルID={selected.id} を完全削除します。この操作は元に戻せません。",
        ):
            self._set_message("タイトル完全削除をキャンセルしました")
            return
        self._core_service.hard_delete_title(selected.id, operator_id=operator_id, role=self._role_context.role)
        self._set_message("タイトル完全削除しました")
        self._refresh_titles()

    def _delete_subtitle(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではサブタイトル論理削除できません", is_error=True)
            return
        selected_title = self._require_selected_title()
        selected_subtitle = self._require_selected_subtitle()
        if selected_title is None or selected_subtitle is None:
            return
        if selected_title.deleted:
            self._set_message("削除済みタイトル配下のサブタイトルは操作できません", is_error=True)
            return
        if selected_subtitle.deleted:
            self._set_message("既に削除済みサブタイトルです", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if not confirm_destructive_action(
            self,
            "論理削除の確認",
            f"サブタイトルID={selected_subtitle.id} を論理削除します。よろしいですか？",
        ):
            self._set_message("サブタイトル論理削除をキャンセルしました")
            return
        self._core_service.delete_subtitle(
            selected_subtitle.id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._selected_subtitle = type(selected_subtitle)(selected_subtitle.id, True)
        self._set_message("サブタイトル論理削除しました")
        self._update_action_states()

    def _restore_subtitle(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではサブタイトル復元できません", is_error=True)
            return
        selected_title = self._require_selected_title()
        selected_subtitle = self._require_selected_subtitle()
        if selected_title is None or selected_subtitle is None:
            return
        if selected_title.deleted:
            self._set_message("削除済みタイトル配下のサブタイトルは操作できません", is_error=True)
            return
        if not selected_subtitle.deleted:
            self._set_message("有効サブタイトルは復元できません", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if not confirm_destructive_action(
            self,
            "復元の確認",
            f"サブタイトルID={selected_subtitle.id} を復元します。よろしいですか？",
        ):
            self._set_message("サブタイトル復元をキャンセルしました")
            return
        self._core_service.restore_subtitle(
            selected_subtitle.id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._selected_subtitle = type(selected_subtitle)(selected_subtitle.id, True)
        self._set_message("サブタイトル復元しました")
        self._update_action_states()

    def _hard_delete_subtitle(self) -> None:
        if not can_run_destructive_actions(self._role_context.role):
            self._set_message("このロールではサブタイトル完全削除できません", is_error=True)
            return
        selected_title = self._require_selected_title()
        selected_subtitle = self._require_selected_subtitle()
        if selected_title is None or selected_subtitle is None:
            return
        if selected_title.deleted:
            self._set_message("削除済みタイトル配下のサブタイトルは操作できません", is_error=True)
            return
        if not selected_subtitle.deleted:
            self._set_message("完全削除は削除済みサブタイトルのみ可能です", is_error=True)
            return
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if not confirm_destructive_action(
            self,
            "完全削除の確認",
            f"サブタイトルID={selected_subtitle.id} を完全削除します。この操作は元に戻せません。",
        ):
            self._set_message("サブタイトル完全削除をキャンセルしました")
            return
        self._core_service.hard_delete_subtitle(
            selected_subtitle.id,
            operator_id=operator_id,
            role=self._role_context.role,
        )
        self._set_message("サブタイトル完全削除しました")
        self._refresh_subtitles()

    def _refresh_name_candidates(self) -> None:
        try:
            self._name_rows = _call_with_optional_role(
                self._query_service.search_names,
                include_deleted=False,
                role=self._role_context.role,
            )
        except Exception:  # noqa: BLE001
            self._name_rows = []

        self.title_link_names_list.clear()
        for row in self._name_rows:
            label = f"{row.raw_name} (公開ID={short_public_id(row.public_id)})"
            item = QListWidgetItem(label)
            item.setData(0x0100, row.id)
            item.setToolTip(f"内部ID={row.id} / 公開ID={row.public_id or '未採番'}")
            self.title_link_names_list.addItem(item)

    def _update_selected_title_label(self, title: TitleDetail | None = None) -> None:
        if title is None:
            self.selected_title_label.setText("選択中タイトル: 未選択")
            return
        status = "削除済み" if title.deleted_at else "有効"
        self.selected_title_label.setText(
            "選択中タイトル: "
            f"公開ID={short_public_id(title.public_id)} / "
            f"内部ID={title.id} / {title.title_name} ({status})"
        )

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

    def _update_action_states(self) -> None:
        can_write = can_create_or_update(self._role_context.role)
        can_destructive = can_run_destructive_actions(self._role_context.role)
        has_title = self._selected_title is not None
        title_deleted = bool(self._selected_title and self._selected_title.deleted)
        has_subtitle = self._selected_subtitle is not None
        subtitle_deleted = bool(self._selected_subtitle and self._selected_subtitle.deleted)

        self.title_create_button.setEnabled(can_write)
        self.title_update_button.setEnabled(can_write and has_title and not title_deleted)
        self.title_delete_button.setEnabled(can_destructive and has_title and not title_deleted)
        self.title_restore_button.setEnabled(can_destructive and has_title and title_deleted)
        self.title_hard_delete_button.setEnabled(can_destructive and has_title and title_deleted)
        self.subtitle_refresh_button.setEnabled(has_title)
        self.subtitle_create_button.setEnabled(can_write and has_title and not title_deleted)
        self.subtitle_update_button.setEnabled(
            can_write and has_title and has_subtitle and not title_deleted and not subtitle_deleted
        )
        self.subtitle_delete_button.setEnabled(
            can_destructive
            and has_title
            and has_subtitle
            and not title_deleted
            and not subtitle_deleted
        )
        self.subtitle_restore_button.setEnabled(
            can_destructive and has_title and has_subtitle and not title_deleted and subtitle_deleted
        )
        self.subtitle_hard_delete_button.setEnabled(
            can_destructive and has_title and has_subtitle and not title_deleted and subtitle_deleted
        )

        if not has_title:
            self.subtitle_hint_label.setText("タイトルを選択してください")
        elif title_deleted:
            self.subtitle_hint_label.setText(
                "削除済みタイトルが選択されています（サブタイトル操作は無効）"
            )
        else:
            self.subtitle_hint_label.setText("選択中タイトル配下のサブタイトルを操作できます")
