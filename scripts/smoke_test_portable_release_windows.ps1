param(
    [string]$ReleaseName = "v0.1.0-rc2"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptRoot = $PSScriptRoot
. (Join-Path $ScriptRoot "common_windows.ps1")

$PackageDir = Join-Path $ProjectRoot ("release\" + $ReleaseName)
$ExePath = Join-Path $PackageDir "10_app\NameVerification.exe"
$DbPath = Join-Path $PackageDir "30_prod_db\nameverification.db"
$ChangeLogPath = Join-Path $PackageDir "40_logs\change_logs.jsonl"
$OperationsLogPath = Join-Path $PackageDir "40_logs\operations_events.jsonl"
$UnexpectedRootDbPath = Join-Path $PackageDir "nameverification.db"

Write-Host "[1/7] Check portable package exists"
if (-not (Test-Path $PackageDir)) {
    throw "Portable package not found: $PackageDir. Run .\scripts\package_release_windows.ps1 -ReleaseName $ReleaseName first."
}
if (-not (Test-Path $ExePath)) {
    throw "Portable EXE not found: $ExePath. Run .\scripts\package_release_windows.ps1 -ReleaseName $ReleaseName first."
}

Write-Host "[2/7] Clear path override environment variables"
Remove-Item Env:NAMEVERIFICATION_PACKAGE_ROOT -ErrorAction SilentlyContinue
Remove-Item Env:NAMEVERIFICATION_DB_PATH -ErrorAction SilentlyContinue
Remove-Item Env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH -ErrorAction SilentlyContinue
Remove-Item Env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH -ErrorAction SilentlyContinue

Write-Host "[3/7] Stop stale EXE processes"
Stop-NameVerificationProcesses

Write-Host "[4/7] Prepare isolated portable runtime files"
Remove-Item $DbPath -Force -ErrorAction SilentlyContinue
Remove-Item $ChangeLogPath -Force -ErrorAction SilentlyContinue
Remove-Item $OperationsLogPath -Force -ErrorAction SilentlyContinue
Remove-Item $UnexpectedRootDbPath -Force -ErrorAction SilentlyContinue

Write-Host "[5/7] Launch portable EXE"
$process = Start-Process -FilePath $ExePath -PassThru
Start-Sleep -Seconds 5

Write-Host "[6/7] Check process and package-relative database"
try {
    if ($process.HasExited) {
        throw "Portable EXE exited during smoke test with exit code $($process.ExitCode)"
    }
    if (-not (Test-Path $DbPath)) {
        throw "Portable database was not created at package-relative path: $DbPath"
    }
    if (Test-Path $UnexpectedRootDbPath) {
        throw "Unexpected root-level database was created: $UnexpectedRootDbPath"
    }
} finally {
    Write-Host "[7/7] Stop portable EXE"
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    $process.WaitForExit(5000) | Out-Null
    Start-Sleep -Milliseconds 500
}

Write-Host "Portable release smoke test complete: $ExePath"
Write-Host "Portable database created: $DbPath"
Write-Host "Change log target: $ChangeLogPath"
Write-Host "Operations log target: $OperationsLogPath"
