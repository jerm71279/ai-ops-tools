<#
.SYNOPSIS
    Builds the Obera Network Scanner Windows installer package.

.DESCRIPTION
    This script:
    1. Downloads Python embedded distribution
    2. Downloads Nmap portable
    3. Packages all components
    4. Compiles the NSIS installer

.NOTES
    Prerequisites:
    - NSIS installed (https://nsis.sourceforge.io/)
    - Internet connection for downloads
#>

param(
    [switch]$SkipDownloads,
    [string]$OutputDir = ".\output"
)

$ErrorActionPreference = "Stop"

$PythonVersion = "3.11.0"
$NmapVersion = "7.94"
$InstallerDir = $PSScriptRoot

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Obera Network Scanner Installer Build" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Download Python embedded
if (!$SkipDownloads) {
    $pythonDir = "$InstallerDir\python-embedded"
    if (!(Test-Path $pythonDir)) {
        Write-Host "Downloading Python $PythonVersion embedded..." -ForegroundColor Yellow
        $pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
        $pythonZip = "$env:TEMP\python-embed.zip"

        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
        Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
        Remove-Item $pythonZip

        # Download get-pip.py
        Write-Host "Downloading pip installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$pythonDir\get-pip.py"

        Write-Host "Python embedded downloaded" -ForegroundColor Green
    } else {
        Write-Host "Python embedded already exists, skipping download" -ForegroundColor Gray
    }

    # Download Nmap portable
    $nmapDir = "$InstallerDir\nmap"
    if (!(Test-Path $nmapDir)) {
        Write-Host "Downloading Nmap $NmapVersion..." -ForegroundColor Yellow
        $nmapUrl = "https://nmap.org/dist/nmap-$NmapVersion-win32.zip"
        $nmapZip = "$env:TEMP\nmap.zip"

        Invoke-WebRequest -Uri $nmapUrl -OutFile $nmapZip
        Expand-Archive -Path $nmapZip -DestinationPath $env:TEMP -Force

        # Move and rename
        Move-Item "$env:TEMP\nmap-$NmapVersion" $nmapDir
        Remove-Item $nmapZip

        Write-Host "Nmap downloaded" -ForegroundColor Green
    } else {
        Write-Host "Nmap already exists, skipping download" -ForegroundColor Gray
    }
}

# Create placeholder icon if not exists
$iconPath = "$InstallerDir\assets\obera-icon.ico"
if (!(Test-Path $iconPath)) {
    Write-Host "Note: obera-icon.ico not found. Using placeholder." -ForegroundColor Yellow
    Write-Host "Replace with actual icon at: $iconPath" -ForegroundColor Yellow

    # Create a minimal ICO file (1x1 pixel)
    # This is a valid but tiny ICO for testing
    $icoBytes = [byte[]]@(
        0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00,
        0x18, 0x00, 0x30, 0x00, 0x00, 0x00, 0x16, 0x00, 0x00, 0x00, 0x28, 0x00,
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01, 0x00,
        0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00
    )
    [System.IO.File]::WriteAllBytes($iconPath, $icoBytes)
}

# Check for NSIS
$nsisPath = Get-Command makensis -ErrorAction SilentlyContinue
if (!$nsisPath) {
    # Try common install locations
    $nsisLocations = @(
        "C:\Program Files (x86)\NSIS\makensis.exe",
        "C:\Program Files\NSIS\makensis.exe"
    )

    foreach ($loc in $nsisLocations) {
        if (Test-Path $loc) {
            $nsisPath = $loc
            break
        }
    }

    if (!$nsisPath) {
        Write-Host "ERROR: NSIS not found!" -ForegroundColor Red
        Write-Host "Download from: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "After installing NSIS, run this script again." -ForegroundColor Yellow
        exit 1
    }
} else {
    $nsisPath = $nsisPath.Source
}

Write-Host ""
Write-Host "Building installer with NSIS..." -ForegroundColor Yellow

# Compile installer
Push-Location $InstallerDir
try {
    & $nsisPath OberaScanner.nsi
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "======================================" -ForegroundColor Green
        Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Installer created: $InstallerDir\OberaNetworkScanner-Setup.exe" -ForegroundColor White

        # Move to output directory
        if (Test-Path "$InstallerDir\OberaNetworkScanner-Setup.exe") {
            Move-Item "$InstallerDir\OberaNetworkScanner-Setup.exe" "$OutputDir\" -Force
            Write-Host "Moved to: $OutputDir\OberaNetworkScanner-Setup.exe" -ForegroundColor White
        }
    } else {
        Write-Host "BUILD FAILED!" -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the installer on a Windows machine"
Write-Host "2. Replace placeholder icon with actual Obera icon"
Write-Host "3. Sign the installer with a code signing certificate"
Write-Host ""
