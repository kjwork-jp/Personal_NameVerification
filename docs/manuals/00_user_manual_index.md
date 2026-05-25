# NameVerification ユーザー向けマニュアル入口

## 目的

このページは、通常利用者・運用担当者が読む文書の入口です。
release証跡、開発台帳、実装計画はここでは扱いません。

## まず読む文書

| 用途 | 文書 | 対象 |
|---|---|---|
| 初回説明 | `NameVerification_初回教育用_簡易マニュアル.md` | 初めて触る人 |
| 通常操作 | `NameVerification_運用操作マニュアル_機能説明.md` | 日常利用者 / 運用担当 |
| 詳細手順 | `NameVerification_運用手順書_詳細版.md` | Day0 / Day1担当 |

## 利用者向けの基本ルール

- 起動後はローカルログインを行う。
- 通常確認は「検索」から行う。
- 登録・更新は各管理タブで行う。
- 復元・完全削除は削除データタブに集約する。
- Export / Backup / Restore / Import はデータ入出力タブで行う。
- DB / backup / export / log はOS上のファイルなので、保存先のアクセス権に注意する。

## ロール早見

| role | 主な用途 |
|---|---|
| viewer | 参照のみ |
| editor | 通常登録・更新・export・backup |
| admin | destructive操作、import、restore、ユーザー管理 |

## 読まなくてよい文書

通常利用者は、以下を読む必要はありません。

- release evidence
- v0.x backlog
- migration計画
- 実装台帳
- CI/CD証跡

これらは `docs/release_ledger/00_release_ledger_index.md` 側で扱います。
