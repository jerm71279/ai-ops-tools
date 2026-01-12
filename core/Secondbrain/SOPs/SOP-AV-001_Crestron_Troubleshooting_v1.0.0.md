# Standard Operating Procedure: SOP-AV-001

**Title:** Crestron Panel - "Loading Content" Error Troubleshooting
**Version:** 1.0
**Date:** 2025-12-02

---

## 1.0 Purpose

This document provides a systematic procedure for diagnosing and resolving the "Loading Content" error on Crestron scheduling panels (TSW-770/1070 series) that are integrated with the AskCody room booking service.

## 2.0 Scope

This SOP applies to all IT Support and AV Technicians responsible for maintaining Crestron AV hardware and associated room scheduling software. It specifically covers Crestron TSW-770, TSW-1070, and similar models failing to connect to the AskCody service.

## 3.0 Responsibilities

- **IT Support Staff:** First line of support for troubleshooting network and application-level issues.
- **AV Technicians:** Responsible for hardware-level troubleshooting, firmware updates, and factory resets.

## 4.0 Prerequisites

Before beginning this procedure, ensure you have the following:

- Administrative PIN for the Crestron panel's settings menu.
- Credentials for the AskCody Admin Portal.
- Credentials for the Crestron XiO Cloud portal or direct web UI access to the panel.
- Network access to the same VLAN as the affected panel for testing purposes.

## 5.0 Procedure

Follow these steps sequentially. Do not proceed to the next step unless the current one fails to resolve the issue.

### 5.1 Step 1: Verify Network and Internet Connectivity

**Objective:** Confirm the panel has a valid network connection and can reach required external services.

1.  **Check Local Network Configuration:**
    -   Access the panel's setup menu (requires admin PIN).
    -   Navigate to `Settings` → `Network`.
    -   Verify that the panel has a valid IP Address, Subnet Mask, Gateway, and DNS server assigned.
2.  **Test Network Path:**
    -   From another device on the same VLAN, attempt to `ping` the AskCody service endpoint (e.g., `ping <tenant>.askcody.com`).
    -   If the ping fails, investigate network infrastructure.
3.  **Validate Firewall Rules:**
    -   Confirm that outbound HTTPS traffic on **TCP port 443** to `*.askcody.com` is permitted.
    -   Recent changes to VLANs, firewalls, or proxies are common causes of blockage.

### 5.2 Step 2: Confirm AskCody Service Health

**Objective:** Ensure the issue is not related to a service-wide outage or misconfiguration in the AskCody platform.

1.  **Log in to the AskCody Admin Portal.**
2.  **Verify Room Resource:** Check that the room resource associated with the panel is correctly configured and assigned.
3.  **Check License Status:** Ensure all required licenses for the panel and resource are active.
4.  **Check for Service Incidents:** Review the official AskCody status page for any reported service-wide incidents.

### 5.3 Step 3: Re-authenticate the Panel

**Objective:** Refresh the authentication token and configuration URL on the device.

1.  **Access Panel Setup:** On the Crestron panel, exit the AskCody app to access the setup menu (typically by holding a screen corner for ~10 seconds).
2.  **Navigate to Web App Settings:** Go to `Apps` → `Web App Settings` (or the specific AskCody integration menu).
3.  **Verify URL:**
    -   Check the configured AskCody URL.
    -   It must match your tenant’s booking page exactly (e.g., `https://<tenant>.askcody.com/panel/...`).
4.  **Re-authenticate:** Use the on-screen options to re-enter credentials or re-pair the device with the AskCody service.

### 5.4 Step 4: Clear Cached Configuration and Reload

**Objective:** Remove outdated cached data that may be causing the loading loop.

1.  **Navigate to Application Settings:** In the panel's setup menu, find the application management section.
2.  **Clear Cache:** Select the option to `Clear Cache` or `Reload Web App`.
3.  **Reboot:** After clearing the cache, perform a soft reboot of the panel from the settings menu.

> **Note:** This step is critical if the AskCody URL has recently changed due to a migration or tenant update.

### 5.5 Step 5: Update Firmware and Application

**Objective:** Resolve potential compatibility issues between the panel's firmware and the AskCody application.

1.  **Check Current Version:** Log in to **Crestron XiO Cloud** or the panel's local web UI to identify the current firmware version.
2.  **Update Firmware:** If the firmware is outdated, update it to the latest stable release recommended for use with AskCody.
3.  **Verify App Version:** Ensure the AskCody application package installed on the panel is the latest version.

### 5.6 Step 6: Hard Reboot and Factory Reset (Last Resort)

**Objective:** Return the panel to a factory default state and perform a clean installation.

1.  **Perform Factory Reset:**
    -   From the panel's setup menu, locate the option to perform a factory reset.
    -   **WARNING:** This will erase all configuration from the device.
2.  **Reinstall Application:** After the reset is complete, reinstall the AskCody integration package.
3.  **Re-register Panel:** Follow the initial setup process to re-register the panel in the AskCody Admin Portal and configure it for the correct room resource.

## 6.0 Escalation

If the procedure outlined above does not resolve the issue, escalate the ticket to a **Senior AV Engineer** and open a support case with the appropriate vendor (Crestron or AskCody). Include all troubleshooting steps performed.

## 7.0 Common Causes Summary

- **URL Mismatch:** The URL in the panel's web app settings does not match the current AskCody tenant URL.
- **Cached Session:** The panel is holding onto an old, invalid session. (Resolved by Step 5.4)
- **Network Block:** Firewall or proxy rules are blocking outbound HTTPS traffic to `*.askcody.com`. (Resolved by Step 5.1)

## 8.0 Revision History

| Version | Date       | Author | Change Description                |
|---------|------------|--------|-----------------------------------|
| 1.0     | 2025-12-02 | Gemini | Initial document creation from source. |

