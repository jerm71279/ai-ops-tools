# Adding Engineering Hub to Microsoft Teams

This guide walks you through adding the Engineering Command Center app to your Teams channel.

---

## Option 1: Add as a Website Tab (Quick & Easy)

This is the simplest way to add the app to your Teams channel:

### Steps

1. **Open your Teams channel** (e.g., SOCTEAM-Engineering)

2. **Click the `+` button** next to your existing tabs at the top

3. **Select "Website"** from the app list

4. **Configure the tab:**
   - **Tab name:** `Engineering Hub`
   - **URL:** `https://jolly-island-06ade710f.3.azurestaticapps.net`
   - Check "Post to the channel about this tab"

5. **Click Save**

Your team can now access the Engineering Command Center directly from the Teams channel!

---

## Option 2: Install as a Teams App (Full Integration)

For deeper integration with Teams features, install as a custom app.

### Prerequisites

- Teams Admin access or permission to upload custom apps
- The Teams app package (manifest.zip)

### Create the App Package

1. Navigate to the teams-app folder:
   ```
   /home/mavrick/Projects/Secondbrain/teams-app/
   ```

2. Create icon files (192x192 color.png and 32x32 outline.png)

3. Create a ZIP file containing:
   - manifest.json
   - color.png
   - outline.png

### Upload to Teams

1. **Open Microsoft Teams**

2. **Go to Apps** (left sidebar)

3. **Click "Manage your apps"** at the bottom

4. **Click "Upload an app"**

5. **Select "Upload a custom app"**

6. **Choose your manifest.zip file**

7. **Click "Add"** to install

### Add to Channel

1. Go to your channel

2. Click `+` to add a tab

3. Search for "Engineering Hub"

4. Select the default view and click Save

---

## Option 3: Add via SharePoint (Native Integration)

Since the app already integrates with SharePoint, you can:

1. **Go to your SharePoint site:**
   https://oberaconnect.sharepoint.com/sites/SOCTEAM-Engineering

2. **Add a page** with the app embedded as an iframe

3. **Pin the page** to your Teams channel

---

## Direct Links for Specific Views

Share these links with your team for quick access to specific features:

| View | URL |
|------|-----|
| Projects | https://jolly-island-06ade710f.3.azurestaticapps.net?tab=projects |
| Task Board | https://jolly-island-06ade710f.3.azurestaticapps.net?tab=kanban |
| Time Reports | https://jolly-island-06ade710f.3.azurestaticapps.net?tab=timereports |
| To-Do List | https://jolly-island-06ade710f.3.azurestaticapps.net?tab=todos |
| Calendar | https://jolly-island-06ade710f.3.azurestaticapps.net?tab=calendar |

---

## Configuring Azure AD for Teams SSO

For seamless single sign-on in Teams:

### 1. Update App Registration

In Azure Portal → App Registrations → Your App:

1. Go to **Authentication**
2. Add platform: **Single-page application**
3. Add redirect URI: `https://jolly-island-06ade710f.3.azurestaticapps.net`
4. Enable: "Access tokens" and "ID tokens"

### 2. Add Teams Redirect URIs

Add these redirect URIs:
```
https://jolly-island-06ade710f.3.azurestaticapps.net/auth-end
https://jolly-island-06ade710f.3.azurestaticapps.net/blank-auth-end.html
```

### 3. API Permissions

Ensure these permissions are granted:
- `User.Read`
- `Sites.ReadWrite.All`
- `Team.ReadBasic.All` (optional, for Teams features)

---

## Troubleshooting

### "App can't be loaded"
- Check that the URL is accessible outside Teams first
- Verify the domain is in the manifest's validDomains

### "Sign-in required repeatedly"
- Enable SSO in Azure AD app registration
- Use sessionStorage for token caching

### "SharePoint data not loading"
- Verify Sites.ReadWrite.All permission is consented
- Check that user has access to the SharePoint site

---

## Teams App Manifest Details

**App ID:** `2527689c-fd5b-47d6-820c-45e4157f9a4f`
**Tenant:** `ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd` (OberaConnect)

### Static Tabs
- Projects
- Task Board
- Time Reports
- To-Do List

### Permissions Required
- identity (for SSO)
- Sites.ReadWrite.All (for SharePoint)

---

## Support

For issues with the Teams integration:
1. Check the browser console for errors
2. Verify Azure AD configuration
3. Contact your Teams administrator
