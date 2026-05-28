"""Presentation copy for the Data I/O operations screen."""

from __future__ import annotations

DATA_IO_PAGE_TITLE = "Data I/O"
DATA_IO_PAGE_DESCRIPTION = (
    "Export, Backup, Restore, Import, and operation-log review are managed here. "
    "This module only defines presentation copy; permissions and service behavior stay in "
    "operations_tab.py."
)

DATA_IO_GROUP_DESCRIPTIONS = {
    "Export": "Output current data for review, migration, or external backup.",
    "Backup": "Copy the current SQLite database before risky maintenance work.",
    "Restore": "Replace a target database from a backup. Admin-only operation.",
    "Import": "Load CSV or JSON into an initial or prepared database. Admin-only operation.",
}

DATA_IO_RESULT_DESCRIPTION = "Execution results are appended here with OK/ERROR prefixes."
DATA_IO_LOG_DESCRIPTION = "Operation logs can be filtered, paged, and exported for review evidence."
