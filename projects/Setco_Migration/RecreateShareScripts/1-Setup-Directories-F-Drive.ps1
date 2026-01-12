# ============================================================================
# Script: 1-Setup-Directories.ps1
# Purpose: Create directory structure for file shares
# Run as: Administrator on the new Domain Controller
# Modified for F:\ drive
# ============================================================================

# Ensure running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "Creating directory structure on F:\ drive..." -ForegroundColor Cyan

# Define directories to create
$directories = @(
    "F:\FTP Data",
    "F:\HomeDirs",
    "F:\HomeDirs\Legal",
    "F:\PostClosing",
    "F:\Qbooks",
    "F:\SeaCrestScans",
    "F:\SetcoDocs",
    "F:\Versacheck",
    "F:\Whole Life Fitness",
    "F:\NTSYS\worddocs"
)

# Create each directory if it doesn't exist
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        try {
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
            Write-Host "Created: $dir" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to create $dir : $_"
        }
    }
    else {
        Write-Host "Already exists: $dir" -ForegroundColor Yellow
    }
}

Write-Host "`nDirectory creation complete!" -ForegroundColor Green
Write-Host "Next step: Run 2-Set-NTFS-Permissions.ps1" -ForegroundColor Cyan
