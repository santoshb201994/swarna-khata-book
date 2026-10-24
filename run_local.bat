@echo off
title Swarna Khata Book - Local MVP
echo ==========================================================
echo  Starting Swarna Khata Book - Jewellery ERP (Local MVP)
echo ==========================================================

where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    set "PATH=C:\Users\lenovo\AppData\Local\Programs\Python\Python312\Scripts;%PATH%"
)

if not exist "%~dp0.venv" (
    echo Syncing environment with uv...
    uv sync
)

start "Swarna Khata Backend (Django ASGI)" /D "%~dp0backend" uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
start "Swarna Khata Frontend (Vite)" /D "%~dp0frontend" npm.cmd run dev

echo.
echo Servers starting in background windows:
echo   - Frontend:    http://localhost:5173
echo   - Backend API: http://localhost:8000/api/
echo   - Admin Panel: http://localhost:8000/admin/
echo   - Credentials: admin / admin123
echo.
pause
