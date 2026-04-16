# 40_test_strategy.md

## 1. 目的
品質保証の全体戦略を定義する。

## 2. テストレベル
- Unit Test
- Integration Test
- UI smoke test
- UAT
- Pre-Go-Live Review

## 3. 原則
- 仕様に紐づくテストを作る
- バグ修正には再発防止テストを付ける
- 権限、削除、復旧、インポートは必ずテストする

## 4. 優先対象
- 正規化
- 一意制約
- 権限制御
- 状態遷移
- Export / Import
- Backup / Restore
- Audit logging

## 5. UAT の位置づけ
UAT は利用者観点での受入判定であり、単体テストの代替ではない。
