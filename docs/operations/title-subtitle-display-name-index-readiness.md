# Title/Subtitle Display-name Index Readiness Gate

## Purpose

This document defines the final readiness gate before adding database indexes for
active title and subtitle display names.

The cleanup policy is already documented in
`docs/operations/title-subtitle-display-name-cleanup-policy.md`. This document
turns that policy into implementation acceptance criteria for the next schema PR.

## Required readiness check

Before a schema change adds title/subtitle display-name indexes, the application
or migration task must run `inspect_duplicate_display_names()` against the target
database.

The schema change is ready only when all of these are true:

- `report.has_blockers is False`
- `report.blocker_count == 0`
- `report.title_duplicates == ()`
- `report.subtitle_duplicates == ()`

When the report contains any duplicate group, the schema change must stop before
writing schema changes. The output should include only safe metadata:

- entity type
- normalized key
- title id for subtitle groups
- row ids
- current display names

## Planned index shape

The schema PR should use active-row partial indexes.

Planned title index:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS uq_titles_active_display_name
ON titles(title_name)
WHERE deleted_at IS NULL;
```

Planned subtitle index:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS uq_subtitles_active_title_display_name
ON subtitles(title_id, subtitle_name)
WHERE deleted_at IS NULL;
```

The preflight remains the required safety check because the future index shape
uses SQLite's stored text values, while the application duplicate policy compares
normalized display names.

## Restore compatibility

Restore flows must keep checking duplicate conflicts before making deleted rows
active again. Deleted rows are not initial readiness blockers, but restoring one
can create an active conflict.

## Acceptance criteria for the schema PR

- The schema PR documents the exact index names.
- The schema PR includes a readiness check that calls `inspect_duplicate_display_names()`.
- The readiness check allows the schema update only for no-blocker reports.
- The readiness check returns safe blocker metadata for duplicate reports.
- Tests cover both no-blocker and duplicate-report states.
- The schema PR keeps existing restore-conflict behavior intact.
