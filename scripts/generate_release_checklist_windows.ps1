param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseName,
    [string]$ReleaseDir = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Today = Get-Date -Format "yyyyMMdd"
$ReleaseRoot = Join-Path $ProjectRoot "release"
if ([string]::IsNullOrWhiteSpace($ReleaseDir)) {
    $ReleaseDir = Join-Path $ReleaseRoot $ReleaseName
} else {
    $ReleaseDir = (Resolve-Path -Path $ReleaseDir).Path
    $ReleaseRoot = Split-Path -Parent $ReleaseDir
}

$EvidenceDir = Join-Path $ReleaseDir "70_release_evidence"
$ZipPath = Join-Path $ReleaseRoot ("NameVerification-" + $ReleaseName + "-portable.zip")
$ManifestPath = Join-Path $ReleaseDir ("00_manifest_" + $ReleaseName + "_" + $Today + ".csv")
$ChecksumPath = Join-Path $EvidenceDir ("checksums_sha256_" + $ReleaseName + "_" + $Today + ".txt")
$ValidationPath = Join-Path $EvidenceDir ("validation_log_template_" + $ReleaseName + "_" + $Today + ".txt")
$ChecklistPath = Join-Path $EvidenceDir ("release_verification_checklist_" + $ReleaseName + "_" + $Today + ".md")

function Test-ItemExists([string]$Path) {
    return Test-Path $Path
}

function Format-CheckRow([string]$Name, [bool]$Passed, [string]$Path) {
    $Status = if ($Passed) { "PASS" } else { "FAIL" }
    return "| $Name | $Status | `$Path` |"
}

New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null

$Checks = @(
    @{ Name = "release directory"; Passed = Test-ItemExists $ReleaseDir; Path = $ReleaseDir },
    @{ Name = "portable zip"; Passed = Test-ItemExists $ZipPath; Path = $ZipPath },
    @{ Name = "manifest csv"; Passed = Test-ItemExists $ManifestPath; Path = $ManifestPath },
    @{ Name = "checksum file"; Passed = Test-ItemExists $ChecksumPath; Path = $ChecksumPath },
    @{ Name = "validation log template"; Passed = Test-ItemExists $ValidationPath; Path = $ValidationPath },
    @{ Name = "app folder"; Passed = Test-ItemExists (Join-Path $ReleaseDir "10_app"); Path = Join-Path $ReleaseDir "10_app" },
    @{ Name = "prod db folder"; Passed = Test-ItemExists (Join-Path $ReleaseDir "30_prod_db"); Path = Join-Path $ReleaseDir "30_prod_db" },
    @{ Name = "logs folder"; Passed = Test-ItemExists (Join-Path $ReleaseDir "40_logs"); Path = Join-Path $ReleaseDir "40_logs" },
    @{ Name = "backups folder"; Passed = Test-ItemExists (Join-Path $ReleaseDir "50_backups"); Path = Join-Path $ReleaseDir "50_backups" },
    @{ Name = "exports folder"; Passed = Test-ItemExists (Join-Path $ReleaseDir "60_exports"); Path = Join-Path $ReleaseDir "60_exports" },
    @{ Name = "release evidence folder"; Passed = Test-ItemExists $EvidenceDir; Path = $EvidenceDir }
)

$FailedChecks = @($Checks | Where-Object { -not $_.Passed })
$OverallStatus = if ($FailedChecks.Count -eq 0) { "PASS" } else { "FAIL" }
$GeneratedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"

$Lines = @(
    "# Release verification checklist: $ReleaseName",
    "",
    "## Summary",
    "",
    "- Release name: `$ReleaseName`",
    "- Generated at: `$GeneratedAt`",
    "- Overall status: **$OverallStatus**",
    "",
    "## Required artifacts",
    "",
    "| Check | Status | Path |",
    "|---|---:|---|"
)

foreach ($Check in $Checks) {
    $Lines += Format-CheckRow $Check.Name $Check.Passed $Check.Path
}

$Lines += @(
    "",
    "## Notes",
    "",
    "- This checklist verifies release artifact presence and the expected package layout.",
    "- It does not replace the portable smoke test.",
    "- If Overall status is FAIL, fix the missing artifact before publishing."
)

Set-Content -Path $ChecklistPath -Value $Lines -Encoding UTF8
Write-Host "Release verification checklist generated: $ChecklistPath"

if ($OverallStatus -ne "PASS") {
    throw "Release verification checklist contains failed checks. See: $ChecklistPath"
}
