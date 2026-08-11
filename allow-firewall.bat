@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PORT=9101"
if not "%~1"=="" set "PORT=%~1"

net session >nul 2>&1
if errorlevel 1 (
    echo Requesting administrator permission...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -ArgumentList '%~1' -Verb RunAs"
    exit /b
)

echo Opening firewall port %PORT%...
netsh advfirewall firewall delete rule name="StreamCast Log Server %PORT%" >nul 2>&1
netsh advfirewall firewall add rule name="StreamCast Log Server %PORT%" dir=in action=allow protocol=TCP localport=%PORT% >nul

if errorlevel 1 (
    echo Failed to open port %PORT%.
) else (
    echo Port %PORT% opened successfully.
)

pause
