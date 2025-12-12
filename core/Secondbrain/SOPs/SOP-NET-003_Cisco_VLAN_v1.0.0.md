# SOP-NET-003: Cisco Device VLAN Configuration

---

### **1.0 Document Control**

| | |
|---|---|
| **ID** | SOP-NET-003 |
| **Version** | 1.0 |
| **Status** | Final |
| **Author** | OberaConnect IT |
| **Date** | 2025-12-02 |
| **Approved By** | |

---

### **2.0 Purpose**

To define the standard procedure for configuring, verifying, and managing Virtual Local Area Networks (VLANs) on Cisco switches to ensure network segmentation and security.

---

### **3.0 Scope**

This SOP applies to all network administration personnel responsible for configuring and managing Cisco network infrastructure within the organization.

---

### **4.0 Prerequisites**

- **Access:** Administrative access to the target Cisco switch via console cable or SSH.
- **Credentials:** Valid username and password with privileges to make configuration changes.
- **Network Knowledge:** Understanding of the network design, including required VLAN IDs, names, and port assignments.

---

### **5.0 Procedure**

#### **5.1 Access the Switch**

1.  Connect to the switch using your preferred method (console or SSH).
    ```bash
    ssh admin@<switch-ip-address>
    ```
2.  Enter your credentials when prompted.

#### **5.2 Enter Global Configuration Mode**

1.  Enter privileged EXEC mode.
    ```
    enable
    ```
2.  Enter global configuration mode.
    ```
    configure terminal
    ```

#### **5.3 Create and Name VLANs**

1.  Create a new VLAN and enter the VLAN configuration sub-mode.
    ```
    vlan <VLAN_ID>
    ```
    *Example:*
    ```
    vlan 10
    ```
2.  Assign a descriptive name to the VLAN.
    ```
    name <VLAN_Name>
    ```
    *Example:*
    ```
    name VLAN_SALES
    ```
3.  Exit the VLAN configuration sub-mode.
    ```
    exit
    ```
4.  Repeat steps 5.3.1 - 5.3.3 for each required VLAN.
    *Example:*
    ```
    vlan 20
    name VLAN_HR
    exit
    ```

#### **5.4 Assign Access Ports to VLANs**

1.  Select the interface or range of interfaces to configure.
    ```
    interface range <interface_type> <port_range>
    ```
    *Example:*
    ```
    interface range fastEthernet 0/1 - 12
    ```
2.  Set the port mode to `access`.
    ```
    switchport mode access
    ```
3.  Assign the port to the desired VLAN.
    ```
    switchport access vlan <VLAN_ID>
    ```
    *Example:*
    ```
    switchport access vlan 10
    ```
4.  Exit the interface configuration sub-mode.
    ```
    exit
    ```

#### **5.5 Configure Trunk Ports (If Required)**

*This step is necessary when connecting to another switch or a device that needs to handle traffic from multiple VLANs.*

1.  Select the interface to configure as a trunk.
    ```
    interface <interface_type> <port>
    ```
    *Example:*
    ```
    interface gigabitEthernet 0/1
    ```
2.  Set the port mode to `trunk`.
    ```
    switchport mode trunk
    ```
3.  (Optional but Recommended) Specify which VLANs are allowed on the trunk.
    ```
    switchport trunk allowed vlan <vlan_list>
    ```
    *Example:*
    ```
    switchport trunk allowed vlan 10,20
    ```
4.  Exit the interface configuration sub-mode.
    ```
    exit
    ```

---

### **6.0 Verification**

Use the following commands from privileged EXEC mode to verify the configuration.

1.  **Display VLAN Information:**
    *   Check that VLANs are created and ports are assigned correctly.
    ```
    show vlan brief
    ```

2.  **Display Trunk Port Information:**
    *   Verify that trunk ports are active and allowing the correct VLANs.
    ```
    show interfaces trunk
    ```

---

### **7.0 Save Configuration**

To ensure the configuration persists after a device reboot, save the running configuration to the startup configuration.

1.  From privileged EXEC mode, execute one of the following commands:
    ```
    write memory
    ```
    *or*
    ```
    copy running-config startup-config
    ```
2.  Confirm the save when prompted.

---

### **8.0 Contingency/Rollback**

- **To remove a VLAN:**
  ```
  configure terminal
  no vlan <VLAN_ID>
  exit
  ```
- **To reset a port to its default state:**
  ```
  configure terminal
  default interface <interface_type> <port>
  exit
  ```
- **To revert all changes:** If changes have not been saved, reboot the switch without saving the configuration.

---

### **9.0 Revision History**

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2025-12-02 | OberaConnect IT | Initial document creation from source. |
