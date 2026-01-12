# ============================================================================
# Script: BONUS-SID-Translation-Helper.ps1
# Purpose: Help identify and translate SIDs if domain has changed
# Run as: Administrator on the new Domain Controller
# ============================================================================

# Ensure running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "SID TRANSLATION HELPER" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

# ============================================================================
# GET CURRENT DOMAIN SID
# ============================================================================

Write-Host "`n--- Current Domain Information ---" -ForegroundColor Cyan

try {
    $domain = Get-ADDomain
    $currentDomainSID = $domain.DomainSID.Value
    Write-Host "Domain Name: $($domain.DNSRoot)" -ForegroundColor White
    Write-Host "NetBIOS Name: $($domain.NetBIOSName)" -ForegroundColor White
    Write-Host "Current Domain SID: $currentDomainSID" -ForegroundColor Green
}
catch {
    Write-Error "Could not retrieve domain information. Is this a Domain Controller?"
    exit 1
}

# Original domain SID
$originalDomainSID = "S-1-5-21-117609710-1303643608-725345543"
Write-Host "Original Domain SID: $originalDomainSID" -ForegroundColor Yellow

if ($currentDomainSID -eq $originalDomainSID) {
    Write-Host "`nSUCCESS: Domain SIDs match! No SID translation needed." -ForegroundColor Green
    Write-Host "Your user accounts should have maintained their original SIDs." -ForegroundColor Green
}
else {
    Write-Host "`nWARNING: Domain SIDs do NOT match!" -ForegroundColor Red
    Write-Host "You will need to update user permissions or recreate them." -ForegroundColor Yellow
}

# ============================================================================
# FIND USERS BY USERNAME
# ============================================================================

Write-Host "`n--- Looking up User Accounts ---" -ForegroundColor Cyan

# List of users found in original permissions
$usernames = @(
    "Administrator",
    "PJarvis",
    "gbrannon",
    "GBrannonjr",
    "kcouvillion",
    "datatrustinc",
    "oberaconnect",
    "JMFSolutions",
    "lsavio",
    "setcoadmin",
    "wgibson",
    "oc-michael.mccool",
    "kyork",
    "mhelms",
    "Tmarsh",
    "Bdeweese",
    "bbuege",
    "cgeiselman",
    "cbrooks",
    "kmcdonald",
    "oc-theresa.gilbert",
    "ktoolan",
    "mbrannon",
    "mhudson-2",
    "brookebrannon"
)

$foundUsers = @()
$missingUsers = @()

foreach ($username in $usernames) {
    try {
        $user = Get-ADUser -Identity $username -ErrorAction Stop
        $foundUsers += [PSCustomObject]@{
            Username = $username
            SID = $user.SID.Value
            Enabled = $user.Enabled
            DistinguishedName = $user.DistinguishedName
        }
        Write-Host "[FOUND] $username - $($user.SID)" -ForegroundColor Green
    }
    catch {
        $missingUsers += $username
        Write-Host "[MISSING] $username" -ForegroundColor Red
    }
}

# ============================================================================
# SUMMARY REPORT
# ============================================================================

Write-Host "`n--- Summary ---" -ForegroundColor Cyan
Write-Host "Users Found: $($foundUsers.Count)" -ForegroundColor Green
Write-Host "Users Missing: $($missingUsers.Count)" -ForegroundColor $(if($missingUsers.Count -eq 0){"Green"}else{"Red"})

if ($missingUsers.Count -gt 0) {
    Write-Host "`nMissing Users:" -ForegroundColor Red
    foreach ($missing in $missingUsers) {
        Write-Host "  - $missing" -ForegroundColor Yellow
    }
    Write-Host "`nYou need to create these user accounts in Active Directory." -ForegroundColor Yellow
}

# ============================================================================
# CHECK FOR UNRESOLVED SIDS IN PERMISSIONS
# ============================================================================

Write-Host "`n--- Checking for Unresolved SIDs in Permissions ---" -ForegroundColor Cyan

$pathsToCheck = @(
    "E:\",
    "E:\FTP Data",
    "E:\HomeDirs",
    "E:\HomeDirs\Legal",
    "E:\PostClosing",
    "E:\Qbooks",
    "E:\SeaCrestScans",
    "E:\SetcoDocs",
    "E:\Versacheck",
    "E:\Whole Life Fitness",
    "E:\NTSYS\worddocs"
)

$unresolvedSIDs = @()

foreach ($path in $pathsToCheck) {
    if (Test-Path $path) {
        try {
            $acl = Get-Acl -Path $path
            foreach ($access in $acl.Access) {
                $identity = $access.IdentityReference.Value
                # Check if it's a SID (starts with S-1-5-21-)
                if ($identity -match '^S-1-5-21-') {
                    $unresolvedSIDs += [PSCustomObject]@{
                        Path = $path
                        SID = $identity
                        Rights = $access.FileSystemRights
                        Type = $access.AccessControlType
                    }
                    Write-Host "[UNRESOLVED] $path - $identity" -ForegroundColor Yellow
                }
            }
        }
        catch {
            Write-Warning "Could not read permissions for: $path"
        }
    }
}

if ($unresolvedSIDs.Count -eq 0) {
    Write-Host "`nNo unresolved SIDs found! All permissions reference valid accounts." -ForegroundColor Green
}
else {
    Write-Host "`nFound $($unresolvedSIDs.Count) unresolved SID entries" -ForegroundColor Yellow
    Write-Host "These SIDs reference accounts from the old domain." -ForegroundColor Yellow
}

# ============================================================================
# ORIGINAL SID TO USERNAME MAPPING
# ============================================================================

Write-Host "`n--- Original SID to Username Mapping (Reference) ---" -ForegroundColor Cyan
Write-Host "These are the RIDs from the original domain:" -ForegroundColor White

$originalMapping = @{
    "1128" = "PJarvis"
    "1136" = "gbrannon"
    "1137" = "GBrannonjr"
    "2113" = "PostClosers (group)"
    "3641" = "brookebrannon"
    "5646" = "JMFSolutions"
    "5654" = "kcouvillion"
    "7644" = "bbuege"
    "8107" = "Unknown User"
    "8131" = "mbrannon"
    "9138" = "lsavio"
    "9165" = "cgeiselman"
    "9169" = "mhudson-2"
    "9202" = "cbrooks"
    "9296" = "ktoolan"
    "21132" = "kmcdonald"
    "21608" = "datatrustinc"
    "21609" = "setcoadmin"
    "22616" = "Tmarsh"
    "22617" = "Bdeweese"
    "22623" = "Unknown User"
    "22624" = "wgibson"
    "22632" = "oc-theresa.gilbert"
    "22633" = "oc-michael.mccool"
    "24120" = "kyork"
    "24126" = "oberaconnect"
    "24127" = "mhelms"
}

foreach ($rid in $originalMapping.Keys | Sort-Object) {
    $originalSID = "$originalDomainSID-$rid"
    $username = $originalMapping[$rid]
    Write-Host "  $originalSID = $username" -ForegroundColor Gray
}

# ============================================================================
# EXPORT USER SID MAPPING
# ============================================================================

Write-Host "`n--- Exporting User SID Mapping ---" -ForegroundColor Cyan

if ($foundUsers.Count -gt 0) {
    $exportPath = "C:\ShareMigration\UserSIDMapping.csv"
    $foundUsers | Export-Csv -Path $exportPath -NoTypeInformation
    Write-Host "Exported user SID mapping to: $exportPath" -ForegroundColor Green
}

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

if ($currentDomainSID -eq $originalDomainSID) {
    Write-Host "Your domain SID matches the original. The permissions should work correctly." -ForegroundColor Green
}
else {
    Write-Host "DOMAIN SID HAS CHANGED - Action Required:" -ForegroundColor Yellow
    Write-Host "1. Create any missing user accounts listed above" -ForegroundColor White
    Write-Host "2. Re-run script 2-Set-NTFS-Permissions.ps1 to update permissions" -ForegroundColor White
    Write-Host "3. Manually verify critical share permissions" -ForegroundColor White
    Write-Host "4. Consider using icacls or other tools for bulk permission updates" -ForegroundColor White
}

if ($missingUsers.Count -gt 0) {
    Write-Host "`nCREATE MISSING USER ACCOUNTS:" -ForegroundColor Yellow
    Write-Host "Run this command for each missing user:" -ForegroundColor White
    Write-Host '  New-ADUser -Name "Username" -SamAccountName "Username" -UserPrincipalName "Username@domain.com" -Enabled $true' -ForegroundColor Gray
}

if ($unresolvedSIDs.Count -gt 0) {
    Write-Host "`nUNRESOLVED SIDS DETECTED:" -ForegroundColor Yellow
    Write-Host "After creating missing user accounts, you may need to:" -ForegroundColor White
    Write-Host "1. Manually update permissions using the SID mapping above" -ForegroundColor White
    Write-Host "2. Re-run script 2-Set-NTFS-Permissions.ps1" -ForegroundColor White
}

Write-Host "`n"
