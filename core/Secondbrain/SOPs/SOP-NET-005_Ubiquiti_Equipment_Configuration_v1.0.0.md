# Standard Operating Procedure: Ubiquiti Equipment Configuration for New Customers

| | |
|---|---|
| **Document ID:** | SOP-NET-005 |
| **Title:** | Ubiquiti Equipment Configuration for New Customers |
| **Category:** | Network Administration |
| **Version:** | 1.2 |
| **Status:** | Draft |
| **Author:** | System |
| **Creation Date:** | 2025-12-04 |
| **Approval Date:** | Pending |

---

### 1.0 Purpose

To establish a standardized, repeatable process for configuring Ubiquiti/UniFi network equipment (switches, access points) for new customer deployments, ensuring proper firmware levels and consistent network configuration.

### 2.0 Scope

This SOP applies to all Network Technicians responsible for deploying Ubiquiti UniFi equipment for clients. It covers switch pre-adoption firmware upgrades, access point deployment, and UniFi Controller adoption.

### 3.0 Definitions

* **SOP:** Standard Operating Procedure
* **AP:** Access Point
* **USW:** UniFi Switch
* **SSH:** Secure Shell
* **DHCP:** Dynamic Host Configuration Protocol
* **OUI:** Organizationally Unique Identifier (MAC address prefix)

### 4.0 Roles & Responsibilities

* **Network Technician/Engineer:** Responsible for executing all steps outlined in this SOP, ensuring equipment is correctly configured for deployment.

### 5.0 Prerequisites

* Ubiquiti UniFi switch and/or access point(s)
* Access to UniFi Network Controller (cloud or self-hosted)
* SSH client (PuTTY or similar)
* Network access to customer subnet
* Customer subnet information from CUSTOMER_SUBNET_TRACKER.csv

---

### 6.0 Procedure

#### 6.0.1 Lab Pre-Staging Environment

All customer equipment is configured in the OberaConnect lab environment before deployment:

| Component | Details |
|-----------|---------|
| Core Switch | Ubiquiti switch (lab) |
| Firewall | SonicWall (lab) |
| Lab Subnet | 10.55.1.0/24 |
| DHCP Source | Lab SonicWall |

**Workflow:**
1. Connect customer device to lab core Ubiquiti switch
2. Device receives DHCP from lab SonicWall (10.55.1.x)
3. Configure/upgrade device in lab environment
4. Device is ready for customer install date

> All device discovery and configuration steps below assume the device is connected to the lab network on 10.55.1.0/24.

#### 6.1 Pre-Deployment: Identify Device IP

After connecting the device to the lab network:

1. **From Windows CMD**, run ping sweep to find active devices:
   ```cmd
   for /L %i in (1,1,254) do @(ping -n 1 -w 30 10.55.1.%i >nul && echo 10.55.1.%i is up)
   ```
   > Adjust subnet (10.55.1) to match customer network. Only responding IPs will be displayed.

2. **Then check ARP table for MAC addresses:**
   ```cmd
   arp -a | findstr "10.55.1"
   ```

3. **Identify Ubiquiti devices** by MAC prefix (OUI):
   | Prefix | Manufacturer |
   |--------|--------------|
   | 24-5a-4c | Ubiquiti |
   | 28-70-4e | Ubiquiti |
   | 78-45-58 | Ubiquiti |
   | 80-2a-a8 | Ubiquiti |
   | 74-83-c2 | Ubiquiti |
   | dc-9f-db | Ubiquiti |
   | f0-9f-c2 | Ubiquiti |

4. **Alternative:** Check DHCP leases on SonicWall:
   * Navigate to **Network > DHCP Server > Current DHCP Leases**
   * Look for recent leases with Ubiquiti MAC prefixes or hostnames like `U7-Pro`, `UBNT`

#### 6.2 Factory Reset (If Device Previously Adopted)

> **NOTE:** If device was previously adopted to another controller, it must be factory reset before re-adoption.

**Physical Reset Button:**
1. Locate the reset button (small pinhole, usually near power port)
2. With device powered on, press and hold reset button for 10+ seconds
3. Release when LED flashes indicating reset
4. Device will reboot to factory defaults (~2-3 minutes)

**SSH Reset (if accessible):**
```
ssh ubnt@<device_ip>
# Default credentials: ubnt / ubnt

# For switches:
set-default

# For access points:
set-default
# OR
syswrapper.sh restore-default
```

**UniFi Controller Reset (if still connected):**
1. In UniFi Controller, select the device
2. Click **Settings** (gear icon)
3. Click **Forget** to remove from controller
4. Device will reset and become available for new adoption

#### 6.3 Switch Configuration (Pre-Adoption)

> **IMPORTANT:** Switches require SSH firmware upgrade BEFORE adoption into UniFi Controller. APs do NOT require this step.

1. **SSH into the switch using PuTTY:**
   1. Launch **PuTTY** from Start Menu or desktop
   2. In the **Session** category:
      - **Host Name (or IP address):** Enter the switch IP (e.g., `10.55.1.25`)
      - **Port:** `22`
      - **Connection type:** Select **SSH**
   3. Click **Open**
   4. If prompted with a security alert about the server's host key, click **Accept** (first connection only)
   5. At the `login as:` prompt, enter: `ubnt`
   6. At the `password:` prompt, enter: `ubnt`

   > **Default credentials:** Username `ubnt`, Password `ubnt`

   You should now see the UniFi switch command prompt (e.g., `UBNT-US.v6.6.65#`)

2. **Upgrade firmware via SSH:**
   At the switch command prompt, enter the upgrade command:
   ```
   upgrade <firmware_url>
   ```

   > **NOTE:** Some older firmware versions use `fwupdate` instead of `upgrade`. If `upgrade` fails, try:
   > ```
   > fwupdate --download <firmware_url>
   > ```

3. **Firmware URLs by model:**

   **USW-16-POE (v7.1.26):**
   ```
   upgrade https://dl.ui.com/unifi/firmware/USMULTUSW16POE/7.1.26.15869/US.MULT.USW_16_POE_7.1.26+15869.240926.2129.bin
   ```

   | Model | Version | Firmware URL |
   |-------|---------|--------------|
   | USW-16-POE | 7.1.26 | `https://dl.ui.com/unifi/firmware/USMULTUSW16POE/7.1.26.15869/US.MULT.USW_16_POE_7.1.26+15869.240926.2129.bin` |

   > See the **Ubiquiti Firmware Reference** document on [SharePoint > Technical Docs](https://oberaconnect.sharepoint.com/sites/support/Shared%20Documents/How%20To%27s/SOPs) for complete firmware URL reference and additional models.

4. **Wait for reboot** - Switch will automatically reboot after firmware download completes (~3-5 minutes).

5. **Verify firmware** by SSH back in after reboot:
   ```
   info
   ```

#### 6.4 Access Point Configuration

> **NOTE:** APs can be adopted directly without manual firmware upgrade. The UniFi Controller will push firmware during adoption.

1. Connect AP to PoE switch port or PoE injector
2. Wait for LED to show solid white (ready for adoption)
3. Proceed to Section 6.5 for adoption

#### 6.5 UniFi Controller Adoption

##### 6.5.1 Same-Subnet Adoption (L2)

If device and controller are on the same network subnet:

1. **Log into UniFi Network Controller**

2. **Navigate to Devices** - Pending devices will appear automatically

3. **Adopt device:**
   * Click on pending device
   * Click **Adopt**
   * Wait for provisioning to complete

4. **Configure device settings:**
   * Set device name (e.g., `SFWB_Main-SW01`, `SFWB_Rockwell-AP01`)
   * Assign to appropriate site

##### 6.5.2 Cross-Subnet Adoption (L3)

If device is on a different subnet than the controller (common in customer deployments):

1. **SSH into the device using PuTTY:**
   - Launch PuTTY, enter the device IP in **Host Name**, Port `22`, Connection type **SSH**
   - Click **Open**, accept host key if prompted
   - Login: `ubnt` / `ubnt`

2. **Set the inform URL to point to the controller:**
   ```
   set-inform http://<controller_ip>:8080/inform
   ```

   For cloud-hosted controllers:
   ```
   set-inform https://unifi.ui.com/inform
   ```

3. **Verify inform URL:**
   ```
   info
   ```
   Look for `Status: Connected (http://<controller>:8080/inform)`

4. **Adopt in controller** - Device should now appear in pending devices

> **NOTE:** The inform URL persists across reboots. For DHCP Option 43 or DNS-based adoption, configure on the DHCP server or internal DNS.

##### 6.5.3 Post-Adoption Configuration

5. **For switches - Configure ports:**
   * Set port profiles as needed
   * Configure VLANs if applicable
   * Enable PoE on AP ports

6. **For APs - Configure wireless:**
   * Assign to appropriate WLAN group
   * Set transmit power if needed
   * Configure band steering preferences

#### 6.6 Network Configuration Standards

Apply the following defaults per customer subnet:

| Setting | Default Value |
|---------|---------------|
| Gateway | .1 |
| DHCP Range | .200-.254 |
| Static Range | .2-.199 |

| IP Range | Purpose |
|----------|---------|
| .1 | Gateway/Router |
| .2-.99 | Infrastructure (switches, APs, servers) |
| .100-.199 | Static client devices (printers, cameras) |
| .200-.254 | DHCP pool |

> See the **Network Configuration Standards** document on [SharePoint > Technical Docs](https://oberaconnect.sharepoint.com/sites/support/Shared%20Documents/How%20To%27s/SOPs) for complete reference.

---

### 7.0 Verification & Quality Checks

* Confirm device shows as "Online" in UniFi Controller
* Verify firmware is current (Controller will show update available if not)
* Test connectivity from client devices
* For APs: Verify SSID broadcast and client connection
* For switches: Verify port connectivity and PoE delivery

### 8.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| Cannot find device IP | 1. Verify device has power (LEDs active). 2. Check DHCP leases on SonicWall. 3. Ensure device is on same L2 network. |
| SSH connection refused | 1. Device may still be booting. 2. Device may already be adopted (different credentials). 3. Try default creds: ubnt/ubnt |
| Firmware upgrade fails | 1. Verify URL is correct and accessible. 2. Check device has internet access. 3. Try alternate firmware version. |
| Device not appearing in Controller | 1. Verify L2 connectivity to Controller. 2. Check if device is on different VLAN. 3. Use UniFi mobile app for local discovery. |
| Adoption fails | 1. Reset device to factory defaults. 2. Verify Controller is accessible from device subnet. 3. Check for IP conflicts. |

### 9.0 Related Documents

* [Ubiquiti Firmware Reference](https://oberaconnect.sharepoint.com/sites/support/Shared%20Documents/How%20To%27s/SOPs)
* [Network Configuration Standards](https://oberaconnect.sharepoint.com/sites/support/Shared%20Documents/How%20To%27s/SOPs)
* [Customer Subnet Tracker](https://oberaconnect.sharepoint.com/sites/support/Shared%20Documents/How%20To%27s/SOPs)
* SOP-NET-001: Initial SonicWall Firewall Setup

### 10.0 Revision History

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2025-12-04 | System | Initial document creation |
| 1.1 | 2025-12-29 | Jeremy Smith | SME Review: Added Section 6.2 (Factory Reset for pre-adopted devices). Added L3 adoption with set-inform URL (6.5.2). Added firmware command variation note. Renumbered sections. |
| 1.2 | 2025-12-30 | Jeremy Smith | Updated SSH access instructions to use PuTTY as preferred method (Sections 6.3, 6.5.2). Added step-by-step PuTTY connection procedure. |

### 11.0 Approval

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | Network Manager | | |
