"""Reference coverage for #179 duplicate display-name cleanup policy."""

from __future__ import annotations

from pathlib import Path


def test_cleanup_policy_document_exists_and_references_preflight() -> None:
    policy_path = Path("docs/operations/title-subtitle-display-name-cleanup-policy.md")

    policy_text = policy_path.read_text(encoding="utf-8")

    assert "inspect_duplicate_display_names()" in policy_text
    assert "has_blockers == False" in policy_text
    assert "blocker_count == 0" in policy_text
    assert "Tests: `tests/test_duplicate_display_name_preflight.py`" in policy_text
