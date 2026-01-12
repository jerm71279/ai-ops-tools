# Standard Operating Procedure: Azure Tenant-to-Tenant VM Migration

| | |
|---|---|
| **Document ID:** | SOP-AZ-004 |
| **Title:** | Azure Tenant-to-Tenant VM Migration |
| **Category:** | Azure/Cloud |
| **Version:** | 1.0 |
| **Status:** | Draft |
| **Author:** | OberaConnect |
| **Creation Date:** | 2026-01-12 |
| **Approval Date:** | Pending |

---

### 1.0 Purpose

This procedure documents the complete workflow for migrating virtual machines between Azure tenants, including OS disk migration via VHD export/import and data migration via robocopy. This is commonly used for tenant consolidation, vendor handoff, or infrastructure reorganization.

### 2.0 Scope

This SOP applies to:
- Windows Server VM migrations between Azure tenants
- Domain Controller migrations requiring AD preservation
- File server migrations with NTFS permissions
- OberaConnect technicians performing Azure infrastructure work

### 3.0 Definitions

| Term | Definition |
|------|------------|
| **Source Tenant** | Original Azure tenant containing the VM to be migrated |
| **Destination Tenant** | Target Azure tenant where VM will be rebuilt |
| **VHD** | Virtual Hard Disk - Azure disk format |
| **Managed Disk** | Azure-managed storage disk attached to VMs |
| **SAS Token** | Shared Access Signature for secure blob access |
| **AzCopy** | Microsoft command-line utility for Azure storage operations |
| **Robocopy** | Robust File Copy - Windows tool for large data transfers |

### 4.0 Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **Destination Tenant Admin** | Prepare infrastructure, receive VHDs, build new VM |
| **Source Tenant Admin** | Export OS VHD, provide access for data sync |
| **Network Admin** | Ensure connectivity between tenants for data transfer |
| **Project Manager** | Coordinate cutover timing, communicate with stakeholders |

### 5.0 Prerequisites

#### 5.1 Source Tenant Requirements
- [ ] Admin access to source Azure portal (or vendor coordination)
- [ ] Remote access to source VM (NinjaOne, RDP, or similar)
- [ ] Source VM in stopped/deallocated state for VHD export
- [ ] Network connectivity from source to destination for robocopy

#### 5.2 Destination Tenant Requirements
- [ ] Azure subscription with sufficient quota
- [ ] Azure CLI or PowerShell Az module installed
- [ ] Storage account for VHD import
- [ ] VNet and subnet planned for new VM
- [ ] File server or staging location for data sync (if applicable)

#### 5.3 Information Required
- [ ] Source VM size and configuration
- [ ] Source OS disk size
- [ ] Source data disk(s) size and content
- [ ] Domain information (if Domain Controller)
- [ ] Network configuration (IP, DNS, gateway)
- [ ] Admin credentials for source VM

---

### 6.0 Procedure

## Phase 1: Data Sync via Robocopy

*Run this phase BEFORE OS VHD export to minimize downtime*

#### 6.1 Prepare Staging Location in Destination Tenant

On destination file server or VM:
```powershell
# Create staging folder
New-Item -Path "F:\Backup" -ItemType Directory -Force

# Verify available space
Get-PSDrive F | Select-Object Used, Free
```

#### 6.2 Connect to Source VM

Via NinjaOne, RDP, or Azure Bastion:
1. Open remote session to source VM
2. Open CMD or PowerShell as Administrator

#### 6.3 Map Network Drive to Destination

On source VM:
```cmd
# Map drive to destination file server
net use Y: \\<DESTINATION_SERVER>\F$ /user:<DOMAIN>\Administrator <PASSWORD>

# Or via IP if DNS not configured
net use Y: \\<DEST_IP>\F$ /user:<DOMAIN>\Administrator <PASSWORD>

# Verify mapping
dir Y:\
```

#### 6.4 Run Initial Robocopy Sync

```cmd
robocopy E:\ Y:\Backup /MIR /COPYALL /DCOPY:T /MT:32 /R:3 /W:5 /B /XD "System Volume Information" "$RECYCLE.BIN" /LOG:C:\Logs\robocopy_initial.log /TEE /NP
```

**Parameters:**
| Switch | Purpose |
|--------|---------|
| `/MIR` | Mirror directories (full sync with deletions) |
| `/COPYALL` | Copy all file attributes including ACLs |
| `/DCOPY:T` | Copy directory timestamps |
| `/MT:32` | Multi-threaded (32 threads) |
| `/R:3` | Retry 3 times on failure |
| `/W:5` | Wait 5 seconds between retries |
| `/B` | Backup mode (bypass file security) |
| `/XD` | Exclude directories |
| `/LOG` | Write log file |
| `/TEE` | Output to console and log |
| `/NP` | No progress percentage |

**Estimated time:** 6-12 hours for ~400GB depending on network speed

#### 6.5 Monitor Progress

On source VM:
```cmd
type C:\Logs\robocopy_initial.log | more
```

On destination:
```powershell
# Monitor data arrival
Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum

# Count files
(Get-ChildItem F:\Backup -Recurse -File).Count
```

---

## Phase 2: Prepare Destination Infrastructure

*Run while data sync is in progress*

#### 6.6 Create Resource Group

```bash
az group create \
  --name RG-Migration-<CUSTOMER> \
  --location eastus
```

#### 6.7 Create Virtual Network

```bash
az network vnet create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name VNet-<CUSTOMER> \
  --address-prefix 10.0.0.0/16 \
  --subnet-name VM-Subnet \
  --subnet-prefix 10.0.1.0/24
```

#### 6.8 Create Network Security Group

```bash
# Create NSG
az network nsg create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name NSG-VM

# Add RDP rule
az network nsg rule create \
  --resource-group RG-Migration-<CUSTOMER> \
  --nsg-name NSG-VM \
  --name AllowRDP \
  --priority 100 \
  --destination-port-ranges 3389 \
  --protocol Tcp \
  --access Allow

# Add additional rules as needed (DNS, LDAP, SMB for DCs)
```

#### 6.9 Create Storage Account for VHD Import

```bash
# Create storage account
az storage account create \
  --name <CUSTOMER>migration \
  --resource-group RG-Migration-<CUSTOMER> \
  --location eastus \
  --sku Standard_LRS

# Create container
az storage container create \
  --account-name <CUSTOMER>migration \
  --name vhd-import \
  --auth-mode login

# Generate SAS token for source tenant to upload
az storage container generate-sas \
  --account-name <CUSTOMER>migration \
  --name vhd-import \
  --permissions racwdl \
  --expiry $(date -u -d "7 days" '+%Y-%m-%dT%H:%MZ') \
  --auth-mode login \
  --as-user \
  --output tsv
```

**Save the SAS token to provide to source tenant admin!**

---

## Phase 3: Export and Transfer OS VHD

*Coordinate with source tenant admin*

#### 6.10 Source Tenant Actions (Vendor/Partner)

Source tenant admin will:
1. Stop/deallocate source VM
2. Create snapshot of OS disk
3. Export snapshot to VHD
4. Transfer VHD to destination storage using AzCopy

```bash
# Example command source admin runs
azcopy copy \
  "https://source-storage.blob.core.windows.net/snapshots/os-disk.vhd?<SOURCE_SAS>" \
  "https://<CUSTOMER>migration.blob.core.windows.net/vhd-import/os-disk.vhd?<DEST_SAS>"
```

#### 6.11 Verify VHD Upload

```bash
az storage blob list \
  --account-name <CUSTOMER>migration \
  --container-name vhd-import \
  --output table \
  --auth-mode login
```

#### 6.12 Create Managed Disk from OS VHD

```bash
# Get VHD URL
VHD_URL=$(az storage blob url \
  --account-name <CUSTOMER>migration \
  --container-name vhd-import \
  --name os-disk.vhd \
  --auth-mode login \
  --output tsv)

# Create OS managed disk
az disk create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name <CUSTOMER>-OS-Disk \
  --location eastus \
  --sku Premium_LRS \
  --source "$VHD_URL" \
  --os-type Windows
```

Wait 10-20 minutes for disk creation.

---

## Phase 4: Create Data Disk

*Only after robocopy sync is complete*

#### 6.13 Verify Robocopy Completion

On source VM, check robocopy log shows completion summary:
```
               Total    Copied   Skipped  Mismatch    FAILED    Extras
    Dirs :      XXXX      XXXX         0         0         0         0
   Files :     XXXXX     XXXXX         0         0         0         0
```

#### 6.14 Option A: Create VHD from Synced Data

On destination file server:
```powershell
# Calculate required size
$dataSize = (Get-ChildItem F:\Backup -Recurse | Measure-Object -Property Length -Sum).Sum
$vhdSizeGB = [Math]::Ceiling($dataSize / 1GB) + 100
Write-Host "Creating VHD of size: $vhdSizeGB GB"

# Create VHD
New-VHD -Path "C:\Temp\data-disk.vhdx" -SizeBytes ($vhdSizeGB * 1GB) -Dynamic

# Mount and format
$vhd = Mount-VHD -Path "C:\Temp\data-disk.vhdx" -Passthru
$disk = Initialize-Disk -Number $vhd.Number -PartitionStyle GPT -PassThru
$partition = New-Partition -DiskNumber $disk.Number -UseMaximumSize -AssignDriveLetter
Format-Volume -DriveLetter $partition.DriveLetter -FileSystem NTFS -NewFileSystemLabel "Data"

# Copy data
$driveLetter = $partition.DriveLetter
robocopy F:\Backup "${driveLetter}:\" /E /COPYALL /DCOPY:T /MT:16 /LOG:C:\Logs\vhd-copy.log

# Dismount
Dismount-VHD -Path "C:\Temp\data-disk.vhdx"
```

#### 6.15 Upload Data VHD to Azure

```bash
azcopy copy \
  "C:\Temp\data-disk.vhdx" \
  "https://<CUSTOMER>migration.blob.core.windows.net/vhd-import/data-disk.vhd" \
  --blob-type PageBlob
```

#### 6.16 Create Data Managed Disk

```bash
DATA_VHD_URL=$(az storage blob url \
  --account-name <CUSTOMER>migration \
  --container-name vhd-import \
  --name data-disk.vhd \
  --auth-mode login \
  --output tsv)

az disk create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name <CUSTOMER>-Data-Disk \
  --location eastus \
  --sku Standard_LRS \
  --source "$DATA_VHD_URL"
```

#### 6.17 Option B: Create Empty Disk (Copy Data Later)

```bash
az disk create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name <CUSTOMER>-Data-Disk \
  --location eastus \
  --sku Standard_LRS \
  --size-gb 500
```

---

## Phase 5: Build New VM

#### 6.18 Create Network Interface

```bash
# Create public IP
az network public-ip create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name <CUSTOMER>-PIP \
  --allocation-method Static \
  --sku Standard

# Create NIC
az network nic create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name <CUSTOMER>-NIC \
  --vnet-name VNet-<CUSTOMER> \
  --subnet VM-Subnet \
  --network-security-group NSG-VM \
  --public-ip-address <CUSTOMER>-PIP \
  --private-ip-address 10.0.1.4
```

#### 6.19 Create VM from Managed Disks

**PowerShell Method (Recommended):**
```powershell
$resourceGroup = "RG-Migration-<CUSTOMER>"
$location = "eastus"
$vmName = "<CUSTOMER>-VM"
$vmSize = "Standard_D2s_v3"

$osDisk = Get-AzDisk -ResourceGroupName $resourceGroup -DiskName "<CUSTOMER>-OS-Disk"
$dataDisk = Get-AzDisk -ResourceGroupName $resourceGroup -DiskName "<CUSTOMER>-Data-Disk"
$nic = Get-AzNetworkInterface -Name "<CUSTOMER>-NIC" -ResourceGroupName $resourceGroup

$vmConfig = New-AzVMConfig -VMName $vmName -VMSize $vmSize
$vmConfig = Set-AzVMOSDisk -VM $vmConfig -ManagedDiskId $osDisk.Id -CreateOption Attach -Windows
$vmConfig = Add-AzVMDataDisk -VM $vmConfig -ManagedDiskId $dataDisk.Id -Lun 0 -CreateOption Attach
$vmConfig = Add-AzVMNetworkInterface -VM $vmConfig -Id $nic.Id -Primary

New-AzVM -ResourceGroupName $resourceGroup -Location $location -VM $vmConfig
```

**Azure CLI Method:**
```bash
OS_DISK_ID=$(az disk show -g RG-Migration-<CUSTOMER> -n <CUSTOMER>-OS-Disk --query id -o tsv)
DATA_DISK_ID=$(az disk show -g RG-Migration-<CUSTOMER> -n <CUSTOMER>-Data-Disk --query id -o tsv)
NIC_ID=$(az network nic show -g RG-Migration-<CUSTOMER> -n <CUSTOMER>-NIC --query id -o tsv)

az vm create \
  --resource-group RG-Migration-<CUSTOMER> \
  --name <CUSTOMER>-VM \
  --attach-os-disk $OS_DISK_ID \
  --attach-data-disks $DATA_DISK_ID \
  --nics $NIC_ID \
  --os-type Windows \
  --size Standard_D2s_v3
```

#### 6.20 Start VM and Get Connection Info

```bash
az vm start -g RG-Migration-<CUSTOMER> -n <CUSTOMER>-VM

# Get public IP
az network public-ip show -g RG-Migration-<CUSTOMER> -n <CUSTOMER>-PIP --query ipAddress -o tsv
```

---

## Phase 6: Post-Migration Configuration

#### 6.21 Initial Connection

```cmd
mstsc /v:<PUBLIC_IP>
```

Login with original domain or local admin credentials.

#### 6.22 Verify Disks

```powershell
Get-Disk
Get-Volume

# Bring data disk online if needed
Set-Disk -Number 1 -IsOffline $false

# Assign drive letter if needed
Get-Partition -DiskNumber 1 | Set-Partition -NewDriveLetter F
```

#### 6.23 Verify Services (Domain Controller)

```powershell
# Check AD services
Get-Service NTDS, DNS, Netlogon, W32Time | Format-Table Name, Status

# Verify domain
Get-ADDomain

# Check FSMO roles
netdom query fsmo

# Run DC diagnostics
dcdiag /v
```

#### 6.24 Configure DNS

```powershell
$adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses ("127.0.0.1", "8.8.8.8")
ipconfig /registerdns
```

#### 6.25 Final Delta Sync (If Needed)

If time elapsed since initial sync, run final robocopy:
```cmd
robocopy \\<SOURCE>\E$ F:\ /MIR /COPYALL /DCOPY:T /MT:32 /R:1 /W:1 /LOG:C:\Logs\final_sync.log /TEE
```

---

### 7.0 Verification & Quality Checks

- [ ] VM boots successfully
- [ ] Can RDP to VM via public IP
- [ ] OS disk accessible (C:\)
- [ ] Data disk accessible (F:\ or assigned letter)
- [ ] All data present and accessible
- [ ] Services running (AD, DNS if applicable)
- [ ] Network connectivity working
- [ ] DNS resolution working
- [ ] File shares accessible (if file server)
- [ ] Users can authenticate (if DC)
- [ ] Backup configured for new VM

---

### 8.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| VHD upload fails | Check SAS token expiry, verify blob type is PageBlob |
| Disk creation fails | Ensure VHD is in same region as target disk |
| VM won't boot | Check boot diagnostics, may need to run startup repair |
| Data disk offline | Run `Set-Disk -Number X -IsOffline $false` |
| Can't RDP | Check NSG rules allow 3389, verify public IP assigned |
| AD services won't start | Check DNS configuration, run `dcdiag /fix` |
| File permissions lost | Re-run permission scripts, verify robocopy used /COPYALL |

---

### 9.0 Related Documents

| Document | Description |
|----------|-------------|
| SOP-AZ-001 | Azure VM Administration |
| SOP-AZ-005 | Azure VHD Export and Import |
| SOP-AD-003 | Azure VM Domain Join/Unjoin |

---

### 10.0 Revision History

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-01-12 | OberaConnect | Initial document creation |

---

### 11.0 Approval

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | Technical Lead | | |
| | Operations Manager | | |
