# Standard Operating Procedure: Mapping a Shared Drive on Mac

| **Document ID** | **SOP-MAC-001** |
| :--- | :--- |
| **Version** | 1.0 |
| **Status** | Approved |
| **Date** | 2025-12-02 |
| **Department** | IT |
| **Author** | OberaConnect IT |

---

## 1.0 Purpose

This document outlines the standard procedure for connecting to (mapping) a network shared drive on a computer running macOS. Following these steps ensures consistent and successful access to shared network resources.

## 2.0 Scope

This procedure applies to all employees and contractors using company-provided Mac computers who require access to network shared drives.

## 3.0 Prerequisites

Before starting, ensure you have the following:
- A Mac computer connected to the company network (either via Ethernet or VPN).
- The server address (file path) for the shared drive (e.g., `smb://servername/sharename`).
- Valid user credentials (username and password) with permission to access the server.

## 4.0 Procedure

Follow these steps to map a shared drive.

### 4.1 Connecting to the Server

1.  Open **Finder** by clicking its icon in the Dock.
2.  From the menu bar at the top of the screen, click **Go**.
3.  In the dropdown menu, select **Connect to Server...**. (Keyboard shortcut: `Command+K`)
4.  In the "Connect to Server" window, enter the server address in the **Server Address** field. The format must be `smb://<server_path>`.
    - *Example:* `smb://fcgserver/fulcrumshared`
5.  Click the **Connect** button.
6.  A credentials prompt will appear. Select **Registered User**.
7.  Enter your assigned server **Name** (username) and **Password**.
8.  Click **Connect**. The drive is now mounted.

### 4.2 Making the Drive Visible

To ensure the connected drive is easily accessible, follow these steps:

1.  With **Finder** as the active application, click **Finder** in the top menu bar.
2.  Select **Settings...** (on macOS Ventura and newer) or **Preferences...** (on older macOS versions).
3.  In the settings/preferences window, click on the **General** tab.
4.  Under "Show these items on the desktop:", ensure the box for **Connected servers** is checked.
5.  Next, click on the **Sidebar** tab.
6.  Under "Locations", ensure the box for **Connected servers** is checked.

## 5.0 Verification

Upon successful completion of the procedure, the shared drive will be visible in the following locations:
- On the **Desktop**.
- In the **Finder sidebar** under the "Locations" section.

You can now navigate the drive's contents by double-clicking its icon in either of these locations.

## 6.0 Revision History

| Version | Date | Author | Change Description |
| :--- | :--- | :--- | :--- |
| 1.0 | 2025-12-02 | OberaConnect IT | Initial document creation from source material. |
