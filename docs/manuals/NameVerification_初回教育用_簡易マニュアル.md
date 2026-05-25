# NameVerification 初回教育用 簡易マニュアル

## 位置づけ

この文書は、初めて NameVerification を触る人向けの最短説明です。
release証跡、開発台帳、CI詳細は扱いません。

## 最初に覚える5点

1. 画面表示は日本語。
2. ID は自動採番。新規作成時に手入力しない。
3. 操作対象は一覧選択で指定する。
4. viewer は参照専用、editor は通常登録/更新、admin は destructive 操作を含む管理者。
5. DB / backup / export / log はローカルファイルなので、保存先のアクセス権にも注意する。

## 初回ログイン

- active user が0件の場合、初回admin作成画面で管理者を作成する。
- 通常起動時は operator_id と password でログインする。
- role はログインユーザーに紐づく `viewer` / `editor` / `admin` を使う。

## まず実施する操作

1. アプリを起動してログインする。
2. 「検索」で既存データの見え方を確認する。
3. 「名前を管理」で名前を作成する。
4. 「タイトル/サブタイトル管理」でタイトルを作成し、必要ならサブタイトルも作成する。
5. 「関連付け」で名前とサブタイトルの例外的な関連登録/解除を確認する。
6. 「削除データ」で復元/完全削除が集約されていることを確認する。
7. 「データ入出力」で CSV / JSON / SQL出力、backup、operations log を確認する。
8. 「ヘルプ/設定」でDB保存先、log保存先、保護対象パス診断を確認する。

## 主要タブ早見

| タブ | 最初に見るポイント |
|---|---|
| 検索 | 名前・タイトル・サブタイトルを横断検索できる |
| 名前を管理 | 一覧を選んで名前を確認・更新する |
| タイトル/サブタイトル管理 | タイトル一覧・サブタイトル一覧を起点に操作する |
| 関連付け | 名前とサブタイトルの関連を登録/解除する |
| 削除データ | 復元/完全削除を行う。admin前提 |
| 操作履歴 | DB内 change_logs を確認する |
| ユーザー管理 | admin専用。local userを管理する |
| ユーザー監査ログ | admin専用。login/user管理auditを確認する |
| データ入出力 | export / backup / restore / import / operations logを扱う |
| ヘルプ/設定 | 保存先、環境変数、保護対象パスを確認する |

## RBAC最小ルール

| role | できること | できないこと |
|---|---|---|
| viewer | 検索・参照 | 登録、更新、export、backup、restore、import、削除 |
| editor | 通常登録/更新、export、backup | destructive操作、restore、import、ユーザー管理 |
| admin | すべての管理操作 | なし。ただしOSファイル保護は別途必要 |

## データ入出力の注意

- SQL dump は full DB dump として扱う。
- 共有用JSON出力は認証・管理・設定系テーブルを除外する用途。
- Restore / Import は destructive 操作なので admin のみ。
- 重要操作前には backup を取得する。

## 初回確認の合格ライン

- ログインできる。
- 検索でデータを確認できる。
- 一覧選択でフォームが更新される。
- roleに応じてボタンが有効/無効になる。
- export / backup の保存先を説明できる。
- Help / Settings でDB/log/export/backupの場所を説明できる。
