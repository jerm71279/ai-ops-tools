# Azure Backup Alert - Add VM Name to Email Notifications

## Overview
Update Azure Backup email alerts to include the VM name in the notification subject and body so each of the 5 daily backup alert emails clearly identifies which VM the alert references.

**Current State:** Backup alerts send to oc-engineering@oberaconnect.com but don't include VM name
**Goal:** Each email should clearly identify which VM (of 5) the backup status refers to

---

## Option 1: Azure Monitor Alert Rules (Recommended)

Azure Backup alerts are typically configured through Azure Monitor. The VM name can be included using dynamic content.

### Step 1: Access Alert Rules

1. Azure Portal > **Monitor** > **Alerts** > **Alert rules**
2. Or: **Recovery Services Vault** > **Alerts** > **Manage alert rules**

### Step 2: Edit Existing Alert Rule

1. Find the backup alert rule
2. Click **Edit**
3. Under **Actions** > **Action Groups**, edit the email action

### Step 3: Update Email Subject/Body with VM Name

In the alert rule, use these dynamic fields:

**Subject Line:**
```
Azure Backup Alert: [{{data.essentials.alertTargetIDs}}] - {{data.essentials.alertRule}}
```

Or more specifically:
```
Backup Status: {{data.alertContext.AffectedConfigurationItems}} - {{data.essentials.monitorCondition}}
```

**Email Body Template:**
```
VM Name: {{data.alertContext.AffectedConfigurationItems}}
Resource: {{data.essentials.alertTargetIDs}}
Status: {{data.essentials.monitorCondition}}
Severity: {{data.essentials.severity}}
Time: {{data.essentials.firedDateTime}}
Description: {{data.essentials.description}}
```

### Common Dynamic Fields for Backup Alerts

| Field | Description |
|-------|-------------|
| `{{data.alertContext.AffectedConfigurationItems}}` | VM/Resource name |
| `{{data.essentials.alertTargetIDs}}` | Full resource ID (includes VM name) |
| `{{data.essentials.alertRule}}` | Alert rule name |
| `{{data.essentials.monitorCondition}}` | Fired/Resolved |
| `{{data.essentials.severity}}` | Sev0-4 |
| `{{data.alertContext.BackupManagementType}}` | AzureIaaSVM, etc. |
| `{{data.alertContext.OperationName}}` | Backup, Restore, etc. |

---

## Option 2: Logic App for Custom Email Formatting

If more control is needed, create a Logic App to process alerts and send formatted emails.

### Step 1: Create Logic App

1. Azure Portal > **Create a resource** > **Logic App**
2. Name: `backup-alert-email-formatter`
3. Region: Same as Recovery Services Vault

### Step 2: Logic App Trigger

1. Add trigger: **When a HTTP request is received**
2. Copy the HTTP POST URL

### Step 3: Parse Alert Payload

Add action: **Parse JSON**

Schema for Azure Backup Alert:
```json
{
    "type": "object",
    "properties": {
        "schemaId": {"type": "string"},
        "data": {
            "type": "object",
            "properties": {
                "essentials": {
                    "type": "object",
                    "properties": {
                        "alertId": {"type": "string"},
                        "alertRule": {"type": "string"},
                        "severity": {"type": "string"},
                        "monitorCondition": {"type": "string"},
                        "alertTargetIDs": {"type": "array"},
                        "firedDateTime": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                "alertContext": {
                    "type": "object",
                    "properties": {
                        "AffectedConfigurationItems": {"type": "array"},
                        "BackupManagementType": {"type": "string"},
                        "OperationName": {"type": "string"},
                        "Status": {"type": "string"}
                    }
                }
            }
        }
    }
}
```

### Step 4: Extract VM Name

Add action: **Compose**

Expression to extract VM name from resource ID:
```
last(split(first(body('Parse_JSON')?['data']?['essentials']?['alertTargetIDs']), '/'))
```

### Step 5: Send Email with VM Name

Add action: **Send an email (V2)** - Office 365 Outlook

**To:** oc-engineering@oberaconnect.com

**Subject:**
```
Azure Backup: @{outputs('Compose_VMName')} - @{body('Parse_JSON')?['data']?['essentials']?['monitorCondition']}
```

**Body:**
```html
<h2>Azure Backup Alert</h2>
<table>
<tr><td><strong>VM Name:</strong></td><td>@{outputs('Compose_VMName')}</td></tr>
<tr><td><strong>Status:</strong></td><td>@{body('Parse_JSON')?['data']?['alertContext']?['Status']}</td></tr>
<tr><td><strong>Operation:</strong></td><td>@{body('Parse_JSON')?['data']?['alertContext']?['OperationName']}</td></tr>
<tr><td><strong>Time:</strong></td><td>@{body('Parse_JSON')?['data']?['essentials']?['firedDateTime']}</td></tr>
<tr><td><strong>Severity:</strong></td><td>@{body('Parse_JSON')?['data']?['essentials']?['severity']}</td></tr>
</table>
```

### Step 6: Update Action Group

1. Go to **Monitor** > **Alerts** > **Action groups**
2. Edit the action group for backup alerts
3. Add action type: **Logic App**
4. Select the Logic App created above

---

## Option 3: PowerShell Automation Runbook

If using Azure Automation for other tasks, add a runbook to format and send backup emails.

### Runbook: Send-BackupAlertWithVMName.ps1

```powershell
param(
    [Parameter(Mandatory=$true)]
    [object]$WebhookData
)

# Parse webhook payload
$alertData = ConvertFrom-Json -InputObject $WebhookData.RequestBody

# Extract VM name from resource ID
$resourceId = $alertData.data.essentials.alertTargetIDs[0]
$vmName = ($resourceId -split '/')[-1]

# Get alert details
$status = $alertData.data.alertContext.Status
$operation = $alertData.data.alertContext.OperationName
$severity = $alertData.data.essentials.severity
$time = $alertData.data.essentials.firedDateTime

# Build email
$subject = "Azure Backup: $vmName - $status"
$body = @"
<html>
<body>
<h2>Azure Backup Alert</h2>
<table border='1' cellpadding='5'>
<tr><td><b>VM Name</b></td><td>$vmName</td></tr>
<tr><td><b>Status</b></td><td>$status</td></tr>
<tr><td><b>Operation</b></td><td>$operation</td></tr>
<tr><td><b>Severity</b></td><td>$severity</td></tr>
<tr><td><b>Time</b></td><td>$time</td></tr>
</table>
</body>
</html>
"@

# Send email via SendGrid or SMTP
$emailParams = @{
    To = "oc-engineering@oberaconnect.com"
    From = "azure-alerts@oberaconnect.com"
    Subject = $subject
    Body = $body
    BodyAsHtml = $true
    SmtpServer = "smtp.sendgrid.net"
    Port = 587
    Credential = Get-AutomationPSCredential -Name "SendGridCredential"
    UseSsl = $true
}

Send-MailMessage @emailParams

Write-Output "Alert email sent for VM: $vmName"
```

---

## Quick Fix: Rename Alert Rules with VM Names

If you have 5 separate alert rules (one per VM), the simplest fix:

1. **Monitor** > **Alerts** > **Alert rules**
2. Edit each rule name to include VM name:
   - `Backup-Alert-VM1-CustomerName`
   - `Backup-Alert-VM2-CustomerName`
   - etc.
3. The alert rule name appears in the email subject

---

## Verification Steps

After updating:

1. [ ] Trigger a test backup on one VM
2. [ ] Wait for alert email
3. [ ] Verify VM name appears in subject
4. [ ] Verify VM name appears in body
5. [ ] Repeat for all 5 VMs
6. [ ] Document final configuration

---

## Customer-Specific Notes

**Customer:** [Customer Name]
**VMs (5 total):**
1. VM1: [name]
2. VM2: [name]
3. VM3: [name]
4. VM4: [name]
5. VM5: [name]

**Recovery Services Vault:** [vault name]
**Resource Group:** [rg name]
**Alert Email:** oc-engineering@oberaconnect.com

---

## References

- [Azure Monitor Alert Schema](https://docs.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-common-schema)
- [Azure Backup Alerts](https://docs.microsoft.com/en-us/azure/backup/backup-azure-monitoring-built-in-monitor)
- [Action Group Email Templates](https://docs.microsoft.com/en-us/azure/azure-monitor/alerts/action-groups#email)

---

**Created:** 2025-12-01
**Author:** OberaConnect Engineering
