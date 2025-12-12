Loaded cached credentials.
```markdown
# SOP-AD-001: Active Directory Domain Connection Troubleshooting

**Version:** 1.0
**Status:** Final
**Author:** System Administrator
**Date:** 2025-12-02

---

## 1.0 Purpose

The purpose of this Standard Operating Procedure (SOP) is to provide a systematic process for diagnosing and resolving network connectivity issues between an endpoint (computer or user) and the Active Directory (AD) domain controller.

## 2.0 Scope

This procedure applies to any domain-joined computer that is unable to communicate with the Active Directory domain. This includes issues related to user logons, accessing network resources, or receiving group policy updates.

## 3.0 Prerequisites

-   Administrative privileges on the affected endpoint machine.
-   Knowledge of the network's Domain Controller (DC) IP address(es).
-   Access to firewall configuration, if applicable.
-   Familiarity with basic Windows networking commands (`ipconfig`, `nltest`).

## 4.0 Procedure

### 4.1 Initial DNS and Network Configuration Diagnostics

1.  **Open Command Prompt:** On the affected machine, open a Command Prompt window with administrative privileges.
2.  **Gather Network Information:** Execute the following command to display the current network configuration:
    ```cmd
    ipconfig /all
    ```
3.  **Analyze Configuration:** Review the output and verify the following:
    *   The machine has a valid IP address for its subnet.
    *   Note whether the network adapter is configured for **DHCP** or a **Static IP**.
    *   Identify the listed DNS servers.

### 4.2 Correcting DNS Configuration

1.  **Verify DNS Server Order:** The DNS server settings are critical for domain communication. Ensure they are configured in the correct order of priority:
    *   **Primary DNS:** Must be the primary Domain Controller's IP address.
    *   **Secondary DNS:** Should be the secondary Domain Controller's IP address, if one exists. If not, this can be the circuit provider's DNS.
    *   **Tertiary DNS:** A public DNS server (e.g., `8.8.8.8`) can be used as a final fallback.

    *Example Hierarchy:*
    *   Primary: `192.168.1.1` (Primary DC)
    *   Secondary: `192.168.1.2` (Secondary DC)
    *   Tertiary: `142.190.111.111` (ISP DNS)

2.  **Apply DNS Changes:** If the DNS settings are incorrect, update them in the machine's network adapter properties.
3.  **Confirm Changes:** Run `ipconfig /all` again to ensure the new settings have been applied.

### 4.3 Firewall DNS Configuration

1.  If a network firewall is in place, access its management interface.
2.  Verify that the DNS settings configured on the firewall match the required DNS hierarchy for the domain (i.e., pointing to the internal Domain Controllers).

## 5.0 Verification

1.  **Test Domain Controller Discovery:** After confirming the DNS settings are correct, run the following command in the Command Prompt to verify that the endpoint can successfully discover the domain controller. Replace `<domain_name>` with the actual name of your AD domain (e.g., `obera.local`).
    ```cmd
    nltest /dsgetdc:<domain_name>
    ```
2.  **Analyze Output:** A successful output will show the name of the DC that responded and confirm a connection. If the command fails or times out, the endpoint is still unable to communicate with the DC, and further troubleshooting is required.

## 6.0 Additional Considerations

-   **Network Equipment Power Cycle:** If settings have been changed but are not propagating, a restart or power cycle of network switches, routers, and the affected endpoint may be required to force the changes to apply.
-   **Firewall IP Reservation:** In environments with a firewall managing DHCP, it may be necessary to create a static IP reservation for the Domain Controller(s) to ensure their IP addresses do not change.
-   **DHCP Lease Scope:** Adjustments to the DHCP lease scope on the firewall or DHCP server may be necessary in specific cases, such as network segmentation or IP address exhaustion. This should be evaluated on a case-by-case basis.

---
**End of Document**
```
