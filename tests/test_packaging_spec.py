from __future__ import annotations

from pathlib import Path


def test_pyinstaller_spec_includes_root_migrations() -> None:
    spec_text = Path("packaging/NameVerification.spec").read_text(encoding="utf-8")

    assert 'PROJECT_ROOT / "migrations"' in spec_text
    assert '"migrations"' in spec_text
