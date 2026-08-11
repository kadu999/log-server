@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PORT=9101"
if not "%~1"=="" set "PORT=%~1"

if not exist "cloudflared.exe" (
    echo Downloading cloudflared...
    curl -L -o cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    if errorlevel 1 (
        echo Cloudflared download failed.
        pause
        exit /b 1
    )
)

echo Starting local log server on port %PORT%...
powershell -NoProfile -Command "Start-Process -FilePath 'python' -ArgumentList @('server.py','--host','127.0.0.1','--port','%PORT%','--upload-dir','%~dp0uploads') -WorkingDirectory '%~dp0' -WindowStyle Hidden"

echo Starting Cloudflare tunnel...
echo Public URL will be printed below and looks like https://xxxx.trycloudflare.com
cloudflared.exe tunnel --url http://127.0.0.1:%PORT%

pause
