# 70_v0_2_0_auth_user_management_implementation_plan.md

## 1. 目的

本書は、NameVerification v3 `v0.2.0` で実装する認証・ユーザー管理・管理設定の実装計画を定義する。

対象:

- パスワード認証
- role自由選択廃止
- 初回admin作成
- users / app_settings / user_audit_logs
- admin専用ユーザー管理タブ
- migration / 既存DB互換
- portable release smokeの更新

参照:

- `docs/66_security_user_management_gap_analysis.md`
- `docs/67_quality_attribute_gap_analysis.md`
- `docs/68_database_file_protection_policy.md`
- `docs/69_v0_2_0_design_completeness_review.md`

---

## 2. v0.2.0 MVPの結論

v0.2.0 MVPでは、DB暗号化本実装までは行わず、まず **アプリ認証とユーザー管理を成立させる**。

| 項目 | v0.2.0 MVPで実施 |
|---|---:|
| users table | 実施 |
| schema_migrations table | 実施 |
| app_settings table | 実施 |
| user_audit_logs table | 実施 |
| PBKDF2 password hash | 実施 |
| 初回admin setup | 実施 |
| login dialog password化 | 実施 |
| role自由選択廃止 | 実施 |
| admin専用ユーザー管理タブ | 実施 |
| 管理者最低1人保証 | 実施 |
| login/user管理audit | 実施 |
| DB/backup/export/log保護警告 | 実施 |
| SQLCipher本実装 | 見送り。PoC/backlog扱い |
| backup/export暗号化 | 見送り。警告と運用制約を先行 |

---

## 3. DB schema / migration設計

### 3.1 追加テーブル

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
    operator_id TEXT NOT NULL UNIQUE,
    display_name TEXT,
    role TEXT NOT NULL CHECK(role IN ('viewer', 'editor', 'admin')),
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    password_algorithm TEXT NOT NULL DEFAULT 'pbkdf2_sha256',
    password_iterations INTEGER NOT NULL,
    password_updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    disabled_at TEXT,
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    last_login_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_public_id
ON users(public_id)
WHERE public_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_operator_id
ON users(operator_id);

CREATE TABLE IF NOT EXISTS user_audit_logs (
    id INTEGER PRIMARY KEY,
    actor_operator_id TEXT NOT NULL,
    target_operator_id TEXT,
    action TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_audit_logs_actor
ON user_audit_logs(actor_operator_id, created_at);

CREATE INDEX IF NOT EXISTS idx_user_audit_logs_target
ON user_audit_logs(target_operator_id, created_at);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 migration方式

| 項目 | 方針 |
|---|---|
| migration管理 | `schema_migrations` tableで管理 |
| 既存schema適用 | 現行 `schema.sql` 適用後、追加migrationを順次適用 |
| v0.1.0 DB互換 | usersが無いDBを開いたらmigrationで追加 |
| users 0件 | 初回admin setup必須 |
| usersあり | 通常login dialogへ遷移 |
| rollback | v0.2.0 migration後のDBをv0.1.0で使うことは原則非推奨 |

### 3.3 migrationファイル案

```text
migrations/
└─ 20260515_0001_auth_users_settings_audit.sql
```

---

## 4. password hash方式

### 4.1 採用方式

v0.2.0 MVPでは、Python標準ライブラリのみで実装可能な `hashlib.pbkdf2_hmac` を採用する。

| 項目 | 方針 |
|---|---|
| algorithm | `pbkdf2_sha256` |
| salt | ユーザーごとに `secrets.token_bytes(16)` 以上 |
| iterations | 初期値 310000 以上。設定化はP1 |
| 保存形式 | algorithm / iterations / salt / hash を個別カラム保存 |
| password平文保存 | 禁止 |
| passwordログ出力 | 禁止 |

### 4.2 実装関数案

| 関数 | 役割 |
|---|---|
| `hash_password(password: str) -> PasswordHash` | salt生成、hash生成 |
| `verify_password(password: str, stored: PasswordHash) -> bool` | 入力password検証 |
| `needs_rehash(stored: PasswordHash) -> bool` | iterations等が古い場合の再hash判定 |

---

## 5. 認証フロー

### 5.1 初回起動

```text
DB open
↓
schema/migration適用
↓
active users件数確認
↓
0件なら InitialAdminSetupDialog
↓
admin作成
↓
LoginDialog
```

### 5.2 通常ログイン

```text
operator_id + password入力
↓
user存在確認
↓
disabled_at確認
↓
locked_until確認
↓
password verify
↓
成功: failed_login_count reset, last_login_at更新, RoleContext生成
失敗: failed_login_count加算, user_audit_logs記録
```

### 5.3 RoleContext変更

現行はUIでroleを選択している。v0.2.0では、roleはDB上のuser recordから取得する。

```python
RoleContext(
    role=user.role,
    operator_id=user.operator_id,
)
```

---

## 6. UI設計

### 6.1 InitialAdminSetupDialog

| 項目 | 入力/表示 | 必須 |
|---|---|---:|
| operator_id | text | 必須 |
| display_name | text | 任意 |
| password | password | 必須 |
| password confirmation | password | 必須 |
| 注意文 | 初期adminを作成する説明 | - |

validation:

- operator_idは空不可
- passwordは空不可
- password confirmation一致必須
- users active countが0件でない場合は表示しない

### 6.2 LoginDialog

変更点:

| 現行 | v0.2.0 |
|---|---|
| 操作者ID入力 | operator_id入力 |
| role combo | 削除 |
| passwordなし | password入力追加 |
| role自由選択 | DB上のuser role固定 |
| 認証ではない警告 | 通常ログイン説明へ変更 |

### 6.3 UserManagementTab

admin専用。

| 機能 | 内容 | 優先 |
|---|---|---:|
| ユーザー一覧 | operator_id, display_name, role, disabled, last_login_at, locked_until | P0 |
| ユーザー作成 | operator_id, display_name, role, 初期password | P0 |
| role変更 | viewer/editor/admin | P0 |
| 無効化/有効化 | disabled_at設定/解除 | P0 |
| password reset | adminによるreset | P1 |
| 検索/filter | operator_id/role/disabled | P2 |

### 6.4 管理者最低1人保証

禁止する操作:

- 最後のactive adminをdisabledにする
- 最後のactive adminのroleをviewer/editorへ変更する
- 最後のactive adminを削除する

---

## 7. audit設計

### 7.1 user_audit_logs action候補

| action | 内容 |
|---|---|
| login_success | ログイン成功 |
| login_failure | ログイン失敗 |
| user_create | ユーザー作成 |
| user_disable | ユーザー無効化 |
| user_enable | ユーザー有効化 |
| user_role_change | role変更 |
| password_change | 自分のpassword変更 |
| password_reset | adminによるpassword reset |
| lockout | lockout発生 |
| setup_admin_create | 初回admin作成 |

### 7.2 audit注意点

- password値はbefore_json/after_jsonに含めない。
- password_hashも原則ログに含めない。
- 失敗ログはoperator_idのみ記録し、passwordは記録しない。

---

## 8. DB/ファイル保護のv0.2.0 MVP扱い

DB暗号化本実装はv0.2.0 MVPから外す。ただし、以下は実施する。

| ID | 内容 | 優先 |
|---|---|---:|
| DBP-MVP-001 | 起動時にDB/backup/export/logが平文である旨をREADME/警告に明記 | P0 |
| DBP-MVP-002 | portable pathが共有/公共系フォルダなら警告 | P1 |
| DBP-MVP-003 | About/DiagnosticsにDB/log/export/backup pathを表示 | P1 |
| DBP-MVP-004 | OS ACL/BitLocker/EFSの運用手順をdocsへ記載 | P1 |

---

## 9. 実装PR分割

| PR | タイトル案 | 内容 | 受入条件 |
|---|---|---|---|
| PR-020-001 | `feat: add auth schema migrations` | schema_migrations/users/app_settings/user_audit_logs | 既存DBにmigration適用できる |
| PR-020-002 | `feat: add password hashing service` | PBKDF2 hash/verify | 正常/異常/password不一致テストOK |
| PR-020-003 | `feat: add user repository and service` | create/disable/role_change/admin guard | 最後のadmin保護テストOK |
| PR-020-004 | `feat: add first-run admin setup` | InitialAdminSetupDialog | users 0件時のみ表示 |
| PR-020-005 | `feat: require password login` | LoginDialog password化、role combo削除 | roleはDB user由来 |
| PR-020-006 | `feat: add user management tab` | admin専用ユーザー管理 | viewer/editorから不可 |
| PR-020-007 | `feat: audit authentication and user management` | user_audit_logs | login/user操作が記録される |
| PR-020-008 | `feat: add database path protection diagnostics` | path/ACL/平文DB警告 | 共有/公共配置で警告 |
| PR-020-009 | `test: extend portable smoke for auth setup login` | portable smoke更新 | setup/login後にDB作成確認 |
| PR-020-010 | `docs: finalize v0.2.0 release evidence` | release evidence更新 | SHA/manifest/checksum固定 |

---

## 10. 受入基準

### 10.1 P0受入基準

- role comboがログイン画面から消えている。
- users 0件時のみ初回admin setupが出る。
- operator_id + passwordでログインできる。
- 誤passwordでログインできない。
- disabled userでログインできない。
- user.roleがRoleContextに反映される。
- viewerはwrite/destructive不可。
- editorはwrite可/destructive不可。
- adminはwrite/destructive可。
- 最後のactive adminを無効化または降格できない。
- user操作がuser_audit_logsに記録される。
- 既存v0.1.0 DBにmigrationを適用できる。

### 10.2 品質ゲート

- `pytest -q`
- `ruff check .`
- `black --check .`
- `mypy app`
- `./scripts/build_exe_windows.ps1`
- `./scripts/smoke_test_exe_windows.ps1`
- `./scripts/package_release_windows.ps1 -ReleaseName v0.2.0-rc1`
- `./scripts/smoke_test_portable_release_windows.ps1 -ReleaseName v0.2.0-rc1`

---

## 11. v0.2.0で保留するもの

| 項目 | 理由 |
|---|---|
| SQLCipher本実装 | PoC、依存、配布、鍵管理の検証が必要 |
| backup/export暗号化 | DB暗号化/鍵管理と同時設計が必要 |
| read-only詳細分離 | 現行のvalid role共通許可で当面よい |
| dry-run/upsert import | 認証・管理設定の後でよい |
| installer/署名 | portable安全化の後でよい |

---

## 12. 次工程

1. PR-020-001として、schema migration基盤とusers/app_settings/user_audit_logsを追加する。
2. migration済みDBで既存機能が壊れないことを確認する。
3. PR-020-002以降でpassword hash、user service、初回admin、login password化へ進む。
