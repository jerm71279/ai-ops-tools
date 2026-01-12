# Standard Operating Procedure: SOP-NET-004

**Title:** Register Device in MySonicwall
**Version:** 1.1
**Author:** Gemini
**Date:** 2025-12-02

---

## 1.0 Purpose

To provide a standardized procedure for registering a new SonicWall device in the MySonicwall portal, ensuring it is correctly associated with a tenant and ready for management.

## 2.0 Scope

This procedure applies to all IT personnel and network administrators responsible for the deployment and initial configuration of new SonicWall hardware.

## 3.0 Prerequisites

-   **Credentials:** You must have valid login credentials for the [MySonicwall portal](https://www.mysonicwall.com).
-   **Device Information:** You must have the **Serial Number** and **Authentication Code** for the SonicWall device. This information is typically found on the original packaging or on a sticker on the device itself.
-   **Tenant Information:** You must know the name of the tenant the device will be assigned to.

> **TERMINOLOGY NOTE:** SonicWall uses "Authentication Code" (not "Activation Code"). The Authentication Code is printed on the device label alongside the Serial Number.

## 4.0 Procedure

1.  **Log In to MySonicwall Portal:**
    -   Navigate to `https://www.mysonicwall.com`.
    -   Log in with your authorized credentials.

2.  **Navigate to Product Registration:**
    -   Once logged in, locate and click on the **Register Products** option in the portal's main navigation menu.

3.  **Select or Create Tenant:**
    -   You will be prompted to associate the device with a tenant.
    -   **If the tenant already exists,** select it from the list.
    -   **If the tenant does not exist,** select the **Create New Tenant** option and follow the on-screen instructions to create it.

4.  **Enter Device Details:**
    -   Enter the **Serial Number** and **Authentication Code** from the device or its packaging into the appropriate fields.

5.  **Assign a Friendly Name:**
    -   In the "Friendly Name" field, provide a descriptive name for the device that easily identifies its location or purpose (e.g., `Obera Fairhope`).

6.  **Set Management Options:**
    -   Under the "Management Options" section, select **On Box**.
    -   **On Box** = Firewall managed locally through its web interface
    -   **Cloud Management** = Managed via SonicWall Network Security Manager (NSM)

7.  **Complete Registration:**
    -   Click the **Done** or **Register** button to finalize the process.
    -   **Note the Registration Code** displayed - you will need this for the firewall.

8.  **Obtain Registration Code (if not shown):**
    -   Navigate to **My Products** in MySonicWall.
    -   Click on the registered device name or serial number.
    -   Locate the **Registration Code** in the device details.
    -   Copy this code for the next section.

## 5.0 Sync Registration to Firewall (CRITICAL)

> **IMPORTANT:** Portal registration alone is NOT sufficient. The firewall must be synced to recognize the registration and enable firmware updates.

1.  **Access the Firewall:**
    -   Log into the SonicWall web interface.

2.  **Navigate to MySonicWall Settings:**
    -   Go to **Device > Settings > MySonicWall** (Gen 7)
    -   Or **System > Administration > MySonicWall** (Gen 6)

3.  **Check Registration Status:**
    -   If status shows "Registered" with valid licenses, registration is complete.
    -   If status shows "Not Registered", proceed to Step 4.

4.  **Enter Registration Code:**
    -   Enter the **Registration Code** obtained from the MySonicWall portal.
    -   Click **Register** or **Submit**.
    -   Wait for confirmation message.

5.  **Alternative: Login with MySonicWall Credentials:**
    -   If Registration Code entry is not available, enter your MySonicWall credentials directly.
    -   Click **Login** or **Associate**.
    -   The firewall will authenticate and sync registration.

6.  **Verify Licenses Synchronized:**
    -   Navigate to **Device > Settings > Licenses**.
    -   Confirm all purchased services show as active with valid expiration dates.

## 6.0 Verification

-   After completing the procedure, navigate to the **Products** list within the MySonicwall portal.
-   Confirm that the newly registered device appears in the list, associated with the correct tenant and friendly name.
-   On the firewall, confirm registration status shows "Registered" with synchronized licenses.

## 7.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| "Serial number is already registered to another account" | Device is registered under a different MySonicWall account. Log into the correct account, or contact SonicWall support to request a transfer. |
| Firewall shows "Not Registered" after portal registration | Portal registration doesn't auto-sync to firewall. Complete Section 5.0 to sync via Registration Code or credentials. |
| Registration Code not found in portal | Click INTO the device details (not just view in list). Look under "Product Details" or "Registration Info" tab. |
| Firmware upload fails with "Device not registered" | Complete Section 5.0. Registration must be synced to the firewall before firmware operations work. |
| Licenses not showing on firewall | Navigate to Device > Settings > Licenses and click "Synchronize". Ensure firewall has internet access. |
| Cannot access MySonicWall from firewall | Verify WAN has internet connectivity. Check DNS resolution. Firewall needs HTTPS access to `licensemanager.sonicwall.com`. |

## 8.0 References

-   MySonicwall Portal: `https://www.mysonicwall.com`
-   SOP-NET-001: Initial SonicWall Firewall Setup
-   SOP-NET-006: SonicWall Configuration Backup

## 9.0 Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2025-12-02 | Gemini | Initial document creation. |
| 1.1 | 2025-12-29 | Jeremy Smith | SME Review: Corrected terminology (Authentication Code, not Activation Code). Added Section 5.0 for firewall-side registration sync. Added troubleshooting table. Lessons learned from Jubilee Pool deployment. |

---
**End of Document**
---
