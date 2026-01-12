#!/bin/bash
# ===========================
# Rebuild SETCO-DC02 VM from Existing Disks
# Complete Variable-Based Script
# Created: 2025-11-17
# ===========================

set -e  # Exit on any error

# ===========================
# VARIABLES - All Defined
# ===========================

# Resource Group & Location
RESOURCE_GROUP="DataCenter"
LOCATION="eastus"  # Change if your RG is in different region

# VM Configuration
VM_NAME="SETCO-DC02"
VM_SIZE="Standard_D4s_v5"
ZONE="3"

# Existing Disk Names (already created with data)
OS_DISK_NAME="SETCO-DC02_OsDisk_1_183e9544deb6407c96abc84604d1c38c"
DATA_DISK_NAME="SETCO-DC02_1TData_Copy"

# Network Configuration
TARGET_VNET="DataCenter_vNet"
TARGET_SUBNET="DataCenter_Subnet"
NIC_NAME="${VM_NAME}-nic2"

# Optional: Static IP (leave empty for dynamic, or set like "10.0.1.10")
STATIC_PRIVATE_IP=""

# OS Type
OS_TYPE="Windows"

echo "========================================"
echo "SETCO-DC02 VM Rebuild Script"
echo "========================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "VM Name: $VM_NAME"
echo "VM Size: $VM_SIZE"
echo "Zone: $ZONE"
echo "OS Disk: $OS_DISK_NAME"
echo "Data Disk: $DATA_DISK_NAME"
echo "VNet: $TARGET_VNET"
echo "Subnet: $TARGET_SUBNET"
echo "NIC: $NIC_NAME"
echo "========================================"
echo ""

# ===========================
# Step 1: Verify Resource Group exists
# ===========================
echo "[Step 1/7] Verifying Resource Group..."
if az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "  ✓ Resource Group '$RESOURCE_GROUP' exists"
else
    echo "  Creating Resource Group '$RESOURCE_GROUP' in $LOCATION..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
    echo "  ✓ Resource Group created"
fi
echo ""

# ===========================
# Step 2: Verify OS Disk exists
# ===========================
echo "[Step 2/7] Verifying OS Disk..."
OS_DISK_ID=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OS_DISK_NAME" \
    --query id \
    --output tsv 2>/dev/null || echo "")

if [ -z "$OS_DISK_ID" ]; then
    echo "  ✗ ERROR: OS Disk '$OS_DISK_NAME' not found!"
    echo "  This disk must exist before running this script."
    exit 1
fi

OS_DISK_SIZE=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OS_DISK_NAME" \
    --query diskSizeGb \
    --output tsv)

OS_DISK_SKU=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OS_DISK_NAME" \
    --query sku.name \
    --output tsv)

echo "  ✓ OS Disk found"
echo "    - ID: $OS_DISK_ID"
echo "    - Size: ${OS_DISK_SIZE}GB"
echo "    - SKU: $OS_DISK_SKU"
echo ""

# ===========================
# Step 3: Verify Data Disk exists
# ===========================
echo "[Step 3/7] Verifying Data Disk..."
DATA_DISK_ID=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_DISK_NAME" \
    --query id \
    --output tsv 2>/dev/null || echo "")

if [ -z "$DATA_DISK_ID" ]; then
    echo "  ✗ ERROR: Data Disk '$DATA_DISK_NAME' not found!"
    echo "  This disk must exist before running this script."
    exit 1
fi

DATA_DISK_SIZE=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_DISK_NAME" \
    --query diskSizeGb \
    --output tsv)

DATA_DISK_SKU=$(az disk show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DATA_DISK_NAME" \
    --query sku.name \
    --output tsv)

echo "  ✓ Data Disk found"
echo "    - ID: $DATA_DISK_ID"
echo "    - Size: ${DATA_DISK_SIZE}GB"
echo "    - SKU: $DATA_DISK_SKU"
echo ""

# ===========================
# Step 4: Check if VM already exists
# ===========================
echo "[Step 4/7] Checking if VM already exists..."
if az vm show --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" &>/dev/null; then
    echo "  ✗ WARNING: VM '$VM_NAME' already exists!"
    echo "  Please delete it first: az vm delete -g $RESOURCE_GROUP -n $VM_NAME --yes"
    exit 1
fi
echo "  ✓ VM does not exist - safe to proceed"
echo ""

# ===========================
# Step 5: Create or verify Network Interface
# ===========================
echo "[Step 5/7] Creating/verifying Network Interface..."

# Check if NIC exists
if az network nic show --resource-group "$RESOURCE_GROUP" --name "$NIC_NAME" &>/dev/null; then
    echo "  ! NIC '$NIC_NAME' already exists"

    # Get current IP
    CURRENT_NIC_IP=$(az network nic show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$NIC_NAME" \
        --query "ipConfigurations[0].privateIpAddress" \
        --output tsv)

    echo "    - Current IP: $CURRENT_NIC_IP"
    echo "  Will reuse existing NIC"
else
    echo "  Creating new NIC '$NIC_NAME'..."

    # Build NIC create command
    NIC_CREATE_CMD="az network nic create \
        --resource-group $RESOURCE_GROUP \
        --name $NIC_NAME \
        --vnet-name $TARGET_VNET \
        --subnet $TARGET_SUBNET \
        --output none"

    # Add static IP if specified
    if [ -n "$STATIC_PRIVATE_IP" ]; then
        NIC_CREATE_CMD="$NIC_CREATE_CMD --private-ip-address $STATIC_PRIVATE_IP"
        echo "    - Assigning static IP: $STATIC_PRIVATE_IP"
    fi

    eval $NIC_CREATE_CMD
    echo "  ✓ NIC created successfully"

    # Get assigned IP
    CURRENT_NIC_IP=$(az network nic show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$NIC_NAME" \
        --query "ipConfigurations[0].privateIpAddress" \
        --output tsv)

    echo "    - Assigned IP: $CURRENT_NIC_IP"
fi
echo ""

# ===========================
# Step 6: Create VM from existing OS disk
# ===========================
echo "[Step 6/7] Creating VM from existing OS disk..."
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
echo "[Step 7/7] Attaching data disk to VM..."

az vm disk attach \
    --resource-group "$RESOURCE_GROUP" \
    --vm-name "$VM_NAME" \
    --name "$DATA_DISK_ID" \
    --lun 1 \
    --output none

echo "  ✓ Data disk attached at LUN 1"
echo ""

# ===========================
# Step 8: Set NIC IP to Static (if not already)
# ===========================
echo "[Step 8/7] Ensuring NIC IP is static..."

ALLOCATION_METHOD=$(az network nic show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$NIC_NAME" \
    --query "ipConfigurations[0].privateIpAllocationMethod" \
    --output tsv)

if [ "$ALLOCATION_METHOD" != "Static" ]; then
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
else
    echo "  ✓ IP already static: $CURRENT_NIC_IP"
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
    --query "ipConfigurations[0].{Name:name, PrivateIP:privateIpAddress, Allocation:privateIpAllocationMethod, Subnet:subnet.id}" \
    --output table
echo ""

echo "Disk Configuration:"
echo "OS Disk:"
az vm show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --query "storageProfile.osDisk.{Name:name, Size:diskSizeGb, Caching:caching, CreateOption:createOption}" \
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
echo "2. Get VM status:"
echo "   az vm get-instance-view --resource-group $RESOURCE_GROUP --name $VM_NAME --query instanceView.statuses"
echo ""
echo "3. Check boot diagnostics (if boot issues):"
echo "   az vm boot-diagnostics get-boot-log --resource-group $RESOURCE_GROUP --name $VM_NAME"
echo ""
echo "4. Get private IP for RDP connection:"
echo "   az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME -d --query privateIps -o tsv"
echo ""
echo "5. After VM boots, verify in Windows:"
echo "   - C: drive is OS disk (${OS_DISK_SIZE}GB)"
echo "   - F: drive is data disk (${DATA_DISK_SIZE}GB)"
echo "   - Run: Get-Disk and Get-Volume in PowerShell"
echo ""
echo "6. Run delta robocopy sync next weekend (in 5 days)"
echo "   to capture changes since initial sync"
echo ""
echo "========================================"
echo "Script completed successfully!"
echo "========================================"
