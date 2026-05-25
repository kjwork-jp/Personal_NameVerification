param(
    [string]$ReleaseName = "v0.2.0-rc1",
    [string]$ReleaseDir = "",
    [int]$StartupSeconds = 5
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptRoot = $PSScriptRoot
. (Join-Path $ScriptRoot "common_windows.ps1")

$ReleaseRoot = Join-Path $ProjectRoot "release"
if (-not [string]::IsNullOrWhiteSpace($ReleaseDir)) {
    $PackageDir = (Resolve-Path -Path $ReleaseDir).Path
    $ReleaseName = Split-Path -Leaf $PackageDir
    $ReleaseRoot = Split-Path -Parent $PackageDir
} else {
    $PackageDir = Join-Path $ReleaseRoot $ReleaseName
}
$ZipPath = Join-Path $ReleaseRoot ("NameVerification-" + $ReleaseName + "-portable.zip")
$SmokeRoot = Join-Path $ProjectRoot ("tmp\portable_smoke\" + $ReleaseName)
$ExtractRoot = Join-Path $SmokeRoot "extracted"
$TableCheckScriptPath = Join-Path $SmokeRoot "check_portable_tables.py"

function Resolve-SmokePackageDir([string]$Root, [string]$ExpectedReleaseName) {
    if (Test-Path (Join-Path $Root "10_app\NameVerification.exe")) {
        return $Root
    }

    $NamedChild = Join-Path $Root $ExpectedReleaseName
    if (Test-Path (Join-Path $NamedChild "10_app\NameVerification.exe")) {
        return $NamedChild
    }

    $Candidate = Get-ChildItem -Path $Root -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "10_app\NameVerification.exe") } |
        Select-Object -First 1
    if ($null -ne $Candidate) {
        return $Candidate.FullName
    }

    throw "Portable package directory with 10_app\NameVerification.exe was not found under: $Root"
}

function Assert-FileExists([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "Required file not found: $Path"
    }
}

function Assert-DirectoryExists([string]$Path) {
    if (-not (Test-Path $Path -PathType Container)) {
        throw "Required directory not found: $Path"
    }
}

function Assert-WritableDirectory([string]$Path) {
    Assert-DirectoryExists $Path
    $ProbePath = Join-Path $Path (".portable_smoke_write_probe_" + [guid]::NewGuid().ToString("N") + ".tmp")
    try {
        "portable smoke write probe" | Set-Content -Path $ProbePath -Encoding UTF8
    } finally {
        Remove-Item $ProbePath -Force -ErrorAction SilentlyContinue
    }
}

function Assert-TextContains([string]$Path, [string]$ExpectedText) {
    Assert-FileExists $Path
    $Text = Get-Content -Path $Path -Raw -Encoding UTF8
    if (-not $Text.Contains($ExpectedText)) {
        throw "Required text '$ExpectedText' was not found in: $Path"
    }
}

Write-Host "[1/10] Check portable release inputs"
if (Test-Path $ZipPath) {
    Write-Host "Using release zip: $ZipPath"
} elseif (Test-Path $PackageDir) {
    Write-Host "Using release folder: $PackageDir"
} else {
    throw "Portable package not found. Run .\scripts\package_release_windows.ps1 -ReleaseName $ReleaseName first."
}

Write-Host "[2/10] Prepare isolated portable smoke folder"
Remove-PathBestEffort -Path $SmokeRoot
New-Item -ItemType Directory -Path $ExtractRoot -Force | Out-Null

if (Test-Path $ZipPath) {
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractRoot -Force
    $PortableRoot = Resolve-SmokePackageDir -Root $ExtractRoot -ExpectedReleaseName $ReleaseName
} else {
    $PortableRoot = $PackageDir
}

$PortableExePath = Join-Path $PortableRoot "10_app\NameVerification.exe"
$PortableDbPath = Join-Path $PortableRoot "30_prod_db\nameverification.db"
$ChangeLogPath = Join-Path $PortableRoot "40_logs\change_logs.jsonl"
$OperationsLogPath = Join-Path $PortableRoot "40_logs\operations_events.jsonl"
$BackupDailyPath = Join-Path $PortableRoot "50_backups\daily"
$BackupBeforeRestorePath = Join-Path $PortableRoot "50_backups\before_restore"
$BackupBeforeImportPath = Join-Path $PortableRoot "50_backups\before_import"
$ExportCsvPath = Join-Path $PortableRoot "60_exports\csv"
$ExportJsonPath = Join-Path $PortableRoot "60_exports\json"
$ExportSqlPath = Join-Path $PortableRoot "60_exports\sql"

Write-Host "[3/10] Validate portable layout and readme files"
Assert-FileExists $PortableExePath
Assert-FileExists (Join-Path $PortableRoot "00_readme\README_before_start.txt")
Assert-FileExists (Join-Path $PortableRoot "10_app\README_app.txt")
Assert-FileExists (Join-Path $PortableRoot "30_prod_db\README_prod_db.txt")
Assert-FileExists (Join-Path $PortableRoot "40_logs\README_logs.txt")
Assert-FileExists (Join-Path $PortableRoot "50_backups\README_backups.txt")
Assert-FileExists (Join-Path $PortableRoot "60_exports\README_exports.txt")
Assert-FileExists (Join-Path $PortableRoot "70_release_evidence")
Assert-FileExists (Join-Path $PortableRoot "99_review\final_review.txt")
Assert-TextContains (Join-Path $PortableRoot "00_readme\README_before_start.txt") $ReleaseName

Write-Host "[4/10] Validate portable runtime directories"
Assert-WritableDirectory (Join-Path $PortableRoot "30_prod_db")
Assert-WritableDirectory (Join-Path $PortableRoot "40_logs")
Assert-WritableDirectory $BackupDailyPath
Assert-WritableDirectory $BackupBeforeRestorePath
Assert-WritableDirectory $BackupBeforeImportPath
Assert-WritableDirectory $ExportCsvPath
Assert-WritableDirectory $ExportJsonPath
Assert-WritableDirectory $ExportSqlPath

Write-Host "[5/10] Stop stale EXE processes"
Stop-NameVerificationProcesses

Write-Host "[6/10] Launch portable EXE from package root"
$PreviousPackageRoot = $env:NAMEVERIFICATION_PACKAGE_ROOT
$PreviousDbPath = $env:NAMEVERIFICATION_DB_PATH
$PreviousChangeLogPath = $env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH
$PreviousOperationsLogPath = $env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH

try {
    $env:NAMEVERIFICATION_PACKAGE_ROOT = $PortableRoot
    Remove-Item Env:NAMEVERIFICATION_DB_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH -ErrorAction SilentlyContinue

    $process = Start-Process -FilePath $PortableExePath -WorkingDirectory $PortableRoot -PassThru
    Start-Sleep -Seconds $StartupSeconds

    Write-Host "[7/10] Check process and portable runtime files"
    if ($process.HasExited) {
        throw "Portable EXE exited during smoke test with exit code $($process.ExitCode)"
    }
    Assert-FileExists $PortableDbPath
    Assert-DirectoryExists (Split-Path -Parent $ChangeLogPath)
    Assert-DirectoryExists (Split-Path -Parent $OperationsLogPath)

    Write-Host "[8/10] Check required runtime tables"
    $TableCheckScript = @'
from __future__ import annotations

import sqlite3
import sys


def main() -> int:
    db_path = sys.argv[1]
    required_tables = set(sys.argv[2:])
    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in rows}
    finally:
        connection.close()

    missing = sorted(required_tables - tables)
    if missing:
        raise SystemExit("Missing portable smoke database tables: " + ", ".join(missing))
    print("Portable smoke database tables OK: " + ", ".join(sorted(required_tables)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'@
    Set-Content -Path $TableCheckScriptPath -Value $TableCheckScript -Encoding UTF8
    python $TableCheckScriptPath $PortableDbPath `
        "users" `
        "user_audit_logs" `
        "app_settings" `
        "schema_migrations" `
        "names" `
        "titles" `
        "subtitles" `
        "name_title_links" `
        "name_subtitle_links" `
        "change_logs"
    if ($LASTEXITCODE -ne 0) { throw "Portable smoke database table check failed" }

    Write-Host "[9/10] Stop portable EXE"
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    $process.WaitForExit(5000) | Out-Null
    Start-Sleep -Milliseconds 500
} finally {
    if ($null -eq $PreviousPackageRoot) {
        Remove-Item Env:NAMEVERIFICATION_PACKAGE_ROOT -ErrorAction SilentlyContinue
    } else {
        $env:NAMEVERIFICATION_PACKAGE_ROOT = $PreviousPackageRoot
    }
    if ($null -eq $PreviousDbPath) {
        Remove-Item Env:NAMEVERIFICATION_DB_PATH -ErrorAction SilentlyContinue
    } else {
        $env:NAMEVERIFICATION_DB_PATH = $PreviousDbPath
    }
    if ($null -eq $PreviousChangeLogPath) {
        Remove-Item Env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH -ErrorAction SilentlyContinue
    } else {
        $env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = $PreviousChangeLogPath
    }
    if ($null -eq $PreviousOperationsLogPath) {
        Remove-Item Env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH -ErrorAction SilentlyContinue
    } else {
        $env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH = $PreviousOperationsLogPath
    }
}

Write-Host "[10/10] Portable smoke complete"
Write-Host "Release name: $ReleaseName"
Write-Host "Portable root: $PortableRoot"
Write-Host "Portable DB: $PortableDbPath"
Write-Host "Change log path: $ChangeLogPath"
Write-Host "Operations log path: $OperationsLogPath"
Write-Host "Backup daily path: $BackupDailyPath"
Write-Host "Export CSV path: $ExportCsvPath"
Write-Host "Export JSON path: $ExportJsonPath"
Write-Host "Export SQL path: $ExportSqlPath"
