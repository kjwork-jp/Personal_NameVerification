# 66_security_user_management_gap_analysis.md

## 1. 目的

本書は、NameVerification v3 `v0.1.0-rc2` 時点で不足している認証・ユーザー管理・管理設定・運用セキュリティ機能を洗い出し、v0.1.0系の扱いと v0.2.0 以降の改善工程を定義する。

対象:

- ログイン画面
- ユーザー管理
- 権限管理
- 管理設定
- 監査・セキュリティ運用
- portable release 配布時のローカル運用リスク

---

## 2. 現状の重大な問題

現行のログイン画面は、操作者IDと権限を利用者が自由に入力・選択できる。これは認証ではなく、監査ログ用の操作者・権限コンテキスト選択に近い。

現行状態では以下の問題がある。

| ID | 問題 | 影響 | 優先度 |
|---|---|---|---:|
| SEC-001 | 誰でも admin を選択できる | 破壊的操作を任意ユーザーが実行できる | P0 |
| SEC-002 | パスワード認証がない | 操作者本人性を担保できない | P0 |
| SEC-003 | ユーザー管理画面がない | ユーザー追加/無効化/権限変更ができない | P0 |
| SEC-004 | 初期管理者セットアップがない | 初回利用時の安全なadmin作成導線がない | P0 |
| SEC-005 | 権限昇格を防げない | viewer/editorがUIでadmin化できる | P0 |
| SEC-006 | ログイン失敗・ロックアウトがない | 総当たり・なりすまし検知ができない | P1 |
| SEC-007 | パスワード変更/リセットがない | 長期運用・漏えい時の復旧が困難 | P1 |
| SEC-008 | ユーザー操作の管理監査がない | 誰がユーザー/権限を変えたか追えない | P1 |

---

## 3. v0.1.0-rc2 での暫定扱い

v0.1.0-rc2 は portable local release として配布物固定済みだが、ログイン画面は認証機能ではない。

そのため、v0.1.0-rc2 を使う場合の暫定条件は以下とする。

| 条件 | 内容 |
|---|---|
| 利用者 | 実質的に単一ユーザーまたは信頼済みローカル利用者に限定 |
| 端末 | 個人端末・ローカル端末限定 |
| 配布 | 不特定多数へ配布しない |
| 重要データ | 機微情報・第三者管理データを入れない |
| admin操作 | 利用者本人が自己責任で実施 |

v0.1.0-rc2 の実運用Go判定では、上記制約を明示したうえで「限定運用」は可能。ただし、複数ユーザー配布・第三者利用・業務利用へ広げる場合は、P0認証/ユーザー管理を実装するまでGoにしない。

---

## 4. 必須追加機能一覧

### 4.1 認証

| ID | 機能 | 内容 | 優先度 |
|---|---|---|---:|
| AUTH-001 | パスワードログイン | operator_id + password で認証 | P0 |
| AUTH-002 | パスワードhash保存 | 平文保存禁止。PBKDF2/bcrypt/Argon2相当のhash保存 | P0 |
| AUTH-003 | 初回admin作成 | DBにユーザーがいない場合だけ初期管理者作成画面を表示 | P0 |
| AUTH-004 | ロール固定 | ロールはログインユーザーに紐づく。ログイン時に任意選択させない | P0 |
| AUTH-005 | ユーザー無効化 | disabled user はログイン不可 | P0 |
| AUTH-006 | ログイン失敗記録 | 失敗回数・時刻・operator_idを記録 | P1 |
| AUTH-007 | ロックアウト | 連続失敗時に一時ロック | P1 |
| AUTH-008 | セッションロック | 一定時間無操作で再認証 | P2 |

### 4.2 ユーザー管理

| ID | 機能 | 内容 | 優先度 |
|---|---|---|---:|
| USER-001 | ユーザー管理タブ | admin専用でユーザー一覧/追加/編集/無効化 | P0 |
| USER-002 | ユーザー作成 | operator_id, 表示名, role, 初期password | P0 |
| USER-003 | ロール変更 | viewer/editor/admin の変更 | P0 |
| USER-004 | パスワード変更 | 自分のpassword変更、adminによるリセット | P1 |
| USER-005 | ユーザー削除禁止/無効化優先 | 監査整合性のため物理削除より無効化 | P1 |
| USER-006 | 最終ログイン表示 | 最終ログイン日時・失敗回数表示 | P2 |
| USER-007 | 管理者最低1人保証 | admin全員無効化を禁止 | P0 |

### 4.3 管理設定

| ID | 機能 | 内容 | 優先度 |
|---|---|---|---:|
| SETTINGS-001 | 管理設定タブ | admin専用の設定画面 | P1 |
| SETTINGS-002 | パスワードポリシー | 最小文字数、複雑性、有効期限の任意設定 | P1 |
| SETTINGS-003 | ロックアウト設定 | 失敗回数、ロック時間 | P1 |
| SETTINGS-004 | 自動ログアウト設定 | 無操作タイムアウト | P2 |
| SETTINGS-005 | backup/export既定パス設定 | portable既定に加え、UIで変更可 | P2 |
| SETTINGS-006 | log retention設定 | operations/change log retention | P2 |
| SETTINGS-007 | 初回セットアップ完了フラグ | 初回admin作成済み判定 | P0 |

### 4.4 監査・証跡

| ID | 機能 | 内容 | 優先度 |
|---|---|---|---:|
| AUDIT-001 | ログイン成功/失敗ログ | operator_id, result, timestamp | P1 |
| AUDIT-002 | ユーザー管理操作ログ | create/disable/role_change/password_reset | P1 |
| AUDIT-003 | 権限拒否ログ | viewer/editorが拒否された操作を記録 | P2 |
| AUDIT-004 | destructive操作の再認証 | restore/import/完全削除前にpassword再入力 | P1 |
| AUDIT-005 | audit export | 監査ログの期間指定export | P2 |

---

## 5. DB schema 追加候補

v0.2.0で認証/ユーザー管理を実装する場合、最低限以下のテーブルを追加する。

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
    operator_id TEXT NOT NULL UNIQUE,
    display_name TEXT,
    role TEXT NOT NULL CHECK(role IN ('viewer', 'editor', 'admin')),
    password_hash TEXT NOT NULL,
    password_salt TEXT,
    password_updated_at TEXT,
    disabled_at TEXT,
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    last_login_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_audit_logs (
    id INTEGER PRIMARY KEY,
    actor_operator_id TEXT NOT NULL,
    target_operator_id TEXT,
    action TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. UI追加候補

| 画面/タブ | 対象role | 内容 | 優先度 |
|---|---|---|---:|
| 初回セットアップ画面 | 未セットアップ時 | 初期admin作成 | P0 |
| ログイン画面改修 | 全員 | operator_id + password、role選択廃止 | P0 |
| ユーザー管理タブ | admin | ユーザー一覧/追加/編集/無効化/role変更 | P0 |
| パスワード変更画面 | 全員 | 自分のpassword変更 | P1 |
| 管理設定タブ | admin | password policy、lockout、timeout、log retention | P1 |
| destructive再認証dialog | admin | restore/import/完全削除前のpassword再入力 | P1 |

---

## 7. 実装PR分割案

| PR | 内容 | 優先度 |
|---|---|---:|
| PR-AUTH-001 | users/app_settings/user_audit_logs schema追加、migration方針追加 | P0 |
| PR-AUTH-002 | password hash/verify service追加、単体テスト | P0 |
| PR-AUTH-003 | 初回adminセットアップ画面 | P0 |
| PR-AUTH-004 | login dialogをpassword認証へ変更、role選択廃止 | P0 |
| PR-AUTH-005 | ユーザー管理タブ追加 | P0 |
| PR-AUTH-006 | ユーザー操作audit log | P1 |
| PR-AUTH-007 | パスワード変更/リセット | P1 |
| PR-AUTH-008 | lockout / failed login counter | P1 |
| PR-AUTH-009 | destructive操作前の再認証 | P1 |
| PR-AUTH-010 | 管理設定タブ | P1 |

---

## 8. Go / No-Go 判断への影響

### 8.1 個人ローカル限定利用

v0.1.0-rc2 を個人ローカル限定で使う場合、現行ログインの弱さは既知制約として扱える。

判定:

- Conditional Go 可
- 実データや機微情報の投入は慎重に行う
- 不特定多数・他者配布は不可

### 8.2 複数ユーザー利用・第三者配布

複数ユーザー利用や第三者配布を想定する場合、現行ログイン方式は不十分。

判定:

- No-Go
- AUTH-001〜AUTH-005 と USER-001〜USER-003 が最低限必要

---

## 9. 残課題

| ID | 内容 | 方針 |
|---|---|---|
| SEC-BL-001 | 初回admin作成方式の詳細設計 | v0.2.0 P0 |
| SEC-BL-002 | password hash方式選定 | v0.2.0 P0 |
| SEC-BL-003 | user management tab設計 | v0.2.0 P0 |
| SEC-BL-004 | destructive再認証 | v0.2.0 P1 |
| SEC-BL-005 | 管理設定タブ | v0.2.0 P1 |
| SEC-BL-006 | DB暗号化/backup暗号化 | 必要性を別途検討 |

---

## 10. 結論

現行ログイン画面は認証ではない。v0.1.0-rc2では単一ユーザー・ローカル限定の既知制約として扱えるが、複数ユーザー運用または第三者配布では不十分である。

次リリース候補 v0.2.0 では、ユーザー管理・パスワード認証・初回admin作成・管理設定をP0/P1として実装する。
