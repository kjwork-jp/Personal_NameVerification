$ErrorActionPreference = "Stop"

$ScriptRoot = $PSScriptRoot
. (Join-Path $ScriptRoot "common_windows.ps1")

Write-Host "[1/7] Python version"
python --version
if ($LASTEXITCODE -ne 0) { throw "python --version failed" }

Write-Host "[2/7] Stop running EXE processes"
Stop-NameVerificationProcesses

Write-Host "[3/7] Clean previous build outputs"
Remove-PathBestEffort -Path "build"
Remove-PathBestEffort -Path "dist"

Write-Host "[4/7] Install package with dev dependencies"
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { throw "dependency installation failed" }

Write-Host "[5/7] Run quality gates"
pytest -q
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
ruff check .
if ($LASTEXITCODE -ne 0) { throw "ruff failed" }
black --check .
if ($LASTEXITCODE -ne 0) { throw "black failed" }
mypy app
if ($LASTEXITCODE -ne 0) { throw "mypy failed" }

Write-Host "[6/7] Build EXE"
pyinstaller --clean --noconfirm packaging/NameVerification.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path "dist/NameVerification.exe")) {
    throw "PyInstaller finished without creating dist/NameVerification.exe"
}

Write-Host "[7/7] Build complete"
Write-Host "Build complete: dist/NameVerification.exe"
