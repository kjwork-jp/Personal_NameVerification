"""PySide6 formal entrypoint for NameVerification v3."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """Launch the minimal PySide6 application shell."""
    from PySide6.QtWidgets import QApplication

    from app.application.query_services import QueryService
    from app.infrastructure.db import initialize_database
    from app.ui.main_window import MainWindow

    connection = initialize_database(Path("nameverification.db"))
    query_service = QueryService(connection)

    app = QApplication(sys.argv)
    window = MainWindow(query_service=query_service)
    window.show()

    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
