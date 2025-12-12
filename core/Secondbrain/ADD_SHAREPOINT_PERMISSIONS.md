# Add SharePoint Read Permissions to Existing Azure App

## ✅ Good News: You Already Have an Azure App!

Your existing app currently has:
- `User.Read` (Delegated) - Sign in and read user profile

We just need to add SharePoint read-only permissions to it.

---

## 📋 Steps to Add SharePoint Permissions

### Step 1: You're Already Here!
You're looking at the **API permissions** page for your Azure app.

### Step 2: Add SharePoint Read Permissions

1. Click **"+ Add a permission"** button (at the top)

2. In the panel that opens, click **"Microsoft Graph"**

3. **Important:** Click **"Application permissions"** (NOT Delegated permissions)
   - Application permissions = App accesses data on its own (read-only for our case)
   - Delegated permissions = User must sign in each time (not what we want)

4. In the search box, type: **`Sites.Read.All`**
   - Check the box next to `Sites.Read.All`
   - Description: "Read items in all site collections"

5. In the search box, type: **`Files.Read.All`**
   - Check the box next to `Files.Read.All`
   - Description: "Read files in all site collections"

6. Click **"Add permissions"** button at the bottom

### Step 3: Grant Admin Consent

After adding the permissions, you'll see them in the list but they'll show **"Not granted"** status.

1. Click the **"Grant admin consent for [OberaConnect]"** button (at the top)
2. Click **"Yes"** in the confirmation dialog
3. Wait a moment for the green checkmarks to appear

**After granting consent, you should see:**
```
✓ User.Read (Delegated) - Granted
✓ Sites.Read.All (Application) - Granted
✓ Files.Read.All (Application) - Granted
```

---

## 🔑 Get Your App Credentials

### You Need 3 Values:

#### 1. Tenant ID
- Go to **Overview** page of your app (left sidebar)
- Copy the **Directory (tenant) ID**

#### 2. Application (Client) ID
- Still on the **Overview** page
- Copy the **Application (client) ID**

#### 3. Client Secret

**If you already have a client secret:**
- Go to **Certificates & secrets** (left sidebar)
- If you have an active secret, you're good (but you can't see the value again)
- If it's expired or you don't have one, create a new one:

**To create a new client secret:**
1. Go to **Certificates & secrets**
2. Click **"+ New client secret"**
3. Description: `SecondBrain SharePoint Access`
4. Expires: `24 months`
5. Click **Add**
6. **IMMEDIATELY COPY THE VALUE** (you only see it once!)
   - It looks like: `abc123xyz...`

---

## 💾 Add Credentials to .env File

```bash
cd /home/mavrick/Projects/Secondbrain

# Edit .env file
nano .env
```

Add these three lines (replace with your actual values):
```bash
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-application-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-value-here
```

Save the file:
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter`

---

## ✅ Test the Connection

```bash
cd /home/mavrick/Projects/Secondbrain

# Test if it can connect to SharePoint
./venv/bin/python sharepoint_importer.py
```

**Expected result:**
```
📍 Listing SharePoint sites...
📍 Found X SharePoint sites:
   - Site Name 1 (https://...)
   - Site Name 2 (https://...)
```

---

## 🔒 Security Check

After adding permissions, verify you have:

**✅ Should Have (Read-Only):**
- Sites.Read.All (Application)
- Files.Read.All (Application)
- User.Read (Delegated) - already there

**❌ Should NOT Have:**
- Sites.ReadWrite.All
- Sites.Manage.All
- Sites.FullControl.All
- Files.ReadWrite.All
- Any other write permissions

---

## 🎯 What These Permissions Allow

### Sites.Read.All (Application)
- List all SharePoint sites
- Read site structure and metadata
- Access document libraries
- **Cannot:** Create, modify, or delete sites

### Files.Read.All (Application)
- Download files from SharePoint
- Read file metadata (name, size, modified date)
- **Cannot:** Upload, modify, or delete files

### User.Read (Delegated) - Your Existing Permission
- Used for user sign-in (not needed for this project, but harmless)

---

## 🚀 Next Steps

Once credentials are in `.env` and test is successful:

```bash
# 1. List your SharePoint sites
./venv/bin/python sharepoint_importer.py

# 2. Note the site_id you want to download from

# 3. Download files (interactive Python)
./venv/bin/python
```

```python
from sharepoint_importer import SharePointImporter

importer = SharePointImporter()

# List document libraries in your site
libraries = importer.list_document_libraries(site_id="YOUR_SITE_ID")

# Download files
importer.download_files_from_library(
    site_id="YOUR_SITE_ID",
    drive_id="YOUR_DRIVE_ID",
    output_dir="input_documents/sharepoint/oberaconnect"
)
```

---

## 📞 Troubleshooting

### "Insufficient privileges to complete the operation"
- Make sure you clicked "Grant admin consent"
- Wait 5 minutes for permissions to propagate

### "Failed to get access token"
- Check your tenant ID, client ID, and client secret are correct
- Make sure the secret hasn't expired

### "Collection does not exist"
- The site ID might be wrong
- Make sure you're using the full site ID from the list

---

## ✅ Checklist

- [ ] Added Sites.Read.All (Application permission)
- [ ] Added Files.Read.All (Application permission)
- [ ] Clicked "Grant admin consent"
- [ ] Got Tenant ID from Overview page
- [ ] Got Application (Client) ID from Overview page
- [ ] Created/have Client Secret
- [ ] Added all three to `.env` file
- [ ] Tested connection with `sharepoint_importer.py`
- [ ] Successfully listed SharePoint sites

---

**You're reusing your existing Azure app - just adding SharePoint read permissions!** 🎯

*No new app needed, no impact on existing permissions.*
