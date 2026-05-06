# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

block_cipher = None
PROJECT_ROOT = Path.cwd()


a = Analysis(
    [str(PROJECT_ROOT / "app" / "pyside6_main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "db" / "schema.sql"), "db"),
        (str(PROJECT_ROOT / "db" / "migrations"), "db/migrations"),
        (
            str(PROJECT_ROOT / "app" / "ui" / "old" / "title_subtitle_management_tab.py"),
            "app/ui/old",
        ),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "mypy",
        "ruff",
        "black",
        "tests",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="NameVerification",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
