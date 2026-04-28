# 45_uat_plan.md

## 1. 目的
利用者観点で NameVerification v3 の受入可否を判定する。

## 2. 主要シナリオ
1. 名前検索
2. 名前新規登録
3. タイトル / サブタイトル登録
4. 名前とサブタイトル紐づけ
5. 更新
6. 論理削除
7. 復元
8. 完全削除
9. CSV / JSON Export
10. Import
11. バックアップ
12. 復旧
13. 監査ログ確認
14. Operations ログビューア確認（source切替 / filter / regex flags / paging / 表示件数）

## 3. 判定
- 全シナリオ成功で Go 候補
- 業務影響のある Fail が 1 件でもあれば No-Go


## 4. UAT 実施前の固定条件
- UAT対象ビルドの Git SHA を明示し、記録する。
- UAT期間中は対象SHAを変更しない（修正時は再ビルドし、別SHAとして再判定）。
- 実施記録には実行日（YYYY-MM-DD）と担当者名を残す。
