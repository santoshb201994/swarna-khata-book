Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " Starting Swarna Khata Book - Jewellery ERP (Local MVP)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Yellow

$RootDir = $PSScriptRoot

# Ensure uv is in PATH
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    $env:PATH = "C:\Users\lenovo\AppData\Local\Programs\Python\Python312\Scripts;$env:PATH"
}

# Ensure uv environment is prepared with Python 3.12
if (-not (Test-Path "$RootDir\.venv\Scripts\python.exe")) {
    Write-Host "`nSyncing Python 3.12 virtual environment using uv..." -ForegroundColor Cyan
    & uv sync
}

# Start Backend (ASGI with Uvicorn for WebSocket Mobile QR Sync)
Write-Host "`n[1/2] Starting Django ASGI Server on http://localhost:8000..." -ForegroundColor Green
$BackendProcess = Start-Process -FilePath "uv" `
    -ArgumentList "run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload" `
    -WorkingDirectory "$RootDir\backend" `
    -PassThru

# Start Frontend
Write-Host "[2/2] Starting React + Vite Dev Server on http://localhost:5173..." -ForegroundColor Green
$FrontendProcess = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run dev" `
    -WorkingDirectory "$RootDir\frontend" `
    -PassThru

Write-Host "`nSwarna Khata Book is running!" -ForegroundColor Cyan
Write-Host "  - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend API: http://localhost:8000/api/" -ForegroundColor White
Write-Host "  - Django Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "  - Demo Login: admin / admin123" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C or close this window to stop both servers."

try {
    Wait-Process -Id $FrontendProcess.Id
} finally {
    Stop-Process -Id $BackendProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $FrontendProcess.Id -ErrorAction SilentlyContinue
}
