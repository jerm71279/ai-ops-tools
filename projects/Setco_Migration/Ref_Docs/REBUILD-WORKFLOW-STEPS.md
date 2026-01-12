# SETCO-DC02 Rebuild Workflow - Complete Steps

**Created:** 2025-11-17
**Timeline:** Next weekend (5 days from now)

---

## Overview

This weekend you're rebuilding SETCO-DC02 VM with:
- **OS Disk:** Created from vendor VHD (via SAS URL)
- **Data Disk:** Created from snapshot after robocopy delta sync to FS

---

## Timeline & Prerequisites

### Before Next Weekend:
- ✅ Initial robocopy completed 2 days ago (~380GB transferred to FS F:\Backup)
- ✅ Vendor restarted DC in their portal
- ⏳ Waiting for vendor to provide new OS VHD SAS URL
- ⏳ 5 days until rebuild weekend

### Next Weekend Tasks:
1. Run delta robocopy sync (capture ~5 days of changes, <100GB)
2. Create snapshot from FS F: drive
3. Get OS VHD SAS URL from vendor
4. Run rebuild script
5. Configure and validate new DC

---

## Step-by-Step Workflow

### PHASE 1: Delta Robocopy Sync (Friday Evening)

**Estimated time:** 30 min - 2 hours (for <100GB delta)

#### 1.1 Connect to Source DC via NinjaOne

1. Open NinjaOne console
2. Find source DC
3. Remote control → Open CMD as Administrator

#### 1.2 Map FS Drive

```cmd
# Map Y: to your FS (replace with actual FS hostname/IP)
net use Y: \\FS-SERVERNAME\F$ /user:DESTINATION\Administrator

# Or use IP
net use Y: \\10.x.x.x\F$ /user:DESTINATION\Administrator

# Verify
dir Y:\Backup
```

#### 1.3 Run Delta Robocopy

```cmd
# This will only copy changes since 2 days ago
robocopy E:\ Y:\Backup /MIR /COPYALL /DCOPY:T /MT:32 /R:3 /W:5 /B /LOG:C:\Logs\robocopy-delta.log /TEE /NP
```

**What happens:**
- Robocopy compares timestamps
- Only transfers new/modified files since last sync
- Much faster than initial 380GB sync

#### 1.4 Verify Completion

**On source DC:**
```cmd
# Check log for summary
notepad C:\Logs\robocopy-delta.log
# Look for "Total Copied" at bottom
```

**On FS:**
```powershell
# Verify data updated
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum
```

---

### PHASE 2: Create Data Snapshot from FS (After Robocopy)

**Estimated time:** 20-40 minutes

#### 2.1 Identify FS Data Disk

```bash
# List all disks in DataCenter resource group
az disk list -g DataCenter --query "[].{Name:name, Size:diskSizeGb, Owner:managedBy}" -o table
```

**Find the disk attached to FS VM that is 1TB (F: drive)**

Example output:
```
Name                    Size    Owner
----------------------  ------  -------------------------
FS_DataDisk_F          1024    /subscriptions/.../FS-VM
```

#### 2.2 Create Snapshot

```bash
# Create snapshot with today's date
az snapshot create \
  -g DataCenter \
  -n SETCO-DC02-Data-Snapshot-$(date +%Y-%m-%d) \
  --source <FS-DISK-NAME> \
  --sku Premium_LRS

# Example:
az snapshot create \
  -g DataCenter \
  -n SETCO-DC02-Data-Snapshot-2025-11-23 \
  --source FS_DataDisk_F \
  --sku Premium_LRS
```

**Save the snapshot name - you'll need it for the rebuild script!**

#### 2.3 Verify Snapshot

```bash
az snapshot show -g DataCenter -n SETCO-DC02-Data-Snapshot-2025-11-23 \
  --query "{Name:name, Size:diskSizeGb, State:provisioningState}" -o table
```

Expected: `State: Succeeded`

---

### PHASE 3: Get OS VHD from Vendor

**Estimated time:** Vendor task (coordinate timing)

#### 3.1 Request from Vendor

**Send to vendor:**
> "Please export the SETCO-DC02 OS disk as VHD and provide SAS URL.
>
> We need:
> - VHD of OS disk (C: drive)
> - SAS URL with read permissions
> - Valid for at least 7 days
>
> Please send the full blob URL with SAS token."

#### 3.2 Expected Format

Vendor should provide something like:
```
https://vendorstorage.blob.core.windows.net/vhds/setco-dc02-os.vhd?sp=r&st=2025-11-23T00:00:00Z&se=2025-11-30T00:00:00Z&sv=...
```

#### 3.3 Test SAS URL (Optional)

```bash
# Verify you can access the VHD
curl -I "<VHD-URL-WITH-SAS>"
# Should return HTTP 200 OK
```

---

### PHASE 4: Run Rebuild Script

**Estimated time:** 30-60 minutes (disk creation from VHD/snapshot)

#### 4.1 Configure Script Variables

Edit the script:
```bash
nano /home/mavrick/Projects/Setco_Migration/Ref_Docs/rebuild-setco-dc02-final.sh
```

**Set these variables:**
```bash
# OS VHD from vendor
OS_VHD_URL="https://vendorstorage.blob.core.windows.net/vhds/setco-dc02-os.vhd?sp=r&st=..."

# Snapshot you created in Phase 2
DATA_SNAPSHOT_NAME="SETCO-DC02-Data-Snapshot-2025-11-23"

# Optional: Set static IP if needed
STATIC_PRIVATE_IP=""  # Leave empty for dynamic
```

#### 4.2 Run Script

```bash
cd /home/mavrick/Projects/Setco_Migration/Ref_Docs
./rebuild-setco-dc02-final.sh
```

**Script will:**
1. ✓ Verify prerequisites (VHD URL and snapshot exist)
2. ✓ Create OS managed disk from vendor VHD (10-20 min)
3. ✓ Create data managed disk from your snapshot (10-30 min)
4. ✓ Create NIC with IP
5. ✓ Build VM from OS disk
6. ✓ Attach data disk at LUN 1
7. ✓ Set static IP
8. ✓ Display summary

#### 4.3 Monitor Progress

The script will show progress for each step. If it fails, it will tell you exactly what went wrong.

---

### PHASE 5: Start and Validate VM

**Estimated time:** 30-60 minutes

#### 5.1 Start VM

```bash
az vm start -g DataCenter -n SETCO-DC02
```

#### 5.2 Monitor Boot

```bash
# Check VM status
az vm get-instance-view -g DataCenter -n SETCO-DC02 \
  --query "instanceView.statuses[?starts_with(code, 'PowerState')].displayStatus" -o tsv

# If boot issues, check diagnostics
az vm boot-diagnostics get-boot-log -g DataCenter -n SETCO-DC02
```

#### 5.3 Get IP and Connect via RDP

```bash
# Get private IP
az vm show -g DataCenter -n SETCO-DC02 -d --query privateIps -o tsv
```

**RDP to the IP:**
- Username: `SOUTHERN\Administrator`
- Password: [Domain admin password]

#### 5.4 Verify Disks (In Windows)

**PowerShell on DC:**
```powershell
# Check disks
Get-Disk
Get-Volume

# Should see:
# - C: drive (OS, ~512GB)
# - F: drive (Data, ~1TB)

# If F: not assigned, bring online and assign letter
Set-Disk -Number 1 -IsOffline $false
Get-Partition -DiskNumber 1 | Set-Partition -NewDriveLetter F

# Verify data
Get-ChildItem F:\ -Directory
# Should see: FTP Data, HomeDirs, PostClosing, Qbooks, etc.
```

#### 5.5 Verify AD Services

```powershell
# Check services
Get-Service NTDS, DNS, Netlogon, W32Time | Format-Table Name, Status

# All should be "Running"

# Verify domain
Get-ADDomain
# Should show: SouthernEscrow.com

# Check FSMO roles
netdom query fsmo

# Verify DNS
Get-DnsServerZone

# Test DNS resolution
nslookup SouthernEscrow.com
```

---

### PHASE 6: Configure File Shares

**Estimated time:** 15-30 minutes

#### 6.1 Copy Scripts to DC

Transfer your PowerShell scripts to `C:\ps1` on the DC:
- `2-Set-NTFS-Permissions-F-Drive.ps1`
- `3-Create-SMB-Shares-F-Drive.ps1`
- `4-Validate-Configuration-F-Drive.ps1`

#### 6.2 Run Scripts

```powershell
cd C:\ps1

# Apply NTFS permissions
.\2-Set-NTFS-Permissions-F-Drive.ps1

# Create SMB shares
.\3-Create-SMB-Shares-F-Drive.ps1

# Validate
.\4-Validate-Configuration-F-Drive.ps1
```

#### 6.3 Verify Shares

```powershell
# List shares
Get-SmbShare | Format-Table Name, Path

# Expected shares:
# F, FTP Data, HomeDirs, Legal, PostClosing, Qbooks,
# SeaCrestScans, SetcoDocs, Versacheck, Whole Life Fitness, worddocs

# Test share access
net view \\SETCO-DC02
```

---

### PHASE 7: Final Validation

#### 7.1 Run DC Diagnostics

```cmd
dcdiag /v > C:\Logs\dcdiag.txt
notepad C:\Logs\dcdiag.txt
```

**Look for:**
- ✓ All tests passing (or acceptable warnings)
- ✗ Critical errors that need attention

#### 7.2 Test from Client

**From a domain-joined workstation:**

```cmd
# Test DNS
nslookup SouthernEscrow.com

# Test DC connectivity
nltest /dsgetdc:SouthernEscrow.com

# Test share access
net view \\SETCO-DC02

# Map drive
net use Z: \\SETCO-DC02\HomeDirs

# Test file access
dir Z:
```

#### 7.3 Monitor Event Viewer

**On DC:**
- Check Directory Services log for errors
- Check System log for disk/service issues
- Check Security log for authentication issues

---

## Success Criteria Checklist

- [ ] Delta robocopy completed successfully (<100GB transferred)
- [ ] Snapshot created from FS F: drive
- [ ] OS VHD SAS URL received from vendor
- [ ] Rebuild script completed without errors
- [ ] VM started and booted to Windows
- [ ] C: drive accessible (OS disk)
- [ ] F: drive accessible with all data
- [ ] AD services running (NTDS, DNS, Netlogon)
- [ ] Domain is SouthernEscrow.com
- [ ] FSMO roles correct
- [ ] DNS resolving correctly
- [ ] All 11 file shares created
- [ ] File share permissions applied
- [ ] dcdiag passes (or acceptable warnings)
- [ ] Client can resolve DC via DNS
- [ ] Client can access file shares
- [ ] Users can authenticate

---

## Troubleshooting

### Robocopy Issues

**Can't map Y: drive:**
```cmd
# Test connectivity
ping FS-SERVERNAME
ping 10.x.x.x

# Test SMB
Test-NetConnection -ComputerName FS-SERVERNAME -Port 445

# Use IP instead
net use Y: \\10.x.x.x\F$ /user:DESTINATION\Administrator
```

**Access denied:**
- Ensure running CMD as Administrator on source DC
- Verify FS F$ share has admin permissions
- Check credentials are correct

### Snapshot Creation Issues

**Disk in use:**
- Snapshot creation works even if disk is attached/in-use
- Just ensure robocopy is complete first

**Snapshot fails:**
```bash
# Check disk state
az disk show -g DataCenter -n FS_DataDisk_F --query "{State:provisioningState, Owner:managedBy}"
```

### VM Won't Start

**Check boot diagnostics:**
```bash
az vm boot-diagnostics get-boot-log -g DataCenter -n SETCO-DC02
```

**Common issues:**
- OS disk VHD was corrupted
- Wrong OS type specified
- Zone mismatch

### Data Disk Not Showing as F:

```powershell
# Bring disk online
Set-Disk -Number 1 -IsOffline $false

# Assign F: letter
Get-Partition -DiskNumber 1 | Set-Partition -NewDriveLetter F
```

### AD Services Not Running

```powershell
# Start services manually
Start-Service NTDS
Start-Service DNS
Start-Service Netlogon

# Check for errors
Get-EventLog -LogName "Directory Service" -Newest 50 | Where-Object {$_.EntryType -eq "Error"}
```

---

## Timeline Summary

| Task | Duration | When |
|------|----------|------|
| Delta robocopy sync | 30 min - 2 hours | Friday evening |
| Create snapshot | 20-40 min | After robocopy |
| Get VHD from vendor | Vendor task | Coordinate |
| Run rebuild script | 30-60 min | Saturday |
| Start and validate VM | 30-60 min | Saturday |
| Configure shares | 15-30 min | Saturday |
| Final validation | 1-2 hours | Saturday |
| **Total** | **4-7 hours** | Weekend |

---

## Script Locations

All scripts located in: `/home/mavrick/Projects/Setco_Migration/Ref_Docs/`

**Main rebuild script:**
- `rebuild-setco-dc02-final.sh` ← USE THIS ONE

**File share scripts (run on DC after rebuild):**
- `2-Set-NTFS-Permissions-F-Drive.ps1`
- `3-Create-SMB-Shares-F-Drive.ps1`
- `4-Validate-Configuration-F-Drive.ps1`

**Documentation:**
- `DC-Migration-YOUR-Workflow.md` (streamlined guide)
- `DC-Migration-Destination-Focused.md` (comprehensive guide)
- `REBUILD-WORKFLOW-STEPS.md` (this file)

---

**Ready to go next weekend!**
