Loaded cached credentials.
```markdown
# Standard Operating Procedure: Network Configuration

| | |
| --- | --- |
| **Document ID:** | SOP-NET-002 |
| **Title:** | MikroTik Router Configuration |
| **Version:** | 1.0 |
| **Status:** | Final |
| **Author:** | System Administrator |
| **Approved By:** | Director of Technology |
| **Effective Date:** | 2025-12-02 |

---

## 1.0 Purpose

The purpose of this Standard Operating Procedure (SOP) is to provide a standardized, step-by-step guide for the basic configuration of MikroTik routers. Adhering to this procedure ensures that all routers are set up with consistent, secure, and reliable settings.

## 2.0 Scope

This SOP applies to all IT personnel and network engineers responsible for deploying and managing MikroTik routers within the organization's infrastructure. This document covers the initial setup and essential configuration components. Advanced or client-specific configurations are outside the scope of this document.

## 3.0 Responsibilities

-   **Network Engineers / IT Technicians:** Responsible for executing the procedures outlined in this document.
-   **Director of Technology:** Responsible for reviewing and approving this SOP and any subsequent revisions.

## 4.0 Prerequisites

-   Physical or remote access to the MikroTik router.
-   Access to the MikroTik WinBox utility.
-   Knowledge of the client's network requirements, including WAN IP information, and internal IP schema.

## 5.0 Procedure

This procedure outlines the key configuration steps to be performed in the MikroTik router's interface, typically using WinBox.

### 5.1 System: Identity

Set a unique and identifiable name for the router.

1.  Navigate to **System > Identity**.
2.  Set the `Identity` field to a descriptive name related to the client or location (e.g., `ClientName-Router`).

### 5.2 Interfaces

Review and manage the physical and virtual interfaces.

1.  Navigate to **Interfaces**.
2.  Disable any unused physical ports.
3.  If required, create VLANs by clicking the **Add (+)** button and selecting **VLAN**. Assign a `Name`, `VLAN ID`, and associate it with a physical `Interface`.

### 5.3 Bridge

Create a bridge to logically group multiple interfaces (e.g., for a single LAN segment).

1.  Navigate to **Bridge**.
2.  On the **Bridge** tab, click **Add (+)** to create a new bridge.
3.  On the **Ports** tab, click **Add (+)** to assign interfaces (physical ports or VLANs) to the newly created bridge.

### 5.4 IP: Addresses

Assign IP addresses to the router's interfaces.

1.  Navigate to **IP > Addresses**.
2.  Click **Add (+)** to assign an IP address.
3.  Specify the `Address` with its subnet (e.g., `192.168.1.1/24`).
4.  Assign it to the correct `Interface` (e.g., the WAN port, a LAN bridge, or a VLAN).
5.  Repeat for all necessary interfaces (WAN, LAN, etc.).

### 5.5 IP: DHCP Client

Configure the WAN interface to receive an IP address automatically if a static IP is not provided by the ISP.

1.  Navigate to **IP > DHCP Client**.
2.  Click **Add (+)**.
3.  Set the `Interface` to the primary WAN port (e.g., `ether1`).
4.  Ensure this is only used if the WAN IP is dynamic.

### 5.6 IP: Pool

Define the range of IP addresses to be distributed by the DHCP server.

1.  Navigate to **IP > Pool**.
2.  Click **Add (+)**.
3.  Assign a `Name` to the pool (e.g., `lan-pool`).
4.  Define the `Addresses` range. Format: `192.168.1.20-192.168.1.200`.

### 5.7 IP: DHCP Server

Configure the DHCP server to assign IP addresses to client devices on the LAN.

1.  Navigate to **IP > DHCP Server**.
2.  On the **DHCP** tab, click **Add (+)**.
3.  Configure the server instance:
    -   **Name:** A descriptive name for the server.
    -   **Interface:** The LAN bridge or interface the server will listen on.
    -   **Address Pool:** Select the pool created in step 5.6.
4.  Navigate to the **Networks** tab and click **Add (+)**.
5.  Define the network details:
    -   **Address:** The network address and subnet (e.g., `192.168.1.0/24`).
    -   **Gateway:** The router's LAN IP address (e.g., `192.168.1.1`).
    -   **DNS Servers:** The DNS servers to be provided to clients.
6.  Navigate to the **Leases** tab to view active leases. Static leases can be created here by assigning an IP to a specific MAC address.

### 5.8 IP: DNS

Configure the DNS servers that the router itself will use for resolution.

1.  Navigate to **IP > DNS**.
2.  In the `Servers` field, enter the IP addresses of the primary and secondary DNS servers.

### 5.9 IP: Routes

Ensure a default route exists for outbound internet traffic. This is often added automatically but should be verified.

1.  Navigate to **IP > Routes**.
2.  Check for a route where `Dst. Address` is `0.0.0.0/0`.
3.  If it does not exist, click **Add (+)** and create it:
    -   **Dst. Address:** `0.0.0.0/0`
    -   **Gateway:** The ISP's gateway IP address (the WAN gateway).

### 5.10 IP: Firewall - NAT

Configure Network Address Translation (NAT) to allow devices on the internal network to access the internet.

1.  Navigate to **IP > Firewall > NAT**.
2.  Click **Add (+)** to create a new rule.
3.  In the **General** tab:
    -   **Chain:** `srcnat`
    -   **Out. Interface:** Set to the primary WAN port (e.g., `ether1`).
4.  In the **Action** tab:
    -   **Action:** `masquerade`

### 5.11 IP: Firewall - Firewall Rules

Implement basic firewall rules to block common unsolicited inbound traffic.

1.  Navigate to **IP > Firewall > Firewall Rules**.
2.  Create rules to drop inbound traffic on the WAN interface for the following ports. For each rule, set **Chain**=`input`, **In. Interface**=`ether1` (or your WAN port), and **Action**=`drop`.

| Protocol | Destination Port |
| :--- | :--- |
| UDP | 53, 123, 161 |
| TCP | 21, 22, 23, 53, 80, 443, 8080, 2000 |

### 5.12 IP: Services

Disable non-essential services and change the port for WinBox to enhance security.

1.  Navigate to **IP > Services**.
2.  Disable all services **except for `winbox`**.
3.  Double-click on `winbox` and change the `Port` to `8899`.

### 5.13 Tools: Telnet/SSH

The Telnet/SSH client can be used for initial setup of other network devices, such as access points.

1.  Navigate to **Tools > Telnet** or **Tools > SSH**.
2.  Enter the IP address of the device you need to configure.

## 6.0 Revision History

| Version | Date | Author | Change Description |
| :--- | :--- | :--- | :--- |
| 1.0 | 2025-12-02 | System Administrator | Initial document creation. |

```
