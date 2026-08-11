@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PYTHONUTF8=1"
set "PORT=8000"
if not "%~1"=="" set "PORT=%~1"

echo Starting log server on port %PORT%...
python server.py --host 0.0.0.0 --port %PORT%
if errorlevel 1 (
    echo.
    echo Server failed. Check Python and firewall settings.
    pause
    exit /b 1
)

pause
