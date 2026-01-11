@echo off
setlocal EnableDelayedExpansion

title Obera Network Scanner - Portable Setup

echo ======================================
echo  OBERA NETWORK SCANNER PORTABLE SETUP
echo ======================================
echo.

:: Get the drive/directory where this script is located
set "SCANNER_ROOT=%~dp0"
set "PYTHON_DIR=%SCANNER_ROOT%python"
set "NMAP_DIR=%SCANNER_ROOT%nmap"

:: Check for internet connection
ping -n 1 www.google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: No internet connection detected
    echo Setup requires internet to download components
    echo.
)

:: Download Python embedded if not present
if not exist "%PYTHON_DIR%\python.exe" (
    echo Downloading Python embedded...

    if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"

    :: Download using PowerShell
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip' -OutFile '%TEMP%\python-embed.zip'}"

    if %errorlevel% neq 0 (
        echo ERROR: Failed to download Python
        pause
        exit /b 1
    )

    :: Extract
    echo Extracting Python...
    powershell -Command "Expand-Archive -Path '%TEMP%\python-embed.zip' -DestinationPath '%PYTHON_DIR%' -Force"
    del "%TEMP%\python-embed.zip"

    :: Enable pip
    echo Configuring Python...
    echo import site>> "%PYTHON_DIR%\python311._pth"

    :: Download and install pip
    echo Installing pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py'"
    "%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location

    echo Python installed successfully
    echo.
) else (
    echo Python already present
)

:: Install Python dependencies
echo Installing Python dependencies...
"%PYTHON_DIR%\python.exe" -m pip install -r "%SCANNER_ROOT%service\requirements.txt" --no-warn-script-location -q
echo Dependencies installed
echo.

:: Download Nmap if not present
if not exist "%NMAP_DIR%\nmap.exe" (
    echo Downloading Nmap...

    if not exist "%NMAP_DIR%" mkdir "%NMAP_DIR%"

    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://nmap.org/dist/nmap-7.94-win32.zip' -OutFile '%TEMP%\nmap.zip'}"

    if %errorlevel% neq 0 (
        echo ERROR: Failed to download Nmap
        pause
        exit /b 1
    )

    :: Extract
    echo Extracting Nmap...
    powershell -Command "Expand-Archive -Path '%TEMP%\nmap.zip' -DestinationPath '%TEMP%\nmap-extract' -Force"

    :: Move files
    xcopy /E /I /Y "%TEMP%\nmap-extract\nmap-7.94\*" "%NMAP_DIR%\"
    rmdir /S /Q "%TEMP%\nmap-extract"
    del "%TEMP%\nmap.zip"

    echo Nmap installed successfully
    echo.
) else (
    echo Nmap already present
)

:: Create scans directory
if not exist "%SCANNER_ROOT%service\scans" mkdir "%SCANNER_ROOT%service\scans"

echo.
echo ======================================
echo  SETUP COMPLETE!
echo ======================================
echo.
echo Run Start-Scanner.bat to launch the scanner
echo.

pause
