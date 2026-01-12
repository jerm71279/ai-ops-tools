# DC Migration to Destination Tenant
## Destination Tenant Owner's Guide

---

## Your Role & Environment

**YOU Control:**
- ✅ Destination Azure Tenant
- ✅ File Server (FS) in destination tenant
- ✅ Destination storage accounts and resources
- ✅ Final DC build and configuration
- ✅ **Remote access to Source DC via NinjaOne**

**Vendor Controls:**
- 🔒 Source Azure Tenant (Portal access only)
- 🔒 OS VHD export from Azure Portal

**YOU Have Direct Access To:**
- ✅ Source Domain Controller via NinjaOne remote control
- ✅ Can run commands and scripts on source DC
- ✅ Can execute robocopy from source DC to your FS

---

## Migration Flow Overview

```
┌─────────────────────────────────────────────────────────────┐
│ SOURCE TENANT (Vendor Controls Azure Portal Only)          │
│                                                              │
│  ┌──────────┐                                               │
│  │ Source DC│ ← YOU access via NinjaOne                     │
│  │  (E:\)   │                                               │
│  └────┬─────┘                                               │
│       │                                                     │
│       │ 1. YOU Run Robocopy via NinjaOne                    │
│       │                                                     │
│       ↓                                                     │
└───────┼─────────────────────────────────────────────────────┘
        │
        │ Network/VPN
        │
        ↓
┌───────┼─────────────────────────────────────────────────────┐
│       ↓  DESTINATION TENANT (YOU Control)                   │
│  ┌─────────┐                                                │
│  │   FS    │ ← Robocopy destination (F:\Backup)             │
│  │  (F:\)  │                                                │
│  └────┬────┘                                                │
│       │                                                     │
│       │ 2. After sync complete                              │
│       │ YOU Create Data Disk VHD                            │
│       ↓                                                     │
│  ┌──────────────┐                                           │
│  │ Data Disk    │                                           │
│  │ (from FS)    │                                           │
│  └──────────────┘                                           │
│                                                              │
│  ┌──────────────┐                                           │
│  │  OS Disk     │ ← 3. Vendor exports OS VHD               │
│  │ (from source)│    (via Azure Portal)                    │
│  └──────────────┘                                           │
│                                                              │
│       │                                                     │
│       │ 4. YOU Build New DC VM                              │
│       ↓                                                     │
│  ┌──────────────┐                                           │
│  │  NEW DC      │                                           │
│  │  (C:\ + F:\) │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Your Action Plan

### Phase 1: YOU Run Data Sync via NinjaOne
### Phase 2: Prepare Destination Infrastructure
### Phase 3: Receive and Import OS VHD
### Phase 4: Create Data Disk from FS
### Phase 5: Build New DC VM
### Phase 6: Configure and Validate

---

## PHASE 1: YOU Run Data Sync via NinjaOne

### Your Actions:

#### 1.1 Prepare Staging Folder on FS

**Create staging folder on FS:**
```powershell
# On your FS in destination tenant
New-Item -Path "F:\Backup" -ItemType Directory
```

#### 1.2 Connect to Source DC via NinjaOne

**Via NinjaOne Console:**
1. Open NinjaOne console
2. Find source DC in device list
3. Click "Remote Control" or "Take Control"
4. Open CMD or PowerShell as Administrator on remote DC

#### 1.3 Map FS Drive on Source DC

**On Source DC (via NinjaOne), run CMD as Administrator:**

```cmd
# Map Y: drive to your FS
# Replace FS-SERVERNAME with your actual FS hostname/IP
net use Y: \\FS-SERVERNAME\F$ /user:DESTINATION\Administrator

# Or use IP address if DNS not configured:
net use Y: \\10.x.x.x\F$ /user:DESTINATION\Administrator

# Verify mapping
dir Y:
```

**Expected result:** You should see the F:\Backup folder

#### 1.4 Run Robocopy from Source DC

**Still on Source DC via NinjaOne, run this command:**

```cmd
robocopy E:\ Y:\Backup /MIR /COPYALL /DCOPY:T /MT:32 /R:3 /W:5 /B /LOG:C:\Logs\robocopy.log /TEE /NP
```

**Command breakdown:**
- `E:\` - Source DC data drive
- `Y:\Backup` - Mapped drive to your FS
- `/MIR` - Mirror (copies all, deletes from destination if not in source)
- `/COPYALL` - Copies all file info (permissions, attributes, timestamps, owner, ACLs)
- `/DCOPY:T` - Copies directory timestamps
- `/MT:32` - Multi-threaded (32 threads)
- `/R:3` - Retry 3 times on failed copies
- `/W:5` - Wait 5 seconds between retries
- `/B` - Backup mode (bypasses file security)
- `/LOG:C:\Logs\robocopy.log` - Writes log file
- `/TEE` - Outputs to console AND log file
- `/NP` - No progress (cleaner output)

**Estimated time:** 6-12 hours for ~380GB (depending on network speed)

#### 1.5 Monitor Progress

**While robocopy runs, you can check progress:**

**On Source DC (via NinjaOne):**
```cmd
# View log file
type C:\Logs\robocopy.log | more

# Or open log in notepad
notepad C:\Logs\robocopy.log
```

**On your FS in destination tenant:**
```powershell
# Monitor data arriving
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum

# Check folder count
(Get-ChildItem F:\Backup -Recurse -Directory).Count

# Check file count
(Get-ChildItem F:\Backup -Recurse -File).Count
```

**Checklist:**
- [ ] Created F:\Backup staging folder on FS
- [ ] Connected to source DC via NinjaOne
- [ ] Mapped Y: drive from DC to FS F$
- [ ] Started robocopy command
- [ ] Monitor data arrival on FS
- [ ] **Wait for robocopy to complete (will show summary when done)**

---

## PHASE 2: Prepare Destination Infrastructure

### While Waiting for Data Sync

#### 2.1 Create Resource Group

```bash
az group create \
  --name RG-Setco-DC \
  --location eastus
```

#### 2.2 Create Virtual Network

```bash
# Create VNet
az network vnet create \
  --resource-group RG-Setco-DC \
  --name VNet-Setco-DC \
  --address-prefix 10.0.0.0/16 \
  --subnet-name DC-Subnet \
  --subnet-prefix 10.0.1.0/24

# Create NSG
az network nsg create \
  --resource-group RG-Setco-DC \
  --name NSG-DC

# Add NSG rules for DC
az network nsg rule create \
  --resource-group RG-Setco-DC \
  --nsg-name NSG-DC \
  --name AllowRDP \
  --priority 100 \
  --source-address-prefixes '*' \
  --destination-port-ranges 3389 \
  --protocol Tcp \
  --access Allow

az network nsg rule create \
  --resource-group RG-Setco-DC \
  --nsg-name NSG-DC \
  --name AllowDNS \
  --priority 110 \
  --source-address-prefixes VirtualNetwork \
  --destination-port-ranges 53 \
  --protocol '*' \
  --access Allow

az network nsg rule create \
  --resource-group RG-Setco-DC \
  --nsg-name NSG-DC \
  --name AllowKerberos \
  --priority 120 \
  --source-address-prefixes VirtualNetwork \
  --destination-port-ranges 88 \
  --protocol '*' \
  --access Allow

az network nsg rule create \
  --resource-group RG-Setco-DC \
  --nsg-name NSG-DC \
  --name AllowLDAP \
  --priority 130 \
  --source-address-prefixes VirtualNetwork \
  --destination-port-ranges 389 636 3268 3269 \
  --protocol Tcp \
  --access Allow

az network nsg rule create \
  --resource-group RG-Setco-DC \
  --nsg-name NSG-DC \
  --name AllowSMB \
  --priority 140 \
  --source-address-prefixes VirtualNetwork \
  --destination-port-ranges 445 \
  --protocol Tcp \
  --access Allow
```

#### 2.3 Create Storage Account for VHD Import

```bash
# Create storage account
az storage account create \
  --name setcodcmigration \
  --resource-group RG-Setco-DC \
  --location eastus \
  --sku Standard_LRS

# Create container for VHD import
az storage container create \
  --account-name setcodcmigration \
  --name vhd-import \
  --auth-mode login

# Generate SAS token for vendor to upload OS VHD
az storage container generate-sas \
  --account-name setcodcmigration \
  --name vhd-import \
  --permissions racwdl \
  --expiry $(date -u -d "7 days" '+%Y-%m-%dT%H:%MZ') \
  --auth-mode login \
  --as-user \
  --output tsv
```

**Save this SAS token to provide to vendor!**

**Checklist:**
- [ ] Resource group created
- [ ] VNet and subnet created
- [ ] NSG created with DC rules
- [ ] Storage account created
- [ ] Container `vhd-import` created
- [ ] SAS token generated for vendor
- [ ] SAS token provided to vendor

---

## PHASE 3: Receive and Import OS VHD

### Vendor Will Do via Azure Portal

**Vendor will:**
1. Log in to source Azure tenant portal
2. Navigate to source DC VM
3. Create snapshot of OS disk
4. Export snapshot to VHD blob
5. Use AzCopy to transfer VHD to your storage account

**Example command vendor runs:**
```bash
azcopy copy \
  "https://source-storage.blob.core.windows.net/snapshots/dc-os.vhd?source-sas" \
  "https://setcodcmigration.blob.core.windows.net/vhd-import/dc-os.vhd?YOUR-SAS-TOKEN"
```

**You provide vendor:** SAS token from Phase 2

### Your Actions:

#### 3.1 Verify OS VHD Upload

```bash
# List blobs to confirm OS VHD arrived
az storage blob list \
  --account-name setcodcmigration \
  --container-name vhd-import \
  --output table \
  --auth-mode login
```

**Expected output:**
```
Name        Blob Type    Length
----------  -----------  --------
dc-os.vhd   PageBlob     XXX GB
```

#### 3.2 Create Managed Disk from OS VHD

```bash
# Get VHD URL
VHD_URL=$(az storage blob url \
  --account-name setcodcmigration \
  --container-name vhd-import \
  --name dc-os.vhd \
  --auth-mode login \
  --output tsv)

# Create OS managed disk from VHD
az disk create \
  --resource-group RG-Setco-DC \
  --name DC-Setco-OS-Disk \
  --location eastus \
  --sku Premium_LRS \
  --source "$VHD_URL" \
  --os-type Windows
```

**Wait 10-20 minutes for disk creation.**

**Checklist:**
- [ ] Vendor confirms OS VHD upload complete
- [ ] Verified VHD blob exists in container
- [ ] OS managed disk created successfully
- [ ] Disk shows as "Succeeded" in portal

---

## PHASE 4: Create Data Disk from File Server

### CRITICAL: Only After YOU Confirm Robocopy Complete!

**Verify robocopy finished successfully on source DC (via NinjaOne)**

#### 4.1 Verify Data on File Server

```powershell
# On File Server - verify data
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum

# Expected folders
Get-ChildItem F:\Backup -Directory | Select-Object Name

# Should see:
# FTP Data
# HomeDirs
# PostClosing
# Qbooks
# SeaCrestScans
# SetcoDocs
# Versacheck
# Whole Life Fitness
# NTSYS
```

#### 4.2 Option A: Create VHD from File Server Data (Preferred)

**On File Server, run PowerShell as Administrator:**

```powershell
# Calculate required size
$dataSize = (Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum).Sum
$vhdSizeGB = [Math]::Ceiling($dataSize / 1GB) + 100  # Add 100GB buffer
Write-Host "Creating VHD of size: $vhdSizeGB GB"

# Create VHD
New-VHD -Path "C:\Temp\dc-data.vhdx" -SizeBytes ($vhdSizeGB * 1GB) -Dynamic

# Mount VHD
$vhd = Mount-VHD -Path "C:\Temp\dc-data.vhdx" -Passthru

# Initialize and format
$disk = Initialize-Disk -Number $vhd.Number -PartitionStyle GPT -PassThru
$partition = New-Partition -DiskNumber $disk.Number -UseMaximumSize -AssignDriveLetter
$volume = Format-Volume -DriveLetter $partition.DriveLetter -FileSystem NTFS -NewFileSystemLabel "Data" -Confirm:$false

# Get drive letter
$driveLetter = $partition.DriveLetter
Write-Host "VHD mounted as drive: ${driveLetter}:"

# Copy data to VHD
robocopy F:\Backup "${driveLetter}:\" /E /COPYALL /DCOPY:T /MT:16 /R:3 /W:5 /LOG:C:\Logs\vhd-copy.log /TEE

# Dismount
Dismount-VHD -Path "C:\Temp\dc-data.vhdx"

Write-Host "Data VHD created at C:\Temp\dc-data.vhdx"
```

#### 4.3 Upload Data VHD to Azure

**On File Server or workstation with AzCopy:**

```bash
# Upload data VHD to storage
azcopy copy \
  "C:\Temp\dc-data.vhdx" \
  "https://setcodcmigration.blob.core.windows.net/vhd-import/dc-data.vhd" \
  --blob-type PageBlob
```

**Or use Azure Storage Explorer (GUI method)**

#### 4.4 Create Managed Disk from Data VHD

```bash
# Get VHD URL
DATA_VHD_URL=$(az storage blob url \
  --account-name setcodcmigration \
  --container-name vhd-import \
  --name dc-data.vhd \
  --auth-mode login \
  --output tsv)

# Create data managed disk
az disk create \
  --resource-group RG-Setco-DC \
  --name DC-Setco-Data-Disk \
  --location eastus \
  --sku Standard_LRS \
  --source "$DATA_VHD_URL"
```

**Wait for disk creation (20-40 minutes depending on size).**

#### 4.5 Option B: Create Empty Disk and Copy Data Later

**If VHD creation is too complex, create empty disk:**

```bash
# Create empty data disk (adjust size as needed)
az disk create \
  --resource-group RG-Setco-DC \
  --name DC-Setco-Data-Disk \
  --location eastus \
  --sku Standard_LRS \
  --size-gb 500
```

**Then copy data after VM is built (Phase 6)**

**Checklist:**
- [ ] Robocopy complete (vendor confirmed)
- [ ] Data verified on FS F:\Backup
- [ ] Data VHD created from FS
- [ ] Data VHD uploaded to Azure storage
- [ ] Data managed disk created
- [ ] Both OS and Data disks show "Succeeded"

---

## PHASE 5: Build New DC VM

### 5.1 Create Network Interface

```bash
# Create public IP (optional, for initial access)
az network public-ip create \
  --resource-group RG-Setco-DC \
  --name DC-Setco-PIP \
  --allocation-method Static \
  --sku Standard

# Create NIC with static private IP
az network nic create \
  --resource-group RG-Setco-DC \
  --name DC-Setco-NIC \
  --vnet-name VNet-Setco-DC \
  --subnet DC-Subnet \
  --network-security-group NSG-DC \
  --public-ip-address DC-Setco-PIP \
  --private-ip-address 10.0.1.4
```

### 5.2 Build VM from Managed Disks

**PowerShell method (recommended):**

```powershell
# Variables
$resourceGroup = "RG-Setco-DC"
$location = "eastus"
$vmName = "DC-Setco-NewTenant"
$vmSize = "Standard_D2s_v3"  # 2 vCPU, 8GB RAM
$osDiskName = "DC-Setco-OS-Disk"
$dataDiskName = "DC-Setco-Data-Disk"
$nicName = "DC-Setco-NIC"

# Get resources
$osDisk = Get-AzDisk -ResourceGroupName $resourceGroup -DiskName $osDiskName
$dataDisk = Get-AzDisk -ResourceGroupName $resourceGroup -DiskName $dataDiskName
$nic = Get-AzNetworkInterface -Name $nicName -ResourceGroupName $resourceGroup

# Create VM configuration
$vmConfig = New-AzVMConfig -VMName $vmName -VMSize $vmSize

# Attach OS disk
$vmConfig = Set-AzVMOSDisk -VM $vmConfig -ManagedDiskId $osDisk.Id -CreateOption Attach -Windows

# Attach data disk
$vmConfig = Add-AzVMDataDisk -VM $vmConfig -ManagedDiskId $dataDisk.Id -Lun 0 -CreateOption Attach

# Add network interface
$vmConfig = Add-AzVMNetworkInterface -VM $vmConfig -Id $nic.Id -Primary

# Create VM
New-AzVM -ResourceGroupName $resourceGroup -Location $location -VM $vmConfig

Write-Host "VM created successfully!"
```

**Azure CLI method (alternative):**

```bash
# Get disk IDs
OS_DISK_ID=$(az disk show --resource-group RG-Setco-DC --name DC-Setco-OS-Disk --query id -o tsv)
DATA_DISK_ID=$(az disk show --resource-group RG-Setco-DC --name DC-Setco-Data-Disk --query id -o tsv)
NIC_ID=$(az network nic show --resource-group RG-Setco-DC --name DC-Setco-NIC --query id -o tsv)

# Create VM
az vm create \
  --resource-group RG-Setco-DC \
  --name DC-Setco-NewTenant \
  --attach-os-disk $OS_DISK_ID \
  --attach-data-disks $DATA_DISK_ID \
  --nics $NIC_ID \
  --os-type Windows \
  --size Standard_D2s_v3
```

**Wait 5-10 minutes for VM creation.**

### 5.3 Start VM and Get Connection Info

```bash
# Start VM (if not already started)
az vm start --resource-group RG-Setco-DC --name DC-Setco-NewTenant

# Get public IP
az network public-ip show \
  --resource-group RG-Setco-DC \
  --name DC-Setco-PIP \
  --query ipAddress -o tsv

# Get private IP
az vm show -d \
  --resource-group RG-Setco-DC \
  --name DC-Setco-NewTenant \
  --query privateIps -o tsv
```

**Checklist:**
- [ ] NIC created with static IP
- [ ] VM created successfully
- [ ] VM shows "Running" status
- [ ] Public IP obtained: _________________
- [ ] Private IP: 10.0.1.4

---

## PHASE 6: Configure and Validate New DC

### 6.1 Initial Connection

**RDP to the VM:**
```
mstsc /v:<PUBLIC-IP>
```

**Login with:**
- Username: `SOUTHERN\Administrator` (or original domain admin)
- Password: [From vendor/original DC]

### 6.2 Verify Disks

**On new DC, open PowerShell:**

```powershell
# Check disk status
Get-Disk
Get-Volume

# Bring data disk online if needed
Set-Disk -Number 1 -IsOffline $false

# Verify F: drive exists
Get-PSDrive

# If F: not assigned, assign it
Get-Partition -DiskNumber 1 | Set-Partition -NewDriveLetter F

# Verify data
Get-ChildItem F:\ -Directory
```

**Expected folders on F:\:**
- FTP Data
- HomeDirs
- PostClosing
- Qbooks
- SeaCrestScans
- SetcoDocs
- Versacheck
- Whole Life Fitness
- NTSYS

### 6.3 Verify Active Directory Services

```powershell
# Check AD services
Get-Service NTDS, DNS, Netlogon, W32Time | Format-Table Name, Status

# All should be "Running"

# Verify domain
Get-ADDomain

# Should show: SouthernEscrow.com

# Check FSMO roles
netdom query fsmo

# Verify DNS zones
Get-DnsServerZone

# Check SYSVOL/NETLOGON shares
Get-SmbShare | Where-Object {$_.Name -match "SYSVOL|NETLOGON"}
```

### 6.4 Configure DNS to Point to Itself

```powershell
# Get network adapter
$adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}

# Set DNS to point to itself
Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses ("127.0.0.1", "8.8.8.8")

# Verify
Get-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex

# Register DNS
ipconfig /registerdns

# Test DNS
nslookup SouthernEscrow.com
```

### 6.5 Recreate File Shares

**Copy scripts to C:\ps1:**

Transfer your F: drive scripts to the DC:
- 1-Setup-Directories-F-Drive.ps1
- 2-Set-NTFS-Permissions-F-Drive.ps1
- 3-Create-SMB-Shares-F-Drive.ps1
- 4-Validate-Configuration-F-Drive.ps1

**Run the scripts:**

```powershell
cd C:\ps1

# Directories should already exist from data copy
.\1-Setup-Directories-F-Drive.ps1
# Should show "Already exists" for all

# Apply NTFS permissions
.\2-Set-NTFS-Permissions-F-Drive.ps1
# Press key to confirm

# Create SMB shares
.\3-Create-SMB-Shares-F-Drive.ps1

# Validate everything
.\4-Validate-Configuration-F-Drive.ps1
```

**Verify shares:**

```powershell
# List all shares
Get-SmbShare | Format-Table Name, Path

# Expected shares:
# F, FTP Data, HomeDirs, Legal, PostClosing, Qbooks,
# SeaCrestScans, SetcoDocs, Versacheck, Whole Life Fitness, worddocs
```

### 6.6 Run DC Health Check

```cmd
# Comprehensive DC diagnostic
dcdiag /v > C:\Logs\dcdiag.txt

# Review output
notepad C:\Logs\dcdiag.txt

# Check replication (if multiple DCs)
repadmin /showrepl

# Verify DNS
dcdiag /test:dns
```

### 6.7 Test from Client

**From a client workstation:**

```cmd
# Test DNS resolution
nslookup SouthernEscrow.com

# Test DC connectivity
nltest /dsgetdc:SouthernEscrow.com

# Test share access
net view \\DC-Setco-NewTenant

# Map a test drive
net use Z: \\DC-Setco-NewTenant\HomeDirs

# Test file access
dir Z:
```

**Checklist:**
- [ ] RDP connection successful
- [ ] C:\ drive accessible
- [ ] F:\ drive online and accessible
- [ ] All data folders visible on F:\
- [ ] AD services running
- [ ] Domain is SouthernEscrow.com
- [ ] DNS pointing to itself
- [ ] DNS resolution working
- [ ] All file shares created
- [ ] dcdiag passes (or acceptable warnings)
- [ ] Client can access shares
- [ ] Users can authenticate

---

## PHASE 7: Cutover

### Your Tasks:

#### 7.0 Pre-Cutover Coordination
- Notify users of maintenance window
- Schedule cutover during low-usage time
- Coordinate with vendor if they manage client DNS/DHCP

### DNS/DHCP Updates:
- If YOU manage DNS/DHCP: Update clients to point to new DC IP (10.0.1.4)
- If vendor manages: Provide new DC IP and coordinate timing

### Old DC Decommission:
- **Do NOT decommission immediately**
- Wait 2+ weeks to ensure stability
- Verify all users connecting to new DC
- Coordinate with vendor via NinjaOne to gracefully demote old DC

### Your Post-Cutover Tasks:

#### 7.1 Monitor for 48 Hours

```powershell
# Check Event Viewer - Directory Services log
Get-EventLog -LogName "Directory Service" -Newest 50 | Where-Object {$_.EntryType -eq "Error"}

# Monitor failed logins
Get-EventLog -LogName Security | Where-Object {$_.EventID -eq 4625} | Select-Object -First 10

# Check share access
Get-SmbOpenFile | Format-Table ClientComputerName, ClientUserName, Path

# Monitor disk space
Get-Volume
```

#### 7.2 Configure Backups

```bash
# Enable Azure Backup
az backup vault create \
  --resource-group RG-Setco-DC \
  --name Vault-Setco-DC \
  --location eastus

# Enable backup for VM
az backup protection enable-for-vm \
  --resource-group RG-Setco-DC \
  --vault-name Vault-Setco-DC \
  --vm DC-Setco-NewTenant \
  --policy-name DefaultPolicy
```

#### 7.3 Take Snapshots

```bash
# Snapshot OS disk
az snapshot create \
  --resource-group RG-Setco-DC \
  --name DC-OS-Snapshot-PostMigration \
  --source DC-Setco-OS-Disk

# Snapshot data disk
az snapshot create \
  --resource-group RG-Setco-DC \
  --name DC-Data-Snapshot-PostMigration \
  --source DC-Setco-Data-Disk
```

---

## Quick Reference Commands

### Check Robocopy Progress (on FS)
```powershell
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum
```

### List Azure Resources
```bash
az resource list --resource-group RG-Setco-DC --output table
```

### VM Status
```bash
az vm get-instance-view --resource-group RG-Setco-DC --name DC-Setco-NewTenant --query instanceView.statuses
```

### Check Disk Status
```powershell
Get-Disk
Get-Volume
Get-Partition
```

### Verify Shares
```powershell
Get-SmbShare
Get-SmbShareAccess -Name HomeDirs
```

### Check AD Health
```cmd
dcdiag /v
netdom query fsmo
repadmin /showrepl
```

---

## Coordination Points with Vendor

### What You Need from Vendor:

| Item | When | Format |
|------|------|--------|
| OS VHD export | Phase 3 | Vendor uploads via AzCopy to your storage |
| Domain admin password | Before VM start | Secure method (if not already known) |
| Original DC IP/hostname | During planning | Documentation |
| Azure Portal access confirmation | Pre-migration | Vendor confirms they can export VHD |
| Cutover coordination | Pre-cutover | If they manage client DNS/DHCP |

### What You Provide to Vendor:

| Item | When | Format |
|------|------|--------|
| Storage SAS token | Phase 2 | SAS URL for VHD upload |
| New DC IP address | Post-build | 10.0.1.4 |
| Cutover confirmation | Post-validation | Email/call |
| Old DC decommission request | After 2+ weeks | Via NinjaOne coordination |

---

## Timeline

| Phase | Duration | Dependencies | Who Does It |
|-------|----------|--------------|-------------|
| 1. YOU run robocopy via NinjaOne | 6-12 hours | Network speed | YOU |
| 2. Prep infrastructure | 1 hour | Can run parallel | YOU |
| 3. OS VHD import | 2-4 hours | Vendor export | Vendor exports, YOU import |
| 4. Data disk creation | 2-6 hours | Robocopy done | YOU |
| 5. VM build | 30 min | Both disks ready | YOU |
| 6. Configuration | 2-3 hours | - | YOU |
| 7. Testing | 2-4 hours | - | YOU |
| **Total** | **15-30 hours** | Over 2-3 days | Mostly YOU |

---

## Troubleshooting

### Robocopy Issues

**Can't map Y: drive from DC to FS:**
```cmd
# Test network connectivity from DC
ping FS-SERVERNAME
ping 10.x.x.x

# Check SMB port
Test-NetConnection -ComputerName FS-SERVERNAME -Port 445

# Try with IP instead of hostname
net use Y: \\10.x.x.x\F$ /user:DESTINATION\Administrator
```

**Robocopy fails with access denied:**
```cmd
# Ensure you're running CMD as Administrator on source DC
# Verify credentials are correct
# Check that F$ share exists on FS and has admin access

# On FS, verify admin share
Get-SmbShare -Name F$
```

**Robocopy slow or timing out:**
```cmd
# Reduce thread count
robocopy E:\ Y:\Backup /MIR /COPYALL /DCOPY:T /MT:8 /R:3 /W:5 /B /LOG:C:\Logs\robocopy.log /TEE

# Or increase wait time
robocopy E:\ Y:\Backup /MIR /COPYALL /DCOPY:T /MT:32 /R:5 /W:30 /B /LOG:C:\Logs\robocopy.log /TEE
```

### OS VHD Upload Fails
```bash
# Regenerate SAS token (24hr expiry)
az storage container generate-sas \
  --account-name setcodcmigration \
  --name vhd-import \
  --permissions racwdl \
  --expiry $(date -u -d "1 day" '+%Y-%m-%dT%H:%MZ') \
  --auth-mode login \
  --output tsv
```

### Data Disk Not Showing as F:\
```powershell
Set-Disk -Number 1 -IsOffline $false
Get-Partition -DiskNumber 1 | Set-Partition -NewDriveLetter F
```

### VM Won't Start
```bash
# Check boot diagnostics
az vm boot-diagnostics get-boot-log \
  --resource-group RG-Setco-DC \
  --name DC-Setco-NewTenant
```

### Can't RDP
```bash
# Reset RDP (if needed)
az vm user reset-ssh \
  --resource-group RG-Setco-DC \
  --name DC-Setco-NewTenant

# Check NSG rules
az network nsg rule list --resource-group RG-Setco-DC --nsg-name NSG-DC --output table
```

---

## Success Criteria

- [ ] Data sync complete (vendor confirmed)
- [ ] OS VHD imported successfully
- [ ] Data disk created from FS
- [ ] VM boots and runs
- [ ] Can RDP to VM
- [ ] C:\ and F:\ drives accessible
- [ ] AD services running
- [ ] DNS resolving correctly
- [ ] All 11 file shares created
- [ ] dcdiag passes
- [ ] Client can access shares
- [ ] Users can authenticate
- [ ] No critical errors in Event Viewer

---

**Document Version:** 2.0 (Updated for NinjaOne Access)
**Created:** 2025-11-17
**Updated:** 2025-11-17
**Your Environment:** Destination Tenant Owner + NinjaOne Access to Source DC
**Vendor Environment:** Source Azure Tenant Portal Access Only
