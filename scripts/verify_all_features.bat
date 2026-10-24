@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_all_features.ps1"
exit /b %ERRORLEVEL%
