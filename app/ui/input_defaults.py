"""Input defaults for desktop UI screens."""

from __future__ import annotations

import getpass
import os
from uuid import uuid4


def default_operator_id() -> str:
    """Return a user-facing default operator identifier.

    Priority:
    1. NAMEVERIFICATION_OPERATOR_ID environment variable
    2. OS login user
    3. stable local fallback
    """

    env_value = os.environ.get("NAMEVERIFICATION_OPERATOR_ID", "").strip()
    if env_value:
        return env_value

    try:
        login_user = getpass.getuser().strip()
    except Exception:  # noqa: BLE001
        login_user = ""

    return login_user or "local-user"


def generate_subtitle_code() -> str:
    """Generate an internal management number for subtitles."""

    return f"SUB-{uuid4().hex[:8].upper()}"


def friendly_duplicate_message(entity_label: str, value: str) -> str:
    """Return a concise duplicate-value message for display-name conflicts."""

    return f"{entity_label}「{value}」は既に登録されています。別の名称を入力してください。"


def friendly_error_message(action_label: str, exc: Exception) -> str:
    """Convert low-level exceptions into user-facing Japanese messages."""

    raw = str(exc)
    lower_raw = raw.lower()
    duplicate_markers = [
        "unique",
        "duplicate",
        "already exists",
        "integrityerror",
        "一意",
        "重複",
        "既に存在",
        "すでに存在",
    ]
    if any(marker in lower_raw for marker in duplicate_markers):
        return f"{action_label}に失敗しました: 同じ名称のデータが既に登録されています。"
    return f"{action_label}に失敗しました: {raw}"
