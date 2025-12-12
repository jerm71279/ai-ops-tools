#!/usr/bin/env python3
"""
Engineering Tracker - OberaConnect
Manages projects and tickets via SharePoint Lists
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class EngineeringTracker:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = None
        self.site_id = None
        self.projects_list_id = None
        self.tickets_list_id = None
        self.tasks_list_id = None

    def get_token(self):
        """Get OAuth token"""
        if self.token:
            return self.token

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        response = requests.post(url, data=data)
        self.token = response.json().get('access_token')
        return self.token

    def get_headers(self):
        """Get auth headers"""
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/json'
        }

    def find_site(self):
        """Find EE TEAM site"""
        resp = requests.get(
            f"{self.base_url}/sites?search=SOCTEAM",
            headers=self.get_headers()
        )
        sites = resp.json().get('value', [])

        for site in sites:
            if 'SOCTEAM' in site.get('webUrl', ''):
                self.site_id = site['id']
                print(f"Found site: {site.get('displayName')}")
                return True

        print("Site not found")
        return False

    def find_lists(self):
        """Find Projects and Tickets lists"""
        if not self.site_id:
            return False

        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/lists",
            headers=self.get_headers()
        )
        lists = resp.json().get('value', [])

        for lst in lists:
            if lst['displayName'] == 'Engineering Projects':
                self.projects_list_id = lst['id']
                print(f"Found Projects list: {lst['id']}")
            elif lst['displayName'] == 'Engineering Tickets':
                self.tickets_list_id = lst['id']
                print(f"Found Tickets list: {lst['id']}")
            elif lst['displayName'] == 'Engineering Tasks':
                self.tasks_list_id = lst['id']
                print(f"Found Tasks list: {lst['id']}")

        return self.projects_list_id and self.tickets_list_id and self.tasks_list_id

    def generate_dashboard(self, output_path=None):
        """Generate configured dashboard HTML"""
        template_path = Path(__file__).parent / "engineering_command_center.html"

        if not template_path.exists():
            print(f"Template not found: {template_path}")
            return None

        html = template_path.read_text()

        # Replace placeholders
        html = html.replace('{{SITE_ID}}', self.site_id or '')
        html = html.replace('{{PROJECTS_LIST_ID}}', self.projects_list_id or '')
        html = html.replace('{{TICKETS_LIST_ID}}', self.tickets_list_id or '')
        html = html.replace('{{TASKS_LIST_ID}}', self.tasks_list_id or '')
        html = html.replace('{{ACCESS_TOKEN}}', self.get_token() or '')

        # Libraries now loaded from CDN with defer attribute

        if output_path:
            Path(output_path).write_text(html)
            print(f"Dashboard saved to: {output_path}")

        return html

    def _inline_libraries(self, html):
        """Inline external JS libraries for Teams iframe compatibility"""
        lib_dir = Path(__file__).parent / "libs"
        lib_dir.mkdir(exist_ok=True)

        # Lucide Icons
        lucide_path = lib_dir / "lucide.min.js"
        if not lucide_path.exists():
            print("Downloading Lucide icons library...")
            resp = requests.get("https://unpkg.com/lucide@0.294.0/dist/umd/lucide.min.js")
            if resp.status_code == 200:
                lucide_path.write_text(resp.text)
        if lucide_path.exists():
            html = html.replace('LUCIDE_PLACEHOLDER', lucide_path.read_text())

        # SortableJS
        sortable_path = lib_dir / "sortable.min.js"
        if not sortable_path.exists():
            print("Downloading SortableJS library...")
            resp = requests.get("https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js")
            if resp.status_code == 200:
                sortable_path.write_text(resp.text)
        if sortable_path.exists():
            html = html.replace('SORTABLE_PLACEHOLDER', sortable_path.read_text())

        return html

    def upload_to_sharepoint(self, html_content, filename="Engineering_Tracker.html"):
        """Upload dashboard to SharePoint"""
        if not self.site_id:
            return False

        # Get Documents drive
        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/drives",
            headers=self.get_headers()
        )
        drives = resp.json().get('value', [])

        drive_id = None
        for drive in drives:
            if drive['name'] == 'Documents':
                drive_id = drive['id']
                break

        if not drive_id:
            print("Documents drive not found")
            return False

        # Upload file
        headers = {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/octet-stream'
        }

        url = f"{self.base_url}/sites/{self.site_id}/drives/{drive_id}/root:/{filename}:/content"
        response = requests.put(url, headers=headers, data=html_content.encode('utf-8'))

        if response.status_code in [200, 201]:
            web_url = response.json().get('webUrl', '')
            print(f"Uploaded to SharePoint: {web_url}")
            return True
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return False

    def add_project(self, name, description="", status="Not Started", priority="Medium",
                    assignee="", team="Engineering", customer="", due_date=None, notes=""):
        """Add a new project"""
        data = {
            "fields": {
                "ProjectName": name,
                "Description": description,
                "Status": status,
                "Priority": priority,
                "AssignedTo": assignee,
                "Team": team,
                "Customer": customer,
                "Notes": notes
            }
        }
        if due_date:
            data["fields"]["DueDate"] = due_date

        resp = requests.post(
            f"{self.base_url}/sites/{self.site_id}/lists/{self.projects_list_id}/items",
            headers=self.get_headers(),
            json=data
        )

        if resp.status_code in [200, 201]:
            print(f"Added project: {name}")
            return resp.json()
        else:
            print(f"Failed to add project: {resp.status_code}")
            return None

    def add_ticket(self, title, description="", status="Open", priority="Medium",
                   assignee="", team="Engineering", customer="", due_date=None,
                   related_project="", resolution=""):
        """Add a new ticket"""
        data = {
            "fields": {
                "TicketTitle": title,
                "Description": description,
                "Status": status,
                "Priority": priority,
                "AssignedTo": assignee,
                "Team": team,
                "Customer": customer,
                "RelatedProject": related_project,
                "Resolution": resolution
            }
        }
        if due_date:
            data["fields"]["DueDate"] = due_date

        resp = requests.post(
            f"{self.base_url}/sites/{self.site_id}/lists/{self.tickets_list_id}/items",
            headers=self.get_headers(),
            json=data
        )

        if resp.status_code in [200, 201]:
            print(f"Added ticket: {title}")
            return resp.json()
        else:
            print(f"Failed to add ticket: {resp.status_code}")
            return None

    def list_projects(self):
        """List all projects"""
        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/lists/{self.projects_list_id}/items?expand=fields",
            headers=self.get_headers()
        )
        return resp.json().get('value', [])

    def list_tickets(self):
        """List all tickets"""
        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/lists/{self.tickets_list_id}/items?expand=fields",
            headers=self.get_headers()
        )
        return resp.json().get('value', [])


def main():
    tracker = EngineeringTracker()

    print("=" * 60)
    print("Engineering Tracker - OberaConnect")
    print("=" * 60)

    # Initialize
    if not tracker.find_site():
        print("Error: Could not find EE TEAM site")
        sys.exit(1)

    if not tracker.find_lists():
        print("Error: Could not find Engineering lists")
        sys.exit(1)

    # Menu
    while True:
        print("\n--- Menu ---")
        print("1. Generate dashboard (local)")
        print("2. Upload dashboard to SharePoint")
        print("3. Add sample data")
        print("4. List projects")
        print("5. List tickets")
        print("6. Add project")
        print("7. Add ticket")
        print("8. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == '1':
            output = Path(__file__).parent / "output" / "Engineering_Tracker.html"
            output.parent.mkdir(exist_ok=True)
            tracker.generate_dashboard(str(output))
            print(f"\nOpen in browser: file://{output}")

        elif choice == '2':
            html = tracker.generate_dashboard()
            if html:
                tracker.upload_to_sharepoint(html)

        elif choice == '3':
            # Add sample projects
            tracker.add_project(
                "rev.io Migration",
                "Migrate billing system from OneBill to rev.io",
                "In Progress",
                "High",
                "Engineering Team",
                "Engineering"
            )
            tracker.add_project(
                "Network Monitoring Setup",
                "Implement comprehensive network monitoring",
                "Not Started",
                "Medium",
                "",
                "Network"
            )

            # Add sample tickets
            tracker.add_ticket(
                "Configure rev.io API integration",
                "Set up API connections for rev.io billing",
                "Open",
                "High",
                "",
                "Engineering",
                "",
                None,
                "rev.io Migration"
            )
            tracker.add_ticket(
                "Update customer templates",
                "Update all customer templates for new branding",
                "Pending",
                "Medium",
                "",
                "Support"
            )
            print("\nSample data added")

        elif choice == '4':
            projects = tracker.list_projects()
            print(f"\n--- Projects ({len(projects)}) ---")
            for p in projects:
                f = p['fields']
                print(f"  - {f.get('ProjectName', 'Untitled')} [{f.get('Status', 'N/A')}] - {f.get('Priority', 'N/A')}")

        elif choice == '5':
            tickets = tracker.list_tickets()
            print(f"\n--- Tickets ({len(tickets)}) ---")
            for t in tickets:
                f = t['fields']
                print(f"  - {f.get('TicketTitle', 'Untitled')} [{f.get('Status', 'N/A')}] - {f.get('Priority', 'N/A')}")

        elif choice == '6':
            print("\n--- New Project ---")
            name = input("Project name: ").strip()
            if not name:
                print("Name required")
                continue
            desc = input("Description: ").strip()
            status = input("Status [Not Started]: ").strip() or "Not Started"
            priority = input("Priority [Medium]: ").strip() or "Medium"
            assignee = input("Assigned to: ").strip()
            team = input("Team [Engineering]: ").strip() or "Engineering"
            customer = input("Customer: ").strip()

            tracker.add_project(name, desc, status, priority, assignee, team, customer)

        elif choice == '7':
            print("\n--- New Ticket ---")
            title = input("Ticket title: ").strip()
            if not title:
                print("Title required")
                continue
            desc = input("Description: ").strip()
            status = input("Status [Open]: ").strip() or "Open"
            priority = input("Priority [Medium]: ").strip() or "Medium"
            assignee = input("Assigned to: ").strip()
            team = input("Team [Engineering]: ").strip() or "Engineering"
            customer = input("Customer: ").strip()

            tracker.add_ticket(title, desc, status, priority, assignee, team, customer)

        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
