# ==============================================================================
# LPU GoCart - Automated Windows Setup Script
# ==============================================================================
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "          Setting up LPU GoCart Development Workspace     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Setup Backend Python Virtual Environment
Write-Host "`n[1/3] Setting up Python Virtual Environment in /backend..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\backend"

if (-not (Test-Path -Path ".\.venv")) {
    Write-Host "Creating virtual environment '.venv'..." -ForegroundColor Cyan
    python -m venv .venv
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "Virtual environment '.venv' already exists." -ForegroundColor Green
}

# 2. Setup environment files from templates if not existing
Write-Host "`n[2/3] Checking environment configuration (.env) files..." -ForegroundColor Yellow
if (-not (Test-Path -Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "Created backend/.env from .env.example (Remember to fill in Supabase credentials!)" -ForegroundColor Green
} else {
    Write-Host "backend/.env already exists." -ForegroundColor Green
}

# Admin dashboard env
Set-Location -Path "$PSScriptRoot\..\apps\admin-dashboard"
if (Test-Path -Path ".\.env.example") {
    if (-not (Test-Path -Path ".\.env")) {
        Copy-Item ".\.env.example" ".\.env"
        Write-Host "Created apps/admin-dashboard/.env from .env.example" -ForegroundColor Green
    }
}

# 3. Monorepo Root setup complete
Set-Location -Path "$PSScriptRoot\.."
Write-Host "`n[3/3] Setup complete!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Next Step: Proceed with Phase 2 (Supabase Database Setup)!" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

