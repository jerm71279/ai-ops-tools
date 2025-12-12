#!/usr/bin/env python3
"""
Create TimeEntries SharePoint List via Microsoft Graph API
"""

import requests
import json
import sys
import time

TENANT_ID = "ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd"
SITE_ID = "oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef"
GRAPH_API = "https://graph.microsoft.com/v1.0"
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"

def get_access_token():
    device_code_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
    response = requests.post(device_code_url, data={
        "client_id": CLIENT_ID,
        "scope": "https://graph.microsoft.com/Sites.FullControl.All https://graph.microsoft.com/Sites.Manage.All"
    })
    if response.status_code != 200:
        print(f"Error: {response.text}")
        sys.exit(1)
    device_data = response.json()
    print("\n" + "="*60)
    print("GO TO: https://microsoft.com/devicelogin")
    print(f"ENTER CODE: {device_data['user_code']}")
    print("="*60 + "\n")
    
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    while True:
        token_response = requests.post(token_url, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": CLIENT_ID,
            "device_code": device_data["device_code"]
        })
        token_data = token_response.json()
        if "access_token" in token_data:
            return token_data["access_token"]
        elif token_data.get("error") == "authorization_pending":
            time.sleep(5)
        else:
            print(f"Error: {token_data}")
            sys.exit(1)

def main():
    print("\nTimeEntries List Creator")
    print("="*60)
    token = get_access_token()
    print("✓ Authenticated!\n")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create list
    print("Creating TimeEntries list...")
    response = requests.post(f"{GRAPH_API}/sites/{SITE_ID}/lists", headers=headers, json={
        "displayName": "TimeEntries",
        "description": "Time tracking entries",
        "list": {"template": "genericList"}
    })
    
    if response.status_code == 201:
        list_id = response.json()['id']
        print(f"✓ Created! ID: {list_id}")
    elif response.status_code == 409:
        print("List exists, finding it...")
        lists = requests.get(f"{GRAPH_API}/sites/{SITE_ID}/lists", headers=headers).json()
        list_id = next((l['id'] for l in lists.get('value', []) if l['displayName'].lower() == 'timeentries'), None)
        print(f"✓ Found: {list_id}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)
    
    # Add columns
    columns = [
        {"name": "Employee", "displayName": "Employee", "text": {"maxLength": 255}, "required": True},
        {"name": "EntryDate", "displayName": "Date", "dateTime": {"format": "dateOnly"}, "required": True},
        {"name": "Hours", "displayName": "Hours", "number": {"decimalPlaces": "two", "minimum": 0, "maximum": 24}, "required": True},
        {"name": "ProjectID", "displayName": "Project ID", "text": {"maxLength": 255}},
        {"name": "ProjectName", "displayName": "Project Name", "text": {"maxLength": 255}},
        {"name": "TicketID", "displayName": "Ticket ID", "text": {"maxLength": 255}},
        {"name": "TicketTitle", "displayName": "Ticket Title", "text": {"maxLength": 255}},
        {"name": "TaskID", "displayName": "Task ID", "text": {"maxLength": 255}},
        {"name": "Description", "displayName": "Description", "text": {"allowMultipleLines": True, "maxLength": 5000}},
        {"name": "Billable", "displayName": "Billable", "boolean": {}, "defaultValue": {"value": "true"}},
        {"name": "BillableRate", "displayName": "Billable Rate", "number": {"decimalPlaces": "two", "minimum": 0}},
        {"name": "Category", "displayName": "Category", "choice": {"choices": ["Development", "Support", "Meeting", "Documentation", "Testing", "Other"], "displayAs": "dropDownMenu"}},
        {"name": "Status", "displayName": "Status", "choice": {"choices": ["Draft", "Submitted", "Approved", "Invoiced"], "displayAs": "dropDownMenu"}, "defaultValue": {"value": "Draft"}}
    ]
    
    print("\nAdding columns...")
    for col in columns:
        r = requests.post(f"{GRAPH_API}/sites/{SITE_ID}/lists/{list_id}/columns", headers=headers, json=col)
        status = "✓" if r.status_code == 201 else "(exists)" if "already exists" in r.text.lower() else f"✗ {r.status_code}"
        print(f"  {col['displayName']}: {status}")
    
    print("\n" + "="*60)
    print("DONE! TimeEntries list is ready.")
    print(f"List ID: {list_id}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
