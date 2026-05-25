# ruff: noqa: I001
"""Static contract tests for Windows release orchestration scripts."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_RELEASE_SCRIPT = PROJECT_ROOT / "scripts" / "run_release_windows.ps1"


def _script_text() -> str:
    return RUN_RELEASE_SCRIPT.read_text(encoding="utf-8")


def test_run_release_script_exists() -> None:
    assert RUN_RELEASE_SCRIPT.exists()


def test_run_release_script_orchestrates_expected_steps() -> None:
    text = _script_text()

    assert "build_exe_windows.ps1" in text
    assert "package_release_windows.ps1" in text
    assert "smoke_test_portable_windows.ps1" in text
    assert text.index("build_exe_windows.ps1") < text.index("package_release_windows.ps1")
    assert text.index("package_release_windows.ps1") < text.index("smoke_test_portable_windows.ps1")


def test_run_release_script_checks_release_assets() -> None:
    text = _script_text()

    assert "NameVerification-" in text
    assert "-portable.zip" in text
    assert "00_manifest_" in text
    assert "checksums_sha256_" in text
    assert "validation_log_template_" in text
    assert "Assert-FileExists $ZipPath" in text
    assert "Assert-FileExists $ManifestPath" in text
    assert "Assert-FileExists $ChecksumPath" in text
    assert "Assert-FileExists $ValidationPath" in text


def test_run_release_script_supports_optional_github_release() -> None:
    text = _script_text()

    assert "CreateGitHubRelease" in text
    assert "Prerelease" in text
    assert "Get-Command gh" in text
    assert "release" in text
    assert "create" in text
    assert "--prerelease" in text
