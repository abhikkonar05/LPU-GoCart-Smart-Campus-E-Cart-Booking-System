# ==============================================================================
# LPU GoCart - PostgreSQL Database Backup Script (Windows 11)
# Exports database tables and records to a timestamped SQL dump.
# ==============================================================================
param (
    [string]$DbUrl = $env:DATABASE_URL,
    [string]$OutputDir = "$PSScriptRoot\..\database\backups"
)

Write-Host "=== LPU GoCart Database Backup Tool ===" -ForegroundColor Cyan

if (-not $DbUrl) {
    # Check backend/.env
    $envFile = "$PSScriptRoot\..\backend\.env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^DATABASE_URL=(.+)$") {
                $DbUrl = $matches[1].Trim()
            }
        }
    }
}

if (-not $DbUrl -or $DbUrl -like "*sqlite*") {
    Write-Host "[INFO] Local SQLite in use. Copying lpu_gocart.db..." -ForegroundColor Yellow
    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }
    $timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $target = "$OutputDir\lpu_gocart_$timestamp.db"
    Copy-Item "$PSScriptRoot\..\backend\lpu_gocart.db" $target -ErrorAction SilentlyContinue
    Write-Host "[OK] SQLite backup saved to $target" -ForegroundColor Green
    exit 0
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$backupFile = "$OutputDir\backup_$timestamp.sql"

Write-Host "Dumping PostgreSQL database to $backupFile..." -ForegroundColor Yellow

$pgDump = Get-Command "pg_dump" -ErrorAction SilentlyContinue
if ($pgDump) {
    & pg_dump $DbUrl -f $backupFile --clean --if-exists
    Write-Host "[OK] PostgreSQL backup created: $backupFile" -ForegroundColor Green
} else {
    Write-Host "[ERROR] pg_dump not found in system PATH." -ForegroundColor Red
    Write-Host "Please install PostgreSQL client tools or export via Render dashboard." -ForegroundColor Yellow
}
