import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
SharePoint List Reader
Fetches and displays data from OberaConnect SharePoint Lists

Run: python list_sharepoint_data.py

Requires: You must be authenticated via Azure CLI or have a token
"""
import os
import sys
import json
import subprocess

# SharePoint Configuration
SITE_ID = "oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef"
GRAPH_API = "https://graph.microsoft.com/v1.0"

def get_access_token():
    """Get access token from Azure CLI"""
    try:
        result = subprocess.run(
            ["az", "account", "get-access-token", "--resource", "https://graph.microsoft.com"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("accessToken")
    except Exception as e:
        print(f"Error getting token from Azure CLI: {e}")

    # Check environment variable
    token = os.getenv("GRAPH_ACCESS_TOKEN")
    if token:
        return token

    return None

def fetch_lists(token):
    """Fetch all lists from SharePoint site"""
    import urllib.request

    url = f"{GRAPH_API}/sites/{SITE_ID}/lists"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("value", [])
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return []

def fetch_list_items(token, list_id, list_name):
    """Fetch items from a specific list"""
    import urllib.request

    url = f"{GRAPH_API}/sites/{SITE_ID}/lists/{list_id}/items?expand=fields&$top=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("value", [])
    except urllib.error.HTTPError as e:
        print(f"Error fetching {list_name}: {e.code} - {e.reason}")
        return []

def print_projects(items):
    """Print projects in a nice format"""
    print("\n" + "="*80)
    print("PROJECTS")
    print("="*80)

    for item in items:
        fields = item.get("fields", {})
        name = fields.get("Title") or fields.get("ProjectName") or "Unnamed"
        status = fields.get("Status", "N/A")
        priority = fields.get("Priority", "N/A")
        assigned = fields.get("AssignedTo", "Unassigned")
        customer = fields.get("Customer", "")
        percent = fields.get("PercentComplete", 0)

        print(f"\n[{item.get('id')}] {name}")
        print(f"    Status: {status} | Priority: {priority} | Progress: {percent}%")
        print(f"    Assigned: {assigned} | Customer: {customer}")

def print_tasks(items):
    """Print tasks in a nice format"""
    print("\n" + "="*80)
    print("TASKS")
    print("="*80)

    for item in items:
        fields = item.get("fields", {})
        title = fields.get("Title", "Unnamed")
        status = fields.get("Status", "N/A")
        priority = fields.get("Priority", "N/A")
        assigned = fields.get("AssignedTo", "Unassigned")
        project = fields.get("ProjectName", "No Project")
        due = fields.get("DueDate", "No due date")

        print(f"\n[{item.get('id')}] {title}")
        print(f"    Status: {status} | Priority: {priority}")
        print(f"    Assigned: {assigned} | Project: {project}")
        print(f"    Due: {due}")

def print_tickets(items):
    """Print tickets in a nice format"""
    print("\n" + "="*80)
    print("TICKETS")
    print("="*80)

    for item in items:
        fields = item.get("fields", {})
        title = fields.get("Title") or fields.get("TicketTitle") or "Unnamed"
        status = fields.get("Status", "N/A")
        priority = fields.get("Priority", "N/A")
        customer = fields.get("Customer", "Unknown")
        sla = fields.get("SLAStatus", "N/A")

        print(f"\n[{item.get('id')}] {title}")
        print(f"    Status: {status} | Priority: {priority} | SLA: {sla}")
        print(f"    Customer: {customer}")

def print_time_entries(items):
    """Print time entries summary"""
    print("\n" + "="*80)
    print("TIME ENTRIES (Last 20)")
    print("="*80)

    total_hours = 0
    billable_hours = 0

    for item in items[:20]:
        fields = item.get("fields", {})
        employee = fields.get("Employee", "Unknown")
        hours = float(fields.get("Hours", 0) or 0)
        date = fields.get("EntryDate", "")[:10] if fields.get("EntryDate") else "N/A"
        project = fields.get("ProjectName", "General")
        billable = fields.get("Billable", False)

        total_hours += hours
        if billable:
            billable_hours += hours

        bill_mark = "[$]" if billable else "   "
        print(f"  {bill_mark} {date} | {employee:20} | {hours:5.1f}h | {project}")

    print(f"\n  Total: {total_hours:.1f}h | Billable: {billable_hours:.1f}h")

def main():
    print("SharePoint List Reader for OberaConnect Engineering")
    print("-" * 50)

    # Get token
    token = get_access_token()
    if not token:
        print("\nNo access token available!")
        print("\nTo authenticate, run one of:")
        print("  1. az login (Azure CLI)")
        print("  2. Set GRAPH_ACCESS_TOKEN environment variable")
        print("\nOr copy a token from your browser's Network tab when using the app.")
        sys.exit(1)

    print("Token acquired successfully")

    # Fetch lists
    print("\nDiscovering SharePoint lists...")
    lists = fetch_lists(token)

    if not lists:
        print("No lists found or access denied")
        sys.exit(1)

    print(f"Found {len(lists)} lists:")
    for lst in lists:
        print(f"  - {lst.get('displayName')} (ID: {lst.get('id')[:8]}...)")

    # Find our target lists
    list_map = {lst.get("displayName", "").lower(): lst for lst in lists}

    # Fetch Projects
    if "projects" in list_map:
        items = fetch_list_items(token, list_map["projects"]["id"], "Projects")
        print_projects(items)

    # Fetch Tasks
    if "tasks" in list_map:
        items = fetch_list_items(token, list_map["tasks"]["id"], "Tasks")
        print_tasks(items)

    # Fetch Tickets
    if "tickets" in list_map:
        items = fetch_list_items(token, list_map["tickets"]["id"], "Tickets")
        print_tickets(items)

    # Fetch TimeEntries
    for name in ["timeentries", "time entries"]:
        if name in list_map:
            items = fetch_list_items(token, list_map[name]["id"], "TimeEntries")
            print_time_entries(items)
            break

    print("\n" + "="*80)
    print("Done!")

if __name__ == "__main__":
    main()
