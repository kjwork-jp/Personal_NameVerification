# 68_database_file_protection_policy.md

## 1. 目的

本書は、NameVerification v3 の SQLite DB ファイルへ直接アクセスされるリスクと、防御策を整理する。

対象:

- `release/<ReleaseName>/30_prod_db/nameverification.db`
- `release/<ReleaseName>/50_backups/**/*.db`
- `release/<ReleaseName>/60_exports/**/*`
- `release/<ReleaseName>/40_logs/**/*.jsonl`

---

## 2. 結論

SQLite はローカルファイルDBであるため、DBファイルを読めるOSユーザーは、アプリを通さず直接DBを開ける。

したがって、アプリ内のログイン・RBACだけではDBファイル直アクセスは防げない。

v0.2.0以降の方針は以下とする。

| 区分 | 方針 | 優先度 |
|---|---|---:|
| アプリ認証 | 必須。operator_id + password認証、role自由選択廃止 | P0 |
| OSファイル保護 | Windowsユーザープロファイル配下配置、ACL、BitLocker/EFS等を推奨 | P0 |
| DB暗号化 | SQLCipher / SQLite Encryption Extension 相当の採用可否を検討 | P1 |
| backup/export暗号化 | DB暗号化と同等以上に重要。zip暗号化等を検討 | P1 |
| secrets管理 | DB暗号化キーをDB横に置かない。Windows資格情報等を検討 | P1 |

---

## 3. 現状リスク

| ID | リスク | 影響 | 優先度 |
|---|---|---|---:|
| DBP-001 | `nameverification.db` が平文SQLiteファイル | sqlite tool等で直接参照可能 | P0 |
| DBP-002 | アプリのrole制御を迂回できる | viewer/editor/admin制御が無意味化 | P0 |
| DBP-003 | backup DBも平文 | backupから同じく情報取得可能 | P0 |
| DBP-004 | CSV/JSON/SQL exportも平文 | exportを持ち出されると漏えい | P0 |
| DBP-005 | operations/change logにpathや操作情報が残る | 運用情報漏えい | P1 |
| DBP-006 | DB暗号化しても起動中・ログイン後はアプリ経由で参照可能 | 完全防御ではない | P1 |
| DBP-007 | 暗号化キーを同梱すると実質無効 | ZIP内に鍵があると第三者が復号できる | P0 |

---

## 4. 防御策のレイヤー

### 4.1 アプリ認証

アプリ認証は、通常操作・UI操作・監査ログの本人性を担保するために必要。

ただし、DBファイル自体が平文なら、アプリを通らない直接アクセスは防げない。

必要機能:

- operator_id + password認証
- password hash保存
- role自由選択廃止
- 初回admin作成
- ユーザー管理タブ
- destructive再認証

### 4.2 OSファイル保護

最小構成では、Windows側の保護を利用する。

| 対策 | 内容 | 備考 |
|---|---|---|
| ユーザープロファイル配下配置 | 他ユーザーから読めない場所に配置 | portable配布先の選定が重要 |
| NTFS ACL | DB/log/backup/exportを本人ユーザーだけに制限 | 配布手順に組み込む |
| BitLocker | ディスク全体を暗号化 | PC紛失・盗難対策 |
| EFS | ファイル/フォルダ単位暗号化 | 運用難度と復旧性に注意 |
| Windows Hello/OSログイン | OSログイン自体を強化 | アプリ認証と併用 |

### 4.3 DB暗号化

SQLite標準のPython `sqlite3` は、DBファイル暗号化を標準提供しない。

DB暗号化を行う場合は、以下のような選択肢を検討する。

| 選択肢 | 概要 | メリット | デメリット |
|---|---|---|---|
| SQLCipher系 | SQLite互換の暗号化DB | 実績が多い | Python/Windows/EXE同梱の検証が必要 |
| SQLite Encryption Extension相当 | SQLite公式系の暗号化拡張 | 公式系 | ライセンス/入手/配布条件の確認が必要 |
| OS暗号化のみ | BitLocker/EFS/ACLで保護 | 実装変更が少ない | アプリ外へコピーされたDBは保護外になり得る |
| アプリ独自暗号化 | 特定列やexportを暗号化 | 柔軟 | 検索・照合・保守が複雑化しやすい |

---

## 5. DB暗号化を採用する場合の注意

| 論点 | 注意点 |
|---|---|
| 鍵管理 | DBファイル横にkey.txtを置くと意味がない |
| 起動UX | 起動時にマスターパスワード入力が必要になる可能性 |
| backup | 暗号化DBをbackupするのか、backup時に再暗号化するのか決める |
| export | CSV/JSON/SQL exportは平文になりやすい。export暗号化が必要 |
| restore | 暗号化DB restore時のkey一致・key変更手順が必要 |
| PyInstaller | 暗号化SQLiteライブラリの同梱検証が必要 |
| 移行 | 既存平文DBから暗号化DBへの変換手順が必要 |
| 障害対応 | 鍵紛失時は復旧不能になる可能性がある |

---

## 6. 推奨ロードマップ

### P0: 先に必須

| ID | 内容 |
|---|---|
| DBP-P0-001 | ログインをpassword認証化 |
| DBP-P0-002 | role自由選択廃止 |
| DBP-P0-003 | users table / user management tab |
| DBP-P0-004 | 配布先をユーザープロファイル配下に限定する運用手順 |
| DBP-P0-005 | DB/backup/export/logへのOS権限チェック手順 |
| DBP-P0-006 | v0.1.0系は平文DBであることを起動時またはREADMEで明示 |

### P1: DB/成果物保護強化

| ID | 内容 |
|---|---|
| DBP-P1-001 | SQLCipher等のPoC |
| DBP-P1-002 | 暗号化DBのPyInstaller同梱検証 |
| DBP-P1-003 | マスターパスワード/Windows資格情報連携検討 |
| DBP-P1-004 | backup/export暗号化方針 |
| DBP-P1-005 | DB暗号化移行手順 |
| DBP-P1-006 | restore/importと暗号化キーの整合手順 |

### P2: 追加強化

| ID | 内容 |
|---|---|
| DBP-P2-001 | column-level暗号化の要否判断 |
| DBP-P2-002 | audit logの機微情報マスキング |
| DBP-P2-003 | diagnostic bundleのマスキング |
| DBP-P2-004 | key rotation手順 |

---

## 7. Go / No-Go判断

| 利用形態 | 判定 |
|---|---|
| 単一ユーザー・信頼済みローカル端末・非機微データ | Conditional Go可 |
| 同一Windowsユーザー内での個人利用 | Conditional Go可 |
| 複数Windowsユーザーが触れる端末 | No-Go寄り。ACL/OS保護とアプリ認証が必要 |
| 第三者配布 | No-Go。認証/ユーザー管理/DB保護方針が必要 |
| 機微情報投入 | No-Go。少なくとも認証、OS保護、backup/export保護が必要 |

---

## 8. 暫定運用ルール

v0.1.0-rc2を使う場合は、以下を守る。

- ZIP展開先は自分のWindowsユーザープロファイル配下に限定する。
- 共有フォルダ、OneDrive共有、NAS共有、Public/Desktop共用領域には置かない。
- DB/backup/export/logを他人に渡さない。
- 機微情報を投入しない。
- Windowsログイン、BitLocker、画面ロックを有効化する。
- exportしたCSV/JSON/SQL dumpはDB本体と同等の機密情報として扱う。

---

## 9. 結論

DB直アクセス対策は、アプリ内ログインだけでは不十分である。

最小の現実解は、まずアプリ認証とユーザー管理を実装し、同時にWindowsのACL/BitLocker/EFS等でDB/backup/export/logファイルを保護すること。

本格的に第三者配布・機微情報投入を行う場合は、SQLCipher等のDB暗号化と、backup/export暗号化、鍵管理を含めて設計する必要がある。
