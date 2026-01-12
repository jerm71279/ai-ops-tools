#!/bin/bash
# ===========================
# Rebuild SETCO-DC02 from Existing Disks
# Created: 2025-11-17
# ===========================

set -e  # Exit on any error

# ===========================
# Variables
# ===========================
RG="DataCenter"
VM="SETCO-DC02"
TARGET_VNET="DataCenter_vNet"
TARGET_SUBNET="DataCenter_Subnet"
NEW_NIC="${VM}-nic2"

# VM Size and Zone
SIZE="Standard_D4s_v5"
ZONE="3"

# Disk names
OS_DISK_NAME="SETCO-DC02_OsDisk_1_183e9544deb6407c96abc84604d1c38c"
DATA_DISK_NAME="SETCO-DC02_1TData_Copy"

echo "========================================"
echo "SETCO-DC02 Rebuild Script"
echo "========================================"
echo "Resource Group: $RG"
echo "VM Name: $VM"
echo "VNet: $TARGET_VNET"
echo "Subnet: $TARGET_SUBNET"
echo "Size: $SIZE"
echo "Zone: $ZONE"
echo ""

# ===========================
# Step 1: Resolve disk IDs
# ===========================
echo "[1/6] Resolving disk IDs..."
OS_DISK_ID=$(az disk show -g "$RG" -n "$OS_DISK_NAME" --query id -o tsv)
DATA_DISK_ID=$(az disk show -g "$RG" -n "$DATA_DISK_NAME" --query id -o tsv)

if [ -z "$OS_DISK_ID" ]; then
    echo "ERROR: OS disk '$OS_DISK_NAME' not found!"
    exit 1
fi

if [ -z "$DATA_DISK_ID" ]; then
    echo "ERROR: Data disk '$DATA_DISK_NAME' not found!"
    exit 1
fi

echo "  OS Disk ID: $OS_DISK_ID"
echo "  Data Disk ID: $DATA_DISK_ID"
echo ""

# ===========================
# Step 2: Check if VM already exists
# ===========================
echo "[2/6] Checking if VM already exists..."
if az vm show -g "$RG" -n "$VM" &>/dev/null; then
    echo "WARNING: VM '$VM' already exists!"
    echo "Please delete it first or use a different VM name."
    exit 1
fi
echo "  VM does not exist - OK to proceed"
echo ""

# ===========================
# Step 3: Create or verify NIC
# ===========================
echo "[3/6] Creating/verifying NIC..."
if ! az network nic show -g "$RG" -n "$NEW_NIC" &>/dev/null; then
    echo "  Creating NIC '$NEW_NIC'..."
    az network nic create -g "$RG" -n "$NEW_NIC" \
        --vnet-name "$TARGET_VNET" \
        --subnet "$TARGET_SUBNET" \
        --output none
    echo "  NIC created successfully"
else
    echo "  NIC '$NEW_NIC' already exists - will reuse"
fi

# Show current IP
CURR_IP=$(az network nic show -g "$RG" -n "$NEW_NIC" --query "ipConfigurations[0].privateIpAddress" -o tsv)
echo "  Current IP on NIC: $CURR_IP"
echo ""

# ===========================
# Step 4: Create VM from OS disk
# ===========================
echo "[4/6] Creating VM from OS disk..."
echo "  This may take 2-3 minutes..."
az vm create -g "$RG" -n "$VM" \
    --attach-os-disk "$OS_DISK_ID" \
    --os-type Windows \
    --nics "$NEW_NIC" \
    --zone "$ZONE" \
    --size "$SIZE" \
    --output none

echo "  VM created successfully"
echo ""

# ===========================
# Step 5: Attach data disk
# ===========================
echo "[5/6] Attaching data disk..."
az vm disk attach -g "$RG" \
    --vm-name "$VM" \
    --name "$DATA_DISK_ID" \
    --lun 1 \
    --output none

echo "  Data disk attached at LUN 1"
echo ""

# ===========================
# Step 6: Set NIC IP to static
# ===========================
echo "[6/6] Setting NIC IP to static..."
FINAL_IP=$(az network nic show -g "$RG" -n "$NEW_NIC" --query "ipConfigurations[0].privateIpAddress" -o tsv)

az network nic ip-config update -g "$RG" \
    --nic-name "$NEW_NIC" \
    --name "ipconfig1" \
    --private-ip-address "$FINAL_IP" \
    --output none

echo "  Private IP set to static: $FINAL_IP"
echo ""

# ===========================
# Verification
# ===========================
echo "========================================"
echo "VM Rebuild Complete!"
echo "========================================"
echo ""
echo "VM Details:"
az vm show -g "$RG" -n "$VM" --query "{Name:name, Size:hardwareProfile.vmSize, Zone:zones[0], PowerState:powerState}" -o table
echo ""

echo "Network Configuration:"
echo "  Private IP: $FINAL_IP"
az network nic show -g "$RG" -n "$NEW_NIC" --query "ipConfigurations[0].{Name:name, PrivateIP:privateIpAddress, AllocationMethod:privateIpAllocationMethod}" -o table
echo ""

echo "Attached Disks:"
az vm show -g "$RG" -n "$VM" --query "storageProfile.{OSDisk:osDisk.name, DataDisks:dataDisks[].{LUN:lun, Name:name}}" -o json
echo ""

echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Start the VM:"
echo "   az vm start -g $RG -n $VM"
echo ""
echo "2. Check boot diagnostics if issues:"
echo "   az vm boot-diagnostics get-boot-log -g $RG -n $VM"
echo ""
echo "3. Connect via RDP (after starting):"
echo "   az vm show -g $RG -n $VM -d --query privateIps -o tsv"
echo ""
echo "4. Verify data disk shows as F: drive after boot"
echo "========================================"
