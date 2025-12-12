#!/usr/bin/env python3
"""
Add Comments Column to SharePoint Lists
Adds a multiline text column to store comments in JSON format
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/mavrick/Projects/Secondbrain/.env')

def add_comments_column():
    """Add Comments column to Engineering Projects and Engineering Tickets lists"""
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')

    # Get token
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    token_resp = requests.post(token_url, data=token_data)
    token = token_resp.json().get('access_token')

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    base_url = 'https://graph.microsoft.com/v1.0'
    site_id = 'oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef'

    # Get lists
    resp = requests.get(f'{base_url}/sites/{site_id}/lists', headers=headers)
    lists = resp.json().get('value', [])

    projects_id = None
    tickets_id = None
    for lst in lists:
        if lst['displayName'] == 'Engineering Projects':
            projects_id = lst['id']
        elif lst['displayName'] == 'Engineering Tickets':
            tickets_id = lst['id']

    if not projects_id or not tickets_id:
        print("❌ Could not find required lists")
        return False

    # Define Comments column
    column_def = {
        "name": "Comments",
        "text": {
            "allowMultipleLines": True,
            "maxLength": 65000
        }
    }

    # Add column to Projects list
    print("Adding Comments column to Engineering Projects...")
    resp = requests.post(
        f'{base_url}/sites/{site_id}/lists/{projects_id}/columns',
        headers=headers,
        json=column_def
    )

    if resp.status_code in [200, 201]:
        print("✅ Comments column added to Engineering Projects")
    elif resp.status_code == 400 and 'already exists' in resp.text.lower():
        print("ℹ️  Comments column already exists in Engineering Projects")
    else:
        print(f"❌ Failed to add column to Projects: {resp.status_code}")
        print(resp.text)

    # Add column to Tickets list
    print("Adding Comments column to Engineering Tickets...")
    resp = requests.post(
        f'{base_url}/sites/{site_id}/lists/{tickets_id}/columns',
        headers=headers,
        json=column_def
    )

    if resp.status_code in [200, 201]:
        print("✅ Comments column added to Engineering Tickets")
    elif resp.status_code == 400 and 'already exists' in resp.text.lower():
        print("ℹ️  Comments column already exists in Engineering Tickets")
    else:
        print(f"❌ Failed to add column to Tickets: {resp.status_code}")
        print(resp.text)

    print("\n✅ Comments column setup complete!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Adding Comments Column to SharePoint Lists")
    print("=" * 60)
    add_comments_column()
