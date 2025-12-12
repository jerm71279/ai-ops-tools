#!/usr/bin/env python3
"""
Create Employees SharePoint List via Microsoft Graph API
Stores all team members with roles, departments, and billable rates
"""

import requests
import json
import sys
import time

# Configuration
TENANT_ID = "ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd"
SITE_ID = "oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef"
GRAPH_API = "https://graph.microsoft.com/v1.0"

# Azure app registration client ID
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"

def get_access_token():
    """Get access token using device code flow"""
    device_code_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
    response = requests.post(device_code_url, data={
        "client_id": CLIENT_ID,
        "scope": "https://graph.microsoft.com/Sites.FullControl.All https://graph.microsoft.com/Sites.Manage.All"
    })

    if response.status_code != 200:
        print(f"Error getting device code: {response.text}")
        sys.exit(1)

    device_data = response.json()
    print("\n" + "="*60)
    print("AUTHENTICATION REQUIRED")
    print("="*60)
    print(f"\n{device_data['message']}\n")
    print("="*60 + "\n")

    # Poll for token
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
            time.sleep(device_data.get("interval", 5))
        else:
            print(f"Error getting token: {token_data}")
            sys.exit(1)

def create_list(token):
    """Create the Employees list"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    list_data = {
        "displayName": "Employees",
        "description": "Team members with roles, departments, and billing rates",
        "list": {
            "template": "genericList"
        }
    }

    print("Creating Employees list...")
    response = requests.post(
        f"{GRAPH_API}/sites/{SITE_ID}/lists",
        headers=headers,
        json=list_data
    )

    if response.status_code == 201:
        list_info = response.json()
        print(f"✓ List created successfully! ID: {list_info['id']}")
        return list_info['id']
    elif response.status_code == 409:
        print("List already exists. Fetching existing list...")
        lists_response = requests.get(
            f"{GRAPH_API}/sites/{SITE_ID}/lists",
            headers=headers
        )
        for lst in lists_response.json().get('value', []):
            if lst['displayName'].lower() == 'employees':
                print(f"✓ Found existing list ID: {lst['id']}")
                return lst['id']
    else:
        print(f"Error creating list: {response.status_code}")
        print(response.text)
        sys.exit(1)

def add_columns(token, list_id):
    """Add custom columns to the Employees list"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    columns = [
        {
            "name": "EmployeeName",
            "displayName": "Employee Name",
            "text": {"maxLength": 255},
            "required": True
        },
        {
            "name": "Email",
            "displayName": "Email",
            "text": {"maxLength": 255},
            "required": True
        },
        {
            "name": "AzureADId",
            "displayName": "Azure AD ID",
            "text": {"maxLength": 255},
            "description": "Links to Azure AD user for SSO"
        },
        {
            "name": "Role",
            "displayName": "Role",
            "choice": {
                "choices": [
                    "Engineer",
                    "Senior Engineer",
                    "Lead Engineer",
                    "Project Manager",
                    "Account Manager",
                    "Support Technician",
                    "Administrator",
                    "Executive"
                ],
                "displayAs": "dropDownMenu"
            },
            "required": True
        },
        {
            "name": "Department",
            "displayName": "Department",
            "choice": {
                "choices": [
                    "Engineering",
                    "Support",
                    "Sales",
                    "Operations",
                    "Management",
                    "Administration"
                ],
                "displayAs": "dropDownMenu"
            },
            "required": True
        },
        {
            "name": "BillableRate",
            "displayName": "Billable Rate ($/hr)",
            "number": {
                "decimalPlaces": "two",
                "minimum": 0,
                "maximum": 500
            },
            "description": "Standard hourly billing rate for this employee"
        },
        {
            "name": "CostRate",
            "displayName": "Cost Rate ($/hr)",
            "number": {
                "decimalPlaces": "two",
                "minimum": 0,
                "maximum": 500
            },
            "description": "Internal cost rate for profitability calculations"
        },
        {
            "name": "TargetUtilization",
            "displayName": "Target Utilization %",
            "number": {
                "decimalPlaces": "zero",
                "minimum": 0,
                "maximum": 100
            },
            "defaultValue": {"value": "75"},
            "description": "Target billable hours percentage (e.g., 75%)"
        },
        {
            "name": "WeeklyHours",
            "displayName": "Weekly Hours",
            "number": {
                "decimalPlaces": "zero",
                "minimum": 0,
                "maximum": 60
            },
            "defaultValue": {"value": "40"},
            "description": "Standard work hours per week"
        },
        {
            "name": "StartDate",
            "displayName": "Start Date",
            "dateTime": {"format": "dateOnly"},
            "description": "Employee start date"
        },
        {
            "name": "Status",
            "displayName": "Status",
            "choice": {
                "choices": ["Active", "Inactive", "On Leave", "Terminated"],
                "displayAs": "dropDownMenu"
            },
            "defaultValue": {"value": "Active"}
        },
        {
            "name": "ReportsTo",
            "displayName": "Reports To",
            "text": {"maxLength": 255},
            "description": "Manager's name or email"
        },
        {
            "name": "Skills",
            "displayName": "Skills",
            "text": {
                "allowMultipleLines": True,
                "maxLength": 2000
            },
            "description": "Comma-separated list of skills/certifications"
        },
        {
            "name": "Notes",
            "displayName": "Notes",
            "text": {
                "allowMultipleLines": True,
                "maxLength": 5000
            }
        }
    ]

    for col in columns:
        print(f"Adding column: {col['displayName']}...", end=" ")
        response = requests.post(
            f"{GRAPH_API}/sites/{SITE_ID}/lists/{list_id}/columns",
            headers=headers,
            json=col
        )

        if response.status_code == 201:
            print("✓")
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print("(already exists)")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  {response.text[:200]}")

def add_sample_employees(token, list_id):
    """Add sample employees based on current ALLOWED_USERS"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Sample employees based on existing ALLOWED_USERS
    sample_employees = [
        {
            "fields": {
                "Title": "Mavrick Faison",
                "EmployeeName": "Mavrick Faison",
                "Email": "mfaison@oberaconnect.com",
                "Role": "Lead Engineer",
                "Department": "Engineering",
                "BillableRate": 150,
                "CostRate": 75,
                "TargetUtilization": 75,
                "WeeklyHours": 40,
                "Status": "Active"
            }
        },
        {
            "fields": {
                "Title": "Patrick McFarland",
                "EmployeeName": "Patrick McFarland",
                "Email": "pmcfarland@oberaconnect.com",
                "Role": "Senior Engineer",
                "Department": "Engineering",
                "BillableRate": 135,
                "CostRate": 65,
                "TargetUtilization": 80,
                "WeeklyHours": 40,
                "Status": "Active"
            }
        },
        {
            "fields": {
                "Title": "Robbie McFarland",
                "EmployeeName": "Robbie McFarland",
                "Email": "rmcfarland@oberaconnect.com",
                "Role": "Executive",
                "Department": "Management",
                "BillableRate": 200,
                "CostRate": 100,
                "TargetUtilization": 50,
                "WeeklyHours": 40,
                "Status": "Active"
            }
        }
    ]

    print("\nAdding sample employees...")
    for emp in sample_employees:
        name = emp['fields']['EmployeeName']
        print(f"  Adding {name}...", end=" ")

        response = requests.post(
            f"{GRAPH_API}/sites/{SITE_ID}/lists/{list_id}/items",
            headers=headers,
            json=emp
        )

        if response.status_code == 201:
            print("✓")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"    {response.text[:200]}")

def main():
    print("\n" + "="*60)
    print("Employees SharePoint List Creator")
    print("="*60)
    print("\nThis will create an Employees list with:")
    print("  • Employee Name, Email, Azure AD ID")
    print("  • Role & Department")
    print("  • Billable Rate & Cost Rate ($/hr)")
    print("  • Target Utilization %")
    print("  • Weekly Hours")
    print("  • Status (Active/Inactive/On Leave)")
    print("  • Reports To, Skills, Notes")
    print("="*60 + "\n")

    # Get access token
    token = get_access_token()
    print("\n✓ Authentication successful!\n")

    # Create list
    list_id = create_list(token)

    # Add columns
    print("\nAdding columns to the list...")
    add_columns(token, list_id)

    # Ask about sample data
    add_samples = input("\nAdd sample employees (Mavrick, Patrick, Robbie)? [y/N]: ").strip().lower()
    if add_samples == 'y':
        add_sample_employees(token, list_id)

    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    print(f"\nEmployees list is ready.")
    print(f"List ID: {list_id}")
    print("\nNext steps:")
    print("1. Add your team members to the Employees list in SharePoint")
    print("2. The dashboard will load employees from this list")
    print("3. Time entries will use employee billable rates for reports")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
