"""Duplicate input precheck extension for title/subtitle management UI."""

from __future__ import annotations

from typing import Any

from app.domain.normalization import normalize_with_raw

_PATCHED_ATTR = "_title_subtitle_duplicate_precheck_installed"


def install_title_subtitle_duplicate_precheck() -> None:
    """Install duplicate-input prechecks on TitleSubtitleManagementTab once."""
    from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab

    target: Any = TitleSubtitleManagementTab
    if getattr(target, _PATCHED_ATTR, False):
        return

    original_create_title = target._create_title
    original_update_title = target._update_title
    original_create_subtitle = target._create_subtitle
    original_update_subtitle = target._update_subtitle

    def create_title_with_duplicate_precheck(self: Any) -> None:
        message = _title_duplicate_message(self, self.add_title_name_input.text())
        if message is not None:
            _set_duplicate_message(self, message)
            return
        original_create_title(self)

    def update_title_with_duplicate_precheck(self: Any) -> None:
        selected = getattr(self, "_selected_title", None)
        if selected is not None and not getattr(selected, "deleted", False):
            message = _title_duplicate_message(
                self,
                self.title_name_input.text(),
                excluding_title_id=int(selected.id),
            )
            if message is not None:
                _set_duplicate_message(self, message)
                return
        original_update_title(self)

    def create_subtitle_with_duplicate_precheck(self: Any) -> None:
        title_id = _subtitle_create_title_id(self)
        if title_id is not None:
            message = _subtitle_duplicate_message(
                self,
                title_id=title_id,
                subtitle_code=self.add_subtitle_code_input.text(),
                subtitle_name=self.add_subtitle_name_input.text(),
            )
            if message is not None:
                _set_duplicate_message(self, message)
                return
        original_create_subtitle(self)

    def update_subtitle_with_duplicate_precheck(self: Any) -> None:
        selected_title = getattr(self, "_selected_title", None)
        selected_subtitle = getattr(self, "_selected_subtitle", None)
        if (
            selected_title is not None
            and selected_subtitle is not None
            and not getattr(selected_title, "deleted", False)
            and not getattr(selected_subtitle, "deleted", False)
        ):
            message = _subtitle_duplicate_message(
                self,
                title_id=int(selected_title.id),
                subtitle_code=self.subtitle_code_input.text(),
                subtitle_name=self.subtitle_name_input.text(),
                excluding_subtitle_id=int(selected_subtitle.id),
            )
            if message is not None:
                _set_duplicate_message(self, message)
                return
        original_update_subtitle(self)

    target._create_title = create_title_with_duplicate_precheck
    target._update_title = update_title_with_duplicate_precheck
    target._create_subtitle = create_subtitle_with_duplicate_precheck
    target._update_subtitle = update_subtitle_with_duplicate_precheck
    setattr(target, _PATCHED_ATTR, True)


def _title_duplicate_message(
    tab: Any,
    candidate_title_name: str | None,
    *,
    excluding_title_id: int | None = None,
) -> str | None:
    candidate_key = _comparison_key(candidate_title_name)
    if candidate_key is None:
        return None

    for title in getattr(tab, "_titles", []):
        if title.deleted_at is not None:
            continue
        if excluding_title_id is not None and int(title.id) == excluding_title_id:
            continue
        if _comparison_key(title.title_name) == candidate_key:
            return f"有効なタイトル『{title.title_name}』と同じタイトル名です。"
    return None


def _subtitle_duplicate_message(
    tab: Any,
    *,
    title_id: int,
    subtitle_code: str | None,
    subtitle_name: str | None,
    excluding_subtitle_id: int | None = None,
) -> str | None:
    candidate_code_key = _comparison_key(subtitle_code)
    candidate_name_key = _comparison_key(subtitle_name)
    if candidate_code_key is None and candidate_name_key is None:
        return None

    subtitles = _subtitles_for_title(tab, title_id)
    for subtitle in subtitles:
        if subtitle.deleted_at is not None:
            continue
        if excluding_subtitle_id is not None and int(subtitle.id) == excluding_subtitle_id:
            continue
        if candidate_code_key is not None and _comparison_key(subtitle.subtitle_code) == candidate_code_key:
            return f"同じタイトル配下に有効な管理番号『{subtitle.subtitle_code}』があります。"
        if candidate_name_key is not None and _comparison_key(subtitle.subtitle_name) == candidate_name_key:
            return f"同じタイトル配下に有効なサブタイトル名『{subtitle.subtitle_name}』があります。"
    return None


def _subtitle_create_title_id(tab: Any) -> int | None:
    if tab.workflow_tabs.currentWidget() is tab.add_tab:
        title_id = tab.add_subtitle_title_combo.currentData()
        return int(title_id) if title_id is not None else None
    selected_title = getattr(tab, "_selected_title", None)
    return int(selected_title.id) if selected_title is not None else None


def _subtitles_for_title(tab: Any, title_id: int) -> list[Any]:
    selected_title = getattr(tab, "_selected_title", None)
    if selected_title is not None and int(selected_title.id) == title_id:
        return list(getattr(tab, "_subtitles", []))
    try:
        from app.ui.title_subtitle_management_tab import _call_with_optional_role

        return list(
            _call_with_optional_role(
                tab._query_service.list_subtitles,
                title_id,
                role=tab._role_context.role,
                include_deleted=True,
            )
        )
    except Exception:  # noqa: BLE001
        return []


def _comparison_key(value: str | None) -> str | None:
    return normalize_with_raw(value).normalized_text


def _set_duplicate_message(tab: Any, detail: str) -> None:
    tab._set_message(f"登録前に重複を検出しました: {detail}", is_error=True)
