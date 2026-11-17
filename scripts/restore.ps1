# ==============================================================================
# LPU GoCart - PostgreSQL Database Restore Script (Windows 11)
# Restores database from a SQL backup file.
# ==============================================================================
param (
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$DbUrl = $env:DATABASE_URL
)

Write-Host "=== LPU GoCart Database Restore Tool ===" -ForegroundColor Cyan

if (-not (Test-Path $BackupFile)) {
    Write-Host "[ERROR] Backup file not found: $BackupFile" -ForegroundColor Red
    exit 1
}

if (-not $DbUrl) {
    $envFile = "$PSScriptRoot\..\backend\.env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^DATABASE_URL=(.+)$") {
                $DbUrl = $matches[1].Trim()
            }
        }
    }
}

if ($BackupFile -like "*.db" -or $DbUrl -like "*sqlite*") {
    Write-Host "[INFO] Restoring SQLite database..." -ForegroundColor Yellow
    Copy-Item $BackupFile "$PSScriptRoot\..\backend\lpu_gocart.db" -Force
    Write-Host "[OK] SQLite database restored." -ForegroundColor Green
    exit 0
}

$psql = Get-Command "psql" -ErrorAction SilentlyContinue
if ($psql) {
    Write-Host "Applying $BackupFile to PostgreSQL..." -ForegroundColor Yellow
    & psql $DbUrl -f $BackupFile
    Write-Host "[OK] Database restored successfully." -ForegroundColor Green
} else {
    Write-Host "[ERROR] psql command not found in PATH." -ForegroundColor Red
}
