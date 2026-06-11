# Title/Subtitle Display-name Index Readiness Gate

## Purpose

This document defines the final readiness gate before adding database indexes for
active title and subtitle display names.

The cleanup policy is already documented in
`docs/operations/title-subtitle-display-name-cleanup-policy.md`. This document
turns that policy into implementation acceptance criteria for the schema change.

## Required readiness check

Before title/subtitle display-name indexes are created, the application must run
`inspect_duplicate_display_names()` against the target database.

The schema change is ready only when all of these are true:

- `report.has_blockers is False`
- `report.blocker_count == 0`
- `report.title_duplicates == ()`
- `report.subtitle_duplicates == ()`

When the report contains any duplicate group, the schema change must stop before
writing index changes. The output should include only safe metadata:

- entity type
- normalized key
- title id for subtitle groups
- row ids
- current display names

## Implemented index shape

The schema uses active-row partial expression indexes. The expression calls the
SQLite deterministic function `app_normalize()`, which is registered by
`app.infrastructure.db.register_sqlite_functions()` and follows the repository's
normalization rules.

Index names:

- `uq_titles_active_display_name`
- `uq_subtitles_active_title_display_name`

A raw `title_name` / `subtitle_name` index is not sufficient because the
application duplicate policy compares normalized display names, including NFKC,
casefolding, control-character cleaning, and whitespace collapsing.

## Restore compatibility

Restore flows must keep checking duplicate conflicts before making deleted rows
active again. Deleted rows are not initial readiness blockers, but restoring one
can create an active conflict.

## Acceptance criteria

- The exact index names are documented.
- The readiness check calls `inspect_duplicate_display_names()`.
- Index creation is allowed only for no-blocker reports.
- The readiness check returns safe blocker metadata for duplicate reports.
- Tests cover both no-blocker and duplicate-report states.
- Existing restore-conflict behavior remains intact.
