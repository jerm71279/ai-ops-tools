# Setco DC Migration - VHD & Data Sync Plan
## Azure Tenant to Tenant Migration Using VHD Copy Method

---

## Migration Strategy Overview

**Approach:** Copy VHD files from source tenant to destination tenant, then build VMs

### Components:
1. **OS Disk VHD** - Domain Controller OS and configuration
2. **Data Disk VHD** - F:\ drive with file shares (synced with Robocopy first)

### Steps:
1. Sync data from source to file server using Robocopy
2. Create VHD snapshot of data disk
3. Copy VHD to destination Azure tenant
4. Build new VMs from VHDs in new tenant
5. Reconfigure and validate

---

## Phase 1: Pre-Migration Data Sync

### 1.1 Prepare File Server for Data Sync
- [ ] Identify file server to receive data sync
  - Server name: _____________________
  - IP address: _____________________
  - Available disk space: _____________________

- [ ] Verify network connectivity between source DC and file server
- [ ] Test write permissions on file server destination
- [ ] Create destination folder structure on file server:
  ```
  \\FileServer\MigrationStaging\
    ├── FTP Data\
    ├── HomeDirs\
    ├── PostClosing\
    ├── Qbooks\
    ├── SeaCrestScans\
    ├── SetcoDocs\
    ├── Versacheck\
    ├── Whole Life Fitness\
    └── NTSYS\worddocs\
  ```

### 1.2 Initial Robocopy Data Sync
Run Robocopy from source DC to file server for initial sync:

**Recommended Robocopy Command:**
```cmd
robocopy "E:\SourceFolder" "\\FileServer\MigrationStaging\SourceFolder" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\robocopy_initial.log /TEE /NP /NDL
```

**Parameters Explained:**
- `/E` - Copy subdirectories, including empty ones
- `/COPYALL` - Copy all file info (data, attributes, timestamps, NTFS ACLs, owner info, auditing info)
- `/DCOPY:T` - Copy directory timestamps
- `/R:3` - Retry 3 times on failed copies
- `/W:10` - Wait 10 seconds between retries
- `/MT:16` - Multi-threaded copy (16 threads - adjust based on network/CPU)
- `/LOG:` - Output log file location
- `/TEE` - Output to console and log file
- `/NP` - No progress percentage (cleaner logs)
- `/NDL` - No directory list (reduces log size)

### 1.3 Sync Each Share Individually

- [ ] **FTP Data**
  ```cmd
  robocopy "E:\FTP Data" "\\FileServer\MigrationStaging\FTP Data" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\FTPData_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **HomeDirs**
  ```cmd
  robocopy "E:\HomeDirs" "\\FileServer\MigrationStaging\HomeDirs" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:8 /LOG:C:\Logs\HomeDirs_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **PostClosing**
  ```cmd
  robocopy "E:\PostClosing" "\\FileServer\MigrationStaging\PostClosing" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\PostClosing_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **Qbooks** (Critical - QuickBooks data)
  ```cmd
  robocopy "E:\Qbooks" "\\FileServer\MigrationStaging\Qbooks" /E /COPYALL /DCOPY:T /R:5 /W:15 /MT:8 /LOG:C:\Logs\Qbooks_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________
  - **IMPORTANT:** Close QuickBooks on all workstations before sync

- [ ] **SeaCrestScans**
  ```cmd
  robocopy "E:\SeaCrestScans" "\\FileServer\MigrationStaging\SeaCrestScans" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\SeaCrestScans_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **SetcoDocs**
  ```cmd
  robocopy "E:\SetcoDocs" "\\FileServer\MigrationStaging\SetcoDocs" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\SetcoDocs_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **Versacheck**
  ```cmd
  robocopy "E:\Versacheck" "\\FileServer\MigrationStaging\Versacheck" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\Versacheck_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **Whole Life Fitness**
  ```cmd
  robocopy "E:\Whole Life Fitness" "\\FileServer\MigrationStaging\Whole Life Fitness" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\WholeLifeFitness_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

- [ ] **NTSYS\worddocs**
  ```cmd
  robocopy "E:\NTSYS\worddocs" "\\FileServer\MigrationStaging\NTSYS\worddocs" /E /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\worddocs_initial.log /TEE
  ```
  - Start time: _______________
  - End time: _______________
  - Files copied: _______________
  - Total size: _______________
  - Errors: _______________

### 1.4 Verify Initial Sync
- [ ] Review all Robocopy log files for errors
- [ ] Check file counts match source
- [ ] Verify total data size matches
- [ ] Spot-check files opened successfully
- [ ] Verify permissions were copied (check ACLs)
- [ ] Test file access on file server
- [ ] Document any errors or skipped files

### 1.5 Delta Sync (Incremental Updates)

**Schedule delta syncs until final cutover:**

**Delta Sync Command (adds /MIR for mirror):**
```cmd
robocopy "E:\SourceFolder" "\\FileServer\MigrationStaging\SourceFolder" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG+:C:\Logs\robocopy_delta_DATE.log /TEE
```

**Delta Sync Schedule:**
- [ ] Delta sync #1 - Date: _____________ Time: _____________
- [ ] Delta sync #2 - Date: _____________ Time: _____________
- [ ] Delta sync #3 - Date: _____________ Time: _____________
- [ ] Final sync (during cutover) - Date: _____________ Time: _____________

**Note:** `/MIR` mirrors the directories (adds deletions). Use with caution!

---

## Phase 2: Prepare Source VHDs for Export

### 2.1 Source DC Preparation
- [ ] Stop all non-essential services on source DC
- [ ] Close all open file handles: `openfiles /query`
- [ ] Run final delta sync with Robocopy
- [ ] Flush DNS cache: `ipconfig /flushdns`
- [ ] Clear temp files and logs
- [ ] Run disk cleanup
- [ ] Defragment disks (if time permits)
- [ ] Take final backup of source DC
- [ ] Document current DC configuration:
  - IP address: _____________________
  - Hostname: _____________________
  - FSMO roles: _____________________
  - DNS settings: _____________________

### 2.2 Shutdown Source DC for VHD Capture
- [ ] Schedule maintenance window
- [ ] Notify all users of downtime
- [ ] Disable user logins (optional): `shutdown /l`
- [ ] Stop Active Directory services (or leave running for live capture)
- [ ] Flush all disk caches
- [ ] **Graceful shutdown:**
  ```cmd
  shutdown /s /t 60 /c "Shutting down for VHD export"
  ```

### 2.3 Create Snapshots in Source Azure Tenant
- [ ] Navigate to source Azure Portal
- [ ] Go to source VM: _____________________
- [ ] Stop the VM (deallocate)
- [ ] Create snapshot of **OS Disk**:
  - Snapshot name: DC-OS-Snapshot-[DATE]
  - Resource group: _____________________
  - Snapshot type: Full
  - Storage type: Standard HDD (cheaper for transfer)
  - [ ] Wait for snapshot completion

- [ ] Create snapshot of **Data Disk (E:\ or current data drive)**:
  - Snapshot name: DC-Data-Snapshot-[DATE]
  - Resource group: _____________________
  - Snapshot type: Full
  - Storage type: Standard HDD
  - [ ] Wait for snapshot completion

### 2.4 Export Snapshots to Storage Account
- [ ] Create Azure Storage Account in source tenant (if not exists):
  - Name: setcomigration[unique]
  - Performance: Standard
  - Replication: LRS (cheapest)
  - [ ] Create blob container: `vhd-export`

- [ ] Generate SAS URL for OS disk snapshot:
  - [ ] Navigate to OS snapshot
  - [ ] Click "Export"
  - [ ] Generate SAS URL (valid for 24-48 hours)
  - [ ] Copy SAS URL: _____________________

- [ ] Generate SAS URL for Data disk snapshot:
  - [ ] Navigate to Data snapshot
  - [ ] Click "Export"
  - [ ] Generate SAS URL (valid for 24-48 hours)
  - [ ] Copy SAS URL: _____________________

- [ ] Download VHDs using AzCopy (recommended):
  ```powershell
  # Download OS VHD
  azcopy copy "OS_SNAPSHOT_SAS_URL" "C:\VHD-Export\DC-OS.vhd"

  # Download Data VHD
  azcopy copy "DATA_SNAPSHOT_SAS_URL" "C:\VHD-Export\DC-Data.vhd"
  ```
  - OS VHD size: _______________ GB
  - Data VHD size: _______________ GB
  - Download time: _______________

---

## Phase 3: Transfer VHDs to Destination Azure Tenant

### 3.1 Prepare Destination Azure Tenant
- [ ] Log into destination Azure Portal
- [ ] Create Resource Group:
  - Name: RG-Setco-DC-Migration
  - Region: _____________________

- [ ] Create Storage Account in destination tenant:
  - Name: setcodestination[unique]
  - Performance: Standard (or Premium for better performance)
  - Replication: LRS
  - Region: Same as where DC will be deployed
  - [ ] Create blob container: `vhd-import`

### 3.2 Upload VHDs to Destination Storage Account

**Option A: Direct Upload via AzCopy (Recommended)**
```powershell
# Upload OS VHD
azcopy copy "C:\VHD-Export\DC-OS.vhd" "https://setcodestination.blob.core.windows.net/vhd-import/DC-OS.vhd?[SAS_TOKEN]"

# Upload Data VHD
azcopy copy "C:\VHD-Export\DC-Data.vhd" "https://setcodestination.blob.core.windows.net/vhd-import/DC-Data.vhd?[SAS_TOKEN]"
```

**Option B: Azure Portal Upload (Slower)**
- [ ] Navigate to storage account → Containers → vhd-import
- [ ] Upload DC-OS.vhd
- [ ] Upload DC-Data.vhd

**Upload Progress:**
- [ ] OS VHD upload started: _______________
- [ ] OS VHD upload completed: _______________
- [ ] Data VHD upload started: _______________
- [ ] Data VHD upload completed: _______________

### 3.3 Verify VHD Integrity
- [ ] Check OS VHD file size matches source
- [ ] Check Data VHD file size matches source
- [ ] Verify MD5 checksum (if available)
- [ ] Verify blobs are visible in Azure Portal

---

## Phase 4: Create Managed Disks from VHDs

### 4.1 Create OS Managed Disk
- [ ] Navigate to Azure Portal → Disks → Create
- [ ] Source type: Storage blob
- [ ] Browse to: vhd-import/DC-OS.vhd
- [ ] Disk settings:
  - Name: DC-NewTenant-OS-Disk
  - Resource group: RG-Setco-DC-Migration
  - Region: _____________________
  - Disk type: Premium SSD (recommended for DC)
  - Size: _____ GB (auto-detected from VHD)
- [ ] Create disk
- [ ] Wait for completion

### 4.2 Create Data Managed Disk
- [ ] Navigate to Azure Portal → Disks → Create
- [ ] Source type: Storage blob
- [ ] Browse to: vhd-import/DC-Data.vhd
- [ ] Disk settings:
  - Name: DC-NewTenant-Data-Disk
  - Resource group: RG-Setco-DC-Migration
  - Region: _____________________ (same as OS disk)
  - Disk type: Standard SSD or Premium SSD
  - Size: _____ GB (auto-detected from VHD)
- [ ] Create disk
- [ ] Wait for completion

---

## Phase 5: Build New DC VMs from VHDs

### 5.1 Create Virtual Network Infrastructure
- [ ] Create Virtual Network:
  - Name: VNet-Setco-DC
  - Address space: 10.0.0.0/16 (example)
  - Subnet: DC-Subnet (10.0.1.0/24)
  - Region: _____________________

- [ ] Create Network Security Group:
  - Name: NSG-DC
  - Inbound rules:
    - [ ] RDP (3389) from management IPs only
    - [ ] DNS (53) from VNet
    - [ ] LDAP (389, 636) from VNet
    - [ ] Kerberos (88) from VNet
    - [ ] SMB (445) from VNet
    - [ ] RPC (135, dynamic) from VNet

### 5.2 Create VM from OS Disk

- [ ] Navigate to Azure Portal → Virtual Machines → Create
- [ ] **Basics:**
  - Resource group: RG-Setco-DC-Migration
  - VM name: DC-Setco-NewTenant
  - Region: _____________________ (same as disks)
  - Availability: No infrastructure redundancy (single DC initially)
  - Security type: Standard
  - Image: "Attach an existing disk" - NOT AVAILABLE IN WIZARD

**IMPORTANT: You cannot directly create VM from managed disk in portal wizard!**

**Use PowerShell or CLI Instead:**

```powershell
# Set variables
$resourceGroup = "RG-Setco-DC-Migration"
$location = "eastus"  # Change to your region
$vmName = "DC-Setco-NewTenant"
$vmSize = "Standard_D2s_v3"  # 2 vCPU, 8GB RAM
$osDiskName = "DC-NewTenant-OS-Disk"
$dataDiskName = "DC-NewTenant-Data-Disk"
$vnetName = "VNet-Setco-DC"
$subnetName = "DC-Subnet"
$nsgName = "NSG-DC"

# Get the managed disks
$osDisk = Get-AzDisk -ResourceGroupName $resourceGroup -DiskName $osDiskName
$dataDisk = Get-AzDisk -ResourceGroupName $resourceGroup -DiskName $dataDiskName

# Create network interface
$vnet = Get-AzVirtualNetwork -Name $vnetName -ResourceGroupName $resourceGroup
$subnet = Get-AzVirtualNetworkSubnetConfig -Name $subnetName -VirtualNetwork $vnet
$nsg = Get-AzNetworkSecurityGroup -Name $nsgName -ResourceGroupName $resourceGroup

$nicName = "$vmName-NIC"
$pip = New-AzPublicIpAddress -Name "$vmName-PIP" -ResourceGroupName $resourceGroup -Location $location -AllocationMethod Static
$nic = New-AzNetworkInterface -Name $nicName -ResourceGroupName $resourceGroup -Location $location -SubnetId $subnet.Id -PublicIpAddressId $pip.Id -NetworkSecurityGroupId $nsg.Id

# Set static private IP (important for DC)
$nic.IpConfigurations[0].PrivateIpAllocationMethod = "Static"
$nic.IpConfigurations[0].PrivateIpAddress = "10.0.1.4"  # Choose your IP
Set-AzNetworkInterface -NetworkInterface $nic

# Create VM configuration
$vmConfig = New-AzVMConfig -VMName $vmName -VMSize $vmSize

# Attach OS disk
$vmConfig = Set-AzVMOSDisk -VM $vmConfig -ManagedDiskId $osDisk.Id -CreateOption Attach -Windows

# Attach data disk
$vmConfig = Add-AzVMDataDisk -VM $vmConfig -ManagedDiskId $dataDisk.Id -Lun 0 -CreateOption Attach

# Add network interface
$vmConfig = Add-AzVMNetworkInterface -VM $vmConfig -Id $nic.Id

# Create the VM
New-AzVM -ResourceGroupName $resourceGroup -Location $location -VM $vmConfig
```

- [ ] Execute PowerShell script
- [ ] Wait for VM creation (5-10 minutes)
- [ ] Verify VM is created
- [ ] Note VM IP address: _____________________

### 5.3 Initial VM Startup and Validation

- [ ] Start the VM from Azure Portal
- [ ] Wait for VM to fully boot (5-10 minutes)
- [ ] Connect via RDP using public IP or Bastion
  - Public IP: _____________________
  - Username: _____________________ (from original DC)
  - Password: _____________________ (from original DC)

- [ ] **First Login Checks:**
  - [ ] VM boots successfully
  - [ ] Windows loads without errors
  - [ ] Can log in with domain admin account
  - [ ] Check Event Viewer for boot errors
  - [ ] Verify C:\ drive is accessible
  - [ ] Verify data disk appears (may need to be brought online)

### 5.4 Configure Data Disk (F:\)

- [ ] Open Disk Management (`diskmgmt.msc`)
- [ ] Check if data disk is online
  - If offline: Right-click → Online
- [ ] Verify drive letter assignment
  - If not F:\: Right-click volume → Change Drive Letter → F:
- [ ] Verify all folders are accessible:
  - [ ] F:\FTP Data
  - [ ] F:\HomeDirs
  - [ ] F:\PostClosing
  - [ ] F:\Qbooks
  - [ ] F:\SeaCrestScans
  - [ ] F:\SetcoDocs
  - [ ] F:\Versacheck
  - [ ] F:\Whole Life Fitness
  - [ ] F:\NTSYS\worddocs

- [ ] Check disk health:
  ```powershell
  Get-PhysicalDisk
  Get-Volume
  chkdsk F: /scan
  ```

---

## Phase 6: Sync Latest Data to New DC

### 6.1 Copy Data from File Server to New DC F:\ Drive

Now copy the data from your file server staging area to the new DC's F:\ drive:

```powershell
# Run from new DC, pulling from file server
robocopy "\\FileServer\MigrationStaging\FTP Data" "F:\FTP Data" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\FTPData_final.log /TEE

robocopy "\\FileServer\MigrationStaging\HomeDirs" "F:\HomeDirs" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:8 /LOG:C:\Logs\HomeDirs_final.log /TEE

robocopy "\\FileServer\MigrationStaging\PostClosing" "F:\PostClosing" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\PostClosing_final.log /TEE

robocopy "\\FileServer\MigrationStaging\Qbooks" "F:\Qbooks" /MIR /COPYALL /DCOPY:T /R:5 /W:15 /MT:8 /LOG:C:\Logs\Qbooks_final.log /TEE

robocopy "\\FileServer\MigrationStaging\SeaCrestScans" "F:\SeaCrestScans" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\SeaCrestScans_final.log /TEE

robocopy "\\FileServer\MigrationStaging\SetcoDocs" "F:\SetcoDocs" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\SetcoDocs_final.log /TEE

robocopy "\\FileServer\MigrationStaging\Versacheck" "F:\Versacheck" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\Versacheck_final.log /TEE

robocopy "\\FileServer\MigrationStaging\Whole Life Fitness" "F:\Whole Life Fitness" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\WholeLifeFitness_final.log /TEE

robocopy "\\FileServer\MigrationStaging\NTSYS\worddocs" "F:\NTSYS\worddocs" /MIR /COPYALL /DCOPY:T /R:3 /W:10 /MT:16 /LOG:C:\Logs\worddocs_final.log /TEE
```

**Sync Progress:**
- [ ] FTP Data - Completed: _______________
- [ ] HomeDirs - Completed: _______________
- [ ] PostClosing - Completed: _______________
- [ ] Qbooks - Completed: _______________
- [ ] SeaCrestScans - Completed: _______________
- [ ] SetcoDocs - Completed: _______________
- [ ] Versacheck - Completed: _______________
- [ ] Whole Life Fitness - Completed: _______________
- [ ] NTSYS\worddocs - Completed: _______________

### 6.2 Verify Data Integrity
- [ ] Review all Robocopy logs for errors
- [ ] Compare file counts: source vs. file server vs. new DC
- [ ] Verify total size matches
- [ ] Spot-check files can be opened
- [ ] Verify permissions are intact: `Get-Acl F:\HomeDirs | fl`
- [ ] Check for any access denied errors

---

## Phase 7: Reconfigure New DC

### 7.1 Network Configuration
- [ ] Set static IP address (if not already set)
  - IP: _____________________
  - Subnet: _____________________
  - Gateway: _____________________
- [ ] Set DNS to point to itself (127.0.0.1 or own IP)
- [ ] Verify network connectivity
- [ ] Test internet connectivity
- [ ] Configure Windows Firewall for DC traffic

### 7.2 Active Directory Validation
- [ ] Check AD services are running:
  ```powershell
  Get-Service NTDS, DNS, Netlogon, W32Time
  ```
- [ ] Verify domain: `Get-ADDomain`
- [ ] Check FSMO roles: `netdom query fsmo`
- [ ] Verify SYSVOL and NETLOGON shares exist
- [ ] Test user authentication
- [ ] Run `dcdiag /v` and review output
- [ ] Check DNS zones are present
- [ ] Verify SRV records exist

### 7.3 File Share Recreation
- [ ] Run file share migration scripts from C:\ps1:
  ```powershell
  cd C:\ps1
  .\1-Setup-Directories-F-Drive.ps1  # Should show "already exists"
  .\2-Set-NTFS-Permissions-F-Drive.ps1  # Re-apply permissions
  .\3-Create-SMB-Shares-F-Drive.ps1  # Create shares
  .\4-Validate-Configuration-F-Drive.ps1  # Validate
  ```

- [ ] Verify all shares created: `Get-SmbShare`
- [ ] Test share access from another machine
- [ ] Verify permissions work correctly

---

## Phase 8: Testing & Validation

### 8.1 DC Functionality Tests
- [ ] Test DNS resolution: `nslookup SouthernEscrow.com`
- [ ] Test user authentication from client
- [ ] Verify group policy application
- [ ] Test file share access
- [ ] Verify time synchronization
- [ ] Check AD replication (if multiple DCs)
- [ ] Test LDAP connectivity: `ldp.exe`
- [ ] Verify Kerberos: `klist tickets`

### 8.2 File Share Access Tests
- [ ] Test access to each share from client PC
- [ ] Verify read permissions
- [ ] Verify write permissions
- [ ] Test with different user accounts
- [ ] Verify QuickBooks can access Qbooks share
- [ ] Test application data access
- [ ] Verify printer shares (if configured)

---

## Phase 9: Cutover & Go-Live

### 9.1 Pre-Cutover
- [ ] Schedule cutover window
- [ ] Notify all users
- [ ] Take final backups
- [ ] Snapshot new DC VM
- [ ] Prepare rollback plan

### 9.2 Cutover
- [ ] Update DNS settings for clients
- [ ] Update DHCP to provide new DC IP
- [ ] Monitor user logins
- [ ] Verify services are operational
- [ ] Monitor for errors

### 9.3 Post-Cutover
- [ ] Monitor for 24-48 hours
- [ ] Address any issues
- [ ] Decommission old DC (after 2+ weeks)
- [ ] Update documentation
- [ ] Close migration project

---

## Robocopy Tips & Best Practices

### Recommended Robocopy Switches
```
/E          Copy subdirectories, including empty ones
/COPYALL    Copy ALL file info (equivalent to /COPY:DATSOU)
/DCOPY:T    Copy directory timestamps
/MIR        Mirror directory tree (use for delta syncs)
/R:3        Retry 3 times on failed copies
/W:10       Wait 10 seconds between retries
/MT:16      Multi-threaded copy with 16 threads
/LOG:file   Output log to file
/LOG+:file  Append to existing log file
/TEE        Output to console and log file
/NP         No progress - don't display percentage
/NDL        No directory listing
/NFL        No file listing (reduces log size)
/XO         Exclude older files (only copy newer)
/XX D       Exclude extra directories (in destination)
/XF file    Exclude files matching pattern
/XD dir     Exclude directories matching pattern
```

### Monitoring Robocopy Progress
```powershell
# View last 50 lines of log in real-time
Get-Content C:\Logs\robocopy.log -Tail 50 -Wait

# Count files copied
(Get-Content C:\Logs\robocopy.log | Select-String "New File").Count
```

### Robocopy Exit Codes
- 0 = No files copied
- 1 = Files copied successfully
- 2 = Extra files or directories detected
- 4 = Mismatched files or directories
- 8 = Copy errors occurred
- 16 = Fatal error

---

## Emergency Contacts & Escalation

| Role | Name | Contact |
|------|------|---------|
| Azure Administrator | _____________ | _____________ |
| Network Administrator | _____________ | _____________ |
| File Server Administrator | _____________ | _____________ |
| Microsoft Support | _____________ | 1-800-MSFT |

---

## Notes & Issues

| Date | Issue | Resolution |
|------|-------|------------|
|  |  |  |
|  |  |  |

---

**Plan Version:** 1.0
**Created:** 2025-11-17
**Last Updated:** _____________
**Next Review:** After Phase 1 Completion
