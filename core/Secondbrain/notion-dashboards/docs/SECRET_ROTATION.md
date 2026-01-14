# Secret Rotation Policy

## Overview

This document defines the secret rotation procedures for OberaConnect Notion Dashboards.
All credentials MUST be rotated on schedule to maintain security compliance.

## Rotation Schedule

| Secret | Rotation Frequency | Owner | Alert Before |
|--------|-------------------|-------|--------------|
| NOTION_TOKEN | 90 days | Platform Team | 14 days |
| UNIFI_API_TOKEN | 90 days | Network Team | 14 days |
| NINJAONE_CLIENT_SECRET | 90 days | RMM Team | 14 days |
| SMTP_PASSWORD | 90 days | IT Admin | 14 days |
| Azure Key Vault Access | 365 days | Security Team | 30 days |

## Rotation Procedures

### 1. Notion Integration Token

**Where**: https://www.notion.so/my-integrations

**Steps**:
1. Log into Notion as workspace admin
2. Go to Settings & Members → Integrations → Internal integrations
3. Select the OberaConnect integration
4. Click "Show" next to Internal Integration Token
5. Click "Regenerate token"
6. Copy new token immediately (shown only once)
7. Update in Azure Key Vault OR environment variable:
   ```bash
   # Azure Key Vault (production)
   az keyvault secret set --vault-name oberaconnect-vault \
     --name notion-token --value "secret_NEW_TOKEN_HERE"

   # Or update .env file (development)
   NOTION_TOKEN=secret_NEW_TOKEN_HERE
   ```
8. Restart sync services
9. Verify sync completes successfully
10. Document rotation in audit log

**Rollback**: Old token remains valid for 24 hours after regeneration.

### 2. UniFi API Token

**Where**: UniFi Site Manager → Settings → API

**Steps**:
1. Log into unifi.ui.com as admin
2. Navigate to Settings → API
3. Click "Create New API Key"
4. Copy the new token
5. Update in Key Vault or environment:
   ```bash
   az keyvault secret set --vault-name oberaconnect-vault \
     --name unifi-api-token --value "NEW_TOKEN_HERE"
   ```
6. Test connection:
   ```bash
   curl -H "Authorization: Bearer NEW_TOKEN" \
     https://api.ui.com/ea/sites
   ```
7. Delete old API key from UniFi console
8. Restart sync services

**Rollback**: Create new key before deleting old one. Keep old key active until verified.

### 3. NinjaOne OAuth Credentials

**Where**: NinjaOne Admin → Administration → Apps → API

**Steps**:
1. Log into app.ninjarmm.com as admin
2. Go to Administration → Apps → API
3. Select existing API application
4. Click "Regenerate Secret"
5. Copy new Client ID and Client Secret
6. Update in Key Vault:
   ```bash
   az keyvault secret set --vault-name oberaconnect-vault \
     --name ninjaone-client-id --value "NEW_CLIENT_ID"
   az keyvault secret set --vault-name oberaconnect-vault \
     --name ninjaone-client-secret --value "NEW_SECRET"
   ```
7. Test OAuth flow:
   ```bash
   curl -X POST https://app.ninjarmm.com/oauth/token \
     -d "grant_type=client_credentials" \
     -d "client_id=NEW_CLIENT_ID" \
     -d "client_secret=NEW_SECRET"
   ```
8. Restart sync services

**Rollback**: NinjaOne allows multiple active secrets. Create new before disabling old.

### 4. SMTP Password (M365)

**Where**: Microsoft 365 Admin Center

**Steps**:
1. Log into admin.microsoft.com
2. Go to Users → Active users
3. Select the alerts@oberaconnect.com shared mailbox
4. Click "Reset password"
5. Generate or set new password
6. Update in Key Vault:
   ```bash
   az keyvault secret set --vault-name oberaconnect-vault \
     --name smtp-password --value "NEW_PASSWORD"
   ```
7. Test email sending:
   ```bash
   python -c "
   import smtplib
   s = smtplib.SMTP('smtp.office365.com', 587)
   s.starttls()
   s.login('alerts@oberaconnect.com', 'NEW_PASSWORD')
   print('SMTP auth successful')
   s.quit()
   "
   ```

## Azure Key Vault Rotation

For production environments using Azure Key Vault:

### Enable Auto-Rotation (Recommended)

```bash
# Set rotation policy for a secret
az keyvault secret rotation-policy update \
  --vault-name oberaconnect-vault \
  --name notion-token \
  --auto-rotate \
  --rotation-interval P90D \
  --notification-time P14D \
  --notification-contacts security@oberaconnect.com
```

### Manual Rotation via CLI

```bash
# List current secrets
az keyvault secret list --vault-name oberaconnect-vault -o table

# Get current version
az keyvault secret show --vault-name oberaconnect-vault --name notion-token

# Set new version (creates new version, old remains accessible)
az keyvault secret set --vault-name oberaconnect-vault \
  --name notion-token --value "NEW_VALUE"

# Disable old version after verification
az keyvault secret set-attributes --vault-name oberaconnect-vault \
  --name notion-token --version OLD_VERSION --enabled false
```

## Monitoring & Alerts

### Secret Expiration Alerts

Add to monitoring system:

```python
# In health_check.py
from datetime import datetime, timedelta

SECRET_ROTATION_SCHEDULE = {
    "NOTION_TOKEN": 90,
    "UNIFI_API_TOKEN": 90,
    "NINJAONE_CLIENT_SECRET": 90,
}

def check_secret_age(secret_name: str, last_rotated: datetime) -> dict:
    """Check if secret needs rotation."""
    max_age = SECRET_ROTATION_SCHEDULE.get(secret_name, 90)
    age_days = (datetime.utcnow() - last_rotated).days

    return {
        "secret": secret_name,
        "age_days": age_days,
        "max_age_days": max_age,
        "needs_rotation": age_days > (max_age - 14),
        "overdue": age_days > max_age
    }
```

### Audit Trail

All rotations MUST be logged:

```json
{
  "event": "secret_rotation",
  "timestamp": "2025-01-15T10:30:00Z",
  "secret_name": "NOTION_TOKEN",
  "rotated_by": "jsmith@oberaconnect.com",
  "method": "azure_keyvault",
  "verification": "passed",
  "old_version_disabled": true
}
```

## Emergency Rotation

If a secret is compromised:

1. **Immediately** rotate the compromised secret
2. Check audit logs for unauthorized access
3. Review all API calls made with compromised credential
4. Notify security team
5. Document incident in security log
6. Consider rotating related secrets

```bash
# Emergency rotation script
#!/bin/bash
SECRET_NAME=$1
NEW_VALUE=$2

echo "EMERGENCY ROTATION: $SECRET_NAME"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Update Key Vault
az keyvault secret set --vault-name oberaconnect-vault \
  --name "$SECRET_NAME" --value "$NEW_VALUE"

# Restart services
systemctl restart oberaconnect-sync

# Send alert
curl -X POST "$SLACK_WEBHOOK" -d "{\"text\":\"SECURITY: Emergency rotation of $SECRET_NAME completed\"}"
```

## Compliance Checklist

- [ ] All secrets stored in Azure Key Vault (not .env in production)
- [ ] Rotation schedule documented and followed
- [ ] Audit logs retained for 1 year
- [ ] Access to Key Vault restricted to authorized personnel
- [ ] Emergency rotation procedure tested quarterly
- [ ] Secret expiration alerts configured
