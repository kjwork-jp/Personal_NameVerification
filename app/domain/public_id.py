"""Public identifier helpers.

Public IDs are app-managed UUID strings used for UI/export/import compatibility.
Integer primary keys remain internal database implementation details.
"""

from __future__ import annotations

from uuid import uuid4


def new_public_id() -> str:
    """Return a new externally stable UUID public ID."""

    return str(uuid4())
