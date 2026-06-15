"""データ入出力画面で使用する表示文言。"""

from __future__ import annotations

DATA_IO_PAGE_TITLE = "データ入出力"
DATA_IO_PAGE_DESCRIPTION = (
    "データ出力、バックアップ、復元、データ取込、実行ログ確認を管理します。"
)

DATA_IO_GROUP_DESCRIPTIONS = {
    "データ出力": "現在のデータを確認、移行、外部保管用に出力します。",
    "バックアップ": "保守作業の前に現在のSQLiteデータベースを複製します。",
    "復元": "バックアップから対象データベースを置換します。管理者専用操作です。",
    "データ取込": "CSVまたはJSONを初期化済みデータベースへ取り込みます。管理者専用操作です。",
}

DATA_IO_RESULT_DESCRIPTION = "実行結果をOKまたはERROR付きで追記します。"
DATA_IO_LOG_DESCRIPTION = "実行ログを絞り込み、ページ移動、証跡用出力できます。"
