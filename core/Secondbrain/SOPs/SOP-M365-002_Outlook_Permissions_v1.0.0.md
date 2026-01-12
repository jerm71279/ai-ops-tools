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

### 4.3 Method C: Using Exchange Online PowerShell (Bulk/Scripted)

This method is preferred for bulk assignments or automation.

**Prerequisites:**
```powershell
# Install Exchange Online Management Module (if not installed)
Install-Module -Name ExchangeOnlineManagement

# Connect to Exchange Online
Connect-ExchangeOnline -UserPrincipalName admin@yourdomain.com
```

**Grant Full Access:**
```powershell
# Single user
Add-MailboxPermission -Identity "SharedMailbox@domain.com" -User "user@domain.com" -AccessRights FullAccess -InheritanceType All

# Multiple users (from CSV)
Import-Csv "C:\users.csv" | ForEach-Object {
    Add-MailboxPermission -Identity "SharedMailbox@domain.com" -User $_.Email -AccessRights FullAccess -InheritanceType All
}
```

**Grant Send As:**
```powershell
Add-RecipientPermission -Identity "SharedMailbox@domain.com" -Trustee "user@domain.com" -AccessRights SendAs -Confirm:$false
```

**Grant Send on Behalf:**
```powershell
Set-Mailbox -Identity "SharedMailbox@domain.com" -GrantSendOnBehalfTo @{Add="user@domain.com"}
```

**View Current Permissions:**
```powershell
# Full Access permissions
Get-MailboxPermission -Identity "SharedMailbox@domain.com" | Where-Object {$_.User -ne "NT AUTHORITY\SELF"}

# Send As permissions
Get-RecipientPermission -Identity "SharedMailbox@domain.com"

# Send on Behalf permissions
Get-Mailbox -Identity "SharedMailbox@domain.com" | Select-Object GrantSendOnBehalfTo
```

**Remove Permissions:**
```powershell
# Remove Full Access
Remove-MailboxPermission -Identity "SharedMailbox@domain.com" -User "user@domain.com" -AccessRights FullAccess -Confirm:$false

# Remove Send As
Remove-RecipientPermission -Identity "SharedMailbox@domain.com" -Trustee "user@domain.com" -AccessRights SendAs -Confirm:$false

# Remove Send on Behalf
Set-Mailbox -Identity "SharedMailbox@domain.com" -GrantSendOnBehalfTo @{Remove="user@domain.com"}
```

**Disconnect when done:**
```powershell
Disconnect-ExchangeOnline -Confirm:$false
```

## 5.0 Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Shared mailbox not appearing in Outlook | Auto-mapping disabled or Outlook cache | Enable auto-mapping: `Add-MailboxPermission -Identity "Shared" -User "user" -AccessRights FullAccess -AutoMapping $true`. Restart Outlook. |
| "Send As" emails showing as sent by user | Send As not granted, using Send on Behalf | Verify Send As permission granted. Check sent email headers. Remove Send on Behalf if Send As is desired. |
| Permission changes not taking effect | Replication delay | Wait 15-60 minutes for changes to propagate. User may need to restart Outlook. |
| Cannot connect to Exchange Online PowerShell | Module not installed or auth issues | Install module: `Install-Module ExchangeOnlineManagement`. Use MFA-enabled connection. |
| Delegate cannot see calendar/inbox | Only Full Access granted, not folder permissions | Grant specific folder permissions via Outlook or `Add-MailboxFolderPermission`. |
| User receives NDR when sending as shared mailbox | Send As permission missing or mailbox disabled | Verify `Get-RecipientPermission`. Check mailbox is enabled and not hidden. |
| Permissions removed after mailbox migration | Permissions not migrated | Re-apply permissions post-migration using PowerShell scripts. |
| Too many shared mailboxes slowing Outlook | Auto-mapping adds all to profile | Disable auto-mapping for less-used mailboxes: `-AutoMapping $false`. |

**Verification Commands:**
```powershell
# Check all permissions on a mailbox
Get-MailboxPermission -Identity "SharedMailbox@domain.com" | Format-Table User, AccessRights

# Check Send As
Get-RecipientPermission -Identity "SharedMailbox@domain.com" | Format-Table Trustee, AccessRights

# Check Send on Behalf
Get-Mailbox -Identity "SharedMailbox@domain.com" | Select-Object GrantSendOnBehalfTo

# Check if auto-mapping is enabled (requires examining AD attribute)
Get-ADUser -Identity "username" -Properties msExchDelegateListLink
```

## 6.0 References

-   [Original Support Document](https://oberaconnect.sharepoint.com/:w:/s/support/ESrUdO18N4JElnoByGjp8REBipQPYTsAjT_9q2S0kZVXzw?e=1KwWbL)

## 7.0 Revision History

| Version | Date       | Author          | Description               |
|---------|------------|-----------------|---------------------------|
| 1.0     | 2025-12-02 | Gemini Assistant | Initial document creation. |
| 1.1     | 2025-12-29 | Jeremy Smith | SME Review: Added Section 4.3 (PowerShell methods for bulk/scripted assignments). Added Section 5.0 (Troubleshooting) with common permission issues and verification commands. |

