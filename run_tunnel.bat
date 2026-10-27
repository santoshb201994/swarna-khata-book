@echo off
title Swarna Khata Book - Cloudflare Quick Tunnel
echo ==========================================================
echo  Starting Swarna Khata Book - Cloudflare Quick Tunnel
echo ==========================================================
echo.
echo Tunneling Frontend (and proxied Backend APIs) to the Internet...
echo Note: Only the frontend port (5173) is tunneled. Backend (8000)
echo       remains securely hidden on localhost via Vite reverse proxy.
echo.
cloudflared tunnel --url http://127.0.0.1:5173
pause
