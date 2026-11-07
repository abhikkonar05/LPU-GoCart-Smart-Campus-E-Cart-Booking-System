# ==============================================================================
# LPU GoCart - Windows 11 Environment & Prerequisite Diagnostic Tool
# ==============================================================================
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       LPU GoCart - Windows 11 Environment Check          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$AllGood = $true

# Helper function to check commands
function Test-CommandAvailable {
    param (
        [string]$CommandName,
        [string]$DisplayName,
        [string]$VersionCommand,
        [string]$MinRecommended
    )
    
    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($cmd) {
        try {
            $versionOutput = Invoke-Expression $VersionCommand 2>$null
            $cleanVersion = ($versionOutput | Select-Object -First 1).Trim()
            Write-Host "[OK] $DisplayName found: $cleanVersion" -ForegroundColor Green
        } catch {
            Write-Host "[OK] $DisplayName found at: $($cmd.Source)" -ForegroundColor Green
        }
    } else {
        Write-Host "[MISSING] $DisplayName is NOT installed or not in PATH." -ForegroundColor Red
        Write-Host "          Recommendation: $MinRecommended" -ForegroundColor Yellow
        $script:AllGood = $false
    }
}

# 1. Check Node.js
Test-CommandAvailable -CommandName "node" -DisplayName "Node.js" -VersionCommand "node -v" -MinRecommended "Install Node.js v20+ LTS from https://nodejs.org/"

# 2. Check NPM
Test-CommandAvailable -CommandName "npm" -DisplayName "NPM" -VersionCommand "npm -v" -MinRecommended "Installed with Node.js"

# 3. Check Python
Test-CommandAvailable -CommandName "python" -DisplayName "Python" -VersionCommand "python --version" -MinRecommended "Install Python 3.11+ from https://python.org/ (Check 'Add Python to PATH')"

# 4. Check Git
Test-CommandAvailable -CommandName "git" -DisplayName "Git" -VersionCommand "git --version" -MinRecommended "Install Git from https://git-scm.com/download/win"

# 5. Check Ports (8000 for FastAPI, 5173 for Vite Admin)
Write-Host ""
Write-Host "--- Checking Local Ports Availability ---" -ForegroundColor Cyan

function Test-PortAvailability {
    param ([int]$Port, [string]$ServiceDescription)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "[WARNING] Port $Port ($ServiceDescription) is currently in use by PID: $($connection[0].OwningProcess)" -ForegroundColor Yellow
    } else {
        Write-Host "[AVAILABLE] Port $Port ($ServiceDescription) is free." -ForegroundColor Green
    }
}

Test-PortAvailability -Port 8000 -ServiceDescription "FastAPI Backend"
Test-PortAvailability -Port 5173 -ServiceDescription "Admin Dashboard (Vite)"
Test-PortAvailability -Port 8081 -ServiceDescription "Expo Dev Server"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
if ($AllGood) {
    Write-Host " System Status: READY FOR DEVELOPMENT!" -ForegroundColor Green
} else {
    Write-Host " System Status: Some recommended tools are missing." -ForegroundColor Yellow
    Write-Host " Please install missing tools and re-run this script." -ForegroundColor Yellow
}
Write-Host "==========================================================" -ForegroundColor Cyan

