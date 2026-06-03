# Personal_NameVerification / 名前解決アプリ 開発引継ぎ詳細版

作成日: 2026-06-03
対象repo: `kjwork-jp/Personal_NameVerification`

このファイルは、新規チャットへ開発作業を引き継ぐための詳細版メモです。GitHub repoを一次情報として扱い、チャット本文やローカル手元メモよりこのファイルとGitHub上のPR/CI状態を優先してください。

---

## 1. 引継ぎの目的

- 新チャットで、名前解決アプリのUI改善・UAT整備・CI修正・PR管理・mergeを継続する。
- 人間の手元確認に依存せず、AIがGitHub上で実装、テスト追加、PR作成、CI確認、失敗修正、レビュー指摘対応、mergeまで進める。
- ユーザーは基本的に最終UATだけを行う想定。

---

## 2. 最重要の現在地点

最初に必ず PR #152 を確認する。

- PR: #152
- Title: `feat: normalize link management labels`
- Branch: `feature/link-label-normalization`
- Base: `main`
- Head SHA: `738bf29d7bed0f3fb2e4d6c33965151fcd1aecd4`
- 内容: `LinkManagementTab` の名前/タイトル/サブタイトル/ID表記改善
- 最新CI: Quality Gates run #196 success
- 直近確認: open / 未merge / mergeable=true

新チャットの最初の実作業:

1. PR #152の最新状態を再取得する。
2. 最新head SHA、CI success、review未解決指摘、mergeable状態を確認する。
3. 問題なければPR #152をsquash mergeする。
4. merge後、次の残工程へ進む。

注意:

- `mergeable=false` や `unknown/null` が出た場合、GitHub側の一時評価遅延、base branch更新、または実競合の可能性がある。
- その場合はPRを再取得し、base/head差分・conflict有無・最新CIを確認する。
- 必要ならbase追従・競合解消commitを作成し、再CI通過後にmergeする。

---

## 3. 基本運用方針

- AIがGitHub上で、実装・テスト追加・PR作成・CI確認・失敗修正・review対応・mergeまで進める。
- 人間の手元UAT/EXE/portable確認は残工程に入れない。
- 手元確認は、ユーザーがやりたい時だけ任意確認として扱う。
- 軽いタスクは小分けにせず、まとめて進める。
- 毎回、必ず「完了済みを除いた残工程一覧」を併記する。
- 残工程表は「優先度 / 残工程 / 難易度 / 状態」を基本列にする。
- 完了済みタスクは残工程一覧から除外する。
- CI未通過PRはmergeしない。
- Codex review / GitHub review指摘が妥当ならmerge前に対応する。
- merge方式は原則squash merge。
- Google Driveは基本参照しない。GitHub repoを一次情報として扱う。
- コマンドが必要な場合は、PowerShell前提で完全コマンドを書く。
- PR本文には、任意確認としてUAT / EXE / portableコマンドを残してよい。
- ただし、それらはチャット回答の残工程には含めない。

ユーザーに確認を求めるのは、以下の場合だけ:

- GitHub権限不足で操作できない
- 破壊的操作や設定変更が必要で、影響範囲が不明
- CI/PR状態が矛盾していて、複数の復旧方針が同程度に妥当
- 手元環境でしか確認できない問題が発生した

それ以外はGitHub上で自律的に進める。

---

## 4. Repo / 技術構成

- GitHub repo: `kjwork-jp/Personal_NameVerification`
- ローカル想定パス: `C:\Users\nkaji\Documents\GitHub\Personal_NameVerification`
- 技術:
  - Python
  - PySide6
  - SQLite
  - pytest
  - ruff
  - black
  - mypy
  - PyInstaller
- GUI起動: `python -m app.pyside6_main`
- UAT demo起動: `.\scripts\reset_uat_demo_windows.ps1 -Launch`

---

## 5. PR #152 の詳細

PR #152 は `LinkManagementTab` の表示改善。

目的:

- 名前/タイトル/サブタイトル/ID表記の混在を解消する。
- UI上は表示名中心にする。
- 公開ID・内部ID・リンクIDはtooltipへ移す。

変更内容:

| 対象 | 旧表示 | 新表示 |
|---|---|---|
| 名前候補 | `名前: Alice（公開ID: ...）` | `Alice` |
| タイトル候補 | `タイトル: Title1（公開ID: ...）` | `Title1` |
| サブタイトル候補 | `S1: Sub1（公開ID: ...）` | `S1 / Sub1` |
| 既存関連候補 | `Title1 > S1: Sub1（リンクID: ...）` | `Title1 / S1 / Sub1` |
| ID情報 | 表示文字列に混在 | tooltipへ分離 |
| 登録ボタン | `登録` | `関連付けを登録` |
| 解除ボタン | `解除` | `関連付けを解除` |

テスト観点:

- 表示名中心のコンボ表示。
- tooltipに公開ID/内部ID/リンクIDが残っていること。
- UAT系テストも新仕様へ更新済み。
- `AuditLogsTab` の現行属性は `tabs`。
- `user_audit_service` 未指定時、`ユーザー/認証ログ` タブは存在しないため、存在時のみ検証する。

---

## 6. PR #152 のCI修正履歴

| run | 結果 | 原因 | 修正 |
|---:|---|---|---|
| #190 | failure | ruff `UP035` | `pyproject.toml` の `app/ui/link_management_tab.py` per-file ignoreへ `UP035` 追加 |
| #191 | failure | pytest / 旧UAT表示期待値 | 表示名中心 + tooltip ID確認へ修正 |
| #193 | failure | ruff E501 | tooltip ID確認assertを折り返し |
| #194 | failure | pytest / `audit.audit_tabs` 旧属性参照 | `audit.tabs` へ修正 |
| #195 | failure | pytest / `ユーザー/認証ログ` タブ常在前提 | `user_audit_tab` 存在時のみ確認へ修正 |
| #196 | success | 修正後通過 | merge待ち |

---

## 7. 主要ファイル構成と責務

### 7.1 UI主要ファイル

| ファイル | 役割 | 備考 |
|---|---|---|
| `app/ui/main_window.py` | メインウィンドウ、主要タブ構成 | UATテストで `_tabs_by_name` 経由参照あり |
| `app/pyside6_main.py` | PySide6アプリ起動エントリ | 起動コマンドは `python -m app.pyside6_main` |
| `app/ui/search_tab.py` | 検索タブ | 過去に色・summary改善対象 |
| `app/ui/name_management_tab.py` | 名前管理 | summary改善済み |
| `app/ui/title_management_tab.py` | タイトル管理focused wrapper | 対象文脈・summary改善済み |
| `app/ui/subtitle_management_tab.py` | サブタイトル管理focused wrapper | summary改善済み |
| `app/ui/title_subtitle_management_tab.py` | タイトル/サブタイトル管理基盤 | 本体summary改善済み |
| `app/ui/title_subtitle_summary_patch.py` | 基盤summary拡張 | PR #151で追加 |
| `app/ui/link_management_tab.py` | 名前↔サブタイトル関連付けUI | PR #152の本体 |
| `app/ui/audit_logs_tab.py` | 監査ログUI | 属性は `tabs`。`user_audit_tab` はoptional |
| `app/ui/operations_tab.py` | データ入出力 | role別表示テストあり |
| `app/ui/trash_tab.py` | 削除データ/復元系 | 今後 `DELETE-FLOW-CLARITY` 対象 |
| `app/ui/ui_style.py` | 共通スタイル | 今後 `SHARED-RICH-UI-COMPONENTS` の中心 |
| `app/ui/navigation_polish.py` | workflow tab guidance | PR #146で追加 |
| `app/ui/public_id_display.py` | 公開ID表示補助 | short/detail表示に使用 |
| `app/ui/role_context.py` | role/operator context | viewer/editor/admin制御 |
| `app/ui/permissions.py` | role別権限制御 | can_link/can_unlink等 |

### 7.2 application/domain/infrastructure

| 領域 | 役割 |
|---|---|
| `app/application/read_models.py` | UI表示用read model。`NameSearchRow`, `TitleDetail`, `SubtitleDetail`, `RelatedRow` など |
| `app/application/user_services.py` | ユーザー認証・role変更 |
| `app/application/windows_identity.py` | Windows認証 |
| `app/domain/*` | ドメインエラー、入力モデル等 |
| `app/infrastructure/db.py` | SQLite schema適用 |
| `db/`, `migrations/` | DB schema/migration関連 |
| `nameverification.db` | ローカル実DB。PR作業で不用意に変更しない |

---

## 8. 主要テスト構成

| ファイル | 役割 |
|---|---|
| `tests/test_link_management_tab_ui.py` | LinkManagementTabのrole guard・表示名/tooltip検証 |
| `tests/test_release_uat_coverage.py` | release UAT主要カバレッジ |
| `tests/test_release_remaining_uat.py` | 公開ID full表示、CRUD/削除権限、監査ログ/操作ガイド |
| `tests/test_title_management_tab_ui.py` | TitleManagementTab focused wrapper |
| `tests/test_subtitle_management_tab_ui.py` | SubtitleManagementTab focused wrapper |
| `tests/test_title_subtitle_management_tab_ui.py` | TitleSubtitleManagementTab基盤 |
| `tests/test_table_microcopy_ui.py` | table readability/microcopy |
| `tests/test_navigation_polish_ui.py` | workflow navigation guidance |
| `tests/test_main_window_smoke.py` | MainWindow smoke、Operations dependency patch補助 |

---

## 9. 既知スクリプト

| スクリプト | 用途 |
|---|---|
| `scripts/reset_uat_demo_windows.ps1` | UAT demo DB/CSV/users生成、`-Launch` でGUI起動 |
| `scripts/build_exe_windows.ps1` | Windows EXE build |
| `scripts/smoke_test_exe_windows.ps1` | EXE smoke test |
| `scripts/package_release_windows.ps1` | release package作成 |
| `scripts/smoke_test_portable_windows.ps1` | portable release smoke test |
| `scripts/generate_sample_data.py` | sample data生成系 |

注意:

- 新チャットで必要なら `scripts/` 配下をGitHubで再確認する。
- 手元UAT/EXE/portable確認は残工程に入れない。

---

## 10. 直近PR履歴

| PR | タイトル | 意味 |
|---:|---|---|
| #152 | `feat: normalize link management labels` | 関連付けUIの表示名/ID混在を解消。現在open/merge前 |
| #151 | `feat: add base title subtitle summary counters` | `TitleSubtitleManagementTab` 本体にsummary追加 |
| #150 | `feat: add title list summary counters` | タイトル管理focused tabにsummary追加 |
| #149 | `feat: add subtitle list summary counters` | サブタイトル管理focused tabにsummary追加 |
| #148 | `feat: add name list summary counters` | 名前管理にsummary追加 |
| #147 | `feat: enrich search tab summaries` | 検索タブsummary強化系。merge済みかは必要時に再確認 |
| #146 | `feat: polish workflow navigation guidance` | workflow navigation guidance追加 |
| #145 | `feat: polish table readability and microcopy` | table readability/microcopy改善 |
| #144 | `feat: polish title management target context` | タイトル管理の対象文脈改善 |
| #143 | `fix: block restore to active database` | restore safety系 |

---

## 11. 品質ゲート / CI失敗時フロー

GitHub Actions `Quality Gates` が基本ゲート。

CI失敗時の基本フロー:

1. 必ず最新head commitに紐づくrunを見る。
2. 古いcommitのrunを見て判断しない。
3. `fetch_commit_workflow_runs` で対象commitのrunを確認。
4. `fetch_workflow_run_jobs` で失敗jobを確認。
5. artifactがある場合はartifactを優先して確認する。
6. artifactがない場合はjob logs/stepsを確認する。
7. 失敗原因を1つずつ修正する。
8. 修正後は新commit SHAでCIを確認する。
9. successになるまで繰り返す。
10. success後、レビュー指摘を確認する。
11. 妥当な指摘が残っていなければsquash mergeする。

同じ種類の失敗が3回以上続く場合:

- 局所修正を続ける前に、仕様・テスト期待値・実装差分の整合性を再レビューする。
- 特にUAT系テストでは、現行UI仕様に追従しているか確認する。

よくある失敗:

- ruff E501
- ruff UP035
- pytestでUAT旧仕様期待値
- PySide6属性名変更にテストが追従していない
- optional UI要素を常在前提でassertしている

ruff修正ルール:

- まず実装/テストの整形で直す。
- 既存UIファイルの運用上どうしても妥当な場合のみ、`pyproject.toml` の per-file-ignores を追加する。
- ignore追加は最小範囲・最小ルールに限定する。

---

## 12. UI改善ポリシー

| 原則 | 内容 |
|---|---|
| 表示名中心 | 人間が読む主表示は名前・タイトル・サブタイトル名を中心にする |
| IDは補助情報 | 公開ID・内部ID・リンクIDはtooltip、詳細表示、補助列へ移す |
| 対象明示 | 編集/削除/解除対象が一目で分かるようsummary/カード/選択行で示す |
| 件数明示 | 一覧件数、表示中、選択中、有効/削除済み件数をsummaryに出す |
| role整合 | viewer/editor/adminで表示・実行可否を明確にする |
| 危険操作明示 | 削除/復元/完全削除は対象名・ID・状態・不可逆性を出す |
| 共通化 | 似たsummary/card/toolbar/empty stateは共通部品化する |
| テスト必須 | UI変更は表示文字列・tooltip・role guard・UAT系を更新する |

---

## 13. PR #152 merge後の残工程

| 優先度 | 残工程 | 難易度 | 内容 |
|---:|---|---:|---|
| P2 | `DELETE-FLOW-CLARITY` | 4 | 削除/復元/完全削除の対象明示・危険操作UI改善 |
| P2 | `USER-MGMT-VISUAL-POLISH` | 4 | ユーザー管理UIの視認性改善 |
| P2 | `TITLE-MGMT-SELECTION-REDESIGN` | 7 | タイトル編集/削除対象をドロップダウンから一覧＋検索へ変更 |
| P2 | `SUBTITLE-MGMT-SELECTION-REDESIGN` | 6 | サブタイトル編集/削除対象も一覧＋検索へ変更 |
| P2 | `SHARED-RICH-UI-COMPONENTS` | 6 | 共通カード/summary/toolbar/empty state化 |
| P3 | `AUDIT-DATAIO-HELP-POLISH` | 4 | 監査ログ・データ入出力・ヘルプのUI磨き込み |

推奨順:

1. PR #152 merge
2. `DELETE-FLOW-CLARITY`
3. `USER-MGMT-VISUAL-POLISH`
4. `TITLE-MGMT-SELECTION-REDESIGN`
5. `SUBTITLE-MGMT-SELECTION-REDESIGN`
6. `SHARED-RICH-UI-COMPONENTS`
7. `AUDIT-DATAIO-HELP-POLISH`

---

## 14. 任意確認コマンド

通常UAT。これは残工程ではなく、人間がやりたい時だけ実行する任意確認。

```powershell
git switch main
git pull --ff-only
git status

python -m ruff check .
python -m black --check .
python -m mypy app
python -m pytest -q

.\scripts\reset_uat_demo_windows.ps1 -Launch

git status
```

EXE/portable確認。これも任意確認。

```powershell
git switch main
git pull --ff-only
git status

$ReleaseName = "v0.3.0-ui-polish-uat"
.\scripts\build_exe_windows.ps1
.\scripts\smoke_test_exe_windows.ps1
.\scripts\package_release_windows.ps1 -ReleaseName $ReleaseName
.\scripts\smoke_test_portable_windows.ps1 -ReleaseName $ReleaseName -StartupSeconds 5

git status
```

---

## 15. 回答フォーマット

毎回、最低限以下を含める。

1. 要点サマリ
2. 今回実施した作業
3. 現在状態
4. 完了済みを除いた残工程一覧
5. 任意確認コマンドは必要時のみ

特に、残工程一覧は毎回必須。
手元確認/UAT/EXE/portable確認は、残工程に入れない。
