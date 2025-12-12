# Azure DevOps Integration Setup Guide

## Overview

This guide walks through setting up Azure DevOps integration with the Engineering Command Center (ECC). The integration enables:
- Linking ECC tasks to Azure DevOps work items
- Bidirectional status synchronization
- Viewing commits and PRs linked to tasks

---

## Prerequisites

1. Azure DevOps organization (create at https://dev.azure.com)
2. Azure AD admin access (for app registration)
3. ECC deployed and functional

---

## Step 1: Create Azure DevOps Organization (if needed)

1. Go to https://dev.azure.com
2. Sign in with your Microsoft 365 account
3. Click "Create new organization"
4. Name: `OberaConnect`
5. Choose region: `Central US` (or nearest)

### Create Project

1. Click "New Project"
2. Name: `Engineering`
3. Visibility: Private
4. Version control: Git
5. Work item process: Agile (recommended) or Basic

---

## Step 2: Register Azure AD Application for DevOps API

### 2.1 Create App Registration

1. Go to Azure Portal > Azure Active Directory > App registrations
2. Click "New registration"
3. Configure:
   - Name: `ECC-DevOps-Integration`
   - Supported account types: "Accounts in this organizational directory only"
   - Redirect URI: `https://jolly-island-06ade710f.3.azurestaticapps.net/auth/callback`

4. Click "Register"
5. Note the **Application (client) ID**: `_________________________`

### 2.2 Add API Permissions

1. Go to "API permissions"
2. Click "Add a permission"
3. Select "Azure DevOps"
4. Select "Delegated permissions"
5. Add these permissions:
   - `vso.work` - Read work items
   - `vso.work_write` - Create and update work items
   - `vso.code` - Read source code and commits
   - `vso.build` - Read build information

6. Click "Grant admin consent for OberaConnect"

### 2.3 Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Description: `ECC DevOps Integration`
4. Expires: 24 months
5. Click "Add"
6. **COPY THE SECRET VALUE NOW** - you won't see it again!
7. Store in secure location (Azure Key Vault recommended)

---

## Step 3: Configure DevOps Service Connection

### 3.1 Personal Access Token (Alternative to OAuth)

For simpler setup, use a PAT:

1. Go to Azure DevOps > User Settings (top right) > Personal Access Tokens
2. Click "New Token"
3. Configure:
   - Name: `ECC-Integration`
   - Organization: `OberaConnect`
   - Expiration: 1 year
   - Scopes: Custom defined
     - Work Items: Read & Write
     - Code: Read
     - Build: Read
     - Project and Team: Read

4. Click "Create"
5. **COPY THE TOKEN** - store securely

---

## Step 4: Add Configuration to ECC

### 4.1 Update Environment Variables

Add to `/home/mavrick/Projects/Secondbrain/swa-build/.env`:

```bash
# Azure DevOps Configuration
DEVOPS_ORGANIZATION=OberaConnect
DEVOPS_PROJECT=Engineering
DEVOPS_PAT=<your-personal-access-token>

# Or for OAuth flow:
DEVOPS_CLIENT_ID=<app-registration-client-id>
DEVOPS_CLIENT_SECRET=<client-secret>
```

### 4.2 Update staticwebapp.config.json

Add DevOps API to CSP headers:

```json
{
  "globalHeaders": {
    "Content-Security-Policy": "... connect-src 'self' https://graph.microsoft.com https://dev.azure.com https://vssps.dev.azure.com ..."
  }
}
```

---

## Step 5: SharePoint List Schema Update

Run the schema update script to add DevOps fields:

```bash
cd /home/mavrick/Projects/Secondbrain
python scripts/add_sharepoint_document_fields.py
```

This adds:
- `DevOpsWorkItemId` (Number) - Work item ID
- `DevOpsWorkItemUrl` (Text) - Link to work item

---

## Step 6: Test the Integration

### 6.1 Create Test Work Item in DevOps

1. Go to Azure DevOps > Boards > Work Items
2. Click "New Work Item" > Task
3. Title: "Test ECC Integration"
4. Save and note the Work Item ID

### 6.2 Link from ECC

1. Open ECC
2. Create or edit a task
3. Enter the DevOps Work Item ID
4. Save
5. Verify the link appears

---

## API Endpoints Reference

### Base URL
```
https://dev.azure.com/{organization}/{project}/_apis
```

### Common Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/wit/workitems/{id}?api-version=7.1` | GET | Get work item |
| `/wit/workitems/$Task?api-version=7.1` | POST | Create task |
| `/wit/workitems/{id}?api-version=7.1` | PATCH | Update work item |
| `/git/repositories/{repo}/commits?api-version=7.1` | GET | List commits |
| `/git/repositories/{repo}/pullrequests?api-version=7.1` | GET | List PRs |

### Authentication Header
```
Authorization: Basic {base64(username:PAT)}
```

Or for OAuth:
```
Authorization: Bearer {access_token}
```

---

## Status Mapping

| ECC Status | DevOps State |
|------------|--------------|
| Not Started | New |
| In Progress | Active |
| On Hold | On Hold |
| Done | Closed |
| Completed | Closed |

---

## Troubleshooting

### Error: 401 Unauthorized
- Check PAT hasn't expired
- Verify scopes include required permissions
- Ensure organization name is correct

### Error: 404 Not Found
- Verify project name matches exactly
- Check work item ID exists
- Confirm API version is supported

### Error: 403 Forbidden
- User may lack permissions in DevOps project
- Check if project is private and user has access

---

## Security Considerations

1. **Never commit PAT tokens to source control**
2. Store secrets in Azure Key Vault
3. Use short-lived tokens when possible
4. Rotate tokens regularly
5. Use minimum required scopes

---

## Next Steps

1. [ ] Create DevOps organization
2. [ ] Register Azure AD app
3. [ ] Generate PAT token
4. [ ] Update environment variables
5. [ ] Run schema update script
6. [ ] Test integration
7. [ ] Document any custom configurations

---

**Created:** 2025-12-04
**Version:** 1.0
**Author:** OberaConnect Engineering
