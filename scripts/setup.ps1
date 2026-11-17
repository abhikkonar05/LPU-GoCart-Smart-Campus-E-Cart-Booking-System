# ==============================================================================
# LPU GoCart - Automated Setup Script (Windows 11)
# ==============================================================================
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "        Setting up LPU GoCart Full-Stack Platform         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Backend Python Virtual Environment
Write-Host "`n[1/4] Setting up Python virtual environment in /backend..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\backend"

if (-not (Test-Path -Path ".\.venv")) {
    python -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# 2. Install backend dependencies
Write-Host "`n[2/4] Installing backend Python packages..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Setup backend environment file if missing
if (-not (Test-Path -Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "Created backend/.env from template." -ForegroundColor Green
}

# 4. Install frontend dependencies
Write-Host "`n[3/4] Installing frontend React packages..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\frontend"
npm install

if (-not (Test-Path -Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "Created frontend/.env from template." -ForegroundColor Green
}

Set-Location -Path "$PSScriptRoot\.."
Write-Host "`n[4/4] Setup complete!" -ForegroundColor Green
Write-Host "Run .\scripts\start.ps1 to start both servers." -ForegroundColor Cyan
