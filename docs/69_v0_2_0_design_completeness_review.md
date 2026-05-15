# 69_v0_2_0_design_completeness_review.md

## 1. 目的

本書は、NameVerification v3 `v0.2.0` へ進む前に、現時点の設計資料群に過不足がないかを再点検し、実装前に追加で決めるべき設計論点を整理する。

参照対象:

- `docs/66_security_user_management_gap_analysis.md`
- `docs/67_quality_attribute_gap_analysis.md`
- `docs/68_database_file_protection_policy.md`
- `docs/97_open_issues_and_constraints.md`

---

## 2. 結論

v0.2.0 の方向性は概ね妥当だが、実装に入るにはまだ設計粒度が足りない。

特に不足しているのは、以下の5領域である。

| 領域 | 不足 | 優先度 |
|---|---|---:|
| 認証/ユーザー管理 | DB schema案はあるが、初回admin、password hash、reset、lockout、監査の詳細仕様が不足 | P0 |
| DB/成果物保護 | 方針はあるが、OS ACLと暗号化の採用判断、鍵管理、backup/export暗号化仕様が未決定 | P0〜P1 |
| migration/互換性 | v0.1.0平文DBからv0.2.0 schema/認証付きDBへの移行設計が不足 | P0 |
| UX/管理画面 | 画面一覧はあるが、操作フロー、エラー文言、権限制御、初回セットアップUXが不足 | P1 |
| テスト/受入基準 | PR分割案はあるが、受入条件・異常系・回帰テストの明文化が不足 | P1 |

したがって、次に作るべきものは実装ではなく、`v0.2.0 implementation design` と `v0.2.0 acceptance criteria` である。

---

## 3. 現在の設計で足りているもの

| 領域 | 状態 |
|---|---|
| 認証不足の認識 | 現行ログインは認証ではないと明文化済み |
| P0機能の大枠 | password認証、role自由選択廃止、初回admin、ユーザー管理タブがP0 |
| 品質属性別ギャップ | 信頼性/可用性/保守性/完全性/機密性/UXで洗い出し済み |
| DB直アクセスリスク | アプリ認証だけでは防げないと明文化済み |
| v0.1.0制約 | 単一ユーザー・信頼済みローカル限定と明文化済み |
| v0.1.0 Go/No-Go | 複数ユーザー/第三者配布/機微情報投入はNo-Goと整理済み |

---

## 4. 設計不足一覧

### 4.1 認証・ユーザー管理

| ID | 不足 | 決めるべきこと | 優先度 |
|---|---|---|---:|
| AUTH-D-001 | password hash方式未確定 | PBKDF2を標準採用するか、bcrypt/Argon2等を外部依存で採るか | P0 |
| AUTH-D-002 | 初回admin作成条件が粗い | users 0件時のみか、disabled全件時の復旧をどうするか | P0 |
| AUTH-D-003 | 管理者喪失時の復旧手順がない | emergency reset / recovery token / CLI reset の要否 | P0 |
| AUTH-D-004 | ログイン失敗/lockout仕様不足 | 回数、期間、解除方法、監査ログ | P1 |
| AUTH-D-005 | password変更/リセット仕様不足 | 自分変更、admin reset、一時password、初回変更強制 | P1 |
| AUTH-D-006 | password policy不足 | 最小長、複雑性、有効期限、再利用禁止の採否 | P1 |
| AUTH-D-007 | session仕様不足 | 無操作timeout、再認証、画面ロック | P2 |
| AUTH-D-008 | user_audit_logsのaction列挙不足 | create/disable/enable/role_change/resetなどの固定値 | P1 |

### 4.2 DB/ファイル保護

| ID | 不足 | 決めるべきこと | 優先度 |
|---|---|---|---:|
| DBP-D-001 | OS ACL実装範囲未確定 | package生成時に設定するか、初回起動時に診断のみか | P0 |
| DBP-D-002 | DB暗号化採否未確定 | v0.2.0でPoCまでか、本実装まで入れるか | P1 |
| DBP-D-003 | 鍵管理未確定 | マスターパスワード、Windows資格情報、DPAPI、環境変数のどれを採るか | P1 |
| DBP-D-004 | backup暗号化未確定 | 暗号化DBをcopyするだけか、backup ZIP暗号化を行うか | P1 |
| DBP-D-005 | export暗号化未確定 | CSV/JSON/SQLを平文許可するか、暗号化exportを追加するか | P1 |
| DBP-D-006 | log機微情報マスキング不足 | path、operator_id、before/after_jsonの扱い | P2 |
| DBP-D-007 | 鍵紛失時の方針なし | 復旧不能として明示するか、recovery keyを持つか | P1 |

### 4.3 migration / 互換性

| ID | 不足 | 決めるべきこと | 優先度 |
|---|---|---|---:|
| MIG-D-001 | schema_version管理が未確定 | `schema_migrations` tableを導入するか | P0 |
| MIG-D-002 | v0.1.0 DBへのusers追加手順不足 | 既存DBにusers/app_settings/user_audit_logsを安全追加 | P0 |
| MIG-D-003 | 初回admin作成と既存DBの関係不足 | 既存データあり・usersなしDB起動時の扱い | P0 |
| MIG-D-004 | rollback方針不足 | v0.2.0 migration後にv0.1.0へ戻す可否 | P1 |
| MIG-D-005 | release artifact更新条件不足 | v0.2.0実装後のZIP SHA/manifest/checksum再固定手順 | P1 |

### 4.4 UI/UX

| ID | 不足 | 決めるべきこと | 優先度 |
|---|---|---|---:|
| UX-D-001 | 初回セットアップ画面詳細不足 | 入力項目、validation、完了後遷移 | P0 |
| UX-D-002 | ログイン画面詳細不足 | role非表示、失敗時表示、lockout表示 | P0 |
| UX-D-003 | ユーザー管理タブ詳細不足 | 一覧列、作成/編集/無効化/role変更/検索 | P0 |
| UX-D-004 | 操作できない理由表示不足 | role不足、lockout、disabledなどの表示方針 | P1 |
| UX-D-005 | About/Diagnostics不足 | version, Git SHA, DB path, log path, permission status | P1 |
| UX-D-006 | 危険操作ラベル不足 | restore/import/完全削除の文言、対象件数表示 | P1 |

### 4.5 テスト/受入基準

| ID | 不足 | 決めるべきこと | 優先度 |
|---|---|---|---:|
| TEST-D-001 | 認証正常系テスト不足 | 正しいpasswordでloginできる | P0 |
| TEST-D-002 | 認証異常系テスト不足 | 誤password、disabled、unknown user、lockout | P0 |
| TEST-D-003 | role固定テスト不足 | user.roleがUI/サービス権限に反映される | P0 |
| TEST-D-004 | 初回adminテスト不足 | users 0件時だけsetupが出る | P0 |
| TEST-D-005 | 管理者最低1人保証テスト不足 | 最後のadminを無効化/role変更できない | P0 |
| TEST-D-006 | migrationテスト不足 | v0.1.0 DBからv0.2.0 schemaへ移行できる | P0 |
| TEST-D-007 | portable smoke更新不足 | 初回setup/loginを含むsmokeへ拡張 | P1 |
| TEST-D-008 | DB保護診断テスト不足 | ACL/書込権限/DB path診断の確認 | P1 |

---

## 5. v0.2.0 の最小スコープ案

### 5.1 v0.2.0-MVPに含めるべきもの

| ID | 内容 | 理由 |
|---|---|---|
| V020-MVP-001 | users table / app_settings / user_audit_logs | 認証基盤 |
| V020-MVP-002 | PBKDF2 password hash service | 外部依存を増やさず実装しやすい |
| V020-MVP-003 | 初回admin setup | 初回利用の安全な入口 |
| V020-MVP-004 | login dialogのpassword認証化 | role自由選択廃止 |
| V020-MVP-005 | admin専用ユーザー管理タブ | ユーザー追加/無効化/role変更 |
| V020-MVP-006 | 管理者最低1人保証 | ロックアウト防止 |
| V020-MVP-007 | login/user管理audit | 誰が何をしたか追跡 |
| V020-MVP-008 | DB/backup/export/log保護の暫定警告と配置診断 | DB直アクセスリスクの低減 |

### 5.2 v0.2.0から外してよいもの

| ID | 内容 | 理由 |
|---|---|---|
| V020-OUT-001 | SQLCipher本実装 | 依存・配布・鍵管理が重い。まずPoC |
| V020-OUT-002 | column-level暗号化 | 検索/保守が複雑化 |
| V020-OUT-003 | 自動更新/installer署名 | 認証基盤の後でよい |
| V020-OUT-004 | read-only詳細分離 | 現行valid role共通許可で一旦十分 |
| V020-OUT-005 | dry-run/upsert import | 認証・管理が先 |

---

## 6. 推奨PR分割

| PR | 内容 | 優先度 | 備考 |
|---|---|---:|---|
| PR-020-001 | schema_migrations / users / app_settings / user_audit_logs追加 | P0 | 既存DB migrationテスト必須 |
| PR-020-002 | password hash/verify service | P0 | PBKDF2前提、単体テスト |
| PR-020-003 | user repository/service | P0 | create/disable/role_change/admin guard |
| PR-020-004 | first-run admin setup dialog | P0 | users 0件時のみ |
| PR-020-005 | login dialog password認証化 | P0 | role combo削除 |
| PR-020-006 | authorization連携 | P0 | RoleContextをuser record由来へ |
| PR-020-007 | user management tab | P0 | admin専用 |
| PR-020-008 | login/user audit log | P1 | 成功/失敗/管理操作 |
| PR-020-009 | DB path/ACL診断と警告 | P1 | Windows前提 |
| PR-020-010 | portable smoke拡張 | P1 | setup/login含む |

---

## 7. 実装前に決めるべき設計決定

| ID | 決定事項 | 推奨 |
|---|---|---|
| DEC-001 | password hash方式 | Python標準 `hashlib.pbkdf2_hmac` を第一候補 |
| DEC-002 | salt保存 | userごとにrandom salt保存 |
| DEC-003 | hashパラメータ保存 | algorithm/iterations/salt/hashを保存可能にする |
| DEC-004 | 初回admin条件 | users有効件数0件、かつ明示確認後にsetup可能 |
| DEC-005 | recovery | v0.2.0ではCLI recovery scriptを検討、通常UIには出さない |
| DEC-006 | DB暗号化 | v0.2.0ではPoC/設計、MVP本実装からは外す |
| DEC-007 | OS保護 | 初回起動時/診断画面で警告とpath表示を行う |
| DEC-008 | backup/export暗号化 | v0.2.0 P1以降。まず平文注意喚起と保管先制限 |
| DEC-009 | migration | schema_migrations table導入 |
| DEC-010 | test gate | pytest/ruff/black/mypy/build/smoke/portable smoke必須 |

---

## 8. v0.2.0 Go/No-Go 基準

v0.2.0を安全強化版として扱うには、最低限以下が必要。

| 条件 | 判定 |
|---|---|
| role自由選択が廃止されている | 必須 |
| password認証がある | 必須 |
| 初回admin setupがある | 必須 |
| admin専用ユーザー管理がある | 必須 |
| 最後のadminを消せない | 必須 |
| user操作がauditされる | 必須 |
| v0.1.0 DBからmigrationできる | 必須 |
| portable package生成/起動が通る | 必須 |
| DB直アクセスリスクの警告/診断がある | 必須またはP1 |

---

## 9. 結論

v0.2.0設計の方向性は正しい。ただし、現状は「不足機能の洗い出し」段階であり、実装可能な粒度としてはまだ粗い。

次工程は以下の順に進める。

1. `docs/70_v0_2_0_auth_user_management_implementation_plan.md` を作成する。
2. password hash、migration、初回admin、login変更、user management tabの受入基準を確定する。
3. PR-020-001から実装を開始する。
