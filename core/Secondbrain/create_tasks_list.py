#!/usr/bin/env python3
"""
Create Tasks SharePoint List via Microsoft Graph API
Tasks are linked to tickets and tracked on the Kanban board
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
    print("\nTasks List Creator")
    print("="*60)
    print("This creates a Tasks list for Kanban board task management")
    print("Tasks are linked to Tickets via TicketID field")
    print("="*60)

    token = get_access_token()
    print("✓ Authenticated!\n")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Create list
    print("Creating Tasks list...")
    response = requests.post(f"{GRAPH_API}/sites/{SITE_ID}/lists", headers=headers, json={
        "displayName": "Tasks",
        "description": "Project tasks linked to tickets for Kanban tracking",
        "list": {"template": "genericList"}
    })

    if response.status_code == 201:
        list_id = response.json()['id']
        print(f"✓ Created! ID: {list_id}")
    elif response.status_code == 409:
        print("List exists, finding it...")
        lists = requests.get(f"{GRAPH_API}/sites/{SITE_ID}/lists", headers=headers).json()
        list_id = next((l['id'] for l in lists.get('value', []) if l['displayName'].lower() == 'tasks'), None)
        print(f"✓ Found: {list_id}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    # Add columns
    columns = [
        {"name": "TaskTitle", "displayName": "Task Title", "text": {"maxLength": 255}, "required": True},
        {"name": "Description", "displayName": "Description", "text": {"allowMultipleLines": True, "maxLength": 5000}},
        {"name": "TicketID", "displayName": "Ticket ID", "text": {"maxLength": 255}, "required": True, "description": "Links task to a ticket"},
        {"name": "TicketTitle", "displayName": "Ticket Title", "text": {"maxLength": 255}},
        {"name": "ProjectID", "displayName": "Project ID", "text": {"maxLength": 255}},
        {"name": "ProjectName", "displayName": "Project Name", "text": {"maxLength": 255}},
        {"name": "Assignee", "displayName": "Assignee", "text": {"maxLength": 255}},
        {"name": "Status", "displayName": "Status", "choice": {
            "choices": ["To Do", "In Progress", "In Review", "Done", "Blocked"],
            "displayAs": "dropDownMenu"
        }, "defaultValue": {"value": "To Do"}},
        {"name": "Priority", "displayName": "Priority", "choice": {
            "choices": ["Low", "Medium", "High", "Critical"],
            "displayAs": "dropDownMenu"
        }, "defaultValue": {"value": "Medium"}},
        {"name": "DueDate", "displayName": "Due Date", "dateTime": {"format": "dateOnly"}},
        {"name": "EstimatedHours", "displayName": "Estimated Hours", "number": {"decimalPlaces": "one", "minimum": 0, "maximum": 100}},
        {"name": "ActualHours", "displayName": "Actual Hours", "number": {"decimalPlaces": "one", "minimum": 0, "maximum": 500}},
        {"name": "SortOrder", "displayName": "Sort Order", "number": {"decimalPlaces": "zero", "minimum": 0}, "defaultValue": {"value": "0"}}
    ]

    print("\nAdding columns...")
    for col in columns:
        r = requests.post(f"{GRAPH_API}/sites/{SITE_ID}/lists/{list_id}/columns", headers=headers, json=col)
        status = "✓" if r.status_code == 201 else "(exists)" if "already exists" in r.text.lower() else f"✗ {r.status_code}"
        print(f"  {col['displayName']}: {status}")

    # Ask about sample tasks
    add_samples = input("\nAdd sample tasks? [y/N]: ").strip().lower()
    if add_samples == 'y':
        # First, get existing tickets to link to
        print("\nFetching existing tickets...")
        tickets_response = requests.get(
            f"{GRAPH_API}/sites/{SITE_ID}/lists?$filter=displayName eq 'Tickets'",
            headers=headers
        )
        tickets_list = None
        if tickets_response.status_code == 200:
            lists_data = tickets_response.json().get('value', [])
            for lst in lists_data:
                if lst['displayName'].lower() == 'tickets':
                    tickets_list = lst['id']
                    break

        if tickets_list:
            items_response = requests.get(
                f"{GRAPH_API}/sites/{SITE_ID}/lists/{tickets_list}/items?expand=fields&$top=5",
                headers=headers
            )
            if items_response.status_code == 200:
                tickets = items_response.json().get('value', [])
                if tickets:
                    ticket = tickets[0]
                    ticket_id = ticket['id']
                    ticket_title = ticket['fields'].get('Title', 'Sample Ticket')
                    project_id = ticket['fields'].get('ProjectID', '')

                    sample_tasks = [
                        {
                            "fields": {
                                "Title": "Research requirements",
                                "TaskTitle": "Research requirements",
                                "Description": "Gather and document requirements for this ticket",
                                "TicketID": ticket_id,
                                "TicketTitle": ticket_title,
                                "ProjectID": project_id,
                                "Assignee": "Mavrick Faison",
                                "Status": "Done",
                                "Priority": "High",
                                "SortOrder": 0
                            }
                        },
                        {
                            "fields": {
                                "Title": "Implement solution",
                                "TaskTitle": "Implement solution",
                                "Description": "Build the core functionality",
                                "TicketID": ticket_id,
                                "TicketTitle": ticket_title,
                                "ProjectID": project_id,
                                "Assignee": "Patrick McFarland",
                                "Status": "In Progress",
                                "Priority": "High",
                                "SortOrder": 1
                            }
                        },
                        {
                            "fields": {
                                "Title": "Write tests",
                                "TaskTitle": "Write tests",
                                "Description": "Create unit and integration tests",
                                "TicketID": ticket_id,
                                "TicketTitle": ticket_title,
                                "ProjectID": project_id,
                                "Assignee": "Mavrick Faison",
                                "Status": "To Do",
                                "Priority": "Medium",
                                "SortOrder": 2
                            }
                        },
                        {
                            "fields": {
                                "Title": "Code review",
                                "TaskTitle": "Code review",
                                "Description": "Review and approve changes",
                                "TicketID": ticket_id,
                                "TicketTitle": ticket_title,
                                "ProjectID": project_id,
                                "Assignee": "Robbie McFarland",
                                "Status": "To Do",
                                "Priority": "Medium",
                                "SortOrder": 3
                            }
                        }
                    ]

                    print(f"\nAdding sample tasks linked to ticket: {ticket_title}...")
                    for task in sample_tasks:
                        name = task['fields']['TaskTitle']
                        print(f"  Adding {name}...", end=" ")
                        r = requests.post(
                            f"{GRAPH_API}/sites/{SITE_ID}/lists/{list_id}/items",
                            headers=headers,
                            json=task
                        )
                        if r.status_code == 201:
                            print("✓")
                        else:
                            print(f"✗ {r.status_code}")
                else:
                    print("No tickets found to link tasks to. Create tickets first.")
            else:
                print(f"Failed to fetch tickets: {items_response.status_code}")
        else:
            print("Tickets list not found. Create tasks manually after creating tickets.")

    print("\n" + "="*60)
    print("DONE! Tasks list is ready.")
    print(f"List ID: {list_id}")
    print("="*60)
    print("\nNext steps:")
    print("1. Refresh the dashboard to discover the new Tasks list")
    print("2. Create tasks linked to tickets via the dashboard")
    print("3. Tasks will appear on the Kanban board")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
