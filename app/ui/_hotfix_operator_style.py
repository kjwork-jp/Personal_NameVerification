"""Common Japanese operator messages and pastel style hotfix."""
from __future__ import annotations
from typing import Any

STYLE = '''
QWidget{font-family:"Meiryo UI","Yu Gothic UI",sans-serif;font-size:10pt;}
QGroupBox{border:1px solid #B8D8FF;border-radius:12px;margin-top:10px;padding:10px;background:#F7FBFF;}
QGroupBox::title{color:#24527A;left:12px;padding:0 6px;}
QPushButton{background:#E8F3FF;border:1px solid #9CC7F2;border-radius:10px;padding:5px 10px;}
QPushButton:hover{background:#D7ECFF;} QPushButton:disabled{color:#888;background:#EEE;border-color:#D0D0D0;}
QLineEdit,QTextEdit,QComboBox,QTableWidget,QListWidget{border:1px solid #C9DDF2;border-radius:8px;padding:3px;background:#FFF;}
QHeaderView::section{background:#DFF0FF;color:#244563;border:1px solid #B8D8FF;padding:4px;}
QLabel{color:#25364A;}
'''

def style(widget: Any) -> None:
    try:
        widget.setStyleSheet(STYLE)
    except Exception:
        pass

def operator_required(self: Any) -> str | None:
    value = self.operator_input.text().strip()
    if not value:
        self._set_message("操作者ID を入力してください", is_error=True)
        return None
    return value

def apply() -> None:
    targets = [
        ("name_management_tab", "NameManagementTab"),
        ("link_management_tab", "LinkManagementTab"),
        ("trash_tab", "TrashTab"),
    ]
    for module_name, class_name in targets:
        module = __import__("app.ui." + module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        cls._require_operator_id = operator_required
        old_init = cls.__init__
        def __init__(self: Any, *args: Any, _old=old_init, **kwargs: Any) -> None:  # type: ignore[no-untyped-def]
            _old(self, *args, **kwargs)
            style(self)
            if hasattr(self, "operator_input"):
                self.operator_input.setPlaceholderText("操作者ID")
                self.operator_input.setToolTip("操作者ID が必要です")
        cls.__init__ = __init__
