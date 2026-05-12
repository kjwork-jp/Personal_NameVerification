# NameVerification v3

NameVerification v3 は、名前・タイトル・サブタイトル・関連付けをローカルで管理する **PySide6 / SQLite デスクトップアプリ**です。

このリポジトリはドキュメントだけではなく、SQLite schema、アプリケーションサービス、PySide6 UI、テスト、Windows EXE build 手順を含みます。

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

## Local login

起動時にローカルログイン画面で操作者とロールを選択します。

- これは外部認証ではありません。
- 操作者は `change_logs` と自動JSONLログへ記録するためのローカル識別子です。
- ロールは `viewer` / `editor` / `admin` を想定します。
- 操作者を固定したい場合は `NAMEVERIFICATION_OPERATOR_ID` を起動前に設定します。

```powershell
$env:NAMEVERIFICATION_OPERATOR_ID = "operator-local"
```

## Portable release layout

EXE配布版では、`NameVerification.exe` を以下のように配置すると、EXE直起動でもパッケージ配下の相対パスを既定値として使います。

```text
v0.1.0-rc2/
├─ 10_app/
│  └─ NameVerification.exe
├─ 30_prod_db/
└─ 40_logs/
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
| データ入出力 | CSV/JSON/SQL出力、バックアップ、Restore、Import、Operations JSONLログ確認を行う |
| ヘルプ/設定 | DB保存先、環境変数、操作者、自動JSONLログ、基本操作を確認する |

## Data operations

データ入出力タブでは以下を扱います。

| 区分 | 操作 | 権限目安 | 注意 |
|---|---|---|---|
| Export | CSV / JSON / SQL dump | editor / admin | 読み取り系 |
| Backup | SQLite DBバックアップ作成 | editor / admin | 運用前後に取得推奨 |
| Restore | バックアップからDB復元 | admin | destructive。対象DBを置換する |
| Import | CSV / JSON取込 | admin | destructive。事前バックアップ必須 |
| Operations log | データ入出力タブの実行ログ確認/出力 | admin中心 | `operations_events.jsonl` を参照 |

Restore / Import は destructive 操作です。実行前にバックアップを取得してください。

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

## Sample data generation

100万件級の生成物はリポジトリへ置かず、必要時にスクリプトで再生成します。

```powershell
python .\scripts\generate_sample_data.py --help
```

## Implemented layers

- `app/domain`: normalization rules and domain errors
- `app/application`: `CoreService` / `EnhancedQueryService` / read models / authorization helpers / automatic JSONL change log export
- `app/infrastructure`: SQLite schema application helpers
- `app/ui`: PySide6 UI tabs and role-based UI guards
- `db/`: schema and migration SQL
- `tests/`: unit + UI tests

## Operations handoff docs

- Day0/Day1 runbook + initial operations checklist: `docs/58_operations_handoff_runbook_and_day1_checklist.md`
- UAT plan: `docs/45_uat_plan.md`
- Go-Live checklist: `docs/54_go_live_checklist.md`
- Incident runbook: `docs/55_incident_response_runbook.md`

## Manuals

- 運用操作マニュアル（Excel）: `docs/manuals/NameVerification_運用操作マニュアル_機能説明.md`
- 運用手順書（詳細版）: `docs/manuals/NameVerification_運用手順書_詳細版.md`
- 初回教育用（簡易マニュアル）: `docs/manuals/NameVerification_初回教育用_簡易マニュアル.md`

## Notes

- このアプリはローカルSQLiteを使う単体運用前提です。
- 大量データ検証では、実データをリポジトリへ置かず生成スクリプトを使います。
- README/docs wording may be refined over time; functional behavior should be validated against code + tests.
