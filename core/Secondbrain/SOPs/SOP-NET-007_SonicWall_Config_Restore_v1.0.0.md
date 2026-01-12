# Standard Operating Procedure: SOP-NET-007

**Title:** SonicWall Configuration Restore
**Version:** 1.0
**Author:** Jeremy Smith
**Date:** 2025-12-29

---

## 1.0 Purpose

To establish a standardized procedure for restoring a SonicWall firewall configuration from a backup (.exp) file. This procedure is used for disaster recovery, device replacement, or rollback after failed changes.

## 2.0 Scope

This procedure applies to all Network Technicians and Engineers responsible for:
- Disaster recovery of SonicWall firewalls
- Restoring configuration after firmware issues
- Rolling back failed configuration changes
- Device replacement (same model only)

## 3.0 Prerequisites

- **Backup File:** Valid `.exp` configuration backup file (see SOP-NET-006)
- **Access:** Administrative credentials to the SonicWall device
- **Compatibility:**
  - Backup must be from the **same device model** (e.g., TZ 270 → TZ 270)
  - Target firmware should be **same or newer** than backup source
- **Network:** Active connection to the SonicWall management interface

## 4.0 When to Use This Procedure

| Scenario | Use Restore? | Notes |
|----------|--------------|-------|
| Device bricked after firmware upgrade | Yes | Restore after firmware rollback |
| Configuration change caused outage | Yes | Restore pre-change backup |
| Device RMA/replacement (same model) | Yes | Restore to new device |
| Moving config to different model | No | Manual reconfiguration required |
| Factory reset performed | Yes | Restore from backup |

## 5.0 Procedure

### 5.1 Pre-Restore Checklist

1. **Verify Backup File:**
   - Confirm you have the correct `.exp` file
   - Check file size is reasonable (50KB - 500KB typically)
   - Verify file is not corrupted (open in text editor, should show XML)

2. **Document Current State:**
   - Note current firmware version
   - Note current WAN IP (if accessible)
   - Export current config as additional backup (if device is accessible)

3. **Verify Compatibility:**
   - Confirm backup is from same device model
   - Confirm target firmware is same or newer than backup source firmware

### 5.2 Restore Configuration

1. **Access SonicWall Management Interface:**
   - Navigate to the SonicWall management IP
   - Log in with administrative credentials
   - If device is factory reset, use default IP `192.168.168.168`

2. **Navigate to Import Settings:**
   - Go to **Device > Settings > Firmware & Backups**
   - Locate the **Import/Export Configuration** section

3. **Import Configuration:**
   - Click **Import Settings** (or **Import Configuration**)
   - Browse to and select your `.exp` backup file
   - Click **Import**

4. **Review Import Summary:**
   - Review the import summary showing what will be restored
   - Confirm settings look correct
   - Click **OK** or **Confirm** to proceed

5. **Wait for Reboot:**
   - The firewall will automatically reboot to apply configuration
   - This typically takes 3-5 minutes
   - Do NOT power off during this process

### 5.3 Post-Restore Verification

1. **Verify Access:**
   - Log back into the management interface
   - Note: Management IP may have changed to restored configuration

2. **Verify Critical Settings:**
   - [ ] WAN interface configured correctly
   - [ ] LAN interface and DHCP working
   - [ ] Internet connectivity functional
   - [ ] Firewall rules restored
   - [ ] VPN configurations (if applicable)

3. **Re-authenticate Services:**
   - Navigate to **Device > Settings > MySonicWall**
   - Re-enter MySonicWall credentials if prompted
   - Verify license synchronization

4. **Test Connectivity:**
   - Test internet access from LAN
   - Test any VPN connections
   - Verify critical applications accessible

## 6.0 Restore to Factory Reset Device

If restoring to a device that has been factory reset:

1. **Connect to Default IP:**
   - Set your computer to static IP: `192.168.168.2`
   - Connect to firewall LAN port
   - Navigate to `http://192.168.168.168`

2. **Complete Initial Setup:**
   - Log in with default credentials (`admin` / `password`)
   - Change admin password when prompted
   - Select **Manual Setup**

3. **Register Device (if needed):**
   - Complete device registration per SOP-NET-001 Section 6.2
   - Registration must complete before config can be fully applied

4. **Import Configuration:**
   - Follow Section 5.2 above
   - Note: Some settings may require re-entry (MySonicWall credentials, certificates)

## 7.0 Restore to Replacement Device (RMA)

When replacing a failed device with new hardware (same model):

1. **Register New Device:**
   - Register new device in MySonicWall portal
   - Transfer licenses from old device if needed (contact SonicWall support)

2. **Update Firmware:**
   - Upgrade new device to match firmware version of backup
   - Or upgrade to latest stable release

3. **Import Configuration:**
   - Follow Section 5.2 above

4. **Update WAN Settings:**
   - If WAN IP is static, verify ISP settings are correct
   - May need to update MAC address with ISP

5. **Re-establish VPNs:**
   - Site-to-site VPNs may need to be re-established
   - Notify remote sites of device replacement

## 8.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| Import fails with error | 1. Verify .exp file not corrupted <br> 2. Check firmware compatibility <br> 3. Try different browser |
| Cannot access device after restore | 1. Check if management IP changed <br> 2. Connect to LAN and try default gateway IP <br> 3. Factory reset and retry |
| Licenses not showing after restore | 1. Re-enter MySonicWall credentials <br> 2. Click Synchronize in Licenses section <br> 3. Reboot device |
| VPN not connecting after restore | 1. Verify WAN IP correct <br> 2. Re-exchange keys with remote site <br> 3. Check firewall rules restored |
| Services not enabled after restore | 1. Sync licenses with MySonicWall <br> 2. Manually enable services <br> 3. Verify subscription active |

## 9.0 Important Warnings

> **WARNING:** Restoring a configuration will **overwrite all current settings**. Always export current configuration before restoring.

> **WARNING:** Configurations are **device-model specific**. A TZ 270 backup cannot be restored to a TZ 370 or other model.

> **WARNING:** If restoring to older firmware than the backup source, some settings may not apply correctly. Always restore to same or newer firmware.

## 10.0 Related Documents

- SOP-NET-001: Initial SonicWall Firewall Setup
- SOP-NET-004: Register Device in MySonicwall
- SOP-NET-006: SonicWall Configuration Backup

---
**End of Document**
---
