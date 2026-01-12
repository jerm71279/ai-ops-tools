#!/bin/bash
# ===========================
# Rebuild SETCO-DC02 - Final Workflow
# OS Disk: Created from vendor VHD (via SAS URL)
# Data Disk: Created from snapshot after robocopy sync to FS
# Created: 2025-11-17
# ===========================

set -e  # Exit on any error

# ===========================
# VARIABLES - Configure These
# ===========================

# Resource Group & Location
RESOURCE_GROUP="DataCenter"
LOCATION="eastus"

# VM Configuration
VM_NAME="SETCO-DC02"
VM_SIZE="Standard_D4s_v5"
ZONE="3"

# NEW Disk Names (will be created)
OS_DISK_NAME="${VM_NAME}_OsDisk_NEW"
DATA_DISK_NAME="${VM_NAME}_DataDisk_NEW"

# Disk Configuration
OS_DISK_SKU="Premium_LRS"
DATA_DISK_SKU="Premium_LRS"

# ===========================
# SOURCE CONFIGURATION
# ===========================

# OS DISK SOURCE: VHD from vendor (set this after vendor provides SAS URL)
# Example: "https://vendorstorage.blob.core.windows.net/vhds/setco-dc-os.vhd?sp=r&st=..."
OS_VHD_URL=""

# DATA DISK SOURCE: Snapshot name (create snapshot from FS F: drive first)
# Example: "SETCO-DC02-Data-Snapshot-2025-11-23"
DATA_SNAPSHOT_NAME=""

# Network Configuration
TARGET_VNET="DataCenter_vNet"
TARGET_SUBNET="DataCenter_Subnet"
NIC_NAME="${VM_NAME}-nic"

# Static IP (optional - leave empty for dynamic)
STATIC_PRIVATE_IP=""

# OS Type
OS_TYPE="Windows"

echo "========================================"
echo "SETCO-DC02 VM Rebuild - Final Workflow"
echo "========================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "VM Name: $VM_NAME"
echo "VM Size: $VM_SIZE"
echo "Zone: $ZONE"
echo ""
echo "OS Disk Source: VHD from vendor"
echo "Data Disk Source: Snapshot from FS"
echo "========================================"
echo ""

# ===========================
# PRE-FLIGHT CHECKS
# ===========================
echo "[Pre-flight] Checking prerequisites..."

# Check if OS VHD URL is set
if [ -z "$OS_VHD_URL" ]; then
    echo "  ✗ ERROR: OS_VHD_URL not set!"
    echo "  Please set the OS VHD URL from vendor in the script variables."
    echo "  Example: OS_VHD_URL=\"https://storage.blob.core.windows.net/vhds/os.vhd?sas-token\""
    exit 1
fi

# Check if Data Snapshot name is set
if [ -z "$DATA_SNAPSHOT_NAME" ]; then
    echo "  ✗ ERROR: DATA_SNAPSHOT_NAME not set!"
    echo "  Please create snapshot from FS F: drive first, then set the snapshot name."
    echo ""
    echo "  To create snapshot from FS disk:"
    echo "  1. Identify FS data disk ID (F: drive):"
    echo "     az disk list -g DataCenter --query \"[].{Name:name, Size:diskSizeGb}\" -o table"
    echo ""
    echo "  2. Create snapshot:"
    echo "     az snapshot create -g DataCenter -n SETCO-DC02-Data-Snapshot-\$(date +%Y-%m-%d) \\"
    echo "       --source <FS-DISK-NAME>"
    echo ""
    exit 1
fi

echo "  ✓ OS VHD URL configured"
echo "  ✓ Data snapshot name configured"
echo ""

# ===========================
# Step 1: Verify Resource Group
# ===========================
echo "[Step 1/8] Verifying Resource Group..."
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "  Creating Resource Group..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
    echo "  ✓ Created"
else
    echo "  ✓ Exists"
fi
echo ""

# ===========================
# Step 2: Check for existing VM
# ===========================
echo "[Step 2/8] Checking for existing VM..."
if az vm show --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" &>/dev/null; then
    echo "  ✗ VM '$VM_NAME' already exists!"
    echo "  Please delete it first:"
    echo "  az vm delete -g $RESOURCE_GROUP -n $VM_NAME --yes"
    exit 1
else
    echo "  ✓ VM does not exist"
fi
echo ""

# ===========================
# Step 3: Create OS Disk from VHD
# ===========================
echo "[Step 3/8] Creating OS Disk from vendor VHD..."
echo "  Source: $OS_VHD_URL"

# Check if disk already exists
if az disk show --resource-group "$RESOURCE_GROUP" --name "$OS_DISK_NAME" &>/dev/null; then
    echo "  ! OS Disk '$OS_DISK_NAME' already exists"
    echo "  Skipping creation (delete manually if you want to recreate)"
else
    echo "  Creating disk (this may take 10-20 minutes depending on VHD size)..."

    az disk create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$OS_DISK_NAME" \
        --location "$LOCATION" \
        --sku "$OS_DISK_SKU" \
        --os-type "$OS_TYPE" \
        --source "$OS_VHD_URL" \
        --zone "$ZONE" \
        --output none

    echo "  ✓ OS Disk created from VHD"
fi

OS_DISK_ID=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OS_DISK_NAME" \
    --query id \
    --output tsv)

OS_DISK_SIZE=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OS_DISK_NAME" \
    --query diskSizeGb \
    --output tsv)

echo "  OS Disk ID: $OS_DISK_ID"
echo "  OS Disk Size: ${OS_DISK_SIZE}GB"
echo ""

# ===========================
# Step 4: Verify Data Snapshot Exists
# ===========================
echo "[Step 4/8] Verifying data snapshot..."

if ! az snapshot show --resource-group "$RESOURCE_GROUP" --name "$DATA_SNAPSHOT_NAME" &>/dev/null; then
    echo "  ✗ Snapshot '$DATA_SNAPSHOT_NAME' not found!"
    echo ""
    echo "  Create it first by:"
    echo "  1. Ensure robocopy delta sync completed to FS"
    echo "  2. Identify FS data disk (F: drive):"
    echo "     az disk list -g $RESOURCE_GROUP --query \"[].{Name:name, Size:diskSizeGb}\" -o table"
    echo "  3. Create snapshot:"
    echo "     az snapshot create -g $RESOURCE_GROUP -n $DATA_SNAPSHOT_NAME --source <FS-DISK-NAME>"
    exit 1
fi

SNAPSHOT_SIZE=$(az snapshot show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_SNAPSHOT_NAME" \
    --query diskSizeGb \
    --output tsv)

echo "  ✓ Snapshot found: $DATA_SNAPSHOT_NAME"
echo "  Snapshot size: ${SNAPSHOT_SIZE}GB"
echo ""

# ===========================
# Step 5: Create Data Disk from Snapshot
# ===========================
echo "[Step 5/8] Creating Data Disk from snapshot..."

# Check if disk already exists
if az disk show --resource-group "$RESOURCE_GROUP" --name "$DATA_DISK_NAME" &>/dev/null; then
    echo "  ! Data Disk '$DATA_DISK_NAME' already exists"
    echo "  Skipping creation (delete manually if you want to recreate)"
else
    echo "  Creating disk from snapshot (may take 10-30 minutes)..."

    az disk create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$DATA_DISK_NAME" \
        --location "$LOCATION" \
        --sku "$DATA_DISK_SKU" \
        --source "$DATA_SNAPSHOT_NAME" \
        --zone "$ZONE" \
        --output none

    echo "  ✓ Data Disk created from snapshot"
fi

DATA_DISK_ID=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_DISK_NAME" \
    --query id \
    --output tsv)

DATA_DISK_SIZE=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_DISK_NAME" \
    --query diskSizeGb \
    --output tsv)

echo "  Data Disk ID: $DATA_DISK_ID"
echo "  Data Disk Size: ${DATA_DISK_SIZE}GB"
echo ""

# ===========================
# Step 6: Create Network Interface
# ===========================
echo "[Step 6/8] Creating Network Interface..."

if az network nic show --resource-group "$RESOURCE_GROUP" --name "$NIC_NAME" &>/dev/null; then
    echo "  ! NIC exists, will reuse"
    CURRENT_NIC_IP=$(az network nic show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$NIC_NAME" \
        --query "ipConfigurations[0].privateIpAddress" \
        --output tsv)
    echo "    Current IP: $CURRENT_NIC_IP"
else
    echo "  Creating NIC..."

    NIC_CREATE_CMD="az network nic create \
        --resource-group $RESOURCE_GROUP \
        --name $NIC_NAME \
        --vnet-name $TARGET_VNET \
        --subnet $TARGET_SUBNET"

    if [ -n "$STATIC_PRIVATE_IP" ]; then
        NIC_CREATE_CMD="$NIC_CREATE_CMD --private-ip-address $STATIC_PRIVATE_IP"
    fi

    eval $NIC_CREATE_CMD --output none
    echo "  ✓ NIC created"

    CURRENT_NIC_IP=$(az network nic show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$NIC_NAME" \
        --query "ipConfigurations[0].privateIpAddress" \
        --output tsv)
    echo "    Assigned IP: $CURRENT_NIC_IP"
fi
echo ""

# ===========================
# Step 7: Create VM from OS Disk
# ===========================
echo "[Step 7/8] Creating VM from OS disk..."
echo "  This may take 2-4 minutes..."

az vm create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --attach-os-disk "$OS_DISK_ID" \
    --os-type "$OS_TYPE" \
    --nics "$NIC_NAME" \
    --size "$VM_SIZE" \
    --zone "$ZONE" \
    --output none

echo "  ✓ VM created"
echo ""

# ===========================
# Step 8: Attach Data Disk
# ===========================
echo "[Step 8/8] Attaching data disk..."

az vm disk attach \
    --resource-group "$RESOURCE_GROUP" \
    --vm-name "$VM_NAME" \
    --name "$DATA_DISK_ID" \
    --lun 1 \
    --output none

echo "  ✓ Data disk attached at LUN 1"
echo ""

# ===========================
# Step 9: Set Static IP
# ===========================
echo "[Step 9/8] Setting NIC to static IP..."

FINAL_IP=$(az network nic show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NIC_NAME" \
    --query "ipConfigurations[0].privateIpAddress" \
    --output tsv)

az network nic ip-config update \
    --resource-group "$RESOURCE_GROUP" \
    --nic-name "$NIC_NAME" \
    --name "ipconfig1" \
    --private-ip-address "$FINAL_IP" \
    --output none

echo "  ✓ IP set to static: $FINAL_IP"
echo ""

# ===========================
# VERIFICATION
# ===========================
echo "========================================"
echo "✓ VM REBUILD COMPLETE!"
echo "========================================"
echo ""

echo "VM Details:"
az vm show -g "$RESOURCE_GROUP" -n "$VM_NAME" \
    --query "{Name:name, Size:hardwareProfile.vmSize, Zone:zones[0]}" \
    -o table
echo ""

echo "Network:"
echo "  Private IP: $FINAL_IP (Static)"
echo ""

echo "Disks:"
echo "  OS Disk: $OS_DISK_NAME (${OS_DISK_SIZE}GB) - From vendor VHD"
echo "  Data Disk: $DATA_DISK_NAME (${DATA_DISK_SIZE}GB) - From FS snapshot"
echo ""

echo "========================================"
echo "NEXT STEPS:"
echo "========================================"
echo ""
echo "1. Start the VM:"
echo "   az vm start -g $RESOURCE_GROUP -n $VM_NAME"
echo ""
echo "2. Monitor boot (if issues):"
echo "   az vm boot-diagnostics get-boot-log -g $RESOURCE_GROUP -n $VM_NAME"
echo ""
echo "3. Connect via RDP:"
echo "   Private IP: $FINAL_IP"
echo ""
echo "4. After login, verify:"
echo "   - C: drive = OS (${OS_DISK_SIZE}GB)"
echo "   - F: drive = Data (${DATA_DISK_SIZE}GB) with robocopy data"
echo "   - AD services running: Get-Service NTDS,DNS,Netlogon"
echo "   - Domain: Get-ADDomain"
echo ""
echo "5. Run file share recreation scripts:"
echo "   - 2-Set-NTFS-Permissions-F-Drive.ps1"
echo "   - 3-Create-SMB-Shares-F-Drive.ps1"
echo "   - 4-Validate-Configuration-F-Drive.ps1"
echo ""
echo "========================================"
echo "Workflow Summary:"
echo "========================================"
echo "✓ Vendor provided OS VHD → Created OS managed disk"
echo "✓ You ran robocopy to FS → Created snapshot → Created data disk"
echo "✓ VM built with both disks"
echo "✓ Ready to start and configure"
echo "========================================"
