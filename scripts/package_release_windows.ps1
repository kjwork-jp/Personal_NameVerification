$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ExePath = Join-Path $ProjectRoot "dist\NameVerification.exe"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$PackageDir = Join-Path $ReleaseRoot "NameVerification-windows"
$ZipPath = Join-Path $ReleaseRoot "NameVerification-windows.zip"
$ReadmePath = Join-Path $PackageDir "README_起動前に読む.txt"

Write-Host "[1/5] Check EXE exists"
if (-not (Test-Path $ExePath)) {
    throw "EXE not found: $ExePath. Run .\scripts\build_exe_windows.ps1 first."
}

Write-Host "[2/5] Prepare release directory"
if (Test-Path $PackageDir) {
    Remove-Item $PackageDir -Recurse -Force
}
if (-not (Test-Path $ReleaseRoot)) {
    New-Item -ItemType Directory -Path $ReleaseRoot | Out-Null
}
New-Item -ItemType Directory -Path $PackageDir | Out-Null

Write-Host "[3/5] Copy release files"
Copy-Item $ExePath (Join-Path $PackageDir "NameVerification.exe") -Force
@"
NameVerification v3 Windows EXE

起動方法:
1. NameVerification.exe をダブルクリックする。
2. 初回起動時、既定ではEXEと同じ作業ディレクトリに nameverification.db が作成される。
3. 既存DBを使う場合は、NAMEVERIFICATION_DB_PATH 環境変数でDBパスを指定して起動する。

注意:
- 署名付きインストーラではないため、Windows SmartScreen等の警告が出る可能性がある。
- 重要データを投入する前に、アプリ内の データ入出力 タブでバックアップ導線を確認する。
- 自動アップデートは未対応。
"@ | Set-Content -Path $ReadmePath -Encoding UTF8

Write-Host "[4/5] Create zip"
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path (Join-Path $PackageDir "*") -DestinationPath $ZipPath -Force

Write-Host "[5/5] Verify zip"
if (-not (Test-Path $ZipPath)) {
    throw "Release zip was not created: $ZipPath"
}

Write-Host "Release package complete: $ZipPath"
