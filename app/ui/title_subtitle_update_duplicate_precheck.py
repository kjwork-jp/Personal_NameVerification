"""Strict duplicate precheck for subtitle updates."""

from __future__ import annotations

from typing import Any

from app.domain.normalization import normalize_with_raw

_PATCHED_ATTR = "_title_subtitle_update_duplicate_precheck_installed"


def install_title_subtitle_update_duplicate_precheck() -> None:
    from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab

    target: Any = TitleSubtitleManagementTab
    if getattr(target, _PATCHED_ATTR, False):
        return

    original_update_subtitle = target._update_subtitle

    def update_subtitle_with_strict_duplicate_precheck(self: Any) -> None:
        title_id = _selected_title_id(self)
        subtitle_id = _selected_subtitle_id(self)
        if title_id is not None and subtitle_id is not None:
            message = _duplicate_message(
                self,
                title_id=title_id,
                subtitle_id=subtitle_id,
                candidate_code=self.subtitle_code_input.text(),
                candidate_name=self.subtitle_name_input.text(),
            )
            if message is not None:
                self._set_message(f"登録前に重複を検出しました: {message}", is_error=True)
                return
        original_update_subtitle(self)

    target._update_subtitle = update_subtitle_with_strict_duplicate_precheck
    setattr(target, _PATCHED_ATTR, True)


def _selected_title_id(tab: Any) -> int | None:
    selected = getattr(tab, "_selected_title", None)
    return int(selected.id) if selected is not None else None


def _selected_subtitle_id(tab: Any) -> int | None:
    selected = getattr(tab, "_selected_subtitle", None)
    return int(selected.id) if selected is not None else None


def _duplicate_message(
    tab: Any,
    *,
    title_id: int,
    subtitle_id: int,
    candidate_code: str | None,
    candidate_name: str | None,
) -> str | None:
    candidate_code_key = _key(candidate_code)
    candidate_name_key = _key(candidate_name)
    for subtitle in _list_subtitles(tab, title_id):
        if int(subtitle.id) == subtitle_id or subtitle.deleted_at is not None:
            continue
        if candidate_code_key is not None and _key(subtitle.subtitle_code) == candidate_code_key:
            return f"同じタイトル配下に有効な管理番号『{subtitle.subtitle_code}』があります。"
        if candidate_name_key is not None and _key(subtitle.subtitle_name) == candidate_name_key:
            return f"同じタイトル配下に有効なサブタイトル名『{subtitle.subtitle_name}』があります。"
    return None


def _list_subtitles(tab: Any, title_id: int) -> list[Any]:
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
        return list(getattr(tab, "_subtitles", []))


def _key(value: str | None) -> str | None:
    return normalize_with_raw(value).normalized_text
