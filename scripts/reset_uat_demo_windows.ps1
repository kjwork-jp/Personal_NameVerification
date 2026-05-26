<#
.SYNOPSIS
Reset a local UAT demo database with richer sample data and fixed local users.

.DESCRIPTION
This script is intended for manual Windows/PowerShell UAT.
It recreates tmp\uat_demo.db, generates bulk business data, optionally generates CSV data,
and resets fixed local users:

- admin  / admin-pass
- editor / editor-pass
- viewer / viewer-pass

The data is intentionally larger than the small `--preset demo` set so UI tables,
filters, related counts, role guards, and operations screens can be checked with
realistic row volume.
#>

param(
    [string]$DbPath = "tmp\uat_demo.db",
    [string]$CsvDir = "tmp\uat_demo_csv",
    [int]$Names = 80,
    [int]$Titles = 18,
    [int]$SubtitlesPerTitle = 4,
    [int]$LinksPerName = 3,
    [switch]$SkipCsv,
    [switch]$Launch
)

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Remove old UAT demo files" -ForegroundColor Cyan
Remove-Item -Force $DbPath -ErrorAction SilentlyContinue
if (-not $SkipCsv) {
    Remove-Item -Recurse -Force $CsvDir -ErrorAction SilentlyContinue
}

Write-Host "[2/5] Generate richer SQLite sample data" -ForegroundColor Cyan
python .\scripts\generate_sample_data.py `
    --preset bulk `
    --format sqlite `
    --output $DbPath `
    --names $Names `
    --titles $Titles `
    --subtitles-per-title $SubtitlesPerTitle `
    --links-per-name $LinksPerName

if (-not $SkipCsv) {
    Write-Host "[3/5] Generate matching CSV sample data" -ForegroundColor Cyan
    python .\scripts\generate_sample_data.py `
        --preset bulk `
        --format csv `
        --output $CsvDir `
        --names $Names `
        --titles $Titles `
        --subtitles-per-title $SubtitlesPerTitle `
        --links-per-name $LinksPerName
} else {
    Write-Host "[3/5] Skip CSV generation" -ForegroundColor DarkGray
}

Write-Host "[4/5] Reset fixed UAT local users" -ForegroundColor Cyan
@'
from pathlib import Path

from app.application.user_services import CreateUserInput, UserService
from app.infrastructure.db import initialize_database

DB_PATH = Path(r"__DB_PATH__")
connection = initialize_database(DB_PATH)

try:
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("DELETE FROM user_audit_logs;")
    connection.execute("DELETE FROM users;")
    connection.commit()

    service = UserService(connection)
    users = [
        ("admin", "admin-pass", "admin", "UAT Admin"),
        ("editor", "editor-pass", "editor", "UAT Editor"),
        ("viewer", "viewer-pass", "viewer", "UAT Viewer"),
    ]

    for operator_id, password, role, display_name in users:
        service.create_user(
            CreateUserInput(
                operator_id=operator_id,
                password=password,
                role=role,
                display_name=display_name,
            ),
            actor_operator_id="uat-bootstrap",
            actor_role="admin",
        )

    counts = {
        "names": connection.execute("SELECT COUNT(*) FROM names").fetchone()[0],
        "titles": connection.execute("SELECT COUNT(*) FROM titles").fetchone()[0],
        "subtitles": connection.execute("SELECT COUNT(*) FROM subtitles").fetchone()[0],
        "name_title_links": connection.execute("SELECT COUNT(*) FROM name_title_links").fetchone()[0],
        "name_subtitle_links": connection.execute("SELECT COUNT(*) FROM name_subtitle_links").fetchone()[0],
        "users": connection.execute("SELECT COUNT(*) FROM users").fetchone()[0],
    }

    print("UAT data counts:")
    for key, value in counts.items():
        print(f"  {key}: {value}")

    print("UAT users reset:")
    rows = connection.execute(
        """
        SELECT operator_id, role, auth_provider, disabled_at
        FROM users
        ORDER BY
            CASE role
                WHEN 'admin' THEN 1
                WHEN 'editor' THEN 2
                WHEN 'viewer' THEN 3
                ELSE 9
            END
        """
    ).fetchall()
    for row in rows:
        print(tuple(row))
finally:
    connection.close()
'@.Replace("__DB_PATH__", $DbPath.Replace("\", "\")) | python -

Write-Host "[5/5] Verify tmp is not tracked" -ForegroundColor Cyan
git status --short tmp

Write-Host ""
Write-Host "UAT login users:" -ForegroundColor Green
Write-Host "  admin  / admin-pass"
Write-Host "  editor / editor-pass"
Write-Host "  viewer / viewer-pass"
Write-Host ""
Write-Host "Launch manually:" -ForegroundColor Green
Write-Host "  `$env:NAMEVERIFICATION_DB_PATH = `"$DbPath`""
Write-Host "  python -m app.pyside6_main"

if ($Launch) {
    Write-Host "Launching application..." -ForegroundColor Cyan
    $env:NAMEVERIFICATION_DB_PATH = $DbPath
    python -m app.pyside6_main
}
