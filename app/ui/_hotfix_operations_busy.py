"""Operations tab busy guard and Japanese label hotfix."""
from __future__ import annotations
from typing import Any

from app.ui._hotfix_operator_style import style


def apply() -> None:
    from app.ui import operations_tab as m
    old_init = m.OperationsTab.__init__

    def __init__(self: Any, *args: Any, **kwargs: Any) -> None:
        old_init(self, *args, **kwargs)
        style(self)
        _labels(self)

    m.OperationsTab.__init__ = __init__
    for name in [
        "_run_export_csv", "_run_export_json", "_run_export_sql_dump",
        "_run_create_backup", "_run_restore", "_run_import_csv", "_run_import_json",
    ]:
        setattr(m.OperationsTab, name, _guard(getattr(m.OperationsTab, name)))


def _guard(func):  # type: ignore[no-untyped-def]
    def wrapper(self: Any) -> None:
        if getattr(self, "_is_busy", False):
            self._set_message("実行中です。完了またはキャンセルまでお待ちください。", is_error=True)
            return
        func(self)
    return wrapper


def _labels(self: Any) -> None:
    text_map = {
        "csv_export_browse_button": "参照",
        "json_export_browse_button": "参照",
        "sql_dump_browse_button": "参照",
        "db_path_browse_button": "参照",
        "backup_output_browse_button": "参照",
        "restore_backup_browse_button": "参照",
        "restore_target_browse_button": "参照",
        "import_csv_dir_browse_button": "参照",
        "import_json_browse_button": "参照",
        "export_csv_button": "CSV出力",
        "export_json_button": "JSON出力",
        "export_sql_dump_button": "SQLダンプ出力",
        "create_backup_button": "バックアップ作成",
        "restore_button": "復元",
        "import_csv_button": "CSV取込",
        "import_json_button": "JSON取込",
        "cancel_operation_button": "キャンセル",
        "log_prev_button": "前へ",
        "log_next_button": "次へ",
        "reload_logs_button": "ログ再読込",
        "export_logs_button": "ログエクスポート",
    }
    for attr, label in text_map.items():
        widget = getattr(self, attr, None)
        if widget is not None:
            widget.setText(label)
    check_map = {
        "include_archives_checkbox": "アーカイブを含める",
        "log_regex_checkbox": "正規表現",
        "log_regex_ignore_case_checkbox": "大文字小文字を無視",
        "log_regex_multiline_checkbox": "複数行",
        "log_regex_dotall_checkbox": "ドット改行一致",
    }
    for attr, label in check_map.items():
        widget = getattr(self, attr, None)
        if widget is not None:
            widget.setText(label)
    if hasattr(self, "log_page_label"):
        self.log_page_label.setText("ページ 0/0")
