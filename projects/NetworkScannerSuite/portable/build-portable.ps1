<#
.SYNOPSIS
    Builds a portable USB package for Obera Network Scanner.

.DESCRIPTION
    Creates a self-contained portable package that can be copied to USB
    or any folder and run without installation.

.PARAMETER OutputPath
    Where to create the portable package (default: .\OberaScanner-Portable)

.PARAMETER IncludeDependencies
    Pre-download Python and Nmap (makes package work offline)
#>

param(
    [string]$OutputPath = ".\OberaScanner-Portable",
    [switch]$IncludeDependencies
)

$ErrorActionPreference = "Stop"
$PortableDir = $PSScriptRoot

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Obera Network Scanner Portable Build" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (Test-Path $OutputPath) {
    Write-Host "Removing existing output directory..." -ForegroundColor Yellow
    Remove-Item -Path $OutputPath -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputPath | Out-Null
Write-Host "Created output directory: $OutputPath" -ForegroundColor Green

# Copy portable scripts
Write-Host "Copying portable scripts..." -ForegroundColor Yellow
Copy-Item "$PortableDir\Start-Scanner.bat" $OutputPath
Copy-Item "$PortableDir\Setup-Portable.bat" $OutputPath
Copy-Item "$PortableDir\README.txt" $OutputPath

# Copy service
Write-Host "Copying service files..." -ForegroundColor Yellow
$serviceDest = "$OutputPath\service"
New-Item -ItemType Directory -Path $serviceDest | Out-Null
Copy-Item "$PortableDir\..\service\*" $serviceDest -Recurse

# Copy web UI
Write-Host "Copying web UI..." -ForegroundColor Yellow
$webDest = "$OutputPath\web-ui"
New-Item -ItemType Directory -Path $webDest | Out-Null
Copy-Item "$PortableDir\..\web-ui\*" $webDest -Recurse

# Create scans directory
New-Item -ItemType Directory -Path "$serviceDest\scans" | Out-Null

# Optionally include dependencies for offline use
if ($IncludeDependencies) {
    Write-Host ""
    Write-Host "Downloading dependencies for offline use..." -ForegroundColor Yellow

    # Download Python embedded
    $pythonDir = "$OutputPath\python"
    Write-Host "  Downloading Python embedded..." -ForegroundColor Gray

    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip"
    $pythonZip = "$env:TEMP\python-embed.zip"

    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
    Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
    Remove-Item $pythonZip

    # Enable pip
    Add-Content -Path "$pythonDir\python311._pth" -Value "`nimport site"

    # Download get-pip
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$pythonDir\get-pip.py"

    # Install pip and dependencies
    Write-Host "  Installing pip and dependencies..." -ForegroundColor Gray
    & "$pythonDir\python.exe" "$pythonDir\get-pip.py" --no-warn-script-location 2>&1 | Out-Null
    & "$pythonDir\python.exe" -m pip install -r "$serviceDest\requirements.txt" --no-warn-script-location -q

    # Download Nmap
    $nmapDir = "$OutputPath\nmap"
    Write-Host "  Downloading Nmap..." -ForegroundColor Gray

    $nmapUrl = "https://nmap.org/dist/nmap-7.94-win32.zip"
    $nmapZip = "$env:TEMP\nmap.zip"

    Invoke-WebRequest -Uri $nmapUrl -OutFile $nmapZip
    Expand-Archive -Path $nmapZip -DestinationPath $env:TEMP -Force
    Move-Item "$env:TEMP\nmap-7.94" $nmapDir
    Remove-Item $nmapZip

    Write-Host "  Dependencies included" -ForegroundColor Green
}

# Calculate size
$size = (Get-ChildItem $OutputPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
$sizeStr = "{0:N1} MB" -f $size

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "PORTABLE BUILD COMPLETE!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package location: $OutputPath" -ForegroundColor White
Write-Host "Package size: $sizeStr" -ForegroundColor White
Write-Host ""

if ($IncludeDependencies) {
    Write-Host "Package includes all dependencies (offline-ready)" -ForegroundColor Cyan
} else {
    Write-Host "Note: User must run Setup-Portable.bat to download dependencies" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "To create USB package:" -ForegroundColor Cyan
Write-Host "  1. Copy $OutputPath folder to USB drive"
Write-Host "  2. Rename to 'OberaScanner'"
Write-Host ""
