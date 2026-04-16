"""PySide6 formal entrypoint for NameVerification v3."""

from __future__ import annotations

import sys


def main() -> int:
    """Launch the minimal PySide6 application shell."""
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
    )

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("NameVerification v3")
    window.setCentralWidget(QLabel("NameVerification v3 bootstrap"))
    window.resize(640, 320)
    window.show()

    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
