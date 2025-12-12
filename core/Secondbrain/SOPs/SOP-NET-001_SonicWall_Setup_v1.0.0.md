Loaded cached credentials.
```markdown
# Standard Operating Procedure: Initial SonicWall Firewall Setup

| | |
|---|---|
| **Document ID:** | SOP-NET-001 |
| **Title:** | Initial SonicWall Firewall Setup |
| **Category:** | Network Administration |
| **Version:** | 1.0 |
| **Status:** | Final |
| **Author:** | System |
| **Creation Date:** | 2025-12-02 |
| **Approval Date:** | 2025-12-02 |

---

### 1.0 Purpose

To establish a standardized, repeatable process for the initial out-of-the-box configuration of a new SonicWall firewall, ensuring all baseline security and system settings are applied before deployment.

### 2.0 Scope

This SOP applies to all Network Technicians responsible for deploying new SonicWall firewalls for clients. It covers the process from device registration to the final pre-installation configuration step.

### 3.0 Definitions

*   **SOP:** Standard Operating Procedure
*   **WAN:** Wide Area Network; the port connecting to the internet.
*   **LAN:** Local Area Network; the port for the internal network.
*   **MySonicwall Portal:** The official online portal for managing SonicWall device licenses, registration, and firmware.
*   **GUI:** Graphical User Interface.
*   **DNS:** Domain Name System.
*   **IPS:** Intrusion Prevention System.
*   **Geo-IP:** IP address filtering based on geographic location.

### 4.0 Roles & Responsibilities

*   **Network Technician/Engineer:** Responsible for executing all steps outlined in this SOP, ensuring the firewall is correctly configured for on-site installation.

### 5.0 Prerequisites

*   A new SonicWall firewall device.
*   Access to the MySonicwall portal with valid credentials.
*   A computer with an Ethernet port.
*   Two Ethernet cables.
*   Client's network circuit information sheet (containing static IP, subnet, gateway).

---

### 6.0 Procedure

#### 6.1 Initial Connection and Access

1.  **Register Device:** Log in to the MySonicwall portal and register the new firewall device if it has not been done already.
2.  **Connect Hardware:**
    *   Connect the firewall's **WAN (X1)** port to an active internet connection.
    *   Connect your computer's Ethernet port to the firewall's **LAN (X0)** port.
3.  **Power On:** Power on the SonicWall and wait for the status lights for both WAN and LAN ports to turn solid green.
4.  **Configure Static IP:** On your computer, manually configure the IPv4 network adapter settings as follows:
    *   **IP address:** `192.168.168.2`
    *   **Subnet mask:** `255.255.255.0`
    *   **Default gateway:** `192.168.168.168`
    *   **DNS Server:** `8.8.8.8` (or any other public DNS)
5.  **Log In to Firewall:**
    *   Open a web browser in incognito/private mode and navigate to `http://192.168.168.168`.
    *   Use the default credentials to log in:
        *   **Username:** `admin`
        *   **Password:** `password`
    *   You will be prompted to change the administrator password. Set a new, secure password.
    *   When prompted for setup type, select **Manual Setup**.

#### 6.2 System Configuration and Firmware Update

1.  **Sync Licenses:** Navigate to **System > Licenses**. Log in with your MySonicwall credentials to synchronize the device registration and service licenses.
2.  **Set Firewall Name:** Go to **System > Administration**. Set a descriptive name for the firewall (e.g., `Obera-Fairhope`).
3.  **Configure Admin Timeout:**
    *   On the same page, under **Login/Multiple Administrators**, change **Log out the Admin after inactivity (minutes)** to `60`.
4.  **Verify Management Ports:** Select the **Management** tab. Ensure **HTTP Port** is `80` and **HTTPS Port** is `443`.
5.  **Download Latest Firmware:**
    *   Go to the MySonicwall portal and select the firewall.
    *   Navigate to the **Firmware** tab and download the latest stable firmware release (`.sig` file).
6.  **Update Firmware:**
    *   Return to the firewall GUI and navigate to **System > Firmware and Backups**.
    *   Click **Upload Firmware** and select the `.sig` file you downloaded.
    *   **Important:** Check the box to create a backup of your current settings before proceeding.
    *   After the upload completes, click the **Boot** button next to the newly uploaded firmware version with the "Reboot with current settings" option.
    *   The firewall will reboot, which can take 3-5 minutes.

#### 6.3 Security Services Configuration

After the firewall reboots, log back in and configure the following security settings. Click **Accept** at the bottom of each page to save changes.

1.  **UDP Flood Protection:**
    *   Navigate to **Firewall Settings > Flood Protection**.
    *   Select the **UDP** tab.
    *   Check **Enable UDP Flood Protection**.
    *   From the **UDP Flood Attack Protection Destination List** dropdown, select **LAN Subnets**.
2.  **AppFlow Reporting:**
    *   Navigate to **AppFlow > Flow Reporting > Settings**.
    *   Toggle on **Enable Real-Time Data Collection**.
    *   Toggle on **Enable AppFlow to Local Collector**.
    *   Click **Accept**. The firewall will reboot to apply this change. Log back in after it comes back online.
3.  **Gateway Anti-Virus:**
    *   Navigate to **Security > Gateway Anti-Virus**.
    *   Check **Enable Gateway Anti-Virus**.
    *   Check **Enable Inbound and Outbound Inspection** for all listed protocols.
4.  **Intrusion Prevention (IPS):**
    *   Navigate to **Security > Intrusion Prevention**.
    *   Check **Enable IPS**.
    *   Set **High Priority Attacks** to **Prevent All**.
    *   Set **Medium Priority Attacks** to **Prevent All**.
    *   Set **Low Priority Attacks** to **Detect All**.
5.  **Anti-Spyware:**
    *   Navigate to **Security > Anti-Spyware**.
    *   Check **Enable Anti-Spyware**.
    *   Set **High Priority Attacks** to **Prevent All**.
    *   Set **Medium Priority Attacks** to **Prevent All**.
    *   Set **Low Priority Attacks** to **Detect All**.
    *   Ensure all protocols are selected for inspection.
6.  **Geo-IP Filter:**
    *   Navigate to **Security > Geo-IP Filter**.
    *   Check **Block connections to/from countries selected in Countries tab**.
    *   Go to the **Countries** tab and select high-risk countries to block (e.g., China, Russia, North Korea, Iran).
    *   Check **Block all unknown countries**.
    *   From the **Geo-IP Exclusion Object** dropdown, select **Default Geo-IP and Botnet Exclusion Group**.
7.  **Botnet Filter:**
    *   Navigate to **Security > Botnet Filter**.
    *   Check **Block connections to/from botnet command and control servers**.

#### 6.4 Network DNS Configuration

1.  Navigate to **Network > DNS**.
2.  Select **Specify DNS Servers Manually**.
3.  Configure DNS entries based on the client's environment:
    *   **With Domain Controllers:** Set DNS Server 1 and 2 to the client's primary and secondary domain controllers. Set DNS Server 3 to a public DNS (e.g., `8.8.8.8`).
    *   **Without Domain Controllers:** Set DNS servers to the ISP-provided DNS or a reliable public DNS service (e.g., `8.8.8.8`, `1.1.1.1`).

#### 6.5 Final WAN Interface Configuration

> **WARNING:** Executing this final step will reconfigure the WAN (X1) interface, and you will lose access to the firewall's management GUI until it is physically installed at the client's site. Ensure all previous configuration steps are completed and verified before proceeding.

1.  Navigate to **Network > Interfaces**.
2.  Locate the **X1 (WAN)** interface and click the pencil icon to edit it.
3.  Refer to the client's circuit sheet for the following information:
    *   Set **IP Assignment** to **Static**.
    *   Enter the **IP Address** (first usable IP from the client's static block).
    *   Enter the **Subnet Mask**.
    *   Enter the **Default Gateway**.
    *   Set the **DNS Server(s)** to either the client's domain controllers or public DNS, as determined in step 6.4.
4.  Under the **Management** section for the X1 interface, ensure both **HTTPS** and **Ping** are checked to allow remote management and diagnostics.
5.  Click **Accept** to save the changes. Access to the GUI will be lost. The firewall is now ready for on-site installation.

---

### 7.0 Verification & Quality Checks

*   Confirm the device is registered and all licenses are active in the MySonicwall portal.
*   Verify the firmware has been updated to the latest stable release.
*   Double-check that all security services (AV, IPS, Geo-IP, Botnet) are enabled and configured as per Section 6.3.
*   Confirm the WAN interface settings are transcribed correctly from the client circuit sheet before clicking the final 'Accept'.

### 8.0 Troubleshooting

| Issue | Resolution |
|---|---|
| Cannot access login page at 192.168.168.168. | 1. Verify your computer's static IP settings match Section 6.1. <br> 2. Ensure the Ethernet cable is securely connected to the LAN (X0) port. <br> 3. Confirm the firewall's LAN light is green. |
| Licenses fail to synchronize. | 1. Ensure the WAN port is connected to an active internet connection. <br> 2. Verify the MySonicwall portal credentials are correct. <br> 3. Reboot the firewall and try again. |
| Lost access after WAN configuration. | This is expected behavior. The device must now be installed on-site to be accessed via its new WAN or LAN IP address. |

### 9.0 Related Documents

*   Client Network Circuit Information Sheet

### 10.0 Revision History

| Version | Date | Author | Change Description |
|---|---|---|---|
| 1.0 | 2025-12-02 | System | Initial document creation from source material. |

### 11.0 Approval

| Name | Role | Signature | Date |
|---|---|---|---|
| | Network Manager | | |
```
