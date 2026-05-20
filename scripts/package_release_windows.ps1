param(
    [string]$ReleaseName = "v0.1.0-rc2"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ExePath = Join-Path $ProjectRoot "dist\NameVerification.exe"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$PackageDir = Join-Path $ReleaseRoot $ReleaseName
$ZipPath = Join-Path $ReleaseRoot ("NameVerification-" + $ReleaseName + "-portable.zip")
$Today = Get-Date -Format "yyyyMMdd"
$ManifestPath = Join-Path $PackageDir ("00_manifest_" + $ReleaseName + "_" + $Today + ".csv")
$ChecksumPath = Join-Path $PackageDir ("70_release_evidence\checksums_sha256_" + $ReleaseName + "_" + $Today + ".txt")
$ValidationPath = Join-Path $PackageDir ("70_release_evidence\validation_log_template_" + $ReleaseName + "_" + $Today + ".txt")

function New-DirIfMissing([string]$Path) {
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function ConvertFrom-Base64Utf8([string]$Value) {
    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Value))
}

function Expand-ReleaseText([string]$Value) {
    return $Value.Replace("{ReleaseName}", $ReleaseName)
}

function Write-TextFile([string]$Path, [string]$Content) {
    $Parent = Split-Path -Parent $Path
    New-DirIfMissing $Parent
    $Content | Set-Content -Path $Path -Encoding UTF8
    Write-Host "Wrote: $Path"
}

function Write-Base64TextFile([string]$Path, [string]$Base64Content) {
    Write-TextFile -Path $Path -Content (Expand-ReleaseText (ConvertFrom-Base64Utf8 $Base64Content))
}

function Get-LatestSourceWriteTime {
    $SourcePaths = @(
        (Join-Path $ProjectRoot "app"),
        (Join-Path $ProjectRoot "packaging"),
        (Join-Path $ProjectRoot "pyproject.toml")
    )
    $Latest = [DateTime]::MinValue
    foreach ($SourcePath in $SourcePaths) {
        if (-not (Test-Path $SourcePath)) {
            continue
        }
        $Item = Get-Item $SourcePath
        if ($Item.PSIsContainer) {
            $Files = Get-ChildItem -Path $SourcePath -Recurse -File
        } else {
            $Files = @($Item)
        }
        foreach ($File in $Files) {
            if ($File.LastWriteTime -gt $Latest) {
                $Latest = $File.LastWriteTime
            }
        }
    }
    return $Latest
}

Write-Host "[1/7] Check EXE exists and freshness"
if (-not (Test-Path $ExePath)) {
    throw "EXE not found: $ExePath. Run .\scripts\build_exe_windows.ps1 first."
}
$ExeItem = Get-Item $ExePath
$LatestSourceWriteTime = Get-LatestSourceWriteTime
if ($ExeItem.LastWriteTime -lt $LatestSourceWriteTime) {
    throw "EXE appears older than app/packaging sources. Run .\scripts\build_exe_windows.ps1, then rerun package_release_windows.ps1. EXE: $($ExeItem.LastWriteTime.ToString('s')), latest source: $($LatestSourceWriteTime.ToString('s'))"
}

Write-Host "[2/7] Prepare portable release directory"
if (Test-Path $PackageDir) {
    Remove-Item $PackageDir -Recurse -Force
}
New-DirIfMissing $ReleaseRoot
New-DirIfMissing $PackageDir

$Directories = @(
    "00_readme",
    "10_app",
    "20_config",
    "30_prod_db",
    "40_logs",
    "50_backups\daily",
    "50_backups\before_restore",
    "50_backups\before_import",
    "60_exports\csv",
    "60_exports\json",
    "60_exports\sql",
    "70_release_evidence",
    "80_drive_upload",
    "90_docs",
    "99_review"
)
foreach ($Dir in $Directories) {
    New-DirIfMissing (Join-Path $PackageDir $Dir)
}

Write-Host "[3/7] Copy EXE"
Copy-Item $ExePath (Join-Path $PackageDir "10_app\NameVerification.exe") -Force

Write-Host "[4/7] Write portable README files"
Write-Base64TextFile (Join-Path $PackageDir "00_readme\README_before_start.txt") "TmFtZVZlcmlmaWNhdGlvbiBwb3J0YWJsZSByZWxlYXNlOiB7UmVsZWFzZU5hbWV9Cgrotbfli5Xmlrnms5U6CjEuIDEwX2FwcFxOYW1lVmVyaWZpY2F0aW9uLmV4ZSDjgpLotbfli5XjgZnjgovjgIIKMi4gcG9ydGFibGXphY3luIPjgafjga/jgIHml6LlrppEQuOBryAzMF9wcm9kX2RiXG5hbWV2ZXJpZmljYXRpb24uZGIg44Gn44GZ44CCCjMuIERCIGNoYW5nZSBsb2cg44GvIDQwX2xvZ3NcY2hhbmdlX2xvZ3MuanNvbmwg44G45Ye65Yqb44GV44KM44G+44GZ44CCCjQuIE9wZXJhdGlvbnMgbG9nIOOBryA0MF9sb2dzXG9wZXJhdGlvbnNfZXZlbnRzLmpzb25sIOOBuOWHuuWKm+OBleOCjOOBvuOBmeOAggoK5rOo5oSPOgotIOe9suWQjeS7mOOBjeOCpOODs+OCueODiOODvOODqeOBp+OBr+OBguOCiuOBvuOBm+OCk+OAggotIOWIneWbnumBi+eUqOWJjeOBq+ODkOODg+OCr+OCouODg+ODl+OAgUV4cG9ydOOAgVJlc3RvcmUvSW1wb3J044Gu56K66KqN5omL6aCG44KS5a6f5pa944GX44Gm44GP44Gg44GV44GE44CCCi0gUmVzdG9yZS9JbXBvcnQg44GvYWRtaW7lsILnlKjjga5kZXN0cnVjdGl2ZeaTjeS9nOOBp+OBmeOAguWun+ihjOWJjeOBq2JlZm9yZV9yZXN0b3JlL2JlZm9yZV9pbXBvcnTjgbjoh6rli5XpgIDpgb/jgZXjgozjgb7jgZnjgIIK"
Write-Base64TextFile (Join-Path $PackageDir "10_app\README_app.txt") "TmFtZVZlcmlmaWNhdGlvbi5leGUg44KS6YWN572u44GZ44KL44OV44Kp44Or44OA44Gn44GZ44CCRVhF55u06LW35YuV5pmC44Gv44CB44GT44Gu6Kaq44OV44Kp44Or44OA44KScG9ydGFibGUgcGFja2FnZSByb29044Go44GX44Gm5omx44GE44G+44GZ44CC"
Write-Base64TextFile (Join-Path $PackageDir "30_prod_db\README_prod_db.txt") "cG9ydGFibGXphY3luIPmmYLjga7ml6LlrppEQumFjee9ruWFiOOBp+OBmeOAguWIneWbnui1t+WLleaZguOBqyBuYW1ldmVyaWZpY2F0aW9uLmRiIOOBjOS9nOaIkOOBleOCjOOBvuOBmeOAgg=="
Write-Base64TextFile (Join-Path $PackageDir "40_logs\README_logs.txt") "Y2hhbmdlX2xvZ3MuanNvbmwg44GoIG9wZXJhdGlvbnNfZXZlbnRzLmpzb25sIOOBruaXouWumuWHuuWKm+WFiOOBp+OBmeOAgg=="
Write-Base64TextFile (Join-Path $PackageDir "50_backups\README_backups.txt") "ZGFpbHkg44Gv6YCa5bi444OQ44OD44Kv44Ki44OD44OX44CBYmVmb3JlX3Jlc3RvcmUvYmVmb3JlX2ltcG9ydCDjga9kZXN0cnVjdGl2ZeaTjeS9nOWJjeOBruiHquWLlemAgOmBv+WFiOOBp+OBmeOAgg=="
Write-Base64TextFile (Join-Path $PackageDir "60_exports\README_exports.txt") "Q1NWL0pTT04vU1FMIGR1bXAg44Gu5pei5a6a5Ye65Yqb5YWI44Gn44GZ44CC"
Write-Base64TextFile (Join-Path $PackageDir "80_drive_upload\README_drive_upload.txt") "44GT44GuIHtSZWxlYXNlTmFtZX0g44OV44Kp44Or44OA44KS44G+44Go44KB44GmR29vZ2xlIERyaXZl562J44G46YWN572u44GZ44KL5oOz5a6a44Gn44GZ44CC"
Write-TextFile (Join-Path $PackageDir "99_review\final_review.txt") "release package generated by scripts/package_release_windows.ps1 on $(Get-Date -Format s)."
Write-TextFile $ValidationPath "Validation commands to run before release: pytest -q; ruff check .; black --check .; mypy app; .\scripts\build_exe_windows.ps1; .\scripts\smoke_test_exe_windows.ps1; .\scripts\package_release_windows.ps1 -ReleaseName $ReleaseName; .\scripts\smoke_test_portable_windows.ps1"

Write-Host "[5/7] Create manifest"
$ManifestRows = New-Object System.Collections.Generic.List[string]
$ManifestRows.Add("relative_path,size_bytes,sha256")
$Files = Get-ChildItem -Path $PackageDir -Recurse -File | Sort-Object FullName
foreach ($File in $Files) {
    $RelativePath = $File.FullName.Substring($PackageDir.Length + 1).Replace("\", "/")
    $Hash = (Get-FileHash -Algorithm SHA256 -Path $File.FullName).Hash.ToLowerInvariant()
    $ManifestRows.Add("$RelativePath,$($File.Length),$Hash")
}
$ManifestRows | Set-Content -Path $ManifestPath -Encoding UTF8

Write-Host "[6/7] Create checksum file"
$ChecksumLines = New-Object System.Collections.Generic.List[string]
$Files = Get-ChildItem -Path $PackageDir -Recurse -File | Sort-Object FullName
foreach ($File in $Files) {
    $RelativePath = $File.FullName.Substring($PackageDir.Length + 1).Replace("\", "/")
    $Hash = (Get-FileHash -Algorithm SHA256 -Path $File.FullName).Hash.ToLowerInvariant()
    $ChecksumLines.Add("$Hash  $RelativePath")
}
$ChecksumLines | Set-Content -Path $ChecksumPath -Encoding UTF8

Write-Host "[7/7] Create zip"
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path $PackageDir -DestinationPath $ZipPath -Force

if (-not (Test-Path $ZipPath)) {
    throw "Release zip was not created: $ZipPath"
}

Write-Host "Release package complete: $ZipPath"
Write-Host "Portable folder: $PackageDir"
Write-Host "Manifest: $ManifestPath"
Write-Host "Checksums: $ChecksumPath"
