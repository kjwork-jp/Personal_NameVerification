param(
    [string]$Workflow = "Quality Gates",
    [string]$CommitSha = "",
    [string]$Branch = "main",
    [int]$TimeoutSeconds = 900,
    [int]$PollSeconds = 10,
    [string]$Repo = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-GhJson {
    param([string[]]$Arguments)

    $output = & gh @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) {
        return $null
    }
    if ([string]::IsNullOrWhiteSpace($output)) {
        return $null
    }
    return $output | ConvertFrom-Json
}

function Build-GhArgs {
    param([string[]]$Arguments)

    $items = @()
    if (-not [string]::IsNullOrWhiteSpace($Repo)) {
        $items += @("--repo", $Repo)
    }
    $items += $Arguments
    return $items
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI 'gh' was not found. Install gh and run 'gh auth login'."
    exit 2
}

& gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Error "GitHub CLI is not authenticated. Run 'gh auth login' first."
    exit 2
}

if ([string]::IsNullOrWhiteSpace($CommitSha)) {
    $CommitSha = (& git rev-parse HEAD).Trim()
}

if ([string]::IsNullOrWhiteSpace($CommitSha)) {
    Write-Error "Commit SHA could not be resolved. Pass -CommitSha explicitly."
    exit 2
}

Write-Host "Waiting for workflow '$Workflow' on commit $CommitSha ..."
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$run = $null

while ((Get-Date) -lt $deadline) {
    $args = Build-GhArgs @(
        "run", "list",
        "--workflow", $Workflow,
        "--branch", $Branch,
        "--commit", $CommitSha,
        "--limit", "10",
        "--json", "databaseId,status,conclusion,displayTitle,headSha,url,workflowName,createdAt"
    )
    $runs = Invoke-GhJson $args

    if ($null -ne $runs) {
        $run = @($runs | Where-Object { $_.headSha -eq $CommitSha } | Select-Object -First 1)
        if ($run.Count -gt 0) {
            $run = $run[0]
            break
        }
    }

    Start-Sleep -Seconds $PollSeconds
}

if ($null -eq $run) {
    Write-Error "No workflow run found for commit $CommitSha within $TimeoutSeconds seconds."
    exit 3
}

$runId = [string]$run.databaseId
Write-Host "Found run: $runId / $($run.displayTitle)"
Write-Host $run.url

$watchArgs = Build-GhArgs @(
    "run", "watch", $runId,
    "--compact",
    "--exit-status",
    "--interval", [string]$PollSeconds
)
& gh @watchArgs
$watchExit = $LASTEXITCODE

$viewArgs = Build-GhArgs @(
    "run", "view", $runId,
    "--json", "status,conclusion,displayTitle,headSha,url,workflowName"
)
$view = Invoke-GhJson $viewArgs

if ($null -ne $view) {
    Write-Host "Workflow: $($view.workflowName)"
    Write-Host "Title:    $($view.displayTitle)"
    Write-Host "Status:   $($view.status)"
    Write-Host "Result:   $($view.conclusion)"
    Write-Host "Commit:   $($view.headSha)"
    Write-Host "URL:      $($view.url)"
}

if ($watchExit -ne 0) {
    Write-Host ""
    Write-Host "Failed steps log:"
    $failedLogArgs = Build-GhArgs @("run", "view", $runId, "--log-failed")
    & gh @failedLogArgs
    exit $watchExit
}

Write-Host "Quality Gates passed for commit $CommitSha."
exit 0
