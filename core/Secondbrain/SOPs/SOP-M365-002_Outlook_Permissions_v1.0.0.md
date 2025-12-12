Loaded cached credentials.
```markdown
# Standard Operating Procedure: SOP-M365-002

**Title:** Setting Permissions on Shared Mailboxes in Outlook
**Version:** 1.0
**Date:** 2025-12-02

---

## 1.0 Purpose

This document provides standardized procedures for granting and managing user permissions for M365 Shared Mailboxes. Following these steps ensures that access is delegated consistently and securely.

## 2.0 Scope

This SOP applies to all IT support personnel and system administrators responsible for managing Microsoft 365 resources at OberaConnect.

## 3.0 Responsibilities

-   **IT Support Staff:** Responsible for executing permission changes for standard user requests.
-   **M365 Administrators:** Responsible for overseeing mailbox configurations and handling escalated or complex permission assignments.

## 4.0 Procedure

Two methods can be used to set permissions for shared mailboxes. The Exchange Admin Center (EAC) is the preferred and most comprehensive method for administrators.

### 4.1 Method A: Using the Microsoft Outlook Client

This method is for users who have appropriate permissions to delegate access from within Outlook.

1.  **Open Outlook** and navigate to the **File** menu in the top-left corner.
2.  Click on **Account Settings**, and then select **Delegate Access**.
3.  In the "Delegates" dialog box, click the **Add...** button.
4.  Search for and select the user(s) to whom you want to grant access and click **Add ->**.
5.  Click **OK**.
6.  In the "Delegate Permissions" dialog box, specify the desired level of access for each folder (e.g., Calendar, Inbox). The primary permission levels are:
    -   **Reviewer:** Can read items.
    -   **Author:** Can read and create items.
    -   **Editor:** Can read, create, and modify items.
7.  Click **OK** to apply the permissions.

### 4.2 Method B: Using the Exchange Admin Center (EAC)

This is the recommended method for administrators to manage `Full Access` and `Send As` permissions.

1.  **Sign In:** Log in to the **Microsoft 365 Exchange Admin Center**.
2.  **Navigate to Shared Mailboxes:** From the left-hand menu, navigate to **Recipients > Shared**.
3.  **Select Mailbox:** A list of shared mailboxes will appear. Select the mailbox you wish to manage.
4.  **Manage Delegation:** In the pane that opens on the right, click on **Mailbox delegation**.
5.  **Assign Permissions:**
    -   **Full Access:** Allows the delegate to open the mailbox and manage its content as the mailbox owner. Click **Edit**, then **+ Add members** to add users.
    -   **Send As:** Allows the delegate to send email that appears to come from the shared mailbox. Click **Edit**, then **+ Add members** to add users.
    -   **Send on Behalf:** Allows the delegate to send email on behalf of the shared mailbox (e.g., "John Doe on behalf of Support"). Click **Edit**, then **+ Add members** to add users.
6.  **Save Changes:** After adding the desired members to each permission group, close the panes. The changes are saved automatically.

## 5.0 References

-   [Original Support Document](https://oberaconnect.sharepoint.com/:w:/s/support/ESrUdO18N4JElnoByGjp8REBipQPYTsAjT_9q2S0kZVXzw?e=1KwWbL)

## 6.0 Revision History

| Version | Date       | Author          | Description               |
|---------|------------|-----------------|---------------------------|
| 1.0     | 2025-12-02 | Gemini Assistant | Initial document creation. |

```
