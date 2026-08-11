@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PYTHONUTF8=1"
set "PORT=8000"
if not "%~1"=="" set "PORT=%~1"
set "UPLOAD_DIR=%~dp0uploads"
if not "%~2"=="" set "UPLOAD_DIR=%~2"
if not exist "%UPLOAD_DIR%" mkdir "%UPLOAD_DIR%"

echo Starting log server on port %PORT%...
echo Upload directory: %UPLOAD_DIR%
python server.py --host 0.0.0.0 --port %PORT% --upload-dir "%UPLOAD_DIR%"
if errorlevel 1 (
    echo.
    echo Server failed. Check Python and firewall settings.
    pause
    exit /b 1
)

pause
