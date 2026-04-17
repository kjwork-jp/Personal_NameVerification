"""Smoke tests for bootstrap package structure."""

from collections.abc import Callable

import app
from app import pyside6_main


def test_version_is_defined() -> None:
    assert app.__version__ == "0.1.0"


def test_main_entrypoint_exists() -> None:
    assert isinstance(pyside6_main.main, Callable)
