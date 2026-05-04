$ErrorActionPreference = "Stop"

Write-Host "[1/5] Python version"
python --version

Write-Host "[2/5] Install package with dev dependencies"
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

Write-Host "[3/5] Run quality gates"
pytest -q
ruff check .
black --check .
mypy app

Write-Host "[4/5] Clean previous build outputs"
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }

Write-Host "[5/5] Build EXE"
pyinstaller --clean --noconfirm packaging/NameVerification.spec

Write-Host "Build complete: dist/NameVerification.exe"
