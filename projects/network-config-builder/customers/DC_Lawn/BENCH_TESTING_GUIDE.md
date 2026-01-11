# DC Lawn - MikroTik Out-of-Box Bench Testing Guide

**Customer:** DC Lawn
**Circuit ID:** 205922
**Purpose:** Pre-deployment testing and configuration

---

## Overview

This guide walks you through bench testing the MikroTik router before taking it to the customer site. You'll configure the device, test all functionality, and prepare it for field deployment.

**Time Required:** 30-45 minutes
**Location:** Your bench/workshop with internet access

---

## Equipment Needed

- [ ] MikroTik router (factory fresh or reset)
- [ ] Computer with WinBox installed
- [ ] Ethernet cables (2-3)
- [ ] Internet connection for testing
- [ ] USB drive (optional, for config backup)
- [ ] Label maker (for physical labeling)

---

## Phase 1: Initial Connection & Backup

### Step 1: Physical Setup

1. **Power on the MikroTik**
   - Connect power adapter
   - Wait 30-60 seconds for boot

2. **Connect your computer to the MikroTik**
   - Connect Ethernet cable from your computer to **ether2** (or any LAN port, NOT ether1)
   - MikroTik default IP: `192.168.88.1`
   - Your computer should get DHCP: `192.168.88.x`

3. **Verify connectivity**
   ```bash
   ping 192.168.88.1
   
   ```
   You should see replies.

### Step 2: Connect with WinBox

1. **Launch WinBox**
   - Download from: mikrotik.com/download if needed
   - Run WinBox.exe (no installation needed)

2. **Discover the MikroTik**
   - Click on **Neighbors** tab in WinBox
   - You should see your MikroTik listed (MAC address shown)
   - Click on the MAC address to auto-fill connection

3. **Login with default credentials**
   - **Username:** `admin`
   - **Password:** (leave blank)
   - Click **Connect**

4. **First login prompt**
   - RouterOS may ask you to configure the device
   - Click **Remove Configuration** or **Cancel** to keep factory defaults for now
   - You're about to replace it anyway

### Step 3: Document Factory Information

1. **Record device information**
   - In WinBox, go to **System > Resources**
   - Note down:
     - RouterOS Version: ___________
     - Model: ___________
     - Serial Number: ___________
     - Firmware: ___________

2. **Create factory backup**
   - Go to **Files** menu
   - Click **Backup** button
   - Name it: `factory_backup_[date]`
   - Click **Backup**
   - Download the .backup file to your computer (drag from Files list to desktop)

3. **Export factory configuration** (text format)
   - Open **New Terminal**
   - Run:
     ```
     /export file=factory_config
     ```
   - Go to **Files** menu
   - Download `factory_config.rsc` to your computer

✅ **Factory backup complete!** You can now safely proceed with configuration.

---

## Phase 2: Upload DC Lawn Configuration

### Step 4: Reset to Clean State (Optional but Recommended)

1. **Reset the device**
   - Go to **System > Reset Configuration**
   - Check **No Default Configuration**
   - Check **Do Not Backup**
   - Click **Reset Configuration**
   - MikroTik will reboot (takes 30-60 seconds)

2. **Reconnect after reset**
   - You may need to reconnect via WinBox
   - Use MAC address in Neighbors tab
   - Login: `admin` / (no password)

### Step 5: Upload Configuration File

1. **Open Files menu in WinBox**
   - Click **Files** on left menu

2. **Upload the router.rsc file**
   - Drag and drop `customers/DC_Lawn/configs/router.rsc` into the Files window
   - OR click **Upload** button and browse to the file
   - Wait for upload to complete (should be instant for small config)

3. **Verify upload**
   - You should see `router.rsc` in the files list
   - Size should be ~1-2 KB

### Step 6: Import Configuration

1. **Open Terminal** (New Terminal button)

2. **Import the configuration**
   ```
   /import file-name=router.rsc
   ```

3. **Watch for errors**
   - If successful, you'll see multiple "Cmd:" lines
   - Any errors will be displayed in red
   - Common errors and fixes below in Troubleshooting section

4. **Configuration is now active!**
   - You may lose connection if your computer was on ether2
   - This is normal - we'll reconnect next

---

## Phase 3: Reconnect with New Configuration

### Step 7: Adjust Your Connection

**Important:** The new configuration changes the LAN network from `192.168.88.x` to `10.54.0.x`

1. **Reconnect to the new LAN IP**
   - Your computer should get a new DHCP address: `10.54.0.100-200`
   - OR manually set your computer to: `10.54.0.50/24`

2. **Login to WinBox again**
   - Connect to: `10.54.0.1` (new LAN IP)
   - Username: `admin`
   - Password: `ChangeMe@205922!` (from config)
   - Click **Connect**

✅ **You're now connected to the configured router!**

---

## Phase 4: Verify Configuration

### Step 8: Check IP Addresses

1. **Open Terminal**

2. **Verify WAN interface**
   ```
   /ip address print
   ```

   You should see:
   - `142.190.216.66/30` on **ether1** (WAN) ✓
   - `10.54.0.1/24` on **bridge-lan** (LAN) ✓

3. **Check default route**
   ```
   /ip route print
   ```

   You should see:
   - Gateway: `142.190.216.65` ✓

### Step 9: Check DHCP Server

1. **Verify DHCP configuration**
   ```
   /ip dhcp-server print
   /ip pool print
   /ip dhcp-server network print
   ```

2. **Expected output:**
   - DHCP server: `lan-dhcp` on `bridge-lan`
   - IP Pool: `10.54.0.100-10.54.0.200`
   - DNS servers: `142.190.111.111, 142.190.222.222`

### Step 10: Check NAT/Firewall

1. **Verify NAT rule**
   ```
   /ip firewall nat print
   ```

   You should see:
   - Masquerade rule on chain=srcnat, out-interface=ether1 ✓

2. **Check security services**
   ```
   /ip service print
   ```

   Verify:
   - WinBox: enabled ✓
   - SSH: enabled ✓
   - Telnet, FTP, www, api, api-ssl: **disabled** ✓

### Step 11: Check Security Hardening

1. **Verify MAC server disabled**
   ```
   /tool mac-server print
   /tool mac-server mac-winbox print
   /tool mac-server ping print
   ```
   All should show as disabled or none ✓

2. **Check neighbor discovery**
   ```
   /ip neighbor discovery-settings print
   ```
   Should be disabled ✓

---

## Phase 5: Bench Testing (Without Real WAN)

**Note:** You won't have the real WAN connection (142.190.216.66) until on-site, but you can test with a simulated WAN.

### Step 12: Test with Simulated WAN

**Option A: Use Your Office Internet**

1. **Connect ether1 to your office network**
   - Plug ether1 into a switch/router that has internet
   - This temporarily replaces the static WAN config

2. **Change WAN to DHCP temporarily**
   ```
   /ip address remove [find interface=ether1]
   /ip route remove [find gateway=142.190.216.65]
   /ip dhcp-client add interface=ether1 disabled=no
   ```

3. **Wait 10 seconds, check WAN connectivity**
   ```
   /ip dhcp-client print
   ```
   Should show an IP address received

4. **Test internet from router**
   ```
   /ping 8.8.8.8 count=5
   /ping google.com count=5
   ```
   Both should succeed ✓

**Option B: Skip WAN Testing**
- You can skip this if you prefer to test WAN on-site
- Proceed to LAN testing below

### Step 13: Test LAN and DHCP

1. **Connect a test device to ether2-5**
   - Use a laptop or phone
   - It should get DHCP: `10.54.0.100-200`

2. **Verify DHCP lease**
   - On router terminal:
     ```
     /ip dhcp-server lease print
     ```
   - You should see your test device listed ✓

3. **Test internet from LAN device**
   - On the test device, browse to google.com
   - Should work if you completed Step 12 Option A ✓

4. **Test DNS resolution**
   - From test device: `ping google.com`
   - Should resolve and ping ✓

### Step 14: Test Management Access

1. **Test WinBox from LAN**
   - Close current WinBox session
   - Open WinBox from test device on LAN
   - Connect to: `10.54.0.1`
   - Should connect successfully ✓

2. **Test SSH (optional)**
   ```bash
   ssh admin@10.54.0.1
   ```
   Should connect and prompt for password ✓

---

## Phase 6: Prepare for Field Deployment

### Step 15: Restore Production WAN Config

**Important:** If you changed WAN to DHCP for testing, restore it now!

1. **Remove DHCP client**
   ```
   /ip dhcp-client remove [find interface=ether1]
   ```

2. **Restore static WAN IP**
   ```
   /ip address add address=142.190.216.66/30 interface=ether1
   /ip route add gateway=142.190.216.65
   ```

3. **Verify configuration**
   ```
   /ip address print
   /ip route print
   ```
   Should match DC Lawn config ✓

### Step 16: Change Admin Password

1. **Set a secure password**
   ```
   /user set admin password=YourSecurePassword123!
   ```

2. **Test new password**
   - Disconnect WinBox
   - Reconnect with new password
   - Should work ✓

3. **Document the password**
   - Record in your password manager
   - Add to customer documentation

### Step 17: Create Pre-Deployment Backup

1. **Create backup with final config**
   ```
   /system backup save name=DC_Lawn_PreDeploy_2025-11-24
   /export file=DC_Lawn_PreDeploy_2025-11-24
   ```

2. **Download backups**
   - Go to **Files** menu
   - Download both files:
     - `DC_Lawn_PreDeploy_2025-11-24.backup`
     - `DC_Lawn_PreDeploy_2025-11-24.rsc`
   - Store in `customers/DC_Lawn/backups/` folder

### Step 18: Physical Labeling

1. **Label the router**
   - Customer: DC Lawn
   - WAN IP: 142.190.216.66/30
   - LAN IP: 10.54.0.1/24
   - Date configured: 2025-11-24

2. **Label the cables** (optional but helpful)
   - ether1: "WAN - To Calix 142.190.216.66"
   - ether2-5: "LAN"

3. **Add warning label**
   - "Configured - Do Not Reset"
   - "Contact: [Your Name/Number]"

---

## Phase 7: Final Pre-Deployment Checklist

### Step 19: Complete Final Verification

Print this checklist and verify each item:

#### Configuration Verification
- [ ] WAN IP: 142.190.216.66/30 configured on ether1
- [ ] Default gateway: 142.190.216.65 configured
- [ ] LAN IP: 10.54.0.1/24 on bridge-lan
- [ ] DHCP server active (pool: 10.54.0.100-200)
- [ ] DNS servers: 142.190.111.111, 142.190.222.222
- [ ] NAT/Masquerade rule present
- [ ] Admin password changed from default
- [ ] Security hardening applied

#### Functional Testing
- [ ] DHCP assigns addresses to LAN clients
- [ ] LAN clients can reach router (ping 10.54.0.1)
- [ ] WinBox access works from LAN
- [ ] SSH access works (if needed)
- [ ] Telnet/FTP/HTTP disabled
- [ ] MAC server disabled

#### Documentation & Backup
- [ ] Factory backup saved
- [ ] Pre-deployment backup saved
- [ ] New admin password documented
- [ ] Device serial number recorded
- [ ] RouterOS version documented
- [ ] Physical labels applied

#### Ready for Transport
- [ ] Router powered off
- [ ] Packed securely
- [ ] Cables organized
- [ ] Documentation printed
- [ ] Customer site address confirmed

---

## Phase 8: On-Site Deployment Procedure

### Step 20: At Customer Site

1. **Connect WAN (ether1)**
   - Connect to Calix port as specified
   - Verify link lights

2. **Connect LAN**
   - Connect ether2-5 to customer switch/devices

3. **Power on and verify**
   ```
   /ping 142.190.216.65 count=5     # Test gateway
   /ping 8.8.8.8 count=5             # Test internet
   /ping google.com count=5          # Test DNS
   ```

4. **Test from customer device**
   - Connect customer PC/device
   - Should get DHCP 10.54.0.x
   - Test internet connectivity
   - Test DNS resolution

5. **Final documentation**
   - Record installation date/time
   - Document any changes made
   - Update customer site notes

---

## Troubleshooting Guide

### Issue: Can't Connect to 192.168.88.1

**Possible causes:**
- Router not powered on → Check power adapter
- Wrong port → Connect to ether2-5, not ether1
- Computer not getting DHCP → Manually set IP to 192.168.88.50/24

### Issue: Config Import Fails

**Error: "failure: already have such address"**
- Solution: Reset router first (Step 4) or remove conflicting addresses:
  ```
  /ip address remove [find]
  ```

**Error: "failure: interface not found"**
- Solution: Your device may not have the exact interface names. Check:
  ```
  /interface print
  ```
  Modify router.rsc if needed.

### Issue: Lost Connection After Import

**This is normal!** The config changes LAN from 192.168.88.x to 10.54.0.x
- Disconnect and reconnect your network cable
- Connect to new IP: 10.54.0.1
- New password: ChangeMe@205922!

### Issue: WAN Not Working On-Site

**Symptoms:** Can't ping gateway 142.190.216.65

1. **Check physical connection**
   ```
   /interface print
   ```
   Verify ether1 shows "running"

2. **Verify WAN IP**
   ```
   /ip address print
   ```
   Should show 142.190.216.66/30 on ether1

3. **Check with ISP/Unifi**
   - Verify circuit is active
   - Confirm IP assignment is correct
   - Check if port is configured for Auto/Auto

4. **Test from ISP side**
   - Ask ISP to ping 142.190.216.66 from their side

### Issue: LAN Devices Not Getting DHCP

1. **Check DHCP server**
   ```
   /ip dhcp-server print
   ```
   Should show enabled

2. **Check if pool is exhausted**
   ```
   /ip dhcp-server lease print
   ```
   If 101 leases exist, pool is full (only 100 addresses available)

3. **Release old leases**
   ```
   /ip dhcp-server lease remove [find]
   ```

### Issue: Internet Not Working from LAN

1. **Test from router first**
   ```
   /ping 8.8.8.8
   ```
   If this works, but clients can't access internet:

2. **Check NAT rule**
   ```
   /ip firewall nat print
   ```
   Should have masquerade rule

3. **Check DNS**
   ```
   /ping google.com
   ```
   If this fails, DNS issue. Check:
   ```
   /ip dns print
   ```

---

## Emergency Recovery

### If Everything Goes Wrong

1. **Factory Reset**
   - Hold reset button for 10 seconds while powered
   - OR via WinBox: System > Reset Configuration

2. **Restore from backup**
   ```
   /system backup load name=DC_Lawn_PreDeploy_2025-11-24
   ```

3. **Re-import from .rsc file**
   - Upload router.rsc again
   - Import via terminal

---

## Support Contacts

**Obera Connect Support:**
- Phone: [Your Support Number]
- Email: [Your Support Email]

**MikroTik Resources:**
- Documentation: wiki.mikrotik.com
- Forum: forum.mikrotik.com
- Support: support@mikrotik.com

---

## Notes Section

Use this space for any site-specific notes or observations:

```
Date: _______________
Technician: _______________

Notes:
_________________________________________________
_________________________________________________
_________________________________________________
_________________________________________________
_________________________________________________
```

---

**Generated by Multi-Vendor Network Config Builder**
**Customer: DC Lawn | Circuit: 205922**
