# ==============================================================================
# LPU GoCart - One-Click Start Script (Windows 11)
# ==============================================================================
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "             Starting LPU GoCart Services                 " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$BackendScript = "cd '$PSScriptRoot\..\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 127.0.0.1 --port 8000"
$FrontendScript = "cd '$PSScriptRoot\..\frontend'; npm run dev -- --host 127.0.0.1 --port 5173"

Write-Host "`n[1/2] Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $BackendScript

Write-Host "[2/2] Launching React Frontend on http://127.0.0.1:5173..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $FrontendScript

Write-Host "`nBoth services are now running!" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "Backend API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
