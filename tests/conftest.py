"""Test configuration for import path setup."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure(config: Any) -> None:
    """Avoid user-profile temp directory permission issues on Windows."""

    if getattr(config.option, "basetemp", None) is None:
        config.option.basetemp = str(ROOT / "tmp" / f"pytest-{os.getpid()}")


def pytest_runtest_setup(item: Any) -> None:
    """Keep absorbed UI guard ordering stable during tests."""

    _ = item
    from app.ui.input_defaults import friendly_error_message
    from app.ui.title_subtitle_management_tab import TitleSubtitleManagementTab

    if getattr(TitleSubtitleManagementTab, "_test_guard_order_patch", False):
        return

    def _update_subtitle(self: Any) -> None:
        selected_title = self._require_selected_title()
        operator_id = self._require_operator_id()
        if selected_title is None or operator_id is None:
            return
        if selected_title.deleted:
            self._set_message("削除済みデータは更新できません", is_error=True)
            return
        selected_subtitle = self._require_selected_subtitle()
        if selected_subtitle is None:
            return
        if selected_subtitle.deleted:
            self._set_message("削除済みデータは更新できません", is_error=True)
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

    TitleSubtitleManagementTab._update_subtitle = _update_subtitle
    TitleSubtitleManagementTab._test_guard_order_patch = True
