# 16_error_handling_policy.md

## 1. 目的
エラーの分類、表示、ログ化、運用時の扱いを統一する。

## 2. 分類
- ValidationError: 入力値不正
- ConflictError: 重複や競合
- PermissionError: 権限不足
- NotFoundError: 対象不存在
- SystemError: 想定外障害

## 3. UI 表示方針
### ValidationError
- 入力箇所に近い位置で表示
- 修正方法を示す

### ConflictError
- 何と競合したかを示す
- 再実行可否を示す

### PermissionError
- 実行不可理由と必要ロールを示す

### SystemError
- 画面には簡潔表示
- 詳細はログへ記録
- 必要ならダイアログ表示

## 4. ログ記録
- 例外種別
- 発生時刻
- 操作主体
- 操作対象
- 再現条件メモ

## 5. 禁止事項
- traceback をそのまま一般利用者へ表示
- 何をすればよいか分からない曖昧なエラー文
