# ============================================================================
# Script: 4-Validate-Configuration.ps1
# Purpose: Validate file shares and NTFS permissions configuration
# Run as: Administrator on the new Domain Controller
# Modified for F:\ drive
# ============================================================================

# Ensure running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "VALIDATING FILE SHARES AND PERMISSIONS CONFIGURATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

# ============================================================================
# VALIDATE DIRECTORIES
# ============================================================================

Write-Host "`n--- Validating Directories ---" -ForegroundColor Cyan

$directories = @(
    "F:\",
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

$dirMissing = 0
foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "[OK] $dir" -ForegroundColor Green
    }
    else {
        Write-Host "[MISSING] $dir" -ForegroundColor Red
        $dirMissing++
    }
}

if ($dirMissing -eq 0) {
    Write-Host "`nAll directories exist!" -ForegroundColor Green
}
else {
    Write-Host "`nWARNING: $dirMissing directories are missing!" -ForegroundColor Red
}

# ============================================================================
# VALIDATE SMB SHARES
# ============================================================================

Write-Host "`n--- Validating SMB Shares ---" -ForegroundColor Cyan

$expectedShares = @(
    @{Name="F"; Path="F:\"},
    @{Name="FTP Data"; Path="F:\FTP Data"},
    @{Name="HomeDirs"; Path="F:\HomeDirs"},
    @{Name="Legal"; Path="F:\HomeDirs\Legal"},
    @{Name="PostClosing"; Path="F:\PostClosing"},
    @{Name="Qbooks"; Path="F:\Qbooks"},
    @{Name="SeaCrestScans"; Path="F:\SeaCrestScans"},
    @{Name="SetcoDocs"; Path="F:\SetcoDocs"},
    @{Name="Versacheck"; Path="F:\Versacheck"},
    @{Name="Whole Life Fitness"; Path="F:\Whole Life Fitness"},
    @{Name="worddocs"; Path="F:\NTSYS\worddocs"}
)

$shareMissing = 0
foreach ($share in $expectedShares) {
    $smbShare = Get-SmbShare -Name $share.Name -ErrorAction SilentlyContinue
    if ($smbShare) {
        Write-Host "[OK] Share: $($share.Name) -> $($smbShare.Path)" -ForegroundColor Green
    }
    else {
        Write-Host "[MISSING] Share: $($share.Name)" -ForegroundColor Red
        $shareMissing++
    }
}

# Check SYSVOL and NETLOGON (should exist on DC)
$sysvolShare = Get-SmbShare -Name "SYSVOL" -ErrorAction SilentlyContinue
$netlogonShare = Get-SmbShare -Name "NETLOGON" -ErrorAction SilentlyContinue

if ($sysvolShare) {
    Write-Host "[OK] Share: SYSVOL -> $($sysvolShare.Path)" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Share: SYSVOL not found (normal if not promoted to DC yet)" -ForegroundColor Yellow
}

if ($netlogonShare) {
    Write-Host "[OK] Share: NETLOGON -> $($netlogonShare.Path)" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Share: NETLOGON not found (normal if not promoted to DC yet)" -ForegroundColor Yellow
}

if ($shareMissing -eq 0) {
    Write-Host "`nAll expected data shares exist!" -ForegroundColor Green
}
else {
    Write-Host "`nWARNING: $shareMissing shares are missing!" -ForegroundColor Red
}

# ============================================================================
# DISPLAY NTFS PERMISSIONS SUMMARY
# ============================================================================

Write-Host "`n--- NTFS Permissions Summary ---" -ForegroundColor Cyan

function Show-PermissionSummary {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        Write-Host "$Path - [DOES NOT EXIST]" -ForegroundColor Red
        return
    }

    try {
        $acl = Get-Acl -Path $Path
        $accessCount = ($acl.Access | Measure-Object).Count
        Write-Host "`n$Path" -ForegroundColor Yellow
        Write-Host "  Owner: $($acl.Owner)" -ForegroundColor White
        Write-Host "  Group: $($acl.Group)" -ForegroundColor White
        Write-Host "  Access Rules: $accessCount entries" -ForegroundColor White

        # Show first few access rules
        $acl.Access | Select-Object -First 5 | ForEach-Object {
            Write-Host "    - $($_.IdentityReference): $($_.FileSystemRights) ($($_.AccessControlType))" -ForegroundColor Gray
        }

        if ($accessCount -gt 5) {
            Write-Host "    ... and $($accessCount - 5) more" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  ERROR reading permissions: $_" -ForegroundColor Red
    }
}

foreach ($dir in $directories) {
    Show-PermissionSummary -Path $dir
}

# ============================================================================
# SID VALIDATION WARNING
# ============================================================================

Write-Host "`n--- SID Migration Notes ---" -ForegroundColor Cyan
Write-Host "The following SIDs are referenced in the original permissions:" -ForegroundColor Yellow
Write-Host "You may need to update these if the domain SID has changed:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Domain SID from original: S-1-5-21-117609710-1303643608-725345543" -ForegroundColor White
Write-Host ""
Write-Host "Common user RIDs found:" -ForegroundColor White
Write-Host "  - 1128 (PJarvis)" -ForegroundColor Gray
Write-Host "  - 1136 (gbrannon)" -ForegroundColor Gray
Write-Host "  - 1137 (GBrannonjr)" -ForegroundColor Gray
Write-Host "  - 5654 (kcouvillion)" -ForegroundColor Gray
Write-Host "  - 21608 (datatrustinc)" -ForegroundColor Gray
Write-Host "  - 24126 (oberaconnect)" -ForegroundColor Gray
Write-Host "  ... and others" -ForegroundColor Gray
Write-Host ""
Write-Host "To get current domain SID, run: Get-ADDomain | Select-Object DomainSID" -ForegroundColor Cyan
Write-Host "To get user SIDs, run: Get-ADUser -Identity username | Select-Object SID" -ForegroundColor Cyan

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "VALIDATION COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

Write-Host "`nSUMMARY:" -ForegroundColor Green
Write-Host "  Directories Missing: $dirMissing" -ForegroundColor $(if($dirMissing -eq 0){"Green"}else{"Red"})
Write-Host "  Shares Missing: $shareMissing" -ForegroundColor $(if($shareMissing -eq 0){"Green"}else{"Red"})

Write-Host "`nNEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Verify domain SID matches original (or update SIDs in permissions)" -ForegroundColor White
Write-Host "2. Test access from client computers" -ForegroundColor White
Write-Host "3. Configure printer shares via Print Management console" -ForegroundColor White
Write-Host "4. Update DNS records if needed" -ForegroundColor White
Write-Host "5. Configure backup jobs for new share locations" -ForegroundColor White

Write-Host "`n"
