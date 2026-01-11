# Setco - Azure Subscription

## Customer Info
**Customer:** Setco Services
**Managed By:** OberaConnect
**OC Login:** oberaconnect@setcoservices.com

## Azure Details
- **Tenant ID:** 7cf9e47b-84ff-4248-914f-8d8c70947e3b
- **Subscription ID:** 9b9d07f5-059a-4e11-95b4-a7ffda045a9a
- **Subscription Name:** Azure subscription 1
- **Tenant Domain:** SETCO.onmicrosoft.com

## VMs (6 Total)
| VM Name | Resource Group | Last Backup | Status |
|---------|----------------|-------------|--------|
| ADFS | DATACENTER | 2025-12-01 | Healthy |
| ADFSproxy | DATACENTER | 2025-12-01 | Healthy |
| SETCO-DC01-VM | DATACENTER | 2025-12-01 | Healthy |
| SETCO-DC02-VM | DATACENTER | 2025-11-22 | Healthy |
| SETCO-FS01-VM | DATACENTER | 2025-12-01 | Healthy |
| SETCO-RDS001 | DATACENTER | 2025-12-01 | Healthy |

## Backup Configuration
- **Recovery Services Vault:** MyRecoveryServicesVault
- **Resource Group:** DataCenter
- **Backup Policy:** Daily
- **Alert Email:** oc-engineering@oberaconnect.com

## Action Groups
| Name | Short Name | Common Schema | Email |
|------|------------|---------------|-------|
| BackupJobAlerts | BackupJobAle | true | oc-engineering@oberaconnect.com |
| BackupAlertsSetco | Backup | true | OC-Engineering@oberaconnect.com |

## Change Log
### 2025-12-01
- **Updated BackupJobAlerts** action group: Set `useCommonAlertSchema=true`
- This enables VM names in backup alert email subjects and body
- Both action groups now properly configured

## Azure CLI Access
```bash
# Login to Setco tenant
az login --tenant 7cf9e47b-84ff-4248-914f-8d8c70947e3b

# Or switch subscription
az account set --subscription 9b9d07f5-059a-4e11-95b4-a7ffda045a9a

# Verify
az account show -o table

# Check action group settings
az monitor action-group show --name "BackupJobAlerts" --resource-group DataCenter -o json
```
