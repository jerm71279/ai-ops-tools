# SharePoint Read-Only Access Setup
## For OberaConnect Second Brain (Zero Impact on Existing Permissions)

---

## 🔒 Important: This is Read-Only Access Only

**What this does:**
- ✅ Gives this Second Brain system read access to SharePoint files
- ✅ Downloads copies of documents for processing
- ✅ **DOES NOT** modify any SharePoint documents
- ✅ **DOES NOT** affect any employee's existing permissions
- ✅ **DOES NOT** change any Microsoft 365 settings
- ✅ Completely isolated from other OberaConnect Azure apps

**What this is NOT:**
- ❌ NOT a user account (uses app-only authentication)
- ❌ NOT giving new permissions to any employees
- ❌ NOT modifying existing permission structures
- ❌ NOT touching Microsoft 365 settings
- ❌ NOT integrated with any existing apps

---

## 📋 Step-by-Step Azure App Registration

### Step 1: Go to Azure Portal
1. Open: https://portal.azure.com
2. Sign in with your OberaConnect admin account

### Step 2: Navigate to App Registrations
1. Click **Azure Active Directory** (left sidebar)
2. Click **App registrations**
3. Click **+ New registration**

### Step 3: Register the App
Fill in the form:

**Name:** `SecondBrain-ReadOnly-SharePoint`
- This name helps identify it's only for reading SharePoint

**Supported account types:**
- Select: **Accounts in this organizational directory only (OberaConnect only - Single tenant)**
- This keeps it isolated to your organization

**Redirect URI:**
- Leave blank (not needed for read-only app access)

Click **Register**

### Step 4: Save Application IDs
After registration, you'll see the app overview page.

**Copy these values** (you'll need them later):
```
Application (client) ID: [copy this]
Directory (tenant) ID: [copy this]
```

### Step 5: Create Client Secret
1. In the left sidebar, click **Certificates & secrets**
2. Click **+ New client secret**
3. Fill in:
   - **Description:** `SecondBrain Read Access`
   - **Expires:** `24 months` (or your organization's policy)
4. Click **Add**
5. **IMMEDIATELY COPY THE VALUE** (you can only see it once!)
   - It will look like: `abc123...xyz789`

### Step 6: Grant READ-ONLY Permissions

**Critical: These permissions are READ-ONLY and do not affect users**

1. In the left sidebar, click **API permissions**
2. Click **+ Add a permission**
3. Click **Microsoft Graph**
4. Select **Application permissions** (NOT Delegated permissions)
5. Search and add these permissions:
   - `Sites.Read.All` - Read items in all site collections
   - `Files.Read.All` - Read files in all site collections

6. **Important:** Do NOT add any write permissions like:
   - ❌ Sites.ReadWrite.All
   - ❌ Files.ReadWrite.All
   - ❌ Sites.Manage.All
   - ❌ Sites.FullControl.All

7. Click **Add permissions**

### Step 7: Grant Admin Consent
1. Click **Grant admin consent for [OberaConnect]**
2. Click **Yes** to confirm
3. You should see green checkmarks next to the permissions

---

## 🔐 Add Credentials to .env File

On your WSL/Linux system:

```bash
cd /home/mavrick/Projects/Secondbrain

# Edit .env file
nano .env
```

Add these lines (replace with your actual values):
```bash
# SharePoint Read-Only Access
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-secret-value-here
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## ✅ Test the Connection

```bash
cd /home/mavrick/Projects/Secondbrain

# Test SharePoint access
./venv/bin/python sharepoint_importer.py
```

You should see a list of SharePoint sites you have access to.

---

## 🛡️ Security Best Practices

### What This App Can Do:
- ✅ Read SharePoint sites and document libraries
- ✅ Download copies of files
- ✅ View file metadata (names, modified dates, etc.)

### What This App CANNOT Do:
- ❌ Modify any files in SharePoint
- ❌ Delete any files
- ❌ Create new files or folders
- ❌ Change permissions
- ❌ Access user emails or calendars
- ❌ Modify any Microsoft 365 settings
- ❌ Impact any employee's access to anything

### Isolation from Other Systems:
- This is a **separate app registration**
- It does NOT use any existing OberaConnect Azure apps
- It does NOT share credentials with other systems
- It operates independently with its own permissions
- You can revoke access anytime by deleting the app registration

---

## 🔄 How to Revoke Access Later

If you ever want to remove this app's access:

1. Go to Azure Portal > Azure Active Directory
2. Click **App registrations**
3. Find `SecondBrain-ReadOnly-SharePoint`
4. Click **Delete**

Done. The Second Brain will no longer be able to access SharePoint.

---

## 📊 What Gets Downloaded

When you use the importer, it will:

1. **List SharePoint sites** you specify
2. **List document libraries** in those sites
3. **Download files** to local folder: `input_documents/sharepoint/`
4. **Process locally** using Claude AI
5. **Store in Obsidian vault** on your OneDrive

**No impact on SharePoint:**
- Original files remain unchanged
- No new files created in SharePoint
- No modifications to any permissions
- No changes to sharing settings

---

## 🎯 Next Steps

1. ✅ Complete the Azure app registration above
2. ✅ Add credentials to `.env` file
3. ✅ Test connection: `./venv/bin/python sharepoint_importer.py`
4. ✅ Download your first document library
5. ✅ Process into Second Brain

---

## 📞 Verification Checklist

Before proceeding, verify:

- [ ] App is named clearly (e.g., "SecondBrain-ReadOnly-SharePoint")
- [ ] Using "Application permissions" (not Delegated)
- [ ] Only `Sites.Read.All` and `Files.Read.All` permissions granted
- [ ] No write permissions accidentally added
- [ ] Admin consent granted
- [ ] Client secret copied and saved to `.env`
- [ ] Test connection successful

---

**This app is READ-ONLY and completely isolated from other OberaConnect systems.** 🔒

*It will only read SharePoint files - no modifications, no permission changes, no impact on employees.*
