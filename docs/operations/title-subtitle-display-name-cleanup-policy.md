# Title/Subtitle Display-name Cleanup Policy

## Purpose

This policy defines the cleanup path required before adding database-level unique
indexes for title and subtitle display names.

The required gate is `inspect_duplicate_display_names()`. It is read-only and
must report blockers without changing user data.

## Target uniqueness

- Active titles must not share the same normalized display name.
- Active subtitles under the same title must not share the same normalized display name.
- Active means `deleted_at IS NULL`.
- Deleted rows stay outside the initial blocker scope.

## Migration gate

A future unique-index migration may proceed only when the preflight report has:

- `has_blockers == False`
- `blocker_count == 0`
- no title duplicate groups
- no subtitle duplicate groups

If any blocker exists, migration must stop and report the blocker type, IDs, and
display names. It must not perform cleanup automatically.

## Cleanup choices

For each active title duplicate group, the operator must explicitly choose one of
these safe outcomes:

- rename one or more titles until the display names are unique
- merge data into a chosen survivor, then make only the survivor active
- keep one active title and archive the others through an explicit UI action
- cancel cleanup and keep migration blocked

For each active subtitle duplicate group under the same title, the operator must
explicitly choose one of these safe outcomes:

- rename one or more subtitles under that title until the display names are unique
- merge data into a chosen survivor, then make only the survivor active
- keep one active subtitle and archive the others through an explicit UI action
- cancel cleanup and keep migration blocked

The app must not choose a survivor, rename records, merge records, or archive
records silently.

## Deleted-row and restore policy

Deleted rows are ignored by the initial unique-index preflight. Restore flows must
continue to check conflicts before making a deleted row active again. If restore
would create an active duplicate, the restore remains blocked until the operator
chooses a safe cleanup outcome.

## Operator workflow

1. Run `inspect_duplicate_display_names()`.
2. If there are no blockers, continue to the unique-index migration.
3. If blockers exist, show each group with entity type, normalized key, IDs, and
   display names.
4. Apply only operator-selected cleanup actions.
5. Re-run the preflight.
6. Continue migration only after there are no blockers.

## Acceptance criteria

- Preflight remains read-only.
- Cleanup is never automatic.
- Migration is blocked while any active title or per-title subtitle duplicate
  blocker exists.
- Deleted rows remain ignored by the initial preflight.
- Restore paths continue to guard deleted-to-active transitions.
- Tests cover both no-blocker and blocker preflight states before unique-index
  migration work starts.

## References

- Issue: #179
- Preflight: `app/application/duplicate_display_name_preflight.py`
- Tests: `tests/test_duplicate_display_name_preflight.py`
