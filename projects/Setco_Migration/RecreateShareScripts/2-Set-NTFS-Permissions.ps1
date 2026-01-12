# ============================================================================
# Script: 2-Set-NTFS-Permissions.ps1
# Purpose: Configure NTFS permissions based on original DC settings
# Run as: Administrator on the new Domain Controller
# ============================================================================

# Ensure running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "Configuring NTFS Permissions..." -ForegroundColor Cyan
Write-Host "WARNING: This will replace existing permissions!" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to cancel, or any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Function to set NTFS permissions from SDDL
function Set-NTFSPermissionsFromSDDL {
    param(
        [string]$Path,
        [string]$SDDL,
        [string]$Owner,
        [string]$Group
    )

    try {
        if (-not (Test-Path $Path)) {
            Write-Warning "Path not found: $Path"
            return
        }

        $acl = Get-Acl -Path $Path

        # Set SDDL
        $acl.SetSecurityDescriptorSddlForm($SDDL)

        # Set Owner (convert to NTAccount)
        if ($Owner) {
            try {
                $ownerAccount = New-Object System.Security.Principal.NTAccount($Owner)
                $acl.SetOwner($ownerAccount)
            }
            catch {
                Write-Warning "Could not set owner '$Owner' for $Path : $_"
            }
        }

        # Set Group (convert to NTAccount)
        if ($Group) {
            try {
                $groupAccount = New-Object System.Security.Principal.NTAccount($Group)
                $acl.SetGroup($groupAccount)
            }
            catch {
                Write-Warning "Could not set group '$Group' for $Path : $_"
            }
        }

        # Apply the ACL
        Set-Acl -Path $Path -AclObject $acl
        Write-Host "Set permissions for: $Path" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to set permissions for $Path : $_"
    }
}

# ============================================================================
# E:\ ROOT DRIVE PERMISSIONS
# ============================================================================
Write-Host "`n--- Configuring E:\ ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\" `
    -SDDL "O:BAG:SYD:(A;;0x1200a9;;;WD)(A;OICIIO;GA;;;CO)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;CI;LC;;;BU)(A;CIIO;DC;;;BU)(A;OICI;0x1200a9;;;BU)" `
    -Owner "BUILTIN\Administrators" `
    -Group "NT AUTHORITY\SYSTEM"

# ============================================================================
# FTP DATA
# ============================================================================
Write-Host "`n--- Configuring E:\FTP Data ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\FTP Data" `
    -SDDL "O:BAG:DUD:PAI(A;OICI;FA;;;WD)(A;;FA;;;BA)(A;OICI;FA;;;DA)(A;OICI;FA;;;DU)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# HOMEDIRS
# ============================================================================
Write-Host "`n--- Configuring E:\HomeDirs ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\HomeDirs" `
    -SDDL "O:BAG:DUD:PAI(A;;0x1200a9;;;LA)(A;OICI;FA;;;DA)(A;;0x1200a9;;;DA)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-1128)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-5646)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-5646)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-5654)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-7644)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-8107)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-9138)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-9138)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-21608)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-21608)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-21609)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-21609)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-22616)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-22617)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-22623)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-22624)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-22633)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-24120)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-24126)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-24127)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# HOMEDIRS\LEGAL
# ============================================================================
Write-Host "`n--- Configuring E:\HomeDirs\Legal ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\HomeDirs\Legal" `
    -SDDL "O:LAG:DUD:PAI(A;OICI;FA;;;LA)(A;OICI;FA;;;DA)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1136)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1137)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-5654)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-8131)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-9169)" `
    -Owner "SOUTHERN\Administrator" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# POSTCLOSING
# ============================================================================
Write-Host "`n--- Configuring E:\PostClosing ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\PostClosing" `
    -SDDL "O:BAG:DUD:PAI(A;OICI;FA;;;DA)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1137)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-2113)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-5654)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-9165)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-9202)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-21132)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-21608)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-22632)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-24126)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# QBOOKS
# ============================================================================
Write-Host "`n--- Configuring E:\Qbooks ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\Qbooks" `
    -SDDL "O:BAG:DUD:PAI(A;OICI;FA;;;DA)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1128)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1137)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-5654)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-21608)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# SEACRESTSCANS
# ============================================================================
Write-Host "`n--- Configuring E:\SeaCrestScans ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\SeaCrestScans" `
    -SDDL "O:BAG:DUD:AI(A;OICI;FA;;;WD)(A;;FA;;;BA)(A;OICIID;FA;;;BA)(A;OICIID;FA;;;SY)(A;OICIIOID;GA;;;CO)(A;OICIID;0x1200a9;;;BU)(A;CIID;LC;;;BU)(A;CIID;DC;;;BU)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# SETCODOCS
# ============================================================================
Write-Host "`n--- Configuring E:\SetcoDocs ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\SetcoDocs" `
    -SDDL "O:BAG:DUD:PAI(A;OICI;FA;;;WD)(A;;FA;;;BA)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-1136)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-1137)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-9138)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-9296)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-21132)(A;;0x1200a9;;;S-1-5-21-117609710-1303643608-725345543-21608)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# VERSACHECK
# ============================================================================
Write-Host "`n--- Configuring E:\Versacheck ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\Versacheck" `
    -SDDL "O:BAG:DUD:PAI(A;OICIIO;FA;;;CO)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1128)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

# ============================================================================
# WHOLE LIFE FITNESS
# ============================================================================
Write-Host "`n--- Configuring E:\Whole Life Fitness ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\Whole Life Fitness" `
    -SDDL "O:BAG:S-1-5-21-3450599359-2096226002-3553231297-513D:PAI(A;OICI;FA;;;SY)(A;OICI;FA;;;DA)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1128)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1136)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-1137)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-3641)(A;OICI;FA;;;S-1-5-21-117609710-1303643608-725345543-5654)" `
    -Owner "BUILTIN\Administrators" `
    -Group "S-1-5-21-3450599359-2096226002-3553231297-513"

# ============================================================================
# WORDDOCS
# ============================================================================
Write-Host "`n--- Configuring E:\NTSYS\worddocs ---" -ForegroundColor Cyan
Set-NTFSPermissionsFromSDDL -Path "E:\NTSYS\worddocs" `
    -SDDL "O:BAG:DUD:AI(A;;FA;;;BA)(A;OICIID;FA;;;SY)(A;OICIID;FA;;;LA)(A;OICIID;FA;;;BA)(A;OICIID;FA;;;WD)" `
    -Owner "BUILTIN\Administrators" `
    -Group "SOUTHERN\Domain Users"

Write-Host "`n============================================================================" -ForegroundColor Green
Write-Host "NTFS Permissions configuration complete!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "`nNOTE: Some SIDs may need to be updated if user accounts have different SIDs" -ForegroundColor Yellow
Write-Host "in the new domain. Review the permissions after running this script." -ForegroundColor Yellow
Write-Host "`nNext step: Run 3-Create-SMB-Shares.ps1" -ForegroundColor Cyan
