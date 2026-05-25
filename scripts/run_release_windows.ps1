param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseName,
    [switch]$CreateGitHubRelease,
    [switch]$Prerelease,
    [string]$ReleaseTitle = "",
    [string]$ReleaseNotes = "",
    [int]$StartupSeconds = 5
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptRoot = $PSScriptRoot
$Today = Get-Date -Format "yyyyMMdd"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$ReleaseDir = Join-Path $ReleaseRoot $ReleaseName
$ZipPath = Join-Path $ReleaseRoot ("NameVerification-" + $ReleaseName + "-portable.zip")
$ManifestPath = Join-Path $ReleaseDir ("00_manifest_" + $ReleaseName + "_" + $Today + ".csv")
$ChecksumPath = Join-Path $ReleaseDir ("70_release_evidence\checksums_sha256_" + $ReleaseName + "_" + $Today + ".txt")
$ValidationPath = Join-Path $ReleaseDir ("70_release_evidence\validation_log_template_" + $ReleaseName + "_" + $Today + ".txt")
$ChecklistPath = Join-Path $ReleaseDir ("70_release_evidence\release_verification_checklist_" + $ReleaseName + "_" + $Today + ".md")

function Invoke-ReleaseStep([string]$Label, [scriptblock]$Command) {
    Write-Host ""
    Write-Host "=== $Label ==="
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

function Assert-FileExists([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "Required release artifact not found: $Path"
    }
}

function Get-DefaultReleaseTitle([string]$Name) {
    return "NameVerification $Name"
}

function Get-DefaultReleaseNotes([string]$Name, [bool]$IsPrerelease) {
    if ($IsPrerelease) {
        return "$Name release candidate. Build/package/portable smoke passed."
    }
    return "NameVerification $Name stable release. Build/package/portable smoke passed."
}

Push-Location $ProjectRoot
try {
    Invoke-ReleaseStep "quality gate / EXE build" {
        & (Join-Path $ScriptRoot "build_exe_windows.ps1")
    }

    Invoke-ReleaseStep "portable package" {
        & (Join-Path $ScriptRoot "package_release_windows.ps1") -ReleaseName $ReleaseName
    }

    Invoke-ReleaseStep "portable smoke" {
        & (Join-Path $ScriptRoot "smoke_test_portable_windows.ps1") `
            -ReleaseDir $ReleaseDir `
            -StartupSeconds $StartupSeconds
    }

    Assert-FileExists $ZipPath
    Assert-FileExists $ManifestPath
    Assert-FileExists $ChecksumPath
    Assert-FileExists $ValidationPath

    Invoke-ReleaseStep "release verification checklist" {
        & (Join-Path $ScriptRoot "generate_release_checklist_windows.ps1") `
            -ReleaseName $ReleaseName `
            -ReleaseDir $ReleaseDir
    }
    Assert-FileExists $ChecklistPath

    if ($CreateGitHubRelease) {
        $GhCommand = Get-Command gh -ErrorAction SilentlyContinue
        if ($null -eq $GhCommand) {
            throw "GitHub CLI 'gh' was not found. Install GitHub CLI or omit -CreateGitHubRelease."
        }

        if ([string]::IsNullOrWhiteSpace($ReleaseTitle)) {
            $ReleaseTitle = Get-DefaultReleaseTitle $ReleaseName
        }
        if ([string]::IsNullOrWhiteSpace($ReleaseNotes)) {
            $ReleaseNotes = Get-DefaultReleaseNotes $ReleaseName $Prerelease.IsPresent
        }

        $Args = @(
            "release",
            "create",
            $ReleaseName,
            $ZipPath,
            $ManifestPath,
            $ChecksumPath,
            $ValidationPath,
            $ChecklistPath,
            "--title",
            $ReleaseTitle,
            "--notes",
            $ReleaseNotes
        )
        if ($Prerelease) {
            $Args += "--prerelease"
        }

        Invoke-ReleaseStep "GitHub release create" {
            & gh @Args
        }
    }

    Write-Host ""
    Write-Host "Release workflow complete."
    Write-Host "Release name: $ReleaseName"
    Write-Host "Release directory: $ReleaseDir"
    Write-Host "Zip: $ZipPath"
    Write-Host "Manifest: $ManifestPath"
    Write-Host "Checksums: $ChecksumPath"
    Write-Host "Validation template: $ValidationPath"
    Write-Host "Verification checklist: $ChecklistPath"
} finally {
    Pop-Location
}
