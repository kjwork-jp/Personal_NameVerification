"""Selection stability hotfixes for go-live UI actions."""
from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QAbstractItemView

def _row(table: Any) -> int:
    value = table.currentRow()
    if value < 0 and table.selectionModel():
        rows = table.selectionModel().selectedRows()
        if rows:
            value = rows[0].row()
    return value

def apply() -> None:
    _link()
    _name()
    _trash()
    _title_subtitle()

def _link() -> None:
    from app.ui import link_management_tab as m
    old_all = m.LinkManagementTab._refresh_all
    old_links = m.LinkManagementTab._refresh_links
    def _refresh_all(self: Any) -> None:
        old_all(self)
        for table, callback in [
            (self.names_table, self._on_name_selected),
            (self.titles_table, self._on_title_selected),
            (self.subtitles_table, self._on_subtitle_selected),
            (self.links_table, self._on_link_selected),
        ]:
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            if table.rowCount() > 0:
                table.selectRow(0)
                callback()
    def _refresh_links(self: Any) -> None:
        old_links(self)
        if self.links_table.rowCount() > 0:
            self.links_table.selectRow(0)
            self._on_link_selected()
    def _selected_relation_type(self: Any) -> str | None:
        value = str(self.relation_type_combo.currentData())
        if not value:
            self._set_message("関係種別を選択してください", is_error=True)
            return None
        if value == "other":
            custom = self.custom_relation_type_input.text().strip()
            if not custom:
                self._set_message("カスタム関係種別を入力してください", is_error=True)
                return None
            return custom
        return value
    def _unlink_link(self: Any) -> None:
        operator_id = self._require_operator_id()
        if operator_id is None:
            return
        if self._selected_link is None and self.links_table.rowCount() > 0:
            self.links_table.selectRow(0)
            self._on_link_selected()
        if self._selected_link is None:
            self._set_message("解除するリンクを選択してください", is_error=True)
            return
        if not m.confirm_destructive_action(self, "リンク解除の確認", f"リンクID={self._selected_link.id} を解除します。よろしいですか？"):
            self._set_message("リンク解除をキャンセルしました")
            return
        self._core_service.unlink_name_from_subtitle(
            self._selected_link.id, operator_id=operator_id, role=self._role_context.role
        )
        self._set_message("リンク解除しました")
    m.LinkManagementTab._refresh_all = _refresh_all
    m.LinkManagementTab._refresh_links = _refresh_links
    m.LinkManagementTab._selected_relation_type = _selected_relation_type
    m.LinkManagementTab._unlink_link = _unlink_link

def _name() -> None:
    from app.ui import name_management_tab as m
    old_refresh = m.NameManagementTab._refresh_list
    def _refresh_list(self: Any) -> None:
        old_refresh(self)
        self.names_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        if self.names_table.rowCount() > 0:
            self.names_table.selectRow(0)
            self._on_row_selected()
    def _require_selected(self: Any) -> Any | None:
        if self._selected is None:
            row = _row(self.names_table)
            if 0 <= row < len(self._rows):
                rec = self._rows[row]
                self._selected = m._SelectedName(rec.id, rec.deleted_at is not None)
        if self._selected is None:
            self._set_message("行を選択してください", is_error=True)
        return self._selected
    m.NameManagementTab._refresh_list = _refresh_list
    m.NameManagementTab._require_selected = _require_selected

def _trash() -> None:
    from app.ui import trash_tab as m
    old_reload = m.TrashTab._reload
    old_init = m.TrashTab.__init__
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None:
        old_init(self, *args, **kwargs)
        existing = [self.entity_selector.itemText(i) for i in range(self.entity_selector.count())]
        for label in ["Name", "Title", "Subtitle", "Link"]:
            if label not in existing:
                self.entity_selector.addItem(label)
        self.list_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    def _entity_key(self: Any) -> str:
        return {
            "名前": "name", "Name": "name",
            "タイトル": "title", "Title": "title",
            "サブタイトル": "subtitle", "Subtitle": "subtitle",
            "リンク": "link", "Link": "link",
        }.get(self.entity_selector.currentText(), "name")
    def _reload(self: Any) -> None:
        old_reload(self)
        if self.list_table.rowCount() > 0:
            self.list_table.selectRow(0)
            self._on_selected()
    def _restore_selected(self: Any) -> None:
        op = self._require_operator_id()
        selection = self._require_deleted_selection()
        if op is None or selection is None:
            return
        if not m.confirm_destructive_action(self, "復元の確認", f"ID={selection.entity_id} を復元します。よろしいですか？"):
            return
        method = {"name": "restore_name", "title": "restore_title", "subtitle": "restore_subtitle", "link": "restore_link"}[self._entity_key()]
        getattr(self._core_service, method)(selection.entity_id, op, role=self._role_context.role)
        self._set_message("復元しました")
    def _hard_delete_selected(self: Any) -> None:
        op = self._require_operator_id()
        selection = self._require_deleted_selection()
        if op is None or selection is None:
            return
        if not m.confirm_destructive_action(self, "完全削除の確認", f"ID={selection.entity_id} を完全削除します。"):
            return
        method = {"name": "hard_delete_name", "title": "hard_delete_title", "subtitle": "hard_delete_subtitle", "link": "hard_delete_link"}[self._entity_key()]
        getattr(self._core_service, method)(selection.entity_id, op, role=self._role_context.role)
        self._set_message("完全削除しました")
    m.TrashTab.__init__ = __init__
    m.TrashTab._entity_key = _entity_key
    m.TrashTab._reload = _reload
    m.TrashTab._restore_selected = _restore_selected
    m.TrashTab._hard_delete_selected = _hard_delete_selected

def _title_subtitle() -> None:
    from app.ui import title_subtitle_management_tab as m
    from app.ui.permissions import can_create_or_update, can_run_destructive_actions
    def _title(self: Any) -> Any | None:
        row = _row(self.titles_table)
        if 0 <= row < len(self._titles):
            rec = self._titles[row]
            self._selected_title = m._TitleSelection(rec.id, rec.deleted_at is not None)
        return self._selected_title
    def _subtitle(self: Any) -> Any | None:
        row = _row(self.subtitles_table)
        if 0 <= row < len(self._subtitles):
            rec = self._subtitles[row]
            self._selected_subtitle = m._SubtitleSelection(rec.id, rec.deleted_at is not None)
        return self._selected_subtitle
    def _require_selected_title(self: Any) -> Any | None:
        item = _title(self)
        if item is None:
            self._set_message("タイトルを選択してください", is_error=True)
        return item
    def _require_selected_subtitle(self: Any) -> Any | None:
        item = _subtitle(self)
        if item is None:
            self._set_message("サブタイトルを選択してください", is_error=True)
        return item
    def _update_subtitle_action_state(self: Any) -> None:
        can_write = can_create_or_update(self._role_context.role)
        can_destroy = can_run_destructive_actions(self._role_context.role)
        title = _title(self)
        subtitle = _subtitle(self)
        if title is None:
            self.subtitle_hint_label.setText("タイトルを選択してください")
            for button in [self.subtitle_refresh_button, self.subtitle_create_button, self.subtitle_update_button, self.subtitle_delete_button, self.subtitle_restore_button, self.subtitle_hard_delete_button]:
                button.setEnabled(False)
            return
        if title.deleted:
            self.subtitle_hint_label.setText("削除済みタイトル配下のサブタイトルは操作できません")
            self.subtitle_refresh_button.setEnabled(True)
            for button in [self.subtitle_create_button, self.subtitle_update_button, self.subtitle_delete_button, self.subtitle_restore_button, self.subtitle_hard_delete_button]:
                button.setEnabled(False)
            return
        deleted = bool(subtitle and subtitle.deleted)
        has_subtitle = subtitle is not None
        self.subtitle_hint_label.setText("選択中タイトル配下のサブタイトルを操作できます")
        self.subtitle_refresh_button.setEnabled(True)
        self.subtitle_create_button.setEnabled(can_write)
        self.subtitle_update_button.setEnabled(can_write and has_subtitle and not deleted)
        self.subtitle_delete_button.setEnabled(can_destroy and has_subtitle and not deleted)
        self.subtitle_restore_button.setEnabled(can_destroy and has_subtitle and deleted)
        self.subtitle_hard_delete_button.setEnabled(can_destroy and has_subtitle and deleted)
    m.TitleSubtitleManagementTab._require_selected_title = _require_selected_title
    m.TitleSubtitleManagementTab._require_selected_subtitle = _require_selected_subtitle
    m.TitleSubtitleManagementTab._update_subtitle_action_state = _update_subtitle_action_state
