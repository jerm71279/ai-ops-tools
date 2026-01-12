# File Share and Permissions Migration Guide

This guide will help you recreate the file shares and NTFS permissions from your old Domain Controller to the new VM in Azure.

## Overview

You have 4 PowerShell scripts that must be run **in order** on the new Domain Controller:

1. `1-Setup-Directories.ps1` - Creates the directory structure
2. `2-Set-NTFS-Permissions.ps1` - Configures NTFS permissions using SDDL
3. `3-Create-SMB-Shares.ps1` - Creates the SMB file shares
4. `4-Validate-Configuration.ps1` - Validates the configuration

## Prerequisites

### Before You Begin

1. **Ensure you're in the correct Azure tenant** with the new VM
2. **Verify the new VM is promoted to a Domain Controller** (or will be)
3. **Ensure E:\ drive exists** on the new server
4. **Have administrative access** to the new DC
5. **Verify Active Directory users exist** with the same usernames

### Important Notes About Domain Migration

#### Domain SID Considerations

The original domain had this SID: `S-1-5-21-117609710-1303643608-725345543`

If your new domain has a **different SID**, the user account SIDs in the permissions will not resolve correctly. You have two options:

**Option A: Same Domain (Recommended)**
- If this is the same domain migrated to a new tenant, the SIDs should remain the same
- Users should maintain their original SIDs

**Option B: New Domain**
- If this is a completely new domain, you'll need to:
  1. Recreate all user accounts with the same usernames
  2. The SIDs in the NTFS permissions will initially show as unresolved SIDs
  3. After running the scripts, manually update permissions or use a SID translation script

#### Key User Accounts Referenced

The following users appear in the permissions (ensure they exist in AD):
- Administrator
- PJarvis
- gbrannon
- GBrannonjr
- kcouvillion
- datatrustinc
- oberaconnect
- JMFSolutions
- lsavio
- setcoadmin
- wgibson
- oc-michael.mccool
- kyork
- mhelms
- Tmarsh
- Bdeweese
- bbuege
- cgeiselman
- cbrooks
- kmcdonald
- oc-theresa.gilbert
- ktoolan
- mbrannon
- mhudson-2
- brookebrannon

#### Group Accounts Referenced
- Domain Admins
- Domain Users
- PostClosers

## Step-by-Step Instructions

### Step 1: Transfer Scripts to New Server

1. Copy all 4 PowerShell scripts to the new Domain Controller
2. Place them in a folder like `C:\ShareMigration\`

### Step 2: Open PowerShell as Administrator

```powershell
# Right-click PowerShell and select "Run as Administrator"
```

### Step 3: Set Execution Policy (if needed)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Step 4: Run Scripts in Order

#### Script 1: Create Directory Structure

```powershell
cd C:\ShareMigration
.\1-Setup-Directories.ps1
```

**Expected Output:**
- Creates directories: E:\FTP Data, E:\HomeDirs, E:\PostClosing, etc.
- Green "Created" messages for new directories
- Yellow "Already exists" messages for existing directories

#### Script 2: Configure NTFS Permissions

```powershell
.\2-Set-NTFS-Permissions.ps1
```

**Warning:** This script will **replace existing permissions** on the directories!

**Expected Output:**
- Confirmation prompt (press any key to continue or Ctrl+C to cancel)
- Green "Set permissions for" messages
- Possible warnings about SIDs or user accounts that don't exist

**Common Issues:**
- If you see warnings about user accounts not found, ensure those users exist in AD
- Unresolved SIDs (S-1-5-21-...) mean the user doesn't exist or domain SID changed

#### Script 3: Create SMB Shares

```powershell
.\3-Create-SMB-Shares.ps1
```

**Expected Output:**
- Green "Created share" messages
- Gray "Skipping printer share" messages (these are handled separately)
- List of printer shares that need to be configured via Print Management

**Notes:**
- NETLOGON and SYSVOL shares are created automatically when you promote to DC
- Printer shares must be configured through Print Management console

#### Script 4: Validate Configuration

```powershell
.\4-Validate-Configuration.ps1
```

**Expected Output:**
- Directory existence checks (green [OK] or red [MISSING])
- SMB share validation
- NTFS permissions summary for each directory
- SID migration notes
- Overall summary with next steps

### Step 5: Verify and Test

1. **Check domain SID:**
   ```powershell
   Get-ADDomain | Select-Object DomainSID
   ```

2. **Check specific user SIDs:**
   ```powershell
   Get-ADUser -Identity "username" | Select-Object SID
   ```

3. **Test share access from a client:**
   ```
   \\servername\HomeDirs
   \\servername\PostClosing
   ```

4. **Verify NTFS permissions:**
   ```powershell
   Get-Acl "E:\HomeDirs" | Format-List
   ```

## File Share Summary

### Data Shares (Created by Script 3)
- **E** - E:\ root drive
- **FTP Data** - E:\FTP Data
- **HomeDirs** - E:\HomeDirs
- **Legal** - E:\HomeDirs\Legal
- **PostClosing** - E:\PostClosing
- **Qbooks** - E:\Qbooks
- **SeaCrestScans** - E:\SeaCrestScans
- **SetcoDocs** - E:\SetcoDocs
- **Versacheck** - E:\Versacheck
- **Whole Life Fitness** - E:\Whole Life Fitness
- **worddocs** - E:\NTSYS\worddocs

### System Shares (Auto-created)
- **NETLOGON** - C:\Windows\SYSVOL\sysvol\SouthernEscrow.com\SCRIPTS
- **SYSVOL** - C:\Windows\SYSVOL\sysvol

### Printer Shares (Configure Separately)
36 printer shares need to be configured via Print Management console. See script output for full list.

## Troubleshooting

### Issue: "Access Denied" when setting permissions

**Solution:** Ensure you're running PowerShell as Administrator

### Issue: User accounts show as SIDs (S-1-5-21-...)

**Solution:**
1. Verify the user exists in Active Directory
2. Check if domain SID has changed (new domain vs. migrated domain)
3. May need to manually re-add user permissions

### Issue: Share creation fails

**Solution:**
1. Verify the directory exists
2. Check if share already exists: `Get-SmbShare`
3. Ensure no conflicts with existing share names

### Issue: Cannot set owner or group

**Solution:**
1. Verify the account exists in the domain
2. Some SIDs may reference the old domain - update as needed

## Post-Migration Checklist

- [ ] All directories created successfully
- [ ] All SMB shares created successfully
- [ ] NTFS permissions applied without errors
- [ ] Domain SID verified (matches old domain or users recreated)
- [ ] Test access from client workstations
- [ ] Printer shares configured via Print Management
- [ ] DNS records updated to point to new server
- [ ] Backup jobs configured for new locations
- [ ] Group Policy updated if server name changed
- [ ] User logon scripts tested
- [ ] Home directory mappings verified

## Additional Resources

### To modify share permissions after creation:
```powershell
Grant-SmbShareAccess -Name "ShareName" -AccountName "DOMAIN\User" -AccessRight Full
```

### To view current share permissions:
```powershell
Get-SmbShareAccess -Name "ShareName"
```

### To view NTFS permissions:
```powershell
Get-Acl "E:\FolderName" | Format-List
```

### To manually add NTFS permission:
```powershell
$acl = Get-Acl "E:\FolderName"
$permission = "DOMAIN\User","FullControl","ContainerInherit,ObjectInherit","None","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "E:\FolderName" $acl
```

## Support

If you encounter issues:
1. Review the validation script output
2. Check Event Viewer for errors
3. Verify AD user accounts exist
4. Compare original and new configurations
5. Test individual share access

## Migration Timeline

Estimated time: 30-60 minutes
- Script 1: 1 minute
- Script 2: 5-10 minutes
- Script 3: 2 minutes
- Script 4: 2 minutes
- Testing: 15-30 minutes
- Printer configuration: Variable (not included in scripts)
