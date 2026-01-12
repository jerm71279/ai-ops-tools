# DC Migration - YOUR Workflow (Destination Tenant Owner)
## Step-by-Step Process - What YOU Do

---

## 🎯 Your Situation

**YOU Control:**
- ✅ Destination Azure Tenant
- ✅ File Server (FS) in destination tenant
- ✅ Remote access to Source DC via NinjaOne
- ✅ Ability to run robocopy from DC
- ✅ Final control over new DC build

**Vendor Controls:**
- 🔒 Source Azure Tenant (where current DC resides)
- 🔒 Azure Portal access to export VHD

**YOU Will Do:**
- ✅ Connect to DC via NinjaOne
- ✅ Map FS drive to DC
- ✅ Run robocopy from DC to FS
- ✅ All destination tenant activities

---

## 📋 Your 5-Phase Process

```
Phase 1: YOU Run Robocopy (DC → Your FS via NinjaOne)
         ↓
Phase 2: YOU Copy OS VHD from Vendor Storage to Yours
         ↓
Phase 3: YOU Create Data Disk from FS Snapshot (Post-Robocopy)
         ↓
Phase 4: YOU Build New DC from Both Disks
         ↓
Phase 5: Configure File Shares & Validate
```

**Note:** Infrastructure (VNet, Subnet, NIC) already exists - no setup needed!

---

## PHASE 1: Run Robocopy from DC to Your FS

### YOU Will Do This via NinjaOne:

#### 1.1 Connect to Source DC

**Via NinjaOne:**
1. Open NinjaOne console
2. Find source DC in device list
3. Click "Remote Control" or "Take Control"
4. Open CMD or PowerShell as Administrator

#### 1.2 Prepare Your FS

**On your FS in destination tenant (via RDP or console):**
```powershell
# Create staging folder
New-Item -Path "F:\Backup" -ItemType Directory -Force

# Verify FS is accessible from DC
# Note your FS IP or hostname
```

**FS Access Details:**
- Hostname: `FS-SERVERNAME` (or IP: `10.x.x.x`)
- Share: `F$` (admin share)
- Path: `\\FS-SERVERNAME\F$\Backup`

#### 1.3 Map FS Drive on DC

**On Source DC (via NinjaOne), run CMD as Administrator:**

```cmd
# Map Y: drive to your FS
net use Y: \\FS-SERVERNAME\F$ /user:DESTINATION\Administrator
# Enter password when prompted

# Or use IP if DNS doesn't resolve:
net use Y: \\10.x.x.x\F$ /user:DESTINATION\Administrator

# Verify mapping
dir Y:\Backup
```

#### 1.4 Run Robocopy

**Still on Source DC via NinjaOne:**

```cmd
# Create logs folder
mkdir C:\Logs

# Run robocopy - copy E:\ to your FS
robocopy E:\ Y:\Backup /MIR /COPYALL /DCOPY:T /MT:32 /R:3 /W:5 /B /LOG:C:\Logs\robocopy.log /TEE /NP
```

**Command Breakdown:**
- `E:\` - Source (DC's data drive)
- `Y:\Backup` - Destination (mapped to your FS)
- `/MIR` - Mirror (exact copy)
- `/COPYALL` - Copy all attributes, permissions, timestamps
- `/DCOPY:T` - Copy directory timestamps
- `/MT:32` - Use 32 threads (fast!)
- `/R:3` - Retry 3 times on errors
- `/W:5` - Wait 5 seconds between retries
- `/B` - Backup mode (bypasses permissions)
- `/LOG:` - Save log to C:\Logs\robocopy.log
- `/TEE` - Show on screen AND save to log
- `/NP` - No percentage (cleaner output)

#### 1.5 Monitor Progress

**On DC (via NinjaOne) - open second CMD window:**

```cmd
# Watch log in real-time
powershell -command "Get-Content C:\Logs\robocopy.log -Tail 50 -Wait"
```

**Or check from your FS:**
```powershell
# Monitor data arriving
while ($true) {
    $size = (Get-ChildItem F:\Backup -Recurse -ErrorAction SilentlyContinue |
             Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Size: $([math]::Round($size,2)) GB"
    Start-Sleep -Seconds 300  # Check every 5 minutes
}
```

### Checklist:
- [ ] Connected to DC via NinjaOne
- [ ] F:\Backup created on FS
- [ ] Y: drive mapped successfully on DC
- [ ] Robocopy command started
- [ ] Can see progress in log
- [ ] Monitor until complete
- [ ] **Robocopy complete: ___ files, ___ GB**

**⏱️ Estimated Time:** 6-12 hours for ~380GB

**💡 Pro Tip:** Leave NinjaOne session open or check back periodically. Robocopy will continue even if you disconnect.

---

## PHASE 2: Copy OS VHD from Vendor Storage

### Vendor's Role (They Do This):

The vendor will:
1. Stop/deallocate source DC in their Azure portal
2. Create snapshot of OS disk
3. Export snapshot to VHD blob in their storage
4. Generate SAS URL with read permissions
5. Provide you the SAS URL

**You will then copy the VHD from their storage to yours.**

### Your Actions:

#### 2.1 Get VHD SAS URL from Vendor

**Request from vendor:**
```
Hi [Vendor],

Please export the SETCO-DC02 OS disk as VHD and provide a SAS URL.

We need:
- VHD of OS disk (C: drive)
- SAS URL with read permissions (sp=r)
- Valid for at least 7 days

Please send the full blob URL with SAS token.

Thanks!
```

**Vendor will provide something like:**
```
https://vendorstorage.blob.core.windows.net/exports/setco-dc02-os.vhd?sp=r&st=2025-11-23T00:00:00Z&se=2025-11-30T00:00:00Z&spr=https&sv=2022-11-02&sr=b&sig=...
```

#### 2.2 Copy VHD from Vendor Storage to Your Storage

**You need your own storage account and container first (if not exists):**

```bash
# Check if you have storage account (skip if exists)
az storage account list -g DataCenter --query "[].name" -o table

# If you need to create one:
az storage account create \
  --name setcodcvhdstorage \
  --resource-group DataCenter \
  --location eastus \
  --sku Standard_LRS

# Create container for VHD
az storage container create \
  --account-name setcodcvhdstorage \
  --name vhd-import \
  --auth-mode login
```

**Copy VHD using AzCopy:**

```bash
# Set variables
VENDOR_VHD_URL="<VHD_URL>"  # SAS URL from vendor
YOUR_STORAGE_ACCOUNT="setcodcvhdstorage"
YOUR_CONTAINER="vhd-import"
VHD_BLOB_NAME="setco-dc02-os.vhd"

# Get your storage account key (for destination)
STORAGE_KEY=$(az storage account keys list \
  -g DataCenter \
  -n "$YOUR_STORAGE_ACCOUNT" \
  --query "[0].value" -o tsv)

# Build destination URL
DEST_URL="https://${YOUR_STORAGE_ACCOUNT}.blob.core.windows.net/${YOUR_CONTAINER}/${VHD_BLOB_NAME}"

# Copy VHD from vendor to your storage
azcopy copy \
  "$VENDOR_VHD_URL" \
  "${DEST_URL}?${STORAGE_KEY}" \
  --blob-type PageBlob

# Or use SAS token for destination (if you prefer)
# Generate your storage SAS first, then:
# azcopy copy "$VENDOR_VHD_URL" "${DEST_URL}?YOUR_SAS" --blob-type PageBlob
```

**Monitor copy progress:**
- AzCopy will show progress in terminal
- Copying ~127GB OS VHD takes 30 min - 2 hours depending on network

#### 2.3 Verify VHD Copied Successfully

```bash
# List blobs to confirm VHD arrived
az storage blob list \
  --account-name setcodcvhdstorage \
  --container-name vhd-import \
  --output table \
  --auth-mode login
```

**Expected output:**
```
Name                 Blob Type    Length
-------------------  -----------  --------
setco-dc02-os.vhd    PageBlob     ~127 GB
```

#### 2.4 Create OS Managed Disk from VHD

```bash
# Get VHD URL from your storage
VHD_URL=$(az storage blob url \
  --account-name setcodcvhdstorage \
  --container-name vhd-import \
  --name setco-dc02-os.vhd \
  --auth-mode login \
  --output tsv)

# Set the OS disk name
OS_DISK_NAME="<DiskName>"  # Choose a name for the new OS disk

# Create OS managed disk from VHD
az disk create \
  --resource-group DataCenter \
  --name "$OS_DISK_NAME" \
  --location eastus \
  --sku Premium_LRS \
  --source "$VHD_URL" \
  --os-type Windows \
  --zone 3

# Monitor creation status
az disk show \
  --resource-group DataCenter \
  --name "$OS_DISK_NAME" \
  --query "{Name:name, Size:diskSizeGb, State:provisioningState}" -o table
```

**Wait for:** `State: Succeeded` (takes 10-20 minutes)

### Checklist:
- [ ] Vendor provides OS VHD SAS URL
- [ ] Storage account exists in your subscription
- [ ] Container created for VHD import
- [ ] AzCopy installed (download from https://aka.ms/downloadazcopy-v10)
- [ ] VHD copied from vendor storage to your storage
- [ ] VHD verified in your storage container
- [ ] OS managed disk created from VHD
- [ ] Disk status shows "Succeeded"
- [ ] Note the disk name for Phase 4

**⏱️ Estimated Time:** 1-3 hours (VHD copy 30min-2hrs + disk creation 10-20min)

---

## PHASE 3: Create Data Disk from FS Snapshot

### ⚠️ ONLY START AFTER Robocopy Complete!

**Check robocopy completion via NinjaOne on DC:**
```cmd
# View last 30 lines of log
powershell -command "Get-Content C:\Logs\robocopy.log -Tail 30"
```

**Look for:**
```
             Total    Copied   Skipped  Mismatch    FAILED    Extras
  Files :   343197    343197         0         0         0         0
```

**FAILED should be 0 (or only system files)**

### Verify Data on FS

```powershell
# On FS - verify all data arrived
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum

# Check folders
Get-ChildItem F:\Backup -Directory | Select-Object Name

# Expected folders:
# FTP Data, HomeDirs, PostClosing, Qbooks, SeaCrestScans,
# SetcoDocs, Versacheck, Whole Life Fitness, NTSYS
```

### Create Snapshot from FS Data Disk (Azure CLI)

**This is the NEW workflow - create snapshot directly from FS disk!**

#### Step 1: Identify FS Data Disk

```bash
# List all disks in DataCenter resource group
az disk list -g DataCenter \
  --query "[].{Name:name, Size:diskSizeGb, Owner:managedBy}" -o table
```

**Find the 1TB disk attached to FS (F: drive)**

Example output:
```
Name                    Size    Owner
----------------------  ------  -------------------------
FS_DataDisk_F          1024    /subscriptions/.../FS-VM
```

**Set the disk name:**
```bash
FS_DATA_DISK_NAME="FS_DataDisk_F"  # Replace with actual name
```

#### Step 2: Create Snapshot from FS Disk

```bash
# Create snapshot with today's date
SNAPSHOT_NAME="SETCO-DC02-Data-Snapshot-$(date +%Y-%m-%d)"

az snapshot create \
  -g DataCenter \
  -n "$SNAPSHOT_NAME" \
  --source "$FS_DATA_DISK_NAME" \
  --sku Premium_LRS

echo "Snapshot created: $SNAPSHOT_NAME"
```

**This takes 20-40 minutes depending on disk size.**

#### Step 3: Verify Snapshot

```bash
# Check snapshot status
az snapshot show -g DataCenter -n "$SNAPSHOT_NAME" \
  --query "{Name:name, Size:diskSizeGb, State:provisioningState}" -o table
```

**Expected:** `State: Succeeded`

#### Step 4: Create Managed Disk from Snapshot

```bash
# Disk name for new DC
DATA_DISK_NAME="SETCO-DC02_DataDisk_NEW"

# Create managed disk from snapshot
az disk create \
  -g DataCenter \
  -n "$DATA_DISK_NAME" \
  -l eastus \
  --source "$SNAPSHOT_NAME" \
  --sku Premium_LRS \
  --zone 3

echo "Creating data disk from snapshot..."
```

**This takes 10-30 minutes.**

#### Step 5: Monitor Disk Creation

```bash
# Check disk status
az disk show -g DataCenter -n "$DATA_DISK_NAME" \
  --query "{Name:name, Size:diskSizeGb, State:provisioningState, SKU:sku.name}" -o table
```

**Wait for:** `State: Succeeded`

### ALL COMMANDS TOGETHER (Copy/Paste Ready):

```bash
# ===========================
# Create Data Disk from FS Snapshot
# ===========================

# Step 1: Identify FS data disk
az disk list -g DataCenter \
  --query "[].{Name:name, Size:diskSizeGb, Owner:managedBy}" -o table

# Step 2: Set the FS disk name (REPLACE WITH ACTUAL NAME!)
FS_DATA_DISK_NAME="<DiskName>"  # <-- UPDATE THIS after identifying!

# Step 3: Create snapshot
SNAPSHOT_NAME="<SnapshotName>"  # Example: SETCO-DC02-Data-Snapshot-2025-11-23
az snapshot create \
  -g DataCenter \
  -n "$SNAPSHOT_NAME" \
  --source "$FS_DATA_DISK_NAME" \
  --sku Premium_LRS

# Step 4: Verify snapshot
az snapshot show -g DataCenter -n "$SNAPSHOT_NAME" \
  --query "{Name:name, Size:diskSizeGb, State:provisioningState}" -o table

# Step 5: Create managed disk from snapshot
DATA_DISK_NAME="<DiskName>"  # Choose a name for the new data disk
az disk create \
  -g DataCenter \
  -n "$DATA_DISK_NAME" \
  -l eastus \
  --source "$SNAPSHOT_NAME" \
  --sku Premium_LRS \
  --zone 3

# Step 6: Monitor disk creation
az disk show -g DataCenter -n "$DATA_DISK_NAME" \
  --query "{Name:name, Size:diskSizeGb, State:provisioningState, SKU:sku.name}" -o table

echo ""
echo "Data disk ready: $DATA_DISK_NAME"
```

### Checklist:
- [ ] ✅ Robocopy complete (verified on DC)
- [ ] Data verified on F:\Backup on FS
- [ ] FS data disk identified (e.g., FS_DataDisk_F)
- [ ] Snapshot created from FS disk
- [ ] Snapshot status: "Succeeded"
- [ ] Managed disk created from snapshot
- [ ] Disk status: "Succeeded"
- [ ] **Both OS and Data disks ready for VM build**

**⏱️ Estimated Time:** 1-2 hours (snapshot creation + disk creation)

---

## PHASE 4: Build New DC VM (Manual Azure CLI)

### All Prerequisites Met:
- ✅ OS Disk ready (from vendor VHD)
- ✅ Data Disk ready (from FS snapshot)
- ✅ Network infrastructure ready (VNet/Subnet exist)

### YOUR ACTUAL VARIABLES:

```bash
# Set these variables
RESOURCE_GROUP="DataCenter"
LOCATION="eastus"
VM_NAME="SETCO-DC02"
VM_SIZE="Standard_D4s_v5"
ZONE="3"

# Disk names (you'll set these after creating disks in Phase 3 & 4)
OS_DISK_NAME="<DiskName>"      # OS disk created from vendor VHD
DATA_DISK_NAME="<DiskName>"    # Data disk created from FS snapshot

# Network (existing)
TARGET_VNET="DataCenter_vNet"
TARGET_SUBNET="DataCenter_Subnet"
NIC_NAME="SETCO-DC02-nic2"

# Subnet range (for reference)
SUBNET_RANGE="10.20.1.x/24"
PREV_IP="10.20.1.12"  # IP from previous build
```

### Step 1: Get Disk IDs

```bash
# Resolve disk IDs
OS_DISK_ID=$(az disk show -g "$RESOURCE_GROUP" -n "$OS_DISK_NAME" --query id -o tsv)
DATA_DISK_ID=$(az disk show -g "$RESOURCE_GROUP" -n "$DATA_DISK_NAME" --query id -o tsv)

echo "OS_DISK_ID=$OS_DISK_ID"
echo "DATA_DISK_ID=$DATA_DISK_ID"
```

### Step 2: Create Network Interface

```bash
# Check if NIC already exists
if ! az network nic show -g "$RESOURCE_GROUP" -n "$NIC_NAME" &>/dev/null; then
  echo "Creating NIC..."

  # Create NIC (with or without static IP)
  if [ -n "$STATIC_PRIVATE_IP" ]; then
    az network nic create -g "$RESOURCE_GROUP" -n "$NIC_NAME" \
      --vnet-name "$TARGET_VNET" \
      --subnet "$TARGET_SUBNET" \
      --private-ip-address "$STATIC_PRIVATE_IP"
  else
    az network nic create -g "$RESOURCE_GROUP" -n "$NIC_NAME" \
      --vnet-name "$TARGET_VNET" \
      --subnet "$TARGET_SUBNET"
  fi
fi

# View current IP on NIC
az network nic show -g "$RESOURCE_GROUP" -n "$NIC_NAME" \
  --query "ipConfigurations[0].privateIpAddress" -o tsv
```

### Step 3: Create VM from OS Disk

```bash
# Create VM
az vm create -g "$RESOURCE_GROUP" -n "$VM_NAME" \
  --attach-os-disk "$OS_DISK_ID" \
  --os-type Windows \
  --nics "$NIC_NAME" \
  --zone "$ZONE" \
  --size "$VM_SIZE"
```

**This will take 2-4 minutes.**

### Step 4: Attach Data Disk

```bash
# Attach data disk at LUN 1
az vm disk attach -g "$RESOURCE_GROUP" \
  --vm-name "$VM_NAME" \
  --name "$DATA_DISK_ID" \
  --lun 1
```

### Step 5: Verify VM Configuration

```bash
# VM details
echo "VM Configuration:"
az vm show -g "$RESOURCE_GROUP" -n "$VM_NAME" \
  --query "{Name:name, Size:hardwareProfile.vmSize, Zone:zones[0]}" -o table

# Network
echo ""
echo "Private IP:"
az network nic show -g "$RESOURCE_GROUP" -n "$NIC_NAME" \
  --query "ipConfigurations[0].privateIpAddress" -o tsv

# Disks
echo ""
echo "Attached Disks:"
az vm show -g "$RESOURCE_GROUP" -n "$VM_NAME" \
  --query "storageProfile.dataDisks[].{LUN:lun,Name:name}" -o table
```

### Step 6: Start VM

```bash
# Start the VM
az vm start -g "$RESOURCE_GROUP" -n "$VM_NAME"

# Check status
az vm get-instance-view -g "$RESOURCE_GROUP" -n "$VM_NAME" \
  --query "instanceView.statuses[?starts_with(code, 'PowerState')].displayStatus" -o tsv
```

### ALL COMMANDS TOGETHER (Copy/Paste Ready):

```bash
# ===========================
# SETCO-DC02 Rebuild - Manual Commands
# ===========================

# Variables
RESOURCE_GROUP="DataCenter"
LOCATION="eastus"
VM_NAME="SETCO-DC02"
VM_SIZE="Standard_D4s_v5"
ZONE="3"
OS_DISK_NAME="<DiskName>"           # Set after creating OS disk
DATA_DISK_NAME="<DiskName>"         # Set after creating data disk
TARGET_VNET="DataCenter_vNet"
TARGET_SUBNET="DataCenter_Subnet"
NIC_NAME="SETCO-DC02-nic2"

# Get disk IDs
OS_DISK_ID=$(az disk show -g "$RESOURCE_GROUP" -n "$OS_DISK_NAME" --query id -o tsv)
DATA_DISK_ID=$(az disk show -g "$RESOURCE_GROUP" -n "$DATA_DISK_NAME" --query id -o tsv)

echo "OS Disk: $OS_DISK_ID"
echo "Data Disk: $DATA_DISK_ID"

# Create NIC if doesn't exist
if ! az network nic show -g "$RESOURCE_GROUP" -n "$NIC_NAME" &>/dev/null; then
  az network nic create -g "$RESOURCE_GROUP" -n "$NIC_NAME" \
    --vnet-name "$TARGET_VNET" \
    --subnet "$TARGET_SUBNET"
fi

# Create VM from OS disk
az vm create -g "$RESOURCE_GROUP" -n "$VM_NAME" \
  --attach-os-disk "$OS_DISK_ID" \
  --os-type Windows \
  --nics "$NIC_NAME" \
  --zone "$ZONE" \
  --size "$VM_SIZE"

# Attach data disk
az vm disk attach -g "$RESOURCE_GROUP" \
  --vm-name "$VM_NAME" \
  --name "$DATA_DISK_ID" \
  --lun 1

# Start VM
az vm start -g "$RESOURCE_GROUP" -n "$VM_NAME"

# Verify
az vm show -g "$RESOURCE_GROUP" -n "$VM_NAME" -d \
  --query "{Name:name, PowerState:powerState, PrivateIP:privateIps}" -o table
```

### Checklist:
- [ ] Variables set correctly
- [ ] Disk IDs resolved
- [ ] NIC created (reuses existing SETCO-DC02-nic2)
- [ ] VM created from OS disk
- [ ] Data disk attached at LUN 1
- [ ] VM started successfully
- [ ] Can see private IP: _________________

**⏱️ Estimated Time:** 10-15 minutes

---

## PHASE 5: Initial Configuration

### Connect to New DC

**RDP to the VM:**
```
mstsc /v:<PUBLIC_IP>
```

**Login with:**
- Username: `SOUTHERN\Administrator`
- Password: [Original DC admin password]

### Verify Data Disk Online

```powershell
# Check disk status
Get-Disk
Get-Volume

# Bring data disk online if needed
Set-Disk -Number 1 -IsOffline $false

# Verify F: drive accessible
Get-ChildItem F:\ -Directory
```

**Expected folders on F:\:**
- FTP Data, HomeDirs, PostClosing, Qbooks, SeaCrestScans, SetcoDocs, Versacheck, Whole Life Fitness, NTSYS

### Recreate File Shares

**Copy scripts to C:\ps1 on new DC:**
- 1-Setup-Directories-F-Drive.ps1
- 2-Set-NTFS-Permissions-F-Drive.ps1
- 3-Create-SMB-Shares-F-Drive.ps1
- 4-Validate-Configuration-F-Drive.ps1

```powershell
cd C:\ps1

# Run scripts in order
.\1-Setup-Directories-F-Drive.ps1  # Shows "Already exists"
.\2-Set-NTFS-Permissions-F-Drive.ps1  # Apply permissions
.\3-Create-SMB-Shares-F-Drive.ps1  # Create shares
.\4-Validate-Configuration-F-Drive.ps1  # Validate

# Verify shares
Get-SmbShare | Format-Table Name, Path
```

### Run Health Check

```cmd
# DC diagnostic
dcdiag /v > C:\Logs\dcdiag.txt
notepad C:\Logs\dcdiag.txt
```

### Checklist:
- [ ] RDP connection successful
- [ ] F:\ drive online and accessible
- [ ] All folders visible on F:\
- [ ] All 11 shares created
- [ ] dcdiag passes

**⏱️ Estimated Time:** 1-2 hours

---

## Quick Command Reference

### Via NinjaOne on Source DC

**Check robocopy progress:**
```cmd
powershell -command "Get-Content C:\Logs\robocopy.log -Tail 50 -Wait"
```

**Check robocopy completion:**
```cmd
powershell -command "Get-Content C:\Logs\robocopy.log -Tail 30"
```

### On Your FS

**Monitor data arrival:**
```powershell
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum
```

### Azure Commands

**List resources:**
```bash
az resource list --resource-group RG-Setco-DC --output table
```

**Check disk status:**
```bash
az disk show --resource-group RG-Setco-DC --name DC-Setco-OS-Disk --query provisioningState
```

**VM status:**
```bash
az vm get-instance-view --resource-group RG-Setco-DC --name DC-Setco-NewTenant
```

---

## Timeline Summary

| Phase | Duration | Your Action |
|-------|----------|-------------|
| 1. Robocopy (via NinjaOne) | 6-12 hrs | YOU run delta sync |
| 2. Copy OS VHD | 1-3 hrs | Copy from vendor storage + create disk |
| 3. Create data disk | 1-2 hrs | Snapshot + create disk |
| 4. Build VM | 10-15 min | Create VM from both disks |
| 5. Configure | 1-2 hrs | File shares/validation |
| **Total Elapsed** | **9-19 hrs** | **Over 1-2 days** |

---

## Vendor Coordination

### What You Need from Vendor:

| Item | When |
|------|------|
| Confirmation they'll export OS VHD | Before starting |
| OS VHD uploaded to your storage | Phase 3 |
| Original domain admin password | Before VM start |
| Decommission old DC | After 2+ weeks |

### What You Tell Vendor:

| Item | When |
|------|------|
| "I'm running robocopy now via NinjaOne" | Phase 1 start |
| SAS token for VHD upload | Phase 2 |
| "Robocopy complete, please export OS VHD" | Phase 3 |
| "New DC is live, ready to decommission old" | Post-cutover |

---

## Success Criteria

- [ ] Connected to DC via NinjaOne
- [ ] Robocopy complete (verified)
- [ ] All data on F:\Backup on FS
- [ ] OS VHD imported
- [ ] Data disk created
- [ ] VM boots successfully
- [ ] Can RDP to VM
- [ ] F:\ drive online with all folders
- [ ] AD services running
- [ ] DNS working
- [ ] 11 shares created
- [ ] dcdiag passes
- [ ] Client can access shares
- [ ] Users can authenticate

---

**Your Workflow Version 3.0**
**Created:** 2025-11-17
**Access Method:** NinjaOne Remote Control
**You Control:** Everything except vendor's Azure tenant
