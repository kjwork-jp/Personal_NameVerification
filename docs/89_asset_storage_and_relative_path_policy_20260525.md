# 89_asset_storage_and_relative_path_policy_20260525.md

## Purpose

This document defines the current policy for icon/image asset storage and relative path handling in NameVerification.

This is a design and operations ledger. It does not change application behavior by itself.

## Current position

NameVerification is a local SQLite desktop application. The database stores business records, links, users, settings, logs, and metadata. Icon/image paths may exist as metadata fields, but binary assets are not treated as first-class managed application objects yet.

## Asset policy

| Area | Policy |
|---|---|
| DB storage | Do not store large binary icon/image files directly in SQLite by default. |
| Path storage | Store asset references as paths or identifiers, not raw binary blobs. |
| Relative paths | Prefer paths relative to package root or an explicit asset root when assets are bundled. |
| Absolute paths | Accept only as local operator-specific references; do not assume portability. |
| Export | Treat asset paths as metadata only unless an explicit asset bundle export is implemented. |
| Import | Do not import or overwrite external asset files implicitly. |
| Backup | DB backup protects path metadata, not necessarily external asset files. |
| Sharing | Shared JSON/CSV must not imply that referenced image files are included. |

## Recommended portable layout candidate

```text
<package_root>/
├─ 10_app/
├─ 20_assets/
│  ├─ icons/
│  └─ images/
├─ 30_prod_db/
├─ 40_logs/
├─ 50_backups/
└─ 60_exports/
```

## Relative path rules

| Rule | Detail |
|---|---|
| package-root relative | `20_assets/icons/example.png` is portable with the package. |
| asset-root relative | `icons/example.png` may be portable if an asset root is configured. |
| absolute local | `C:\Users\...\example.png` is not portable and may leak local user names. |
| missing file | UI should degrade gracefully and keep text data usable. |
| export/import | Asset path values can be exported/imported as metadata, but files are separate. |

## Security and privacy concerns

- Absolute paths can reveal Windows usernames, folder structures, or customer/project naming.
- Image files can contain personal or copyrighted material.
- Shared JSON/CSV should be reviewed before external sharing.
- SQL dump is full DB dump and may include path metadata.

## Future implementation candidates

| ID | Candidate |
|---|---|
| V050-ASSET-002 | Add explicit asset root setting. |
| V050-ASSET-003 | Normalize stored paths to package-root-relative form where possible. |
| V050-ASSET-004 | Add missing asset diagnostics in Help / Settings. |
| V050-ASSET-005 | Add optional asset bundle export/import workflow. |
| V050-ASSET-006 | Add tests for absolute path sanitization in shared exports if asset fields become active. |

## Non-goals

- Do not add binary asset import/export in this task.
- Do not rewrite existing DB schema in this task.
- Do not commit sample image assets.
- Do not change UAT or release status.

## Operational guidance

If icon/image fields are used before full asset management is implemented:

1. Prefer package-root-relative paths.
2. Keep assets under `20_assets` when portability matters.
3. Confirm that backup/export expectations are clear: DB backup does not necessarily copy external files.
4. Review absolute paths before sharing CSV/JSON/SQL outputs.
5. Record missing-file behavior as a UI issue rather than blocking core text data operations.
