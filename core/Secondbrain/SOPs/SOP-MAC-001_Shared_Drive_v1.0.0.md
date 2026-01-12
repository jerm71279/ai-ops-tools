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
    - For domain-joined servers: `smb://server.domain.com/sharename`
5.  Click the **+** button to save this address to Favorites for future use.
6.  Click the **Connect** button.
7.  A credentials prompt will appear. Select **Registered User**.
8.  Enter your assigned server **Name** (username) and **Password**.
    -   For domain accounts, use: `DOMAIN\username` or `username@domain.com`
9.  **Save Credentials:** Check **Remember this password in my keychain** to avoid entering credentials each time.
10. Click **Connect**. The drive is now mounted.

### 4.2 Configuring Auto-Mount on Login

To automatically reconnect to the shared drive when you log in:

**Method 1: Login Items (Recommended)**
1.  Connect to the server using Section 4.1 (with Keychain enabled).
2.  Open **System Settings** (or System Preferences on older macOS).
3.  Navigate to **General > Login Items** (or Users & Groups > Login Items on older macOS).
4.  Click the **+** button under "Open at Login".
5.  In the file browser, navigate to the mounted drive (under Locations or in /Volumes).
6.  Select the shared drive and click **Add**.
7.  The drive will now auto-mount at each login.

**Method 2: AppleScript (Advanced)**
1.  Open **Script Editor** (Applications > Utilities).
2.  Enter the following script:
    ```applescript
    tell application "Finder"
        try
            mount volume "smb://server/sharename"
        end try
    end tell
    ```
3.  Save as Application: **File > Export** > File Format: **Application**.
4.  Add this application to Login Items (per Method 1 steps 2-6).

### 4.3 Making the Drive Visible

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

## 6.0 Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| "Connection failed" error | Server unreachable or DNS issue | Verify network connection. Try IP address instead of hostname. |
| "Invalid username or password" | Wrong credentials or format | Try `DOMAIN\username` format. Check Caps Lock. |
| Drive disconnects after sleep | macOS drops idle connections | Enable auto-mount via Login Items (Section 4.2). |
| Slow performance | SMB version mismatch | Check server supports SMB3. Try adding `?vers=3` to path. |
| Keychain keeps asking for password | Keychain entry corrupted | Delete entry in Keychain Access app, reconnect with "Remember password". |
| Drive not auto-mounting | Login Item not configured correctly | Remove and re-add Login Item. Ensure Keychain has credentials saved. |

**CLI Connection (Alternative):**
```bash
# Mount share via Terminal
mkdir -p ~/mnt/sharename
mount_smbfs //username@server/sharename ~/mnt/sharename

# Unmount
umount ~/mnt/sharename
```

## 7.0 Related Documents

-   SOP-AD-002: Adding Mac Device to Active Directory Domain

## 8.0 Revision History

| Version | Date | Author | Change Description |
| :--- | :--- | :--- | :--- |
| 1.0 | 2025-12-02 | OberaConnect IT | Initial document creation from source material. |
| 1.1 | 2025-12-29 | Jeremy Smith | SME Review: Added Keychain password storage option. Added Section 4.2 (Auto-Mount on Login with Login Items and AppleScript methods). Added troubleshooting table. Added CLI alternative. |
