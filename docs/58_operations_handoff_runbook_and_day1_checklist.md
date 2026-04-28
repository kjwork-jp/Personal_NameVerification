# 58_operations_handoff_runbook_and_day1_checklist.md

## 1. 目的
本書は、NameVerification v3 の運用開始（Day 0 / Day 1）時に、運用担当が迷わず実施できる最小手順を定義する。

- 対象: 運用担当 / 管理者（admin）
- 前提: Windows ローカル端末、SQLite ローカルファイル、オフライン運用
- 参照: `docs/50_operations_design.md`、`docs/51_backup_restore_policy.md`、`docs/54_go_live_checklist.md`、`docs/55_incident_response_runbook.md`

---

## 2. Day 0（運用開始前）runbook

### 2.1 事前固定情報
- リリース対象 Git SHA を確定し、配布物と一致していることを確認する。
- 実施日（YYYY-MM-DD）/ 実施者 / 端末名 を記録する。
- 利用ロール（viewer/editor/admin）の確認アカウントを用意する。

### 2.2 起動確認
1. アプリを起動する（`python -m app.pyside6_main` または配布実行ファイル）。
2. タブが表示されることを確認する（Search / Name Management / Title-Subtitle / Link / Trash / Audit / Operations）。
3. 異常終了がないことを確認する。

### 2.3 DB 初期化・存在確認
1. 対象 DB ファイルの存在を確認する。
2. 新規環境では初期スキーマが適用済みであることを確認する。
3. 既存環境では、直近バックアップの存在を確認する。

### 2.4 ロール別の確認観点
- viewer:
  - read-only 操作が可能（検索/一覧/監査ログ/ゴミ箱閲覧）。
  - write/destructive 系ボタンが無効である。
- editor:
  - write 操作（作成/更新/リンク）が可能。
  - destructive 操作（復元/完全削除/restore/import）は不可。
  - Operations は export/backup create のみ実行可能。
- admin:
  - read/write/destructive を実行可能。
  - restore/import 実行時に確認ダイアログが表示される。

---

## 3. Day 1（初回運用）runbook

### 3.1 業務導線に沿った確認順
以下を **Search → CRUD → Trash → Audit → Operations** の順で確認する。

1. Search
   - 完全一致/部分一致、絞込、結果表示を確認。
2. CRUD（Name / Title / Subtitle / Link）
   - 作成→更新→参照まで実施。
3. Trash
   - 論理削除後に一覧へ反映されることを確認。
   - admin で復元/完全削除を確認。
4. Audit
   - 主要操作が change log に記録されることを確認。
5. Operations
   - export（CSV/JSON/SQL dump）を実行。
   - backup create を実行。
   - （必要時のみ）restore / import は admin かつ確認ダイアログ経由で実行。

### 3.2 export / import / backup / restore の注意点
- path 指定は Browse ボタンを優先し、手入力ミスを避ける。
- import（CSV/JSON）は空 DB 限定で実施する。
- restore は破壊的操作のため、対象 DB 接続をクローズしてから実施する。
- restore/import 前に現状退避（バックアップ）を必ず取得する。
- viewer は Operations 実行不可、editor は export/backup のみ可能。

### 3.3 operation log の確認場所
- Operations 実行結果は AppDataLocation 配下 `operations_events.jsonl` に記録される。
- ログの保守は size-based rotation / TTL pruning で行われる。

### 3.4 log viewer の確認方法（Operationsタブ）
1. 「ログ再読込」で最新を取得。
2. source を `current only / all / archive` で切替。
3. status/action filter を設定。
4. message 検索（部分一致 or regex）を実施。
   - regex 利用時は `Ignore case / Multiline / Dotall` を必要に応じて切替。
5. 表示順（最新順/古い順）を切替。
6. Prev/Next と表示件数（50/100/200/500）で表示内容を確認。

### 3.5 終業時の保全観点
- 当日バックアップを取得して保存先を記録。
- 当日 Operations 実行ログを確認し、必要に応じてエクスポート。
- 未解決事項・不具合を `docs/97_open_issues_and_constraints.md` に追記する。

---

## 4. 初回運用チェックリスト（Day 1 用）

### 4.1 実施メタ情報
- 対象 Git SHA:
- 実施日（YYYY-MM-DD）:
- 実施者:
- 判定（OK / NG / 保留）:
- 備考:

### 4.2 チェック項目
- [ ] 起動確認（異常終了なし）
- [ ] DB 存在確認 / 初期化確認
- [ ] viewer 権限確認
- [ ] editor 権限確認
- [ ] admin 権限確認
- [ ] Search 確認
- [ ] CRUD 確認
- [ ] Trash 確認
- [ ] Audit 確認
- [ ] Operations（export / backup）確認
- [ ] operation log / log viewer 確認
- [ ] 終業時バックアップ確認

---

## 5. 障害時の一次切り分けメモ（最小）

### 5.1 起動しない
- 実行ファイル/実行コマンドを確認。
- Python 仮想環境・依存関係（PySide6）を確認。
- 直近変更 SHA と配布物 SHA の一致を確認。

### 5.2 DB ファイル問題
- DB path の存在・アクセス権・ロック状態を確認。
- restore 実行直後なら接続クローズ漏れを確認。
- 必要に応じて直近バックアップから復旧を検討。

### 5.3 import/export path 問題
- Browse ボタンで再選択し、拡張子・ディレクトリ種別を再確認。
- 書込権限/空き容量を確認。
- import は空 DB 限定条件を再確認。

### 5.4 role によるボタン無効
- ログイン中ロールを確認（viewer/editor/admin）。
- 期待操作の区分（read/write/destructive）を `docs/19_permissions_rbac_spec.md` で確認。

### 5.5 operation log が見えない
- AppDataLocation 配下の `operations_events.jsonl` の存在確認。
- 実行操作自体が失敗していないか UI メッセージを確認。
- ログローテーションにより archive へ移動していないか確認。

### 5.6 log viewer に出ない
- source が `current only` になっていないか確認（必要なら all/archive へ切替）。
- status/action filter と message 検索条件を解除して再読込。
- 表示件数上限とページ位置（Prev/Next）を確認。

---

## 6. blocker / backlog の扱い
- blocker: Day 1 実施不可・Go/No-Go 判定不能に直結する事項。即時エスカレーション。
- backlog: Day 1 実施は可能だが、改善が必要な事項。次スプリントへ計画投入。
