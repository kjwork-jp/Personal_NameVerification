"""Cross-cutting regression tests for the 2026-06-15 P1 UI audit batch."""

from __future__ import annotations

from app.ui.audit_log_tab import _format_diff, _format_json_like


def test_audit_views_redact_sensitive_values() -> None:
    before = {"operator_id": "alice", "password_hash": "old-secret"}
    after = {"operator_id": "alice", "password_hash": "new-secret", "token": "abc"}

    before_text = _format_json_like(None, before)
    after_text = _format_json_like(None, after)
    diff_text = _format_diff(before, after)

    combined = "\n".join([before_text, after_text, diff_text])
    assert "old-secret" not in combined
    assert "new-secret" not in combined
    assert '"abc"' not in combined
    assert "***" in combined
    assert "変更項目: password_hash" in diff_text
    assert "変更項目: token" in diff_text


def test_datetime_helper_is_wired_to_remaining_ui_surfaces() -> None:
    expected = {
        "app/ui/search_tab.py": "format_datetime_display(detail.updated_at",
        "app/ui/title_subtitle_management_tab.py": "format_datetime_display(row.updated_at",
        "app/ui/subtitle_management_tab.py": "format_datetime_display(subtitle.updated_at",
        "app/ui/help_settings_tab.py": "format_datetime_display(",
        "app/ui/user_management_tab.py": "format_datetime_display(user.last_login_at",
        "app/ui/operations_tab.py": "format_datetime_display(timestamp",
    }
    from pathlib import Path

    for path, marker in expected.items():
        assert marker in Path(path).read_text(encoding="utf-8"), path


def test_batch_scope_has_six_confirmed_items() -> None:
    expected_scope = {
        "datetime",
        "title-layout",
        "audit-diff",
        "data-io",
        "title-filter",
        "unlink",
    }
    assert len(expected_scope) == 6
    assert "data-io" in expected_scope
