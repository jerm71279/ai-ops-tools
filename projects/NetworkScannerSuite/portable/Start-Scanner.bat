@echo off
setlocal EnableDelayedExpansion

title Obera Network Scanner - Portable

echo ======================================
echo  OBERA NETWORK SCANNER - PORTABLE
echo ======================================
echo.

:: Get the drive/directory where this script is located
set "SCANNER_ROOT=%~dp0"
set "PYTHON_DIR=%SCANNER_ROOT%python"
set "SERVICE_DIR=%SCANNER_ROOT%service"
set "NMAP_DIR=%SCANNER_ROOT%nmap"

:: Check if running with admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Not running as Administrator
    echo Some scans may require elevated privileges
    echo.
)

:: Check dependencies
echo Checking dependencies...

if not exist "%PYTHON_DIR%\python.exe" (
    echo ERROR: Python not found at %PYTHON_DIR%
    echo Please run Setup-Portable.bat first
    pause
    exit /b 1
)

if not exist "%NMAP_DIR%\nmap.exe" (
    echo ERROR: Nmap not found at %NMAP_DIR%
    echo Please run Setup-Portable.bat first
    pause
    exit /b 1
)

if not exist "%SERVICE_DIR%\scanner_service.py" (
    echo ERROR: Scanner service not found
    pause
    exit /b 1
)

:: Add Nmap to PATH for this session
set "PATH=%NMAP_DIR%;%PATH%"

:: Create scans directory if it doesn't exist
if not exist "%SERVICE_DIR%\scans" mkdir "%SERVICE_DIR%\scans"

:: Get local IP for display
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
    goto :gotip
)
:gotip

echo.
echo Starting scanner service...
echo.
echo ======================================
echo  Scanner will be available at:
echo  http://localhost:8080
echo  http://!LOCAL_IP!:8080
echo ======================================
echo.
echo Press Ctrl+C to stop the scanner
echo.

:: Start the service
cd /d "%SERVICE_DIR%"
"%PYTHON_DIR%\python.exe" scanner_service.py

pause
