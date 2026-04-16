# 17_state_transition_rules.md

## 1. 目的
主要エンティティの状態遷移を統一する。

## 2. 基本状態
- active
- deleted

## 3. 遷移
### 名前 / タイトル / サブタイトル
- active -> deleted: 論理削除
- deleted -> active: 復元
- deleted -> removed: 完全削除

## 4. ルール
- active の完全削除は原則不可
- 完全削除は deleted を経由する
- 復元時は一意制約再確認を行う
- 関連がある完全削除は整合性ルールに従う

## 5. リンク
- active -> deleted
- deleted -> active
- deleted -> removed

## 6. 監査
すべての状態遷移は change_logs に残す。
