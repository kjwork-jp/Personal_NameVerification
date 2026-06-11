"""Reference coverage for the title/subtitle display-name index readiness gate."""

from __future__ import annotations

from pathlib import Path


def test_index_readiness_doc_links_preflight_and_cleanup_policy() -> None:
    doc = Path("docs/operations/title-subtitle-display-name-index-readiness.md")

    text = doc.read_text(encoding="utf-8")

    assert "inspect_duplicate_display_names()" in text
    assert "title-subtitle-display-name-cleanup-policy.md" in text
    assert "uq_titles_active_display_name" in text
    assert "uq_subtitles_active_title_display_name" in text
    assert "report.has_blockers is False" in text
    assert "report.blocker_count == 0" in text
