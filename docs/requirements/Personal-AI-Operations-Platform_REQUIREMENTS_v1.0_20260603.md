# Personal AI Operations Platform 要件定義書 v1.0

- 文書ID: PAIOP-REQ-v1.0-20260603
- 対象リポジトリ: `kjwork-jp/Personal-AI-Operations-Platform`
- 作成日: 2026-06-03
- ステータス: 確定版 v1.0
- 所有者: Naoki Kajiwara
- 主目的: ローカル環境・Web環境・GitHub・Supabase・ChatGPT・AI開発支援サービスを統合し、人間が1人増えたような実務代行基盤を構築する。

---

## 1. 要点サマリ

Personal AI Operations Platform は、ChatGPT UI の自動継続、GitHub/Supabase 許可ダイアログの自動承認、ローカルファイル入出力、Web/OS/CLI 操作、AIレビュー、証跡保存、チャット引き継ぎを統合する個人向けAI運用基盤である。

最終構成は、**Windmill + Playwright CDP + Power Automate Desktop + Skyvern/Stagehand + 1Password CLI + GitHub Actions + Supabase CLI + Reviewer AI** を中核とする。n8n は連携・通知・軽量ワークフロー用の補助候補、UiPath は将来の重厚RPA候補とする。

この基盤では、人間は初期アイデア、2日に1回程度の非停止レビュー、サブスク費用判断、最終受入を中心に担当する。要件定義、設計、Issue分解、実装、テスト、PR、CI修正、台帳更新、引き継ぎ、ローカル操作、Web操作はAI/サービス側へ最大限委譲する。

---

## 2. 用語定義

| 用語 | 定義 |
|---|---|
| PAIOP | Personal AI Operations Platform の略称。個人向けAI統合運用基盤。 |
| Autopilot Controller | ChatGPT UI、ローカル実行、外部AI、状態管理を統括する制御プロセス。 |
| Browser Controller | Playwright CDP等でブラウザを監視・操作するコンポーネント。 |
| CDP | Chrome DevTools Protocol。既存Chromeへ外部プロセスから接続・操作する仕組み。 |
| Local Agent | ローカルPC上のファイル、Git、CLI、PowerShell、Python、Node等を操作する実行主体。 |
| Reviewer | 直前回答・成果物・CLI結果を評価し、継続/修正/引き継ぎを判断するAIまたはルール。 |
| FSM | Finite State Machine。状態遷移を明示して誤送信・重複実行を防ぐ制御方式。 |
| Ledger | 送信、承認、ダウンロード、アップロード、コマンド実行などの監査ログ。 |
| Handoff | 長いチャットを新規チャットへ移すための引き継ぎ資料・状態整理。 |

---

## 3. 背景・前提

### 3.1 背景

現在のAI作業では、ChatGPT、Devin、Codex、Claude、GitHub Actions、Supabase、1Password、ローカルPC、ブラウザ操作が分断されている。特に以下がボトルネックになっている。

- ChatGPTのGitHub/Supabase許可ダイアログで作業が止まる。
- 回答完了後に人間が毎回「次のアクションに進んでください」と送る必要がある。
- 長いチャットが重くなり、引き継ぎ漏れが起きる。
- ローカルファイルアップロード、GPT出力保存、ダウンロード回収が手動になる。
- GitHub/Supabase/1Password/ローカルCLIの横断作業が手動またはツールごとに分断される。

### 3.2 基本方針

- 最小構成ではなく、最終的にローカル上もWeb上も最大限自動化する。
- ただし、0→1の不安定さを避けるため、巨大な完全自作エージェントは作らない。
- 既製ツールを最大限利用し、ChatGPT UI制御など不足部分のみ薄い自作Controllerで補う。
- GitHub Actions化、Devin/CodexへのGitHub権限付与は前提とする。
- それでも残るChatGPT UI上の許可・継続・入出力をPAIOPが担当する。

### 3.3 人間とAIの責務分担

| 担当 | 責務 |
|---|---|
| 人間 | 初期アイデア、2日に1回程度の非停止レビュー、サブスク費用判断、最終目視確認・受入。 |
| AI/サービス | 要件、設計、実装、Issue、PR、CI修正、台帳、引き継ぎ、ローカル操作、Web操作、調査、比較、分析、成果物生成。 |
| PAIOP | 複数AI/サービス/CLI/ブラウザを接続し、状態・証跡・次アクションを制御する。 |

---

## 4. スコープ

### 4.1 対象範囲

| 区分 | 対象 |
|---|---|
| ChatGPT UI制御 | 許可ダイアログ承認、回答完了判定、次プロンプト送信、ファイルアップロード、成果物ダウンロード。 |
| GitHub | repo操作、Issue/PR、Actions、branch、commit、push、artifact、review、CI再実行。 |
| Supabase | CLI/API、migration、types生成、DB/RLS/Storage/Auth設定、Edge Functions、環境差分確認。 |
| ローカルPC | PowerShell、Git、gh、supabase、npm、node、python、ファイル操作、zip展開・作成。 |
| AIレビュー | 直前回答、成果物、GitHub/Supabase状態、CLI結果の検査と次アクション判断。 |
| 状態管理 | SQLite/JSONL/Supabaseによるturn、承認、送信、入出力、エラー、引き継ぎ管理。 |
| RPA/AIブラウザ | Power Automate Desktop、Skyvern、Stagehand、Browser Use、Midscene等との連携。 |

### 4.2 対象外

| 区分 | 対象外理由 |
|---|---|
| サブスク契約・解約の自動実行 | 費用判断は人間が最終決定する。 |
| クレジットカード決済の自動実行 | 金銭操作は明示確認を残す。 |
| CAPTCHA/MFAの突破 | ログイン・本人確認は人間または公式導線で処理する。 |
| 1Password外へのsecret平文保存 | secretはvault参照を原則とし、ログ・チャットへ値を出さない。 |
| 本番公開前の最終目視確認の完全省略 | 最終受入は人間が担当する。 |

---

## 5. 採用アーキテクチャ

```text
Windows PC
├─ Dedicated Chrome Profile
│  └─ ChatGPT / GitHub / Supabase Web UI
│
├─ Autopilot Controller
│  ├─ Playwright CDP Browser Controller
│  ├─ Dialog Approver
│  ├─ Response Completion Detector
│  ├─ Prompt Scheduler
│  ├─ Upload Manager
│  ├─ Download Manager
│  ├─ Session Rollover Manager
│  └─ Artifact Collector
│
├─ Local Agent
│  ├─ PowerShell Executor
│  ├─ Git / gh CLI
│  ├─ Supabase CLI
│  ├─ 1Password CLI
│  ├─ Node / Python Runner
│  └─ File / Archive Manager
│
├─ Orchestrator
│  ├─ Windmill: primary
│  └─ n8n: optional workflow / notification layer
│
├─ Browser/RPA Fallback
│  ├─ Power Automate Desktop
│  ├─ Skyvern
│  ├─ Browserbase Stagehand
│  ├─ Browser Use
│  └─ Midscene
│
├─ Reviewer Layer
│  ├─ OpenAI API
│  ├─ Claude API fallback
│  ├─ Gemini API fallback
│  └─ Rule-based verification
│
└─ State / Evidence Store
   ├─ SQLite
   ├─ JSONL logs
   ├─ responses/*.md
   ├─ artifacts/*
   ├─ downloads/*
   ├─ screenshots/*
   ├─ dom_snapshots/*
   └─ handoff/*
```

---

## 6. 採用ツール方針

| レイヤー | 採用 | 位置づけ |
|---|---|---|
| 統合オーケストレーター | Windmill | 主担当。code-firstでPython/TS/Bash/Flowを統合。 |
| 補助ワークフロー | n8n | Webhook、通知、軽量連携、可視化用。 |
| ChatGPT UI制御 | Playwright CDP | 主担当。専用Chromeへ接続し、DOM/Role/Textで操作。 |
| Windows RPA | Power Automate Desktop | ローカルWindows GUI・ファイル・Excel・ブラウザ補助操作。 |
| Web自動化fallback | Skyvern / Stagehand | 不安定Web UI、フォーム、抽出、DOM破損時の補助。 |
| Vision fallback | Midscene | DOMで取れないボタン・画面状態の視覚判定。 |
| 開発/PR | Devin / Codex / GitHub Actions | 実装、PR、CI修正、自動テスト。 |
| Secret管理 | 1Password CLI | secretの唯一の信頼ソース。 |
| DB/BaaS | Supabase CLI/API | migration、types、RLS、Storage、Edge Functions管理。 |
| 状態DB | SQLite → Supabase/Postgres | 初期はローカルSQLite、後にクラウド同期。 |

---

## 7. 機能要件

### 7.1 ChatGPT UI制御

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-UI-001 | 専用Chromeプロファイルを起動し、CDPで接続できる。 | P0 | `chatgpt.com` の既存ログインセッションを操作できる。 |
| F-UI-002 | GitHub系の全許可ダイアログで「許可する」を自動クリックする。 | P0 | ダイアログ近傍にGitHubが含まれる場合、内容を問わず許可する。 |
| F-UI-003 | Supabase系の全許可ダイアログで「許可する」を自動クリックする。 | P0 | ダイアログ近傍にSupabaseが含まれる場合、内容を問わず許可する。 |
| F-UI-004 | 「許可する」がグレーアウトしている場合、有効化まで待機する。 | P0 | enabledになるまで最大待機し、force clickは使わない。 |
| F-UI-005 | 同一許可ダイアログを連打しない。 | P0 | dialog hash、cooldown、clicked ledgerで重複クリックを防止。 |
| F-UI-006 | 回答完了後だけ次プロンプトを送信する。 | P0 | 回答中、ツール実行中、許可待ち中には送らない。 |
| F-UI-007 | 次プロンプト文言を内部キューで保持する。 | P0 | 既定値は「次のアクションに進んでください」。 |
| F-UI-008 | 回答完了を複合判定する。 | P0 | Stopボタン消失、入力欄enabled、最終回答安定、許可なしを満たす。 |
| F-UI-009 | フォローアップ質問や確認待ちを検出する。 | P1 | ReviewerでCONTINUE/FIX/HANDOFF/BLOCKEDを判定する。 |
| F-UI-010 | UI変更時に複数セレクタ・DOM scan・Vision fallbackへ切り替える。 | P1 | 主要UI変更後も復旧可能なログを残す。 |

### 7.2 自動継続・チャットローテーション

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-CH-001 | turn数をSQLiteで永続管理する。 | P0 | 再起動後も現在turnを復元できる。 |
| F-CH-002 | 50回目で引き継ぎ準備モードへ強制移行する。 | P0 | 50回目に専用プロンプトを送る。 |
| F-CH-003 | 50〜60回目は引き継ぎ準備に使う。 | P0 | 完了済み、残件、成果物、PR、CI、DB、エラー、次手順を整理する。 |
| F-CH-004 | 60回目で新チャット移行を行う。 | P1 | 新チャット初回プロンプトと引き継ぎファイルを生成・投入する。 |
| F-CH-005 | 長チャット重化対策として定期snapshotを保存する。 | P1 | 40回目、50回目、60回目にcheckpointを保存。 |
| F-CH-006 | 同一プロンプト連投を防止する。 | P0 | prompt hashとturn idで重複送信を抑止。 |

### 7.3 ファイル入出力

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-FILE-001 | ローカルファイルをChatGPTへアップロードできる。 | P0 | `setInputFiles` または `filechooser` で添付できる。 |
| F-FILE-002 | 複数ファイルのアップロードキューを管理する。 | P1 | 失敗時に再試行、分割、manifest送信へ切替できる。 |
| F-FILE-003 | ChatGPTの通常回答をMarkdownとして保存する。 | P0 | turnごとに `responses/turn_XXX.md` へ保存。 |
| F-FILE-004 | 回答内コードブロックを個別ファイル化する。 | P1 | 言語推定・拡張子付与・manifest記録を行う。 |
| F-FILE-005 | ChatGPT生成ファイルをローカルへダウンロード保存する。 | P0 | download eventを捕捉し、保存先を制御する。 |
| F-FILE-006 | ダウンロード取り逃しを検出する。 | P1 | ダウンロードフォルダ監視とファイルサイズ安定待ちを行う。 |
| F-FILE-007 | 成果物manifestを生成する。 | P0 | turn、prompt、response、uploads、downloads、approvalsを記録。 |
| F-FILE-008 | 大容量ファイルは直接添付せず、GitHub/Supabase Storage等を使う。 | P1 | ChatGPTへはmanifestまたはリンク情報を渡す。 |

### 7.4 ローカル操作

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-LOCAL-001 | PowerShellコマンドを実行し、stdout/stderr/exit codeを保存する。 | P0 | コマンドごとにJSONLログが残る。 |
| F-LOCAL-002 | Git操作を実行できる。 | P0 | status/diff/branch/commit/pushが実行・記録できる。 |
| F-LOCAL-003 | GitHub CLIを実行できる。 | P0 | PR、workflow、artifact、issueの操作が可能。 |
| F-LOCAL-004 | Supabase CLIを実行できる。 | P0 | migration、types、functions、db diff等を扱える。 |
| F-LOCAL-005 | 1Password CLIからsecretを参照できる。 | P0 | secret値をログやチャットに出さず、環境変数注入できる。 |
| F-LOCAL-006 | Node/Pythonスクリプトを実行できる。 | P1 | 依存関係、venv、npm scriptを検査できる。 |
| F-LOCAL-007 | 作業ディレクトリ外への不用意な書き込みを制限する。 | P1 | allowlistされたworkspace配下を基本操作対象にする。 |
| F-LOCAL-008 | zip/7z展開・作成を扱える。 | P1 | 成果物一式や引き継ぎ一式を作成できる。 |

### 7.5 GitHub/Supabase連携

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-GH-001 | GitHub Actions化を前提にワークフロー実行・再実行できる。 | P0 | failed job rerun、workflow_dispatch相当を扱える。 |
| F-GH-002 | Devin/CodexによるGitHub権限利用を前提にする。 | P0 | PAIOPは不足するUI承認・状態整理を補完する。 |
| F-GH-003 | PR/Issue/commit/branch状態を取得してReviewerへ渡す。 | P1 | 次アクション判断にGitHub状態を反映する。 |
| F-SB-001 | Supabase CLI/API状態を取得してReviewerへ渡す。 | P1 | migration、RLS、Storage、Auth、Functions状態を確認できる。 |
| F-SB-002 | Supabase関連許可ダイアログは全承認する。 | P0 | ChatGPT UI上のSupabase許可は内容を問わず押下する。 |

### 7.6 Reviewer

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-REV-001 | 直前回答の完了性をレビューする。 | P0 | 未完了・矛盾・成果物不足を検出できる。 |
| F-REV-002 | CONTINUE/FIX/HANDOFF/BLOCKEDを返す。 | P0 | 判定に応じて次プロンプト、修正依頼、引き継ぎ、停止通知を選ぶ。 |
| F-REV-003 | FIX時は具体的な修正依頼を生成する。 | P1 | 抽象的な「修正して」ではなく不足点を指定する。 |
| F-REV-004 | ルールベース検査をLLM判定より優先する。 | P1 | ファイル有無、CLI exit code、manifest整合性は機械的に判定する。 |
| F-REV-005 | 重要作業は複数モデルレビューを可能にする。 | P2 | OpenAI/Claude/Gemini等の二重レビューを設定できる。 |

### 7.7 監査・証跡

| ID | 要件 | 優先度 | 受入条件 |
|---|---|---:|---|
| F-LOG-001 | 全送信プロンプトを保存する。 | P0 | turn、timestamp、source、hashを記録。 |
| F-LOG-002 | 全回答を保存する。 | P0 | Markdown、HTML snapshot、必要に応じてスクショを保存。 |
| F-LOG-003 | 全許可クリックを保存する。 | P0 | provider、dialog text hash、before/after screenshotを記録。 |
| F-LOG-004 | 全ローカルコマンドを保存する。 | P0 | command、cwd、exit code、stdout/stderr pathを記録。 |
| F-LOG-005 | エラー時はスクショ・DOM snapshot・ログを保存する。 | P0 | 復旧に必要な証跡が残る。 |
| F-LOG-006 | 人間向け台帳と機械向け詳細ログを分離する。 | P1 | 人間向けは要約、機械向けは詳細JSONL。 |

---

## 8. 非機能要件

| ID | 要件 | 優先度 | 指標 |
|---|---|---:|---|
| NF-001 | 24時間以上の常駐運用に耐える。 | P1 | Watchdogにより停止検出・再起動可能。 |
| NF-002 | 送信誤爆を防止する。 | P0 | 回答完了判定を満たすまで送信しない。 |
| NF-003 | クリック誤爆を防止する。 | P0 | GitHub/Supabase近傍判定を満たす許可ボタンのみ押す。 |
| NF-004 | グレーアウト状態を正しく待つ。 | P0 | enabled待ち、timeout、再検出を行う。 |
| NF-005 | UI変更に耐える。 | P1 | role locator、text locator、DOM scan、Vision fallbackを持つ。 |
| NF-006 | ログイン切れ/MFAを検出する。 | P1 | 手動復旧が必要な状態として通知する。 |
| NF-007 | secretを漏えいさせない。 | P0 | 1Password参照名のみログ化し、値は保存しない。 |
| NF-008 | 再現可能性を担保する。 | P0 | prompt、response、command、artifact、commitを紐づける。 |
| NF-009 | 失敗ループを防止する。 | P0 | 同一エラー署名の再試行上限を持つ。 |
| NF-010 | 拡張容易性を担保する。 | P1 | tool adapter方式でRPA/AI/CLIを差し替え可能にする。 |

---

## 9. 権限・承認ポリシー

### 9.1 GitHub/Supabase許可ダイアログ

- ChatGPT UI上にGitHubまたはSupabase関連の許可ダイアログが出た場合、PAIOPは内容を問わず「許可する」を自動クリックする。
- これは拒否判定を行わない方針とする。
- ただし、GitHub/Supabaseと判定できない許可ボタンは対象外とし、誤爆防止のため押さない。
- 押下前後のスクリーンショット、ダイアログ本文ハッシュ、timestamp、turn idを必ず保存する。

### 9.2 人間確認が必要な領域

以下は「拒否」ではなく、PAIOPが物理的・契約的・認証的に実行不能な状態として扱う。

- 新規サブスク契約、解約、プラン変更。
- クレジットカード決済。
- MFA、ログイン再認証、本人確認。
- 1Password vault内のsecret値をチャットへ貼る操作。
- 本番公開前の最終受入。

---

## 10. 状態機械

```text
BOOT
  ↓
ATTACH_BROWSER
  ↓
WAIT_READY
  ↓
SEND_PROMPT
  ↓
WAIT_RESPONSE
  ├─ GitHub/Supabase許可あり → WAIT_ALLOW_ENABLED → CLICK_ALLOW → WAIT_RESPONSE
  ├─ ファイルアップロード要求あり → UPLOAD_FILES → WAIT_RESPONSE
  ├─ ダウンロード検出 → COLLECT_DOWNLOADS → WAIT_RESPONSE
  ├─ 回答安定 → SAVE_RESPONSE → REVIEW_RESPONSE
  └─ エラー/ログイン切れ → RECOVERY_OR_NOTIFY

REVIEW_RESPONSE
  ├─ CONTINUE → SEND_NEXT_PROMPT
  ├─ FIX → SEND_FIX_PROMPT
  ├─ HANDOFF → ROLLOVER_PREP
  └─ BLOCKED → NOTIFY_HUMAN
```

---

## 11. チャットローテーション設計

| turn | モード | 動作 |
|---:|---|---|
| 1〜39 | normal | 通常の次アクション継続。 |
| 40 | checkpoint | 軽量checkpointを保存。 |
| 45 | pre-rollover | 引き継ぎ予告と成果物整理を開始。 |
| 50 | rollover_prepare | 以後10回を引き継ぎ準備に使うよう指示。 |
| 51 | completion_summary | 完了済み整理。 |
| 52 | remaining_tasks | 残件整理。 |
| 53 | github_state | GitHub状態整理。 |
| 54 | supabase_state | Supabase状態整理。 |
| 55 | local_artifacts | ローカル成果物整理。 |
| 56 | errors_risks | エラー・懸念整理。 |
| 57 | next_prompt | 新チャット初回プロンプト生成。 |
| 58 | human_summary | 人間向け要約生成。 |
| 59 | ai_handoff | AI向け詳細引き継ぎ生成。 |
| 60 | migrate | 新チャットへ移行。 |

---

## 12. データ設計

### 12.1 SQLite主要テーブル

```sql
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name TEXT NOT NULL,
  chat_url TEXT,
  mode TEXT NOT NULL DEFAULT 'normal',
  turn_count INTEGER NOT NULL DEFAULT 0,
  rollover_start_turn INTEGER NOT NULL DEFAULT 50,
  rollover_final_turn INTEGER NOT NULL DEFAULT 60,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE turns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  turn_no INTEGER NOT NULL,
  prompt TEXT,
  prompt_hash TEXT,
  response_path TEXT,
  reviewer_result TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  turn_id INTEGER,
  provider TEXT NOT NULL,
  dialog_hash TEXT NOT NULL,
  button_text TEXT NOT NULL,
  status TEXT NOT NULL,
  before_screenshot_path TEXT,
  after_screenshot_path TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id),
  FOREIGN KEY(turn_id) REFERENCES turns(id)
);

CREATE TABLE artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  turn_id INTEGER,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id),
  FOREIGN KEY(turn_id) REFERENCES turns(id)
);

CREATE TABLE commands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  turn_id INTEGER,
  cwd TEXT,
  command TEXT NOT NULL,
  exit_code INTEGER,
  stdout_path TEXT,
  stderr_path TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id),
  FOREIGN KEY(turn_id) REFERENCES turns(id)
);
```

---

## 13. ディレクトリ構成

```text
AI_Autopilot/
├─ config/
│  ├─ autopilot.yaml
│  ├─ providers.yaml
│  └─ prompts/
├─ state/
│  ├─ autopilot.sqlite
│  └─ locks/
├─ logs/
│  ├─ jsonl/
│  ├─ stdout/
│  └─ stderr/
├─ responses/
├─ artifacts/
├─ downloads/
├─ uploads/
├─ screenshots/
├─ dom_snapshots/
├─ handoff/
├─ workspaces/
└─ scripts/
```

---

## 14. 設定項目

```yaml
browser:
  cdp_url: "http://127.0.0.1:9222"
  profile_dir: "%USERPROFILE%/chrome-chatgpt-autopilot"
  target_origin: "https://chatgpt.com"

prompt:
  next_action: "次のアクションに進んでください"
  stable_ms: 20000
  next_prompt_cooldown_ms: 8000

approval:
  providers:
    - GitHub
    - Supabase
  allow_all_for_matched_providers: true
  wait_enabled_timeout_ms: 180000
  click_cooldown_ms: 5000
  save_screenshot_before_after: true

rollover:
  checkpoint_turn: 40
  pre_rollover_turn: 45
  start_turn: 50
  final_turn: 60

reviewer:
  enabled: true
  primary: openai
  fallback:
    - claude
    - gemini
  decisions:
    - CONTINUE
    - FIX
    - HANDOFF
    - BLOCKED

local_agent:
  workspace_root: "C:/Users/nkaji/Documents/AI_Autopilot"
  allowed_commands:
    - git
    - gh
    - supabase
    - npm
    - node
    - python
    - powershell
    - op
```

---

## 15. 受入基準

| ID | 受入テスト | 合格条件 |
|---|---|---|
| AC-001 | GitHub許可ダイアログ自動押下 | GitHub表示を含む許可ダイアログでenabled待ち後に押下し、証跡が残る。 |
| AC-002 | Supabase許可ダイアログ自動押下 | Supabase表示を含む許可ダイアログでenabled待ち後に押下し、証跡が残る。 |
| AC-003 | グレーアウト対応 | disabled中は押さず、enabled後に押す。 |
| AC-004 | 回答完了後の自動送信 | 回答途中では送らず、完了後のみ「次のアクションに進んでください」を送る。 |
| AC-005 | 50/60回ローテーション | 50回目で引き継ぎ準備、60回目で新チャット移行準備が発動する。 |
| AC-006 | ファイルアップロード | ローカルファイルを添付し、manifestへ記録できる。 |
| AC-007 | ダウンロード保存 | ChatGPT成果物を任意フォルダへ保存し、manifestへ記録できる。 |
| AC-008 | 回答保存 | turnごとの回答Markdownが保存される。 |
| AC-009 | Reviewer判定 | CONTINUE時は次へ、FIX時は修正依頼、HANDOFF時は引き継ぎへ進む。 |
| AC-010 | Watchdog復旧 | Chrome/Node停止時に検出・再接続または通知できる。 |

---

## 16. 実装フェーズ

| Phase | 内容 | 主担当 |
|---:|---|---|
| 1 | リポジトリ初期構成、要件定義、設計ADR | ChatGPT/Codex |
| 2 | Playwright CDP接続、専用Chrome起動スクリプト | Codex |
| 3 | GitHub/Supabase許可ダイアログ全承認 | Codex |
| 4 | 回答完了判定と次プロンプト送信 | Codex |
| 5 | SQLite状態管理、JSONLログ、スクショ保存 | Codex |
| 6 | 回答本文・コードブロック・ダウンロード保存 | Codex |
| 7 | ローカルファイルアップロード | Codex |
| 8 | 50/60回チャットローテーション | ChatGPT/Codex |
| 9 | Reviewer実装 | ChatGPT/Claude/Codex |
| 10 | Local Agent統合 | Codex/Devin |
| 11 | GitHub/Supabase/1Password CLI統合 | Codex/Devin |
| 12 | Windmill/n8n統合 | Devin/Codex |
| 13 | Power Automate Desktop連携 | 人間初期設定 + AI手順化 |
| 14 | Skyvern/Stagehand fallback | Codex/Devin |
| 15 | Watchdog、常駐化、通知 | Codex |

---

## 17. 残リスク

| リスク | 影響 | 対策 |
|---|---|---|
| ChatGPT UI変更 | selectorが壊れる | 複数locator、DOM snapshot、Vision fallback。 |
| 長時間稼働でChromeが重い | 完了判定遅延、操作失敗 | 50/60回ローテーション、Chrome再起動、checkpoint保存。 |
| AI Reviewer誤判定 | 不完全なまま次へ進む | ルール検査、manifest検査、CLI実確認を優先。 |
| 失敗ループ | 同じエラーを反復 | error signature、retry上限、修正プロンプト生成。 |
| secret漏えい | 認証情報流出 | 1Password参照のみ、値はログ/チャットへ出さない。 |
| 外部入力による指示注入 | 意図しないコマンド実行 | 外部本文を直接system指示にしない。command allowlistを使う。 |
| サブスク費用増 | 予算超過 | 契約・解約・プラン変更は人間確認。 |
| MFA/ログイン切れ | 自動停止 | 検出して通知、手動復旧後再開。 |

---

## 18. 初期バックログ

| ID | タスク | 優先度 | 難易度 |
|---|---|---:|---:|
| B-001 | README/ADR/requirements/docs構成作成 | P0 | 2 |
| B-002 | 専用Chrome起動PowerShell作成 | P0 | 2 |
| B-003 | Playwright CDP接続PoC | P0 | 3 |
| B-004 | GitHub/Supabase許可ボタン検出・enabled待ち・クリック | P0 | 5 |
| B-005 | 回答完了判定FSM | P0 | 6 |
| B-006 | 次プロンプト送信 | P0 | 3 |
| B-007 | SQLite schema実装 | P0 | 4 |
| B-008 | response/artifact/log保存 | P0 | 5 |
| B-009 | 50/60回ローテーション | P1 | 4 |
| B-010 | file upload/download manager | P1 | 6 |
| B-011 | Reviewer API adapter | P1 | 6 |
| B-012 | Local Agent command executor | P1 | 7 |
| B-013 | GitHub/Supabase/1Password CLI adapter | P1 | 7 |
| B-014 | Windmill統合 | P2 | 7 |
| B-015 | PAD/Skyvern/Stagehand fallback | P2 | 8 |

---

## 19. 確定ADR

### ADR-001: 主オーケストレーターはWindmill優先

- 決定: Windmillを主オーケストレーター候補とする。
- 理由: code-firstでPython/TypeScript/Bash/Flowを統合しやすく、今回のCLI/AI/ファイル/状態管理に向く。
- 代替: n8nは通知・Webhook・可視化補助として採用余地を残す。

### ADR-002: ChatGPT UI制御はPlaywright CDPを主担当にする

- 決定: Playwright CDPを主担当にする。
- 理由: 既存ログイン済み専用Chromeに接続でき、DOM/role/textで安定操作できる。
- 代替: Midscene、Skyvern、Stagehandはfallback。

### ADR-003: GitHub/Supabase許可ダイアログは全承認

- 決定: ChatGPT UI上でGitHub/Supabaseと判定できる許可ダイアログは内容を問わず全承認する。
- 理由: GitHub Actions化、Devin/Codex権限付与を前提としても残るUI承認を止めないため。
- 制約: 対象外providerの許可ボタンは押さない。

### ADR-004: 次プロンプトは入力欄常駐ではなく内部キュー保持

- 決定: 「次のアクションに進んでください」は内部キューで保持し、回答完了後のみ入力・送信する。
- 理由: 回答中の誤送信、フォローアップ途中の誤爆を避けるため。

### ADR-005: 50/60回チャットローテーションを標準化

- 決定: 50回目から引き継ぎ準備、60回目で新チャット移行を標準とする。
- 理由: 長チャット重化、文脈混濁、成果物迷子を防ぐため。

### ADR-006: secretは1Passwordを唯一の信頼ソースにする

- 決定: secret値は1Password CLIから参照し、ログ・チャット・repoへ平文保存しない。
- 理由: AI自動化でsecretを扱う場合の漏えい面を最小化するため。

---

## 20. Key Takeaways

- PAIOPは、単なる自動クリックではなく、ローカル・Web・AI・CLI・GitHub・Supabaseを横断する個人AI運用基盤である。
- 主構成は Windmill + Playwright CDP + Power Automate Desktop + Skyvern/Stagehand + 1Password + GitHub Actions + Supabase CLI。
- ChatGPT UI上のGitHub/Supabase許可ダイアログは内容を問わず全承認する。
- 「次のアクションに進んでください」は回答完了後のみ自動送信する。
- 50/60回チャットローテーション、ファイル入出力、Reviewer、証跡保存、Local Agentまで含めて最大設計とする。
