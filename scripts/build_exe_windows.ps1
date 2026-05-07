$ErrorActionPreference = "Stop"

Write-Host "[1/6] Python version"
python --version
if ($LASTEXITCODE -ne 0) { throw "python --version failed" }

Write-Host "[2/6] Clean previous build outputs"
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }

Write-Host "[3/6] Install package with dev dependencies"
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { throw "dependency installation failed" }

Write-Host "[4/6] Run quality gates"
pytest -q
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
ruff check .
if ($LASTEXITCODE -ne 0) { throw "ruff failed" }
black --check .
if ($LASTEXITCODE -ne 0) { throw "black failed" }
mypy app
if ($LASTEXITCODE -ne 0) { throw "mypy failed" }

Write-Host "[5/6] Build EXE"
pyinstaller --clean --noconfirm packaging/NameVerification.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path "dist/NameVerification.exe")) {
    throw "PyInstaller finished without creating dist/NameVerification.exe"
}

Write-Host "[6/6] Build complete"
Write-Host "Build complete: dist/NameVerification.exe"
