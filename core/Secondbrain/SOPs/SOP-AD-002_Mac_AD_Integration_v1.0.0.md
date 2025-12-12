Loaded cached credentials.
```markdown
# Standard Operating Procedure: SOP-AD-002

## 1. Document Control

*   **SOP Number:** SOP-AD-002
*   **Title:** Adding Mac Device to Active Directory Domain
*   **Version:** 1.0
*   **Effective Date:** 2025-12-02
*   **Author:** Gemini Agent
*   **Approval:** IT Department Head (Placeholder)

## 2. Purpose

This Standard Operating Procedure (SOP) outlines the step-by-step process for securely adding a macOS device to an Active Directory (AD) Domain, ensuring proper integration with organizational network services and authentication systems.

## 3. Scope

This SOP applies to all IT personnel responsible for configuring and managing Apple macOS devices within the organization's network environment.

## 4. Definitions / Acronyms

*   **AD:** Active Directory
*   **macOS:** Apple's proprietary operating system for its Mac line of computers.
*   **Directory Utility:** A macOS application used to configure directory services, including Active Directory integration.
*   **Domain Admin:** An account with administrative privileges within the Active Directory domain.

## 5. Responsibilities

*   **IT Administrators:** Responsible for executing this procedure and ensuring the Mac device is successfully joined to the Active Directory domain.

## 6. Procedure

Follow these steps to add a Mac device to the Active Directory Domain:

1.  **Open Directory Utility:**
    *   Press `Command + Space` to open Spotlight Search.
    *   Type "Directory Utility" and press Enter to open the application.

2.  **Unlock for Changes:**
    *   Click the padlock icon at the bottom-left corner of the Directory Utility window.
    *   Enter the administrator password for the Mac device when prompted to allow modifications.

3.  **Select Active Directory:**
    *   In the Directory Utility window, select the "Active Directory" service.
    *   Click the pencil icon (Edit) at the bottom of the window to configure the service.

4.  **Enter Domain Information:**
    *   In the "Active Directory Domain" field, type the full Active Directory domain name (e.g., `yourdomain.com`).
    *   The "Computer ID" field will automatically populate; no further action is required for advanced options unless specifically instructed by system architecture.

5.  **Bind to Domain:**
    *   Click the "Bind" button.

6.  **Provide Domain Administrator Credentials:**
    *   A new window will appear, prompting for a network domain administrator login.
    *   Enter the username and password for a valid Domain Admin account.
    *   Click "OK."

7.  **Confirm Integration:**
    *   Allow a few minutes for the binding process to complete. The Mac device will connect to the Active Directory domain.
    *   Verify the connection by checking System Settings (or System Preferences) > Users & Groups > Login Options, or by attempting to log in with a domain user account.

## 7. Related Documents

*   [N/A]

## 8. Revision History

| Version | Date         | Description of Change | Author         |
| :------ | :----------- | :-------------------- | :------------- |
| 1.0     | 2025-12-02   | Initial release       | Gemini Agent   |
```
