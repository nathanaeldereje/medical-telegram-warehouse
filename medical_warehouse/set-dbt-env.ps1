# medical_warehouse\set-dbt-env.ps1
# Sets ONLY the dbt PostgreSQL environment variables from ../.env
# Run this once per terminal session before dbt commands

$envFile = Join-Path -Path $PSScriptRoot -ChildPath "..\.env"

if (-Not (Test-Path $envFile)) {
    Write-Host "Error: .env not found at $envFile" -ForegroundColor Red
    exit 1
}

Write-Host "Setting dbt env vars from .env..." -ForegroundColor Cyan

# Read .env and set only POSTGRES_* variables
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*$" -or $_ -match "^\s*#") { return }  # skip empty / comments

    if ($_ -match "^(POSTGRES_[A-Z_]+)=(.*)$") {
        $key   = $matches[1].Trim()
        $value = $matches[2].Trim()

        # Strip quotes if present
        if ($value -match '^"(.*)"$') { $value = $matches[1] }
        elseif ($value -match "^'(.*)'$") { $value = $matches[1] }

        Set-Item -Path Env:$key -Value $value
        Write-Host "  $key set" -ForegroundColor Green
    }
}

Write-Host "`ndbt environment variables are now set." -ForegroundColor Green
Write-Host "You can now run dbt commands in this terminal." -ForegroundColor Yellow
Write-Host "Example:"
Write-Host "  dbt debug --profiles-dir ."
Write-Host "  dbt run"
Write-Host "  dbt test"