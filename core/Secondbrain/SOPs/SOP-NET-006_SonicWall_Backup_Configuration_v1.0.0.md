# Standard Operating Procedure: SOP-NET-006

**Title:** SonicWall Configuration Backup
**Version:** 1.0
**Author:** Jeremy Smith
**Date:** 2025-12-05

---

## 1.0 Purpose

To establish a standardized procedure for exporting and securely storing SonicWall firewall configuration backups before deployment, after significant changes, or as part of routine maintenance. This ensures rapid recovery capability and configuration integrity verification.

## 2.0 Scope

This procedure applies to all Network Technicians and Engineers responsible for:
- Pre-deployment configuration backup (before shipping to customer)
- Post-installation configuration backup
- Configuration changes requiring rollback capability
- Routine scheduled backups

## 3.0 Prerequisites

- **Access:** Administrative credentials to the SonicWall device
- **Keeper Access:** Valid credentials to the Obera Connect Keeper vault
- **Network:** Active connection to the SonicWall management interface

## 4.0 Backup File Naming Convention

Use the following format for all configuration backup files:

```
[CustomerCode]_[DeviceModel]_[Date]_[Type].exp

Examples:
SFWB_TZ270_2025-12-05_preshipment.exp
SFWB_TZ270_2025-12-05_postinstall.exp
SFWB_TZ270_2025-12-05_prechange.exp
```

**Customer Codes:** Use standard 4-letter customer abbreviation (e.g., SFWB, SETC, GRLE)

**Type Identifiers:**
- `preshipment` - Before shipping device to customer
- `postinstall` - After successful on-site installation
- `prechange` - Before making configuration changes
- `scheduled` - Routine scheduled backup

## 5.0 Procedure

### 5.1 Export Configuration from SonicWall

1. **Log In to SonicWall:**
   - Open a web browser and navigate to the SonicWall management IP
   - Log in with administrative credentials

2. **Navigate to Backup Settings:**
   - Go to **Device > Settings > Firmware & Backups**
   - Alternatively: **System > Firmware and Backups** (older firmware)

3. **Export Configuration:**
   - Locate the **Import/Export Configuration** section
   - Click **Export Configuration**
   - When prompted, choose to include or exclude the following:
     - **Include Certificates:** Yes (recommended)
     - **Include VPN Keys:** Yes (if VPN configured)
   - Save the `.exp` file using the naming convention in Section 4.0

4. **Verify Export:**
   - Confirm the file downloaded successfully
   - Check file size is reasonable (typically 50KB - 500KB depending on complexity)
   - File size of 0 KB indicates a failed export - retry

### 5.2 Store Configuration in Keeper (Manual Process)

> **Note:** API automation via Keeper Secrets Manager (KSM) is pending approval. Until KSM is enabled, use the manual process below.

1. **Log In to Keeper:**
   - Access Keeper vault at `https://keepersecurity.com/vault`
   - Or use Keeper desktop/browser extension

2. **Navigate to Firewalls Folder:**
   - In **My Vault**, locate the **Firewalls** shared folder
   - This is the central repository for all firewall configurations

3. **Create New Record:**
   - Click **+ Create New**
   - Select **Login** or **File** record type
   - Fill in the following fields:
     - **Title:** `[CustomerCode] - SonicWall [Model] Config - [Date]`
       - Example: `SFWB - SonicWall TZ270 Config - 2025-12-05`
     - **Attachments:** Upload the `.exp` file

4. **Add Metadata in Notes:**
   ```
   Customer: Spanish Fort Water Board (SFWB)
   Device: SonicWall TZ270
   Serial: [Serial Number]
   Firmware: 7.0.1-5161
   WAN IP: [Public IP if applicable]
   Backup Date: 2025-12-05
   Backup Type: Pre-Shipment
   Technician: [Your Name]
   Verified: Yes
   ```

5. **Rename Downloaded File (Optional):**
   - SonicWall exports with default naming like:
     `sonicwall-TZ 270-SonicOS 7.0.1-5161-R6164-2025-12-05T14_05_24.264Z.exp`
   - Rename to standard format before uploading:
     `SFWB_TZ270_2025-12-05_preshipment.exp`

### 5.3 Verify Backup Integrity

1. **File Validation:**
   - Open the `.exp` file in a text editor
   - Verify it contains XML configuration data (not empty or corrupted)
   - First line should contain `<?xml version=` or similar header

2. **Document in Keeper Notes:**
   - Add verification status: `Verified: Yes`
   - Add checksum if required for compliance: `MD5: [hash]`

## 6.0 Pre-Shipment Backup Checklist

Complete this checklist before shipping any SonicWall to customer:

- [ ] Configuration export completed successfully
- [ ] File named according to naming convention
- [ ] File uploaded to Keeper in correct customer folder
- [ ] Metadata added to Keeper record (serial, firmware, date)
- [ ] Backup file verified (not empty/corrupted)
- [ ] MySonicWall portal shows device registered

## 7.0 Restore Procedure (Reference)

If configuration restore is needed:

1. Access SonicWall management interface
2. Navigate to **Device > Settings > Firmware & Backups**
3. Click **Import Configuration**
4. Browse to and select the `.exp` file from Keeper
5. Click **Import**
6. Review import summary and confirm
7. Device will reboot to apply configuration

**Note:** Restore will overwrite current configuration. Ensure you have a backup of current config before restoring.

## 8.0 Backup Schedule

| Backup Type | When | Retention |
|-------------|------|-----------|
| Pre-Shipment | Before shipping to customer | Permanent |
| Post-Install | After successful installation | Permanent |
| Pre-Change | Before any configuration changes | 90 days |
| Scheduled | Monthly (managed devices) | 12 months |

## 9.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| Export fails or 0 KB file | 1. Clear browser cache and retry<br>2. Try different browser<br>3. Check available disk space on management station |
| Cannot upload to Keeper | 1. Verify Keeper permissions<br>2. Check file size limits<br>3. Contact admin for folder access |
| Configuration appears corrupted | 1. Re-export from device<br>2. If device inaccessible, check for previous backups in Keeper |

## 10.0 Future: Automated Storage with Keeper Commander

Keeper Commander CLI can automate config storage without requiring KSM add-on.

### 10.1 Prerequisites
- Keeper Commander installed: `pipx install keepercommander`
- One-time interactive login to cache credentials

### 10.2 Automation Commands
```bash
# Login (interactive, first time only)
keeper shell
> login jeremy.smith@oberaconnect.com

# Upload file to Firewalls folder (batch mode)
keeper --batch-mode upload-attachment --folder "Firewalls" --file "SFWB_TZ270_2025-12-05_preshipment.exp"

# Create record with attachment
keeper --batch-mode add-record --folder "Firewalls" \
  --title "SFWB - SonicWall TZ270 Config - 2025-12-05" \
  --notes "Customer: SFWB\nDevice: TZ270\nBackup Type: Pre-Shipment" \
  --attach "SFWB_TZ270_2025-12-05_preshipment.exp"
```

### 10.3 Full API Automation (Requires KSM)
When Keeper Secrets Manager is approved:
- Programmatic token-based authentication
- REST API access
- CI/CD integration
- Zero-touch automation

**Request KSM from subscription admin to enable full automation.**

## 11.0 References

- SOP-NET-001: Initial SonicWall Firewall Setup
- SOP-NET-004: Register Device in MySonicwall
- Keeper Security Vault: https://keepersecurity.com/vault
- Keeper Commander Docs: https://docs.keeper.io/secrets-manager/commander-cli

---
**End of Document**
---
