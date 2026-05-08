$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptRoot = $PSScriptRoot
. (Join-Path $ScriptRoot "common_windows.ps1")

$ExePath = Join-Path $ProjectRoot "dist\NameVerification.exe"
$SmokeDir = Join-Path $ProjectRoot "tmp\exe_smoke"
$SmokeDbPath = Join-Path $SmokeDir "nameverification_smoke.db"

Write-Host "[1/6] Check EXE exists"
if (-not (Test-Path $ExePath)) {
    throw "EXE not found: $ExePath. Run .\scripts\build_exe_windows.ps1 first."
}

Write-Host "[2/6] Stop stale EXE processes"
Stop-NameVerificationProcesses

Write-Host "[3/6] Prepare isolated smoke database path"
Remove-PathBestEffort -Path $SmokeDir
New-Item -ItemType Directory -Path $SmokeDir | Out-Null
$env:NAMEVERIFICATION_DB_PATH = $SmokeDbPath

Write-Host "[4/6] Launch EXE"
$process = Start-Process -FilePath $ExePath -PassThru
Start-Sleep -Seconds 5

Write-Host "[5/6] Check process and database"
if ($process.HasExited) {
    throw "EXE exited during smoke test with exit code $($process.ExitCode)"
}
if (-not (Test-Path $SmokeDbPath)) {
    try {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    } finally {
        throw "Smoke database was not created: $SmokeDbPath"
    }
}

Write-Host "[6/6] Stop EXE"
Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
$process.WaitForExit(5000) | Out-Null
Start-Sleep -Milliseconds 500

Write-Host "Smoke test complete: $ExePath"
Write-Host "Smoke database created: $SmokeDbPath"
