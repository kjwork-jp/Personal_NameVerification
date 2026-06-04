# 101_unique_display_name_policy_20260604.md

## 1. 目的
2026-06-04 の UAT 画像レビューで、タイトル `test` の重複登録が確認された。

名前・タイトル・サブタイトルの表示名が重複すると、一覧やドロップダウンで内部IDや公開IDを併記しないと識別できず、利用者向け UI が複雑になる。本書は、実装前に重複登録禁止の仕様を固定する。

## 2. 対象
対象エンティティは以下とする。

- `names`
- `titles`
- `subtitles`

対象操作は以下とする。

- 新規作成
- 更新
- 復元
- CSV / JSON import
- backup restore 後の整合性確認

## 3. 正規化方針
重複判定は表示名そのものではなく、比較用の正規化値を主キー候補として扱う。

正規化は既存の `normalize_for_comparison` と同等の処理を前提にする。

- Unicode NFKC 正規化を行う
- 制御文字を空白扱いにする
- 連続空白を単一空白へ畳み込む
- 前後空白を除去する
- 大文字小文字差異を吸収する
- 正規化後に空文字になる値は validation error とする

## 4. 表示名完全一致と正規化値一致の扱い
表示名の完全一致は重複として扱う。ただし、重複判定の最終基準は正規化値一致とする。

| 入力例 | 正規化後 | 判定 |
| --- | --- | --- |
| `test` と `test` | `test` と `test` | 重複 |
| `test` と ` Test ` | `test` と `test` | 重複 |
| `ABC` と `abc` | `abc` と `abc` | 重複 |
| `ＡＢＣ` と `ABC` | `abc` と `abc` | 重複 |
| `A  B` と `A B` | `a b` と `a b` | 重複 |

表示名は利用者が入力した値を保持する。正規化値は検索・一意判定・import 検証・復元検証に使用する。

## 5. 名前のユニーク方針
`names` は、削除未済の範囲で `normalized_name` を全体一意にする。

- 新規作成時、同じ `normalized_name` を持つ削除未済の名前がある場合は拒否する
- 更新時、自分以外の削除未済行と `normalized_name` が一致する場合は拒否する
- 復元時、復元対象と同じ `normalized_name` を持つ削除未済行がある場合は拒否する
- 削除済み行どうしの重複は許容する
- 完全削除後は同じ表示名を新規登録できる

DB 制約は SQLite partial unique index を想定する。

```sql
CREATE UNIQUE INDEX uq_names_normalized_name_active
ON names(normalized_name)
WHERE deleted_at IS NULL;
```

## 6. タイトルのユニーク方針
`titles` は、削除未済の範囲で正規化後タイトル名を全体一意にする。

現行 schema に比較用列がない場合は、実装時に `normalized_title_name` を追加する。

- 新規作成時、同じ `normalized_title_name` を持つ削除未済のタイトルがある場合は拒否する
- 更新時、自分以外の削除未済行と `normalized_title_name` が一致する場合は拒否する
- 復元時、復元対象と同じ `normalized_title_name` を持つ削除未済行がある場合は拒否する
- タイトルに関連付く名前が異なっていても、タイトル名は全体で一意にする
- 削除済み行どうしの重複は許容する

DB 制約は以下を想定する。

```sql
CREATE UNIQUE INDEX uq_titles_normalized_title_name_active
ON titles(normalized_title_name)
WHERE deleted_at IS NULL;
```

## 7. サブタイトルのユニーク方針
`subtitles` は、削除未済の範囲で `title_id + normalized_subtitle_name` を一意にする。

現行 schema に比較用列がない場合は、実装時に `normalized_subtitle_name` を追加する。

- 新規作成時、同じ親タイトル配下に同じ `normalized_subtitle_name` を持つ削除未済のサブタイトルがある場合は拒否する
- 更新時、自分以外の削除未済行と `title_id + normalized_subtitle_name` が一致する場合は拒否する
- 親タイトル変更を伴う更新時も、移動先タイトル配下で重複判定する
- 復元時、復元対象と同じ `title_id + normalized_subtitle_name` を持つ削除未済行がある場合は拒否する
- 異なるタイトル配下の同名サブタイトルは許容する
- 全体一覧やドロップダウンでは、必要に応じて `タイトル名 / サブタイトル名` を表示して識別する
- 削除済み行どうしの重複は許容する

DB 制約は以下を想定する。

```sql
CREATE UNIQUE INDEX uq_subtitles_title_normalized_subtitle_name_active
ON subtitles(title_id, normalized_subtitle_name)
WHERE deleted_at IS NULL;
```

既存の `title_id + subtitle_code` 一意制約は、管理番号の一意性として維持する。サブタイトル表示名の一意制約とは別の責務とする。

## 8. deleted_at の扱い
新規作成・更新のユニーク判定では、`deleted_at IS NULL` の行だけを対象にする。

`deleted_at IS NOT NULL` の行を新規作成・更新時の一意判定に含めない理由は以下である。

- 論理削除後に同じ業務名を再登録できる
- 過去データを監査・復元用に保持しながら、現在有効な候補だけを UI に表示できる
- 既存の `names.normalized_name` 設計と整合する

ただし、復元時は削除済み行を有効行へ戻すため、復元後に active unique constraint へ違反する場合は復元を拒否する。

## 9. 既存重複データがある場合の移行方針
DB 制約追加前に既存データを調査し、重複が残ったまま migration を適用しない。

移行手順は以下とする。

1. `names.normalized_name`、`titles.normalized_title_name`、`subtitles.title_id + normalized_subtitle_name` の重複候補を抽出する。
2. `deleted_at IS NULL` の重複を blocker として migration を停止する。
3. 重複ごとに canonical row を1件選ぶ。
4. 非 canonical row に紐づく link、note、icon、監査上必要な情報を棚卸しする。
5. 統合可能な link は canonical row へ付け替える。
6. 統合できない表示差分は note または別フィールドへの退避を検討する。
7. 非 canonical row は原則として論理削除する。
8. 論理削除できない業務理由がある場合は、表示名を利用者合意済みの別名へ変更する。
9. 重複が解消したことを再検査する。
10. 正規化値列の backfill 後、partial unique index を作成する。

移行レポートには以下を残す。

- 対象テーブル
- 重複キー
- 対象 row の ID / public_id
- canonical row
- 変更内容
- link 付け替え有無
- 操作者
- 実施日時

## 10. UI上のエラーメッセージ案
DB エラー文は直接表示しない。service validation または DB 制約違反を利用者向け日本語メッセージに変換する。

| 操作 | メッセージ案 |
| --- | --- |
| 名前作成 | `同じ名前がすでに登録されています。登録済みの名前を確認してください。` |
| 名前更新 | `同じ名前の有効データがすでにあります。別の名前に変更してください。` |
| 名前復元 | `同じ名前の有効データがあるため復元できません。先に重複先を変更または削除してください。` |
| タイトル作成 | `同じタイトルがすでに登録されています。登録済みのタイトルを選択してください。` |
| タイトル更新 | `同じタイトル名の有効データがすでにあります。別のタイトル名に変更してください。` |
| タイトル復元 | `同じタイトル名の有効データがあるため復元できません。先に重複先を変更または削除してください。` |
| サブタイトル作成 | `同じタイトル内に同じサブタイトルがすでに登録されています。` |
| サブタイトル更新 | `同じタイトル内に同じサブタイトル名の有効データがすでにあります。` |
| サブタイトル復元 | `同じタイトル内に同じサブタイトルがあるため復元できません。先に重複先を変更または削除してください。` |
| import | `重複データが含まれているため import できません。重複一覧を確認してください。` |

可能であれば、エラー詳細には競合対象の表示名と短縮 public_id を出す。ただし、通常操作のドロップダウンや一覧で内部IDを識別目的として常時表示する状態には戻さない。

## 11. DB制約 / service validation / UI事前チェックの役割分担
### 11.1 DB制約
DB 制約は最終防衛線とする。

- 同時操作、import、将来の別 UI、手動スクリプト実行でも一意性を守る
- partial unique index で `deleted_at IS NULL` の有効行だけを対象にする
- 制約違反は domain の `ConflictError` 相当に変換する
- migration 前に既存重複がないことを必ず確認する

### 11.2 service validation
service validation は業務仕様の主判定とする。

- 入力値を正規化し、空文字を拒否する
- 作成・更新・復元・import の各操作で同じ重複判定を使う
- 更新時は自分自身を重複候補から除外する
- 復元時は active row との衝突を検査する
- 競合対象を UI メッセージへ渡せる形で返す
- DB 制約違反が発生した場合も同じ利用者向けメッセージへ正規化する

### 11.3 UI事前チェック
UI 事前チェックは利用者体験の改善を目的とする。DB 制約や service validation の代替にはしない。

- 入力欄の空白だけ入力を早期に拒否する
- 画面上で取得済みの候補と正規化比較し、明らかな重複を登録前に知らせる
- 候補一覧が古い可能性を考慮し、最終判定は service / DB に委ねる
- 競合時は登録済みデータの選択導線や一覧再読込を促す

## 12. 受け入れ条件
本仕様を実装する PR の受け入れ条件は以下とする。

- [ ] 名前の新規作成で、表示名完全一致の重複が拒否される
- [ ] 名前の新規作成で、正規化値一致の重複が拒否される
- [ ] 名前の更新で、自分以外の有効行と正規化値が一致する場合に拒否される
- [ ] タイトルの新規作成で、表示名完全一致の重複が拒否される
- [ ] タイトルの新規作成で、正規化値一致の重複が拒否される
- [ ] タイトルの更新で、自分以外の有効行と正規化値が一致する場合に拒否される
- [ ] サブタイトルの新規作成で、同じタイトル配下の表示名完全一致重複が拒否される
- [ ] サブタイトルの新規作成で、同じタイトル配下の正規化値一致重複が拒否される
- [ ] サブタイトルの更新で、自分以外の有効行と `title_id + normalized_subtitle_name` が一致する場合に拒否される
- [ ] 異なるタイトル配下の同名サブタイトルは登録できる
- [ ] 削除済み行だけと重複する新規作成は登録できる
- [ ] active row と衝突する削除済み行の復元は拒否される
- [ ] import 時に active row の重複候補が検出され、import が拒否される
- [ ] 既存重複データがある DB では、unique index 追加 migration が停止する
- [ ] DB 制約違反が発生しても、利用者には日本語の重複メッセージが表示される
- [ ] 通常の一覧・ドロップダウンで、重複識別のためだけに内部IDを常時表示する必要がない
- [ ] docs、migration、service、UI、tests の責務が本書の役割分担と一致している

## 13. 今回の PR 範囲
今回の PR は docs-only とし、コード・DB schema・migration・テストは変更しない。

実装 PR は本書を参照して、1 PR 1目的で分割する。
