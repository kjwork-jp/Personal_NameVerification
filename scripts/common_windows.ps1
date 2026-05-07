function Stop-NameVerificationProcesses {
    param(
        [int[]]$ExceptProcessIds = @()
    )

    $processes = Get-Process -Name "NameVerification" -ErrorAction SilentlyContinue
    foreach ($process in $processes) {
        if ($ExceptProcessIds -contains $process.Id) {
            continue
        }
        Write-Host "Stopping existing NameVerification process: $($process.Id)"
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        try {
            $process.WaitForExit(5000) | Out-Null
        } catch {
            # Best effort only.
        }
    }
}

function Remove-PathBestEffort {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return
    }

    try {
        Remove-Item $Path -Recurse -Force -ErrorAction Stop
    } catch {
        throw "Failed to remove path: $Path. Close running NameVerification.exe processes and retry. Original error: $($_.Exception.Message)"
    }
}
