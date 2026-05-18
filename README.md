# NameVerification v3

NameVerification v3 は、名前・タイトル・サブタイトル・関連付けをローカルで管理する **PySide6 / SQLite デスクトップアプリ**です。

このリポジトリはドキュメントだけではなく、SQLite schema、migration、アプリケーションサービス、PySide6 UI、テスト、Windows EXE build / smoke test 手順を含みます。

## Runtime / stack

- Python 3.12+
- PySide6
- SQLite
- pytest / ruff / black / mypy
- PyInstaller

## Entry point

```bash
python -m app.pyside6_main
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.pyside6_main
```

## Local authentication

現在の main では、起動時にローカルDB上の `users` table を使ったアプリ内認証を行います。

- active user が0件の場合は、最初に `InitialAdminSetupDialog` で初回adminを作成します。
- 通常起動時は `LoginDialog` で `operator_id` と password を入力します。
- role は利用者が自由選択せず、DB上の `users.role` から `viewer` / `editor` / `admin` を取得します。
- MainWindow の title bar と status bar に `ログイン中: <operator_id> / 権限: <role>` を常時表示します。
- passwordは平文保存せず、PBKDF2-SHA256のhash/salt/iterationsとして保存します。
- login成功/失敗、user作成、role変更、無効化/有効化などは `user_audit_logs` へ記録します。
- これはローカル単体アプリ内の認証であり、SSO / OS認証 / AD連携ではありません。

## RBAC summary

| role | 参照 | 通常登録/更新 | 関連付け登録 | 関連解除 | 削除/復元/完全削除 | export/backup | import/restore | ユーザー管理 | ユーザー監査ログ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| viewer | 可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可/内容非表示 |
| editor | 可 | 可 | 可 | 不可 | 不可 | 可 | 不可 | 不可 | 不可/内容非表示 |
| admin | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 |

RBACの詳細と残作業は `docs/74_rbac_hardening_plan.md`、v0.2.0の横断状況は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` を参照してください。

## Portable release layout

EXE配布版では、`NameVerification.exe` を以下のように配置すると、EXE直起動でもパッケージ配下の相対パスを既定値として使います。

```text
v0.1.0-rc2/
├─ 10_app/
│  └─ NameVerification.exe
├─ 30_prod_db/
├─ 40_logs/
├─ 50_backups/
│  ├─ daily/
│  ├─ before_restore/
│  └─ before_import/
└─ 60_exports/
   ├─ csv/
   ├─ json/
   └─ sql/
```

この配置で `NAMEVERIFICATION_DB_PATH` を指定しない場合、DBは以下に作成されます。

```text
v0.1.0-rc2/30_prod_db/nameverification.db
```

この配置で `NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH` を指定しない場合、自動JSONLログは以下に出力されます。

```text
v0.1.0-rc2/40_logs/change_logs.jsonl
```

`NAMEVERIFICATION_PACKAGE_ROOT` を指定すると、EXE位置ではなくそのパスをパッケージルートとして扱います。

## Database path

保存先を明示的に固定したい場合は `NAMEVERIFICATION_DB_PATH` を起動前に設定します。
この環境変数は、portable release layout の既定値より優先されます。

```powershell
$env:NAMEVERIFICATION_DB_PATH = "C:\\path\\to\\nameverification.db"
python -m app.pyside6_main
```

ソース実行時に環境変数を指定しない場合は、従来どおりカレントディレクトリの `nameverification.db` を使用します。

## Database schema / migrations

起動時のDB初期化では、`db/schema.sql` 適用後に `migrations/*.sql` を filename order で適用します。
適用済みmigrationは `schema_migrations` table で管理します。

現在の認証・ユーザー管理系migrationは以下です。

```text
migrations/20260515_0001_auth_users_settings_audit.sql
```

このmigrationで主に以下を追加します。

- `users`
- `app_settings`
- `user_audit_logs`
- `schema_migrations`

EXE smoke test では、runtime DB内に上記auth系tableが作成されることも確認します。

## Automatic change log JSONL export

DB内の `change_logs` が正の操作履歴です。加えて、運用補助として変更履歴を JSONL へ自動出力します。

portable release layout では既定値として以下を使います。

```text
v0.1.0-rc2/40_logs/change_logs.jsonl
```

ソース実行時の既定値:

```text
logs/change_logs.jsonl
```

設定:

```powershell
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "logs/change_logs.jsonl"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_MAX_BYTES = "5242880"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_ENABLED = "1"
```

挙動:

- DB更新ごとに `timestamp / entity_type / entity_id / action / operator_id / before_json / after_json` をJSONLへ追記します。
- 出力先の親ディレクトリは自動作成します。
- ファイルサイズが上限を超えた場合、既存ログをタイムスタンプ付きファイルへローテーションします。
- JSONL出力に失敗してもDB更新は継続します。JSONLは監査補助であり、DBの `change_logs` が正です。

## Main window tabs

| タブ | 用途 |
|---|---|
| 検索 | 名前・タイトル・サブタイトルを横断検索し、関連数と関連明細を確認する |
| 名前を管理 | 名前の登録・更新、タイトル/サブタイトル関連数確認、ゴミ箱投入を行う |
| タイトルを管理 | タイトル登録・更新、登録時の名前1件関連付け、ゴミ箱投入を行う |
| サブタイトルを管理 | タイトルを選択し、管理番号・サブタイトル名・表示順を登録/更新する |
| 関連付け | 名前とサブタイトルの例外的な関連登録/解除を行う。関連種類は内部で `primary` 固定 |
| 削除データ | 名前・タイトル・サブタイトル・リンクの復元/完全削除を集約する |
| 操作履歴 | DB内 `change_logs` を検索し、変更前/変更後/差分を項目名付きで確認する |
| ユーザー管理 | admin専用でlocal userの作成、role変更、無効化/有効化を行う |
| ユーザー監査ログ | admin専用でlogin/user管理auditを確認する |
| データ入出力 | CSV/JSON/SQL出力、バックアップ、Restore、Import、Operations JSONLログ確認を行う |
| ヘルプ/設定 | DB保存先、環境変数、自動JSONLログ、基本操作を確認する |

## Current UI improvement status

| 区分 | 状態 |
|---|---|
| ユーザー管理 | `ガイド` / `ユーザー作成` / `ユーザー一覧` / `選択ユーザー操作` へサブタブ化済み |
| ログイン状態表示 | title bar / status bar に常時表示済み |
| viewer RBAC | 主要更新系UIを無効化済み |
| editor RBAC | 通常更新/export/backupは有効表示、destructive/import/restore/user管理は無効表示。実行UATは未完 |
| 今後のUI改善 | データ入出力、削除データ、通常CRUD系のサブタブ化を予定 |

## Data operations

データ入出力タブでは以下を扱います。

| 区分 | 操作 | 権限目安 | 注意 |
|---|---|---|---|
| Export | CSV / JSON / SQL dump | editor / admin | 読み取り系。viewerは不可 |
| Backup | SQLite DBバックアップ作成 | editor / admin | 運用前後に取得推奨。viewerは不可 |
| Restore | バックアップからDB復元 | admin | destructive。対象DBを置換する |
| Import | CSV / JSON取込 | admin | destructive。事前バックアップ必須 |
| Operations log | データ入出力タブの実行ログ確認/出力 | viewer/editor/adminで参照可。ログ出力はeditor/admin | `operations_events.jsonl` を参照 |

Restore / Import は destructive 操作です。実行前に自動で `50_backups/before_restore` または `50_backups/before_import` へ退避DBを作成します。
ただし、重要データ投入前後は明示的なbackup取得も推奨します。

portable release layout で起動した場合、データ入出力タブの初期値は配布フォルダ配下を優先します。

```text
v0.1.0-rc2/60_exports/csv/
v0.1.0-rc2/60_exports/json/nameverification_export_YYYYMMDD_HHMMSS.json
v0.1.0-rc2/60_exports/sql/nameverification_dump_YYYYMMDD_HHMMSS.sql
v0.1.0-rc2/50_backups/daily/nameverification_YYYYMMDD_HHMMSS.db
v0.1.0-rc2/30_prod_db/nameverification.db
```

ソース実行や非portable配置では、従来どおりユーザーホーム配下の
`tmp/NameVerification v3` を安全な既定フォルダとして使います。Restore用バックアップ
ファイルとJSON importファイルは誤操作を避けるため初期表示では空欄にします。

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

## Test / checks

```powershell
pytest -q
ruff check .
black --check .
mypy app
```

## Windows EXE build / smoke test

```powershell
.\scripts\build_exe_windows.ps1
.\scripts\smoke_test_exe_windows.ps1
```

成功時は以下が生成されます。

```text
dist/NameVerification.exe
tmp/exe_smoke/nameverification_smoke.db
```

Smoke DBでは、auth/user-management用の `users` / `user_audit_logs` / `app_settings` / `schema_migrations` table 作成も確認します。

## Sample data generation

100万件級の生成物はリポジトリへ置かず、必要時にスクリプトで再生成します。

```powershell
python .\scripts\generate_sample_data.py --help
```

## Implemented layers

- `app/domain`: normalization rules, public ID helpers, domain errors
- `app/application`: `CoreService` / `EnhancedQueryService` / `UserService` / `UserAuditLogService` / read models / authorization helpers / automatic JSONL change log export
- `app/infrastructure`: SQLite schema and migration application helpers
- `app/ui`: PySide6 UI tabs, first-run admin setup, password login, role-based UI guards, login context display
- `db/`: base schema SQL
- `migrations/`: repo-managed SQLite migrations
- `tests/`: unit + UI tests

## Operations handoff docs

- Day0/Day1 runbook + initial operations checklist: `docs/58_operations_handoff_runbook_and_day1_checklist.md`
- UAT plan: `docs/45_uat_plan.md`
- Go-Live checklist: `docs/54_go_live_checklist.md`
- Incident runbook: `docs/55_incident_response_runbook.md`
- v0.1.0-rc2 release evidence: `docs/59_release_evidence_v0_1_0_rc2.md`
- v0.2.0 auth/user management implementation plan: `docs/70_v0_2_0_auth_user_management_implementation_plan.md`
- v0.2.0 integrated UAT checklist: `docs/71_v0_2_0_auth_integrated_uat_checklist.md`
- v0.2.0 integrated UAT execution record: `docs/72_v0_2_0_auth_integrated_uat_execution_record.md`
- UI navigation redesign plan: `docs/73_ui_navigation_redesign_plan.md`
- RBAC hardening plan: `docs/74_rbac_hardening_plan.md`
- v0.2.0 current status and improvement ledger: `docs/75_v0_2_0_current_status_and_improvement_ledger.md`
- Open issues and constraints: `docs/97_open_issues_and_constraints.md`

## Manuals

- 運用操作マニュアル（Excel）: `docs/manuals/NameVerification_運用操作マニュアル_機能説明.md`
- 運用手順書（詳細版）: `docs/manuals/NameVerification_運用手順書_詳細版.md`
- 初回教育用（簡易マニュアル）: `docs/manuals/NameVerification_初回教育用_簡易マニュアル.md`

## Notes

- このアプリはローカルSQLiteを使う単体運用前提です。
- SQLite DB / backup / export / log は、OSユーザーが読める場所ではアプリを迂回して参照され得ます。
- 複数ユーザー運用・第三者配布・機微情報投入では、OS ACL / BitLocker / EFS / 配置先制限などの運用保護を併用してください。
- 大量データ検証では、実データをリポジトリへ置かず生成スクリプトを使います。
- README/docs wording may be refined over time; functional behavior should be validated against code + tests.
