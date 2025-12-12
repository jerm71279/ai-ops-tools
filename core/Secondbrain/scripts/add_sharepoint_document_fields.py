#!/usr/bin/env python3
"""
Add Document URL fields to SharePoint Tasks and Tickets lists
Run this script to add DocumentUrl and DocumentName fields for document linking

Usage:
    python add_sharepoint_document_fields.py

Prerequisites:
    - AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET in .env
    - Graph API permissions: Sites.ReadWrite.All
"""

import os
import sys
import requests
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
env_vars = {}

if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

TENANT_ID = env_vars.get('AZURE_TENANT_ID') or os.getenv('AZURE_TENANT_ID')
CLIENT_ID = env_vars.get('AZURE_CLIENT_ID') or os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = env_vars.get('AZURE_CLIENT_SECRET') or os.getenv('AZURE_CLIENT_SECRET')

# SharePoint configuration
SITE_ID = "oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# Lists to update - using actual SharePoint list names
LISTS_TO_UPDATE = ["Tasks", "Engineering Tickets", "Engineering Projects"]

# New columns to add - using simpler text format
NEW_COLUMNS = [
    {
        "name": "DocumentUrl",
        "displayName": "Document URL",
        "description": "Link to related document in SharePoint",
        "text": {}
    },
    {
        "name": "DocumentName",
        "displayName": "Document Name",
        "description": "Name of the linked document",
        "text": {}
    },
    {
        "name": "DevOpsWorkItemId",
        "displayName": "DevOps Work Item ID",
        "description": "Linked Azure DevOps work item ID",
        "number": {}
    },
    {
        "name": "DevOpsWorkItemUrl",
        "displayName": "DevOps Work Item URL",
        "description": "Link to Azure DevOps work item",
        "text": {}
    }
]


def get_access_token():
    """Get access token using client credentials flow"""
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default'
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()['access_token']


def get_list_id(access_token: str, list_name: str) -> str:
    """Get list ID by name"""
    url = f"{GRAPH_API_BASE}/sites/{SITE_ID}/lists"
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    lists = response.json().get('value', [])
    for lst in lists:
        if lst['displayName'] == list_name:
            return lst['id']

    raise ValueError(f"List '{list_name}' not found")


def get_existing_columns(access_token: str, list_id: str) -> list:
    """Get existing columns in a list"""
    url = f"{GRAPH_API_BASE}/sites/{SITE_ID}/lists/{list_id}/columns"
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return [col['name'] for col in response.json().get('value', [])]


def add_column(access_token: str, list_id: str, column_def: dict) -> bool:
    """Add a column to a list"""
    url = f"{GRAPH_API_BASE}/sites/{SITE_ID}/lists/{list_id}/columns"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=column_def)

    if response.status_code == 201:
        return True
    elif response.status_code == 400 and 'already exists' in response.text.lower():
        return False  # Column already exists
    else:
        print(f"  Error adding column: {response.status_code} - {response.text}")
        return False


def main():
    print("=" * 60)
    print("SharePoint List Schema Update - Document & DevOps Fields")
    print("=" * 60)

    # Validate credentials
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("ERROR: Missing Azure credentials. Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")
        sys.exit(1)

    print(f"\nTenant ID: {TENANT_ID[:8]}...")
    print(f"Client ID: {CLIENT_ID[:8]}...")
    print(f"Site ID: {SITE_ID[:40]}...")

    # Get access token
    print("\n[1/3] Authenticating with Microsoft Graph API...")
    try:
        access_token = get_access_token()
        print("  Authentication successful")
    except Exception as e:
        print(f"  ERROR: Authentication failed - {e}")
        sys.exit(1)

    # Process each list
    print("\n[2/3] Processing lists...")
    results = {}

    for list_name in LISTS_TO_UPDATE:
        print(f"\n  Processing: {list_name}")
        try:
            list_id = get_list_id(access_token, list_name)
            print(f"    List ID: {list_id}")

            existing_columns = get_existing_columns(access_token, list_id)
            results[list_name] = {'added': [], 'skipped': [], 'errors': []}

            for column_def in NEW_COLUMNS:
                col_name = column_def['name']

                if col_name in existing_columns:
                    print(f"    [{col_name}] Already exists - skipping")
                    results[list_name]['skipped'].append(col_name)
                    continue

                if add_column(access_token, list_id, column_def):
                    print(f"    [{col_name}] Added successfully")
                    results[list_name]['added'].append(col_name)
                else:
                    results[list_name]['errors'].append(col_name)

        except Exception as e:
            print(f"    ERROR: {e}")
            results[list_name] = {'error': str(e)}

    # Summary
    print("\n[3/3] Summary")
    print("-" * 40)
    for list_name, result in results.items():
        if 'error' in result:
            print(f"  {list_name}: ERROR - {result['error']}")
        else:
            added = len(result['added'])
            skipped = len(result['skipped'])
            errors = len(result['errors'])
            print(f"  {list_name}: {added} added, {skipped} skipped, {errors} errors")
            if result['added']:
                print(f"    Added: {', '.join(result['added'])}")

    print("\n" + "=" * 60)
    print("Schema update complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
