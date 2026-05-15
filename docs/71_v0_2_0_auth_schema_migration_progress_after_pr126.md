# 71_v0_2_0_auth_schema_migration_progress_after_pr126.md

## 1. Purpose

This note records the repository progress after PR #126.

## 2. Completed

PR #126 completed PR-020-001 from `docs/70_v0_2_0_auth_user_management_implementation_plan.md`.

Completed scope:

- migration runner backed by `schema_migrations`
- `users` table
- `app_settings` table
- `user_audit_logs` table
- tests for migration application and existing data preservation

Changed files in PR #126:

- `app/infrastructure/db.py`
- `migrations/20260515_0001_auth_users_settings_audit.sql`
- `tests/test_db_initialization.py`

## 3. Next implementation step

Next step is PR-020-002: add the credential hashing service.

Scope for PR-020-002:

- hash generation
- verification
- rehash-needed check
- unit tests

Out of scope for PR-020-002:

- login UI changes
- user repository/service
- first-run admin setup UI
- user management tab
- DB encryption

## 4. Review result

- PR #126 is reflected in `main`.
- No open pull requests were found at the time this progress note was created.
- This file is documentation-only and does not change app behavior.
