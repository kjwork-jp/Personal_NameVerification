"""Runtime path resolution for portable release packages."""

from __future__ import annotations

import os
import sys
from pathlib import Path


_RELEASE_APP_DIR_NAME = "10_app"
_DEFAULT_DB_RELATIVE_PATH = Path("30_prod_db") / "nameverification.db"
_DEFAULT_CHANGE_LOG_RELATIVE_PATH = Path("40_logs") / "change_logs.jsonl"


def resolve_package_root(
    *,
    executable_path: Path | None = None,
    frozen: bool | None = None,
) -> Path:
    """Resolve the package root used for portable release layouts.

    Precedence:
    1. NAMEVERIFICATION_PACKAGE_ROOT, when explicitly provided.
    2. Frozen EXE location. If the EXE is under ``10_app``, its parent is the
       release package root.
    3. Current working directory for source/development runs.
    """

    configured_root = os.environ.get("NAMEVERIFICATION_PACKAGE_ROOT")
    if configured_root and configured_root.strip():
        return Path(configured_root).expanduser().resolve()

    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
    if is_frozen:
        exe_path = Path(executable_path or sys.executable).resolve()
        exe_dir = exe_path.parent
        if exe_dir.name == _RELEASE_APP_DIR_NAME:
            return exe_dir.parent
        return exe_dir

    return Path.cwd().resolve()


def resolve_database_path(*, package_root: Path | None = None) -> Path:
    """Resolve the SQLite database path for runtime startup."""

    configured_db_path = os.environ.get("NAMEVERIFICATION_DB_PATH")
    if configured_db_path and configured_db_path.strip():
        return Path(configured_db_path).expanduser()

    root = package_root or resolve_package_root()
    if _looks_like_release_root(root):
        return root / _DEFAULT_DB_RELATIVE_PATH
    return Path("nameverification.db")


def resolve_change_log_jsonl_path(*, package_root: Path | None = None) -> Path:
    """Resolve the automatic DB change-log JSONL path."""

    configured_log_path = os.environ.get("NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH")
    if configured_log_path and configured_log_path.strip():
        return Path(configured_log_path).expanduser()

    root = package_root or resolve_package_root()
    if _looks_like_release_root(root):
        return root / _DEFAULT_CHANGE_LOG_RELATIVE_PATH
    return Path("logs") / "change_logs.jsonl"


def ensure_runtime_parent_dirs(*paths: Path) -> None:
    """Create parent directories for runtime files when they are explicit paths."""

    for path in paths:
        parent = path.parent
        if parent == Path("") or parent == Path("."):
            continue
        parent.mkdir(parents=True, exist_ok=True)


def _looks_like_release_root(root: Path) -> bool:
    return (root / _RELEASE_APP_DIR_NAME).is_dir() or (root / "30_prod_db").is_dir()
