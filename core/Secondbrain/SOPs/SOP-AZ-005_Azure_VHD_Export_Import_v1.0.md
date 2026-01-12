# Standard Operating Procedure: Azure VHD Export and Import

| | |
|---|---|
| **Document ID:** | SOP-AZ-005 |
| **Title:** | Azure VHD Export and Import |
| **Category:** | Azure/Cloud |
| **Version:** | 1.0 |
| **Status:** | Draft |
| **Author:** | OberaConnect |
| **Creation Date:** | 2026-01-12 |
| **Approval Date:** | Pending |

---

### 1.0 Purpose

This procedure documents the process for exporting Virtual Hard Disks (VHDs) from Azure VMs and importing them into different Azure subscriptions or tenants. This enables VM migration, disaster recovery, and infrastructure cloning scenarios.

### 2.0 Scope

This SOP applies to:
- Exporting Azure managed disks to VHD format
- Transferring VHDs between Azure storage accounts
- Importing VHDs to create new managed disks
- Cross-tenant and cross-subscription disk transfers

### 3.0 Definitions

| Term | Definition |
|------|------------|
| **Managed Disk** | Azure-managed storage disk with automatic replication |
| **VHD** | Virtual Hard Disk format used by Azure |
| **Snapshot** | Point-in-time copy of a managed disk |
| **SAS URL** | Shared Access Signature URL for secure blob access |
| **AzCopy** | Microsoft's high-performance Azure storage transfer tool |
| **PageBlob** | Azure blob type required for VHD storage |

### 4.0 Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **Source Admin** | Create snapshots, generate SAS URLs, initiate export |
| **Destination Admin** | Prepare storage, receive VHDs, create disks |
| **Security Admin** | Approve cross-tenant transfers, manage SAS tokens |

### 5.0 Prerequisites

#### 5.1 Source Environment
- [ ] Azure CLI or PowerShell Az module installed
- [ ] Contributor access to source subscription
- [ ] VM stopped/deallocated for consistent snapshot
- [ ] Sufficient storage quota for snapshots

#### 5.2 Destination Environment
- [ ] Storage account created in target subscription
- [ ] Blob container for VHD import
- [ ] Sufficient storage quota for managed disks

#### 5.3 Tools Required
- [ ] Azure CLI (`az`) or PowerShell Az module
- [ ] AzCopy v10 or later
- [ ] Azure Storage Explorer (optional, for GUI)

---

### 6.0 Procedure

## Part A: VHD Export (Source Tenant)

#### 6.1 Stop and Deallocate VM

```bash
# Stop VM to ensure consistent disk state
az vm deallocate \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME>

# Verify VM is deallocated
az vm get-instance-view \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME> \
  --query "instanceView.statuses[?starts_with(code, 'PowerState')].displayStatus" \
  -o tsv
```

Expected output: `VM deallocated`

#### 6.2 Create Snapshot of OS Disk

```bash
# Get OS disk name
OS_DISK=$(az vm show \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME> \
  --query "storageProfile.osDisk.name" \
  -o tsv)

# Create snapshot
az snapshot create \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME>-os-snapshot-$(date +%Y%m%d) \
  --source $OS_DISK \
  --sku Standard_LRS
```

#### 6.3 Create Snapshot of Data Disk(s)

```bash
# List data disks
az vm show \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME> \
  --query "storageProfile.dataDisks[].name" \
  -o tsv

# Create snapshot for each data disk
az snapshot create \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME>-data-snapshot-$(date +%Y%m%d) \
  --source <DATA_DISK_NAME> \
  --sku Standard_LRS
```

#### 6.4 Generate SAS URL for Export

```bash
# Grant access and get SAS URL (valid for 24 hours)
az snapshot grant-access \
  --resource-group <SOURCE_RG> \
  --name <VM_NAME>-os-snapshot-$(date +%Y%m%d) \
  --duration-in-seconds 86400 \
  --access-level Read \
  --query "accessSas" \
  -o tsv
```

**Save this SAS URL - needed for transfer!**

Repeat for data disk snapshots.

#### 6.5 Alternative: Export Directly from Managed Disk

If you don't want to create snapshots:

```bash
# Grant access to managed disk directly
az disk grant-access \
  --resource-group <SOURCE_RG> \
  --name <DISK_NAME> \
  --duration-in-seconds 86400 \
  --access-level Read \
  --query "accessSas" \
  -o tsv
```

**Note:** VM must remain deallocated during export.

---

## Part B: VHD Transfer

#### 6.6 Option 1: Direct Transfer with AzCopy (Recommended)

Transfer directly from source to destination storage:

```bash
# Install AzCopy if not present
# Download from: https://aka.ms/downloadazcopy

# Transfer VHD
azcopy copy \
  "<SOURCE_SAS_URL>" \
  "https://<DEST_STORAGE>.blob.core.windows.net/<CONTAINER>/os-disk.vhd?<DEST_SAS>" \
  --blob-type PageBlob
```

**Important:** Use `--blob-type PageBlob` for VHDs!

#### 6.7 Option 2: Download Then Upload

If direct transfer isn't possible:

**Download to local:**
```bash
azcopy copy "<SOURCE_SAS_URL>" "C:\VHD-Export\os-disk.vhd"
```

**Upload to destination:**
```bash
azcopy copy \
  "C:\VHD-Export\os-disk.vhd" \
  "https://<DEST_STORAGE>.blob.core.windows.net/<CONTAINER>/os-disk.vhd?<DEST_SAS>" \
  --blob-type PageBlob
```

#### 6.8 Option 3: Azure Storage Explorer (GUI)

1. Open Azure Storage Explorer
2. Connect to source storage account
3. Navigate to snapshot/disk blob
4. Right-click > Copy
5. Connect to destination storage account
6. Navigate to target container
7. Right-click > Paste

#### 6.9 Monitor Transfer Progress

AzCopy shows progress automatically. For large VHDs:

```bash
# Check transfer status
azcopy jobs list
azcopy jobs show <JOB_ID>
```

---

## Part C: VHD Import (Destination Tenant)

#### 6.10 Prepare Destination Storage Account

```bash
# Create storage account (if not exists)
az storage account create \
  --name <DEST_STORAGE> \
  --resource-group <DEST_RG> \
  --location <REGION> \
  --sku Standard_LRS

# Create container
az storage container create \
  --account-name <DEST_STORAGE> \
  --name vhd-import \
  --auth-mode login

# Generate SAS token for uploads
az storage container generate-sas \
  --account-name <DEST_STORAGE> \
  --name vhd-import \
  --permissions racwdl \
  --expiry $(date -u -d "7 days" '+%Y-%m-%dT%H:%MZ') \
  --auth-mode login \
  --as-user \
  -o tsv
```

#### 6.11 Verify VHD Upload

```bash
# List blobs in container
az storage blob list \
  --account-name <DEST_STORAGE> \
  --container-name vhd-import \
  --output table \
  --auth-mode login

# Check blob properties
az storage blob show \
  --account-name <DEST_STORAGE> \
  --container-name vhd-import \
  --name os-disk.vhd \
  --auth-mode login
```

Verify:
- Blob Type: PageBlob
- Size matches source

#### 6.12 Create Managed Disk from VHD

**For OS Disk:**
```bash
# Get VHD URL
VHD_URL=$(az storage blob url \
  --account-name <DEST_STORAGE> \
  --container-name vhd-import \
  --name os-disk.vhd \
  --auth-mode login \
  -o tsv)

# Create OS managed disk
az disk create \
  --resource-group <DEST_RG> \
  --name <NEW_VM>-OS-Disk \
  --location <REGION> \
  --sku Premium_LRS \
  --source "$VHD_URL" \
  --os-type Windows
```

**For Data Disk:**
```bash
DATA_VHD_URL=$(az storage blob url \
  --account-name <DEST_STORAGE> \
  --container-name vhd-import \
  --name data-disk.vhd \
  --auth-mode login \
  -o tsv)

az disk create \
  --resource-group <DEST_RG> \
  --name <NEW_VM>-Data-Disk \
  --location <REGION> \
  --sku Standard_LRS \
  --source "$DATA_VHD_URL"
```

**Disk creation time:** 10-30 minutes depending on size.

#### 6.13 Verify Disk Creation

```bash
az disk show \
  --resource-group <DEST_RG> \
  --name <NEW_VM>-OS-Disk \
  --query "{Name:name, State:provisioningState, Size:diskSizeGb}" \
  -o table
```

Expected: `provisioningState: Succeeded`

---

## Part D: Create VM from Imported Disks

#### 6.14 Create Network Resources

```bash
# Create public IP
az network public-ip create \
  --resource-group <DEST_RG> \
  --name <NEW_VM>-PIP \
  --allocation-method Static

# Create NIC
az network nic create \
  --resource-group <DEST_RG> \
  --name <NEW_VM>-NIC \
  --vnet-name <VNET_NAME> \
  --subnet <SUBNET_NAME> \
  --public-ip-address <NEW_VM>-PIP
```

#### 6.15 Create VM from Disks

**Azure CLI:**
```bash
OS_DISK_ID=$(az disk show -g <DEST_RG> -n <NEW_VM>-OS-Disk --query id -o tsv)
DATA_DISK_ID=$(az disk show -g <DEST_RG> -n <NEW_VM>-Data-Disk --query id -o tsv)
NIC_ID=$(az network nic show -g <DEST_RG> -n <NEW_VM>-NIC --query id -o tsv)

az vm create \
  --resource-group <DEST_RG> \
  --name <NEW_VM> \
  --attach-os-disk $OS_DISK_ID \
  --attach-data-disks $DATA_DISK_ID \
  --nics $NIC_ID \
  --os-type Windows \
  --size Standard_D2s_v3
```

**PowerShell:**
```powershell
$osDisk = Get-AzDisk -ResourceGroupName <DEST_RG> -DiskName <NEW_VM>-OS-Disk
$dataDisk = Get-AzDisk -ResourceGroupName <DEST_RG> -DiskName <NEW_VM>-Data-Disk
$nic = Get-AzNetworkInterface -Name <NEW_VM>-NIC -ResourceGroupName <DEST_RG>

$vmConfig = New-AzVMConfig -VMName <NEW_VM> -VMSize Standard_D2s_v3
$vmConfig = Set-AzVMOSDisk -VM $vmConfig -ManagedDiskId $osDisk.Id -CreateOption Attach -Windows
$vmConfig = Add-AzVMDataDisk -VM $vmConfig -ManagedDiskId $dataDisk.Id -Lun 0 -CreateOption Attach
$vmConfig = Add-AzVMNetworkInterface -VM $vmConfig -Id $nic.Id

New-AzVM -ResourceGroupName <DEST_RG> -Location <REGION> -VM $vmConfig
```

---

## Part E: Cleanup

#### 6.16 Revoke Source Access

```bash
# Revoke snapshot access
az snapshot revoke-access \
  --resource-group <SOURCE_RG> \
  --name <SNAPSHOT_NAME>

# Or revoke disk access
az disk revoke-access \
  --resource-group <SOURCE_RG> \
  --name <DISK_NAME>
```

#### 6.17 Delete Temporary Resources

```bash
# Delete snapshots (after confirming VM works)
az snapshot delete \
  --resource-group <SOURCE_RG> \
  --name <SNAPSHOT_NAME>

# Delete VHD blobs from storage (after confirming disks work)
az storage blob delete \
  --account-name <DEST_STORAGE> \
  --container-name vhd-import \
  --name os-disk.vhd \
  --auth-mode login
```

---

### 7.0 Verification & Quality Checks

- [ ] Snapshot created successfully (source)
- [ ] SAS URL generated and valid
- [ ] VHD transfer completed (check size matches)
- [ ] VHD uploaded as PageBlob type
- [ ] Managed disk created successfully
- [ ] Disk shows "Succeeded" provisioning state
- [ ] VM created from disk
- [ ] VM boots and is accessible
- [ ] Source access revoked
- [ ] Temporary resources cleaned up

---

### 8.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| "Blob type mismatch" | Ensure `--blob-type PageBlob` used with AzCopy |
| SAS URL expired | Regenerate with longer duration |
| Disk creation stuck | Check blob is fully uploaded, region matches |
| Transfer slow | Use AzCopy with `--cap-mbps` to throttle, or run from Azure VM |
| "Disk is not in correct state" | Ensure VM is fully deallocated, not just stopped |
| Access denied | Verify RBAC permissions, check SAS token permissions |
| VM won't boot from disk | Check OS type (Windows/Linux) specified correctly |

### 8.1 Common AzCopy Errors

| Error | Resolution |
|-------|------------|
| `AuthenticationFailed` | Regenerate SAS token, check expiry |
| `BlobTypeMismatch` | Use `--blob-type PageBlob` |
| `ServerBusy` | Retry with `--retry-policy exponential` |
| `Network timeout` | Reduce concurrency with `--cap-mbps 100` |

---

### 9.0 Related Documents

| Document | Description |
|----------|-------------|
| SOP-AZ-001 | Azure VM Administration |
| SOP-AZ-004 | Azure Tenant-to-Tenant VM Migration |

### 9.1 External References
- [AzCopy Documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
- [Export Azure Managed Disk](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/download-vhd)
- [Create VM from Managed Disk](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/create-vm-specialized)

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

---

### Appendix A: Quick Reference Commands

**Export Snapshot to SAS URL:**
```bash
az snapshot grant-access -g <RG> -n <SNAP> --duration-in-seconds 86400 --access-level Read -o tsv
```

**AzCopy Transfer:**
```bash
azcopy copy "<SOURCE_SAS>" "<DEST_URL>?<DEST_SAS>" --blob-type PageBlob
```

**Create Disk from VHD:**
```bash
az disk create -g <RG> -n <DISK> --source "<VHD_URL>" --os-type Windows --sku Premium_LRS
```

**Create VM from Disk:**
```bash
az vm create -g <RG> -n <VM> --attach-os-disk <DISK_ID> --os-type Windows
```

### Appendix B: Estimated Transfer Times

| VHD Size | ~Transfer Time (100 Mbps) | ~Transfer Time (1 Gbps) |
|----------|---------------------------|-------------------------|
| 30 GB | 40 minutes | 4 minutes |
| 128 GB | 3 hours | 17 minutes |
| 512 GB | 12 hours | 70 minutes |
| 1 TB | 24 hours | 2.5 hours |

*Times vary based on network conditions and Azure region proximity*
