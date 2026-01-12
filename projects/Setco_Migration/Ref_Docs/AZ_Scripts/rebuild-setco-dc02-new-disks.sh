#!/bin/bash
# ===========================
# Rebuild SETCO-DC02 with NEW Disks
# Creates fresh managed disks from VHD/snapshots
# Created: 2025-11-17
# ===========================

set -e  # Exit on any error

# ===========================
# VARIABLES - All Defined
# ===========================

# Resource Group & Location
RESOURCE_GROUP="DataCenter"
LOCATION="eastus"  # Change to match your resource group location

# VM Configuration
VM_NAME="SETCO-DC02"
VM_SIZE="Standard_D4s_v5"
ZONE="3"

# NEW Disk Names (will be created)
OS_DISK_NAME="${VM_NAME}_OsDisk_NEW"
DATA_DISK_NAME="${VM_NAME}_DataDisk_NEW"

# Disk Configuration
OS_DISK_SIZE_GB="512"      # OS disk size
DATA_DISK_SIZE_GB="1024"   # Data disk size (1TB)
OS_DISK_SKU="Premium_LRS"  # Premium_LRS or StandardSSD_LRS
DATA_DISK_SKU="Premium_LRS"

# SOURCE for disks (choose ONE method below)
# METHOD 1: Create from VHD blob
OS_VHD_URL=""  # Leave empty if creating from snapshot instead
DATA_VHD_URL=""

# METHOD 2: Create from snapshot
OS_SNAPSHOT_NAME=""  # e.g., "SETCO-DC02-OS-Snapshot"
DATA_SNAPSHOT_NAME=""  # e.g., "SETCO-DC02-Data-Snapshot"

# Network Configuration
TARGET_VNET="DataCenter_vNet"
TARGET_SUBNET="DataCenter_Subnet"
NIC_NAME="${VM_NAME}-nic-new"

# Static IP (optional - set if you need specific IP, e.g., "10.0.1.10")
STATIC_PRIVATE_IP=""

# OS Type
OS_TYPE="Windows"

echo "========================================"
echo "SETCO-DC02 VM Rebuild with NEW Disks"
echo "========================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "VM Name: $VM_NAME"
echo "VM Size: $VM_SIZE"
echo "Zone: $ZONE"
echo "NEW OS Disk: $OS_DISK_NAME (${OS_DISK_SIZE_GB}GB)"
echo "NEW Data Disk: $DATA_DISK_NAME (${DATA_DISK_SIZE_GB}GB)"
echo "VNet: $TARGET_VNET"
echo "Subnet: $TARGET_SUBNET"
echo "========================================"
echo ""

# ===========================
# Step 1: Verify Resource Group exists
# ===========================
echo "[Step 1/8] Verifying Resource Group..."
if az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "  ✓ Resource Group '$RESOURCE_GROUP' exists"
else
    echo "  Creating Resource Group '$RESOURCE_GROUP' in $LOCATION..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
    echo "  ✓ Resource Group created"
fi
echo ""

# ===========================
# Step 2: Delete OLD VM if exists
# ===========================
echo "[Step 2/8] Checking for existing VM..."
if az vm show --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" &>/dev/null; then
    echo "  ! VM '$VM_NAME' exists - will be deleted"
    read -p "  Delete existing VM? (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        echo "  Deleting VM (keeping disks)..."
        az vm delete --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" --yes --output none
        echo "  ✓ VM deleted"
    else
        echo "  Aborted by user"
        exit 1
    fi
else
    echo "  ✓ VM does not exist"
fi
echo ""

# ===========================
# Step 3: Create NEW OS Disk
# ===========================
echo "[Step 3/8] Creating NEW OS Disk..."

# Check if disk already exists
if az disk show --resource-group "$RESOURCE_GROUP" --name "$OS_DISK_NAME" &>/dev/null; then
    echo "  ! OS Disk '$OS_DISK_NAME' already exists"
    read -p "  Delete and recreate? (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        az disk delete --resource-group "$RESOURCE_GROUP" --name "$OS_DISK_NAME" --yes --output none
        echo "  Old disk deleted"
    else
        echo "  Using existing disk"
        OS_DISK_CREATED=false
    fi
fi

if [ "${OS_DISK_CREATED:-true}" != "false" ]; then
    # Build OS disk create command
    OS_DISK_CMD="az disk create \
        --resource-group $RESOURCE_GROUP \
        --name $OS_DISK_NAME \
        --location $LOCATION \
        --sku $OS_DISK_SKU \
        --os-type $OS_TYPE"

    # Add zone if specified
    if [ -n "$ZONE" ]; then
        OS_DISK_CMD="$OS_DISK_CMD --zone $ZONE"
    fi

    # Add source (VHD or Snapshot)
    if [ -n "$OS_VHD_URL" ]; then
        echo "  Creating from VHD: $OS_VHD_URL"
        OS_DISK_CMD="$OS_DISK_CMD --source \"$OS_VHD_URL\""
    elif [ -n "$OS_SNAPSHOT_NAME" ]; then
        echo "  Creating from Snapshot: $OS_SNAPSHOT_NAME"
        OS_DISK_CMD="$OS_DISK_CMD --source $OS_SNAPSHOT_NAME"
    else
        echo "  Creating empty disk (${OS_DISK_SIZE_GB}GB)"
        OS_DISK_CMD="$OS_DISK_CMD --size-gb $OS_DISK_SIZE_GB"
    fi

    # Execute
    eval $OS_DISK_CMD --output none
    echo "  ✓ OS Disk created"
fi

# Get OS Disk ID
OS_DISK_ID=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OS_DISK_NAME" \
    --query id \
    --output tsv)
echo "  OS Disk ID: $OS_DISK_ID"
echo ""

# ===========================
# Step 4: Create NEW Data Disk
# ===========================
echo "[Step 4/8] Creating NEW Data Disk..."

# Check if disk already exists
if az disk show --resource-group "$RESOURCE_GROUP" --name "$DATA_DISK_NAME" &>/dev/null; then
    echo "  ! Data Disk '$DATA_DISK_NAME' already exists"
    read -p "  Delete and recreate? (yes/no): " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        az disk delete --resource-group "$RESOURCE_GROUP" --name "$DATA_DISK_NAME" --yes --output none
        echo "  Old disk deleted"
    else
        echo "  Using existing disk"
        DATA_DISK_CREATED=false
    fi
fi

if [ "${DATA_DISK_CREATED:-true}" != "false" ]; then
    # Build data disk create command
    DATA_DISK_CMD="az disk create \
        --resource-group $RESOURCE_GROUP \
        --name $DATA_DISK_NAME \
        --location $LOCATION \
        --sku $DATA_DISK_SKU"

    # Add zone if specified
    if [ -n "$ZONE" ]; then
        DATA_DISK_CMD="$DATA_DISK_CMD --zone $ZONE"
    fi

    # Add source (VHD or Snapshot)
    if [ -n "$DATA_VHD_URL" ]; then
        echo "  Creating from VHD: $DATA_VHD_URL"
        DATA_DISK_CMD="$DATA_DISK_CMD --source \"$DATA_VHD_URL\""
    elif [ -n "$DATA_SNAPSHOT_NAME" ]; then
        echo "  Creating from Snapshot: $DATA_SNAPSHOT_NAME"
        DATA_DISK_CMD="$DATA_DISK_CMD --source $DATA_SNAPSHOT_NAME"
    else
        echo "  Creating empty disk (${DATA_DISK_SIZE_GB}GB)"
        DATA_DISK_CMD="$DATA_DISK_CMD --size-gb $DATA_DISK_SIZE_GB"
    fi

    # Execute
    eval $DATA_DISK_CMD --output none
    echo "  ✓ Data Disk created"
fi

# Get Data Disk ID
DATA_DISK_ID=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_DISK_NAME" \
    --query id \
    --output tsv)
echo "  Data Disk ID: $DATA_DISK_ID"
echo ""

# ===========================
# Step 5: Create Network Interface
# ===========================
echo "[Step 5/8] Creating Network Interface..."

# Check if NIC exists
if az network nic show --resource-group "$RESOURCE_GROUP" --name "$NIC_NAME" &>/dev/null; then
    echo "  ! NIC '$NIC_NAME' already exists"
    CURRENT_NIC_IP=$(az network nic show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$NIC_NAME" \
        --query "ipConfigurations[0].privateIpAddress" \
        --output tsv)
    echo "    - Current IP: $CURRENT_NIC_IP"
    echo "  Will reuse existing NIC"
else
    echo "  Creating new NIC..."

    # Build NIC create command
    NIC_CREATE_CMD="az network nic create \
        --resource-group $RESOURCE_GROUP \
        --name $NIC_NAME \
        --vnet-name $TARGET_VNET \
        --subnet $TARGET_SUBNET"

    # Add static IP if specified
    if [ -n "$STATIC_PRIVATE_IP" ]; then
        NIC_CREATE_CMD="$NIC_CREATE_CMD --private-ip-address $STATIC_PRIVATE_IP"
        echo "    - Assigning static IP: $STATIC_PRIVATE_IP"
    fi

    eval $NIC_CREATE_CMD --output none
    echo "  ✓ NIC created"

    CURRENT_NIC_IP=$(az network nic show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$NIC_NAME" \
        --query "ipConfigurations[0].privateIpAddress" \
        --output tsv)
    echo "    - Assigned IP: $CURRENT_NIC_IP"
fi
echo ""

# ===========================
# Step 6: Create VM from OS Disk
# ===========================
echo "[Step 6/8] Creating VM from OS disk..."
echo "  This may take 2-4 minutes..."

# Build VM create command
VM_CREATE_CMD="az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --attach-os-disk $OS_DISK_ID \
    --os-type $OS_TYPE \
    --nics $NIC_NAME \
    --size $VM_SIZE"

# Add zone if specified
if [ -n "$ZONE" ]; then
    VM_CREATE_CMD="$VM_CREATE_CMD --zone $ZONE"
fi

# Execute VM creation
eval $VM_CREATE_CMD --output none

echo "  ✓ VM created successfully"
echo ""

# ===========================
# Step 7: Attach Data Disk to VM
# ===========================
echo "[Step 7/8] Attaching data disk to VM..."

az vm disk attach \
    --resource-group "$RESOURCE_GROUP" \
    --vm-name "$VM_NAME" \
    --name "$DATA_DISK_ID" \
    --lun 1 \
    --output none

echo "  ✓ Data disk attached at LUN 1"
echo ""

# ===========================
# Step 8: Set NIC IP to Static
# ===========================
echo "[Step 8/8] Setting NIC IP to static..."

FINAL_IP=$(az network nic show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NIC_NAME" \
    --query "ipConfigurations[0].privateIpAddress" \
    --output tsv)

ALLOCATION_METHOD=$(az network nic show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NIC_NAME" \
    --query "ipConfigurations[0].privateIpAllocationMethod" \
    --output tsv)

if [ "$ALLOCATION_METHOD" != "Static" ]; then
    az network nic ip-config update \
        --resource-group "$RESOURCE_GROUP" \
        --nic-name "$NIC_NAME" \
        --name "ipconfig1" \
        --private-ip-address "$FINAL_IP" \
        --output none
    echo "  ✓ IP set to static: $FINAL_IP"
else
    echo "  ✓ IP already static: $FINAL_IP"
fi
echo ""

# ===========================
# VERIFICATION & SUMMARY
# ===========================
echo "========================================"
echo "✓ VM REBUILD COMPLETE!"
echo "========================================"
echo ""

echo "VM Configuration:"
az vm show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --query "{Name:name, ResourceGroup:resourceGroup, Location:location, Size:hardwareProfile.vmSize, Zone:zones[0]}" \
    --output table
echo ""

echo "Network Configuration:"
az network nic show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NIC_NAME" \
    --query "ipConfigurations[0].{Name:name, PrivateIP:privateIpAddress, Allocation:privateIpAllocationMethod}" \
    --output table
echo ""

echo "Disk Configuration:"
echo "OS Disk:"
az vm show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --query "storageProfile.osDisk.{Name:name, Size:diskSizeGb, Caching:caching}" \
    --output table
echo ""
echo "Data Disks:"
az vm show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --query "storageProfile.dataDisks[].{LUN:lun, Name:name, Size:diskSizeGb, Caching:caching}" \
    --output table
echo ""

echo "========================================"
echo "NEXT STEPS:"
echo "========================================"
echo ""
echo "1. Start the VM:"
echo "   az vm start --resource-group $RESOURCE_GROUP --name $VM_NAME"
echo ""
echo "2. If OS disk was created from VHD/snapshot:"
echo "   - VM should boot to existing Windows/DC"
echo "   - Verify AD services running"
echo "   - Verify domain functionality"
echo ""
echo "3. If OS disk was empty:"
echo "   - You'll need to install Windows Server"
echo "   - Promote to Domain Controller"
echo "   - Restore AD from backup"
echo ""
echo "4. For data disk:"
echo "   - If from VHD/snapshot: Verify F: drive has data"
echo "   - If empty: Initialize, format, copy data from FS"
echo ""
echo "5. Run delta robocopy sync (in 5 days) if needed"
echo ""
echo "========================================"
