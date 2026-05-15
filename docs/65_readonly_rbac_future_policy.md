# 65_readonly_rbac_future_policy.md

## 1. 目的

本書は、NameVerification v3 の read-only 権限について、現行 v0.1.0 系の方針と、v0.2.0 以降で検討するロール別分離方針を定義する。

対象:

- v0.1.0-rc2
- v0.1.0 系の後続パッチ
- v0.2.0 以降のRBAC詳細化検討

---

## 2. 結論

| 論点 | 決定 |
|---|---|
| v0.1.0 系の read-only | viewer/editor/admin の valid role 共通許可を継続 |
| v0.1.0 系のGo/No-Go | read-only詳細分離はblockerにしない |
| ゴミ箱/削除済み一覧閲覧 | v0.1.0 系では valid role 共通許可 |
| 監査ログ閲覧 | v0.1.0 系では valid role 共通許可 |
| deleted 含む検索 | v0.1.0 系では valid role 共通許可 |
| v0.2.0 以降 | 業務要件が出た場合のみ分離検討 |

---

## 3. 現行RBACの前提

`docs/19_permissions_rbac_spec.md` の現行方針に従う。

| 操作区分 | viewer | editor | admin |
|---|---:|---:|---:|
| read-only | 許可 | 許可 | 許可 |
| write | 不可 | 許可 | 許可 |
| destructive | 不可 | 不可 | 許可 |

現時点の目的は、ローカル・単一利用における誤操作防止であり、機微情報の閲覧分離ではない。

---

## 4. read-only分離をv0.1.0系で実施しない理由

| 理由 | 内容 |
|---|---|
| 実装複雑性 | UI表示、query service、authorization、テストを横断して変更が必要 |
| UX低下リスク | viewerで見える情報が減ると、検索・確認用途の利便性が下がる |
| 監査性 | 監査ログを隠すより、ローカル運用では確認できる方がトラブルシュートしやすい |
| 現行利用前提 | 単一拠点・ローカル・個人/小規模利用であり、閲覧分離の必然性が低い |
| Go判定影響 | 初期実運用開始の必須要件ではない |

---

## 5. 将来分離する場合の候補

| 候補ID | 分離対象 | viewer | editor | admin | 優先度 |
|---|---|---:|---:|---:|---:|
| RBAC-READ-001 | 監査ログ閲覧 | 不可 | 可 | 可 | 低 |
| RBAC-READ-002 | ゴミ箱/削除済み一覧閲覧 | 不可 | 可 | 可 | 低 |
| RBAC-READ-003 | deleted含む検索 | 不可 | 可 | 可 | 低 |
| RBAC-READ-004 | change log詳細before/after | マスク | 可 | 可 | 低〜中 |
| RBAC-READ-005 | export可能範囲 | 不可 | 可 | 可 | 中 |

---

## 6. 将来分離の実装条件

read-only詳細分離を実施する場合は、以下を同時に更新する。

- `docs/19_permissions_rbac_spec.md`
- UI表示仕様
- authorization service
- query service / application service
- 権限別テスト
- Day1/UATチェックリスト
- 既存ユーザー向け説明

---

## 7. Go / No-Go 判断への影響

v0.1.0-rc2 のGo/No-Go判断では、read-only権限の詳細分離は **blockerではない**。

理由:

- 現行仕様として valid role 共通 read-only 許可が明文化済みである。
- write/destructive の制御が主な安全要件であり、そこは viewer/editor/admin で分離済みである。
- read-only分離はセキュリティ強化・業務分掌強化の将来課題として扱う。

---

## 8. 現時点の決定

v0.1.0 系では以下を固定する。

- read-only は viewer/editor/admin で共通許可する。
- write は editor/admin のみ許可する。
- destructive は admin のみ許可する。
- read-only詳細分離は v0.2.0 以降の任意検討とする。
- Day1 UATでは、viewerがwrite/destructiveできないこと、editorがdestructiveできないこと、adminがdestructiveできることを確認すればよい。

---

## 9. 残Backlog

| ID | 内容 | 方針 |
|---|---|---|
| RBAC-F-001 | read-only詳細分離の要否判断 | 実運用後の利用感・要件に基づいて判断 |
| RBAC-F-002 | 監査ログ閲覧制限 | 必要になった場合のみ設計 |
| RBAC-F-003 | deleted含む検索の表示制御 | 必要になった場合のみ設計 |
| RBAC-F-004 | field masking | 機微情報を扱う場合のみ検討 |
