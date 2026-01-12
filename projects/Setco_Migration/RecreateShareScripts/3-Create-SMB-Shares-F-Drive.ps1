# ============================================================================
# Script: 3-Create-SMB-Shares.ps1
# Purpose: Create SMB file shares based on original DC configuration
# Run as: Administrator on the new Domain Controller
# Modified for F:\ drive
# ============================================================================

# Ensure running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "Creating SMB Shares on F:\ drive..." -ForegroundColor Cyan

# Function to create SMB share with error handling
function New-FileShare {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Description = "",
        [string]$FullAccess = "Everyone"
    )

    try {
        # Check if path exists (skip printer shares)
        if ($Path -notlike "*LocalsplOnly*" -and -not (Test-Path $Path)) {
            Write-Warning "Path does not exist: $Path - Skipping share: $Name"
            return
        }

        # Check if share already exists
        $existingShare = Get-SmbShare -Name $Name -ErrorAction SilentlyContinue
        if ($existingShare) {
            Write-Host "Share already exists: $Name" -ForegroundColor Yellow
            return
        }

        # Skip printer shares (LocalsplOnly)
        if ($Path -like "*LocalsplOnly*") {
            Write-Host "Skipping printer share: $Name" -ForegroundColor Gray
            return
        }

        # Create the share
        New-SmbShare -Name $Name -Path $Path -FullAccess $FullAccess -Description $Description -ErrorAction Stop | Out-Null
        Write-Host "Created share: $Name -> $Path" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to create share '$Name': $_"
    }
}

# ============================================================================
# CREATE DATA SHARES
# ============================================================================

Write-Host "`n--- Creating Data Shares ---" -ForegroundColor Cyan

# F Drive Root
New-FileShare -Name "F" -Path "F:\" -Description "F Drive Root" -FullAccess "Everyone"

# FTP Data
New-FileShare -Name "FTP Data" -Path "F:\FTP Data" -Description "FTP Data Directory" -FullAccess "Everyone"

# HomeDirs
New-FileShare -Name "HomeDirs" -Path "F:\HomeDirs" -Description "User Home Directories" -FullAccess "Domain Admins"

# Legal
New-FileShare -Name "Legal" -Path "F:\HomeDirs\Legal" -Description "Legal Department Files" -FullAccess "Domain Admins"

# PostClosing
New-FileShare -Name "PostClosing" -Path "F:\PostClosing" -Description "Post Closing Documents" -FullAccess "Domain Admins"

# Qbooks
New-FileShare -Name "Qbooks" -Path "F:\Qbooks" -Description "QuickBooks Files" -FullAccess "Domain Admins"

# SeaCrestScans
New-FileShare -Name "SeaCrestScans" -Path "F:\SeaCrestScans" -Description "SeaCrest Scans" -FullAccess "Everyone"

# SetcoDocs
New-FileShare -Name "SetcoDocs" -Path "F:\SetcoDocs" -Description "Setco Documents" -FullAccess "Everyone"

# Versacheck
New-FileShare -Name "Versacheck" -Path "F:\Versacheck" -Description "Versacheck Data" -FullAccess "Domain Admins"

# Whole Life Fitness
New-FileShare -Name "Whole Life Fitness" -Path "F:\Whole Life Fitness" -Description "Whole Life Fitness Files" -FullAccess "Domain Admins"

# worddocs
New-FileShare -Name "worddocs" -Path "F:\NTSYS\worddocs" -Description "Word Documents" -FullAccess "Everyone"

# ============================================================================
# PRINTER SHARES (INFORMATIONAL ONLY - These are printer shares, not file shares)
# ============================================================================

Write-Host "`n--- Printer Shares (Not Created by this script) ---" -ForegroundColor Cyan
Write-Host "The following are printer shares and should be configured via Print Management:" -ForegroundColor Yellow

$printerShares = @(
    "Crestview-Sharp-Upstairs",
    "HP LaserJet Pro M402-M403 n-dne PCB Checks",
    "HP Photosmart D7400 PanamaCity",
    "HPLaserjet1300-Panama City",
    "HPLaserjet2200-Accounting",
    "Lexmark FWB Checks",
    "Lexmark XM1100 Series XL DraperJ-30A",
    "Lexmark-M3150-Crestview",
    "Lexmark-M3150-Defuniak",
    "Lexmark-M3150-Destin-Check",
    "Lexmark-M3150-FWB",
    "Lexmark-M3150-Pace-Check",
    "Lexmark-M3150-PanamaCity-check",
    "Lexmark-M3150-PanamaCity-Plain",
    "Lexmark-M3150-Pensacola-Check",
    "Navarre-Back-Lexmark-M3150",
    "Navarre-Back-MX-M6071",
    "Pensacola Lexmark",
    "RICOH-SP5300-PCB",
    "SHARP MX-B350W PCL6 HudsonLaw",
    "SHARP MX-M316N-Pensacola",
    "SHARP MX-M4070 PCL6 DraperJ-30A",
    "SHARP MX-M4070 PCL6 PanamaCity 23rd St",
    "SHARP MX-M4071 PCL6 -30A Suite 204",
    "SHARP MX-M4071-Crestview",
    "SHARP MX-M4071-FWB",
    "SHARP MX-M4071-Panama-City2",
    "SHARP MX-M4071-PostClosing",
    "SHARP MX-M465N-Destin-Main",
    "SHARP MX-M465N-PanamaCityBeach",
    "SHARP MX-M5070-Pace",
    "SHARP UD3 PCL6",
    "SHARP UD3 PCL6 (Copy 1)",
    "SHARP UD3 PCL6 Port St Joe",
    "SHARP-Destin-Admin",
    "SHARP-MX-M4070-Defuniak"
)

foreach ($printer in $printerShares) {
    Write-Host "  - $printer" -ForegroundColor Gray
}

Write-Host "`n============================================================================" -ForegroundColor Green
Write-Host "SMB Share creation complete!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "`nNOTES:" -ForegroundColor Yellow
Write-Host "1. NETLOGON and SYSVOL shares are created automatically by DCPROMO" -ForegroundColor Yellow
Write-Host "2. Printer shares must be configured through Print Management console" -ForegroundColor Yellow
Write-Host "3. Share permissions are set to default - NTFS permissions control access" -ForegroundColor Yellow
Write-Host "`nNext step: Run 4-Validate-Configuration.ps1 to verify setup" -ForegroundColor Cyan
