import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
EE Team Dashboard - Daily Summary Generator
Generates and updates SharePoint page with project/ticket summaries
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class DashboardGenerator:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.base_url = "https://graph.microsoft.com/beta"
        self.token = None
        self.site_id = None
        self.page_id = "e33a46d9-990e-4060-9133-450e48c88c2f"

    def get_token(self):
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
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/json'
        }

    def find_site(self):
        resp = requests.get(
            "https://graph.microsoft.com/v1.0/sites?search=SOCTEAM",
            headers=self.get_headers()
        )
        for site in resp.json().get('value', []):
            if 'SOCTEAM' in site.get('webUrl', ''):
                self.site_id = site['id']
                return True
        return False

    def get_list_data(self):
        """Get all projects and tickets"""
        headers = self.get_headers()
        v1_url = "https://graph.microsoft.com/v1.0"

        # Get lists
        resp = requests.get(f"{v1_url}/sites/{self.site_id}/lists", headers=headers)
        lists = resp.json().get('value', [])

        projects_id = None
        tickets_id = None
        for lst in lists:
            if lst['displayName'] == 'Engineering Projects':
                projects_id = lst['id']
            elif lst['displayName'] == 'Engineering Tickets':
                tickets_id = lst['id']

        # Get items
        projects = []
        tickets = []

        if projects_id:
            resp = requests.get(
                f"{v1_url}/sites/{self.site_id}/lists/{projects_id}/items?expand=fields",
                headers=headers
            )
            projects = resp.json().get('value', [])

        if tickets_id:
            resp = requests.get(
                f"{v1_url}/sites/{self.site_id}/lists/{tickets_id}/items?expand=fields",
                headers=headers
            )
            tickets = resp.json().get('value', [])

        return projects, tickets

    def generate_summary(self, projects, tickets):
        """Generate HTML summary content"""
        today = datetime.now().strftime('%B %d, %Y')

        # Calculate stats
        total_projects = len(projects)
        projects_in_progress = len([p for p in projects if p['fields'].get('Status') == 'In Progress'])
        projects_completed = len([p for p in projects if p['fields'].get('Status') == 'Completed'])

        total_tickets = len(tickets)
        tickets_open = len([t for t in tickets if t['fields'].get('Status') in ['Open', 'In Progress']])
        tickets_high = len([t for t in tickets if t['fields'].get('Priority') in ['High', 'Critical']])
        tickets_resolved = len([t for t in tickets if t['fields'].get('Status') in ['Resolved', 'Closed']])

        # Build HTML
        html = f'''
<div style="font-family: Segoe UI, sans-serif; max-width: 1200px; margin: 0 auto;">

    <!-- Header -->
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px;">
        <h1 style="margin: 0 0 10px 0; font-size: 28px;">EE Team Daily Summary</h1>
        <p style="margin: 0; opacity: 0.9;">Last updated: {today}</p>
    </div>

    <!-- Stats Cards -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;">
            <div style="font-size: 32px; font-weight: bold; color: #1e3a5f;">{total_projects}</div>
            <div style="color: #666; font-size: 14px;">Total Projects</div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #ff9800;">
            <div style="font-size: 32px; font-weight: bold; color: #1e3a5f;">{projects_in_progress}</div>
            <div style="color: #666; font-size: 14px;">Projects In Progress</div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #2196F3;">
            <div style="font-size: 32px; font-weight: bold; color: #1e3a5f;">{total_tickets}</div>
            <div style="color: #666; font-size: 14px;">Total Tickets</div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #f44336;">
            <div style="font-size: 32px; font-weight: bold; color: #1e3a5f;">{tickets_high}</div>
            <div style="color: #666; font-size: 14px;">High Priority Tickets</div>
        </div>
    </div>

    <!-- Two Column Layout -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">

        <!-- Projects Section -->
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">
            <div style="background: #1e3a5f; color: white; padding: 15px 20px; font-weight: 600;">
                Active Projects
            </div>
            <div style="padding: 0;">
                {''.join([f"""
                <div style="padding: 15px 20px; border-bottom: 1px solid #eee;">
                    <div style="font-weight: 500; color: #1e3a5f; margin-bottom: 5px;">
                        {p['fields'].get('ProjectName', 'Untitled')}
                    </div>
                    <div style="display: flex; gap: 10px; font-size: 12px;">
                        <span style="background: {'#fff3e0' if p['fields'].get('Status') == 'In Progress' else '#e8f5e9' if p['fields'].get('Status') == 'Completed' else '#e9ecef'};
                               color: {'#ef6c00' if p['fields'].get('Status') == 'In Progress' else '#2e7d32' if p['fields'].get('Status') == 'Completed' else '#495057'};
                               padding: 2px 8px; border-radius: 10px;">
                            {p['fields'].get('Status', 'Not Started')}
                        </span>
                        <span style="color: #666;">{p['fields'].get('Team', '')}</span>
                    </div>
                </div>
                """ for p in projects if p['fields'].get('Status') != 'Completed'][:5]) or '<div style="padding: 20px; color: #666; text-align: center;">No active projects</div>'}
            </div>
        </div>

        <!-- Tickets Section -->
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">
            <div style="background: #1e3a5f; color: white; padding: 15px 20px; font-weight: 600;">
                Open Tickets
            </div>
            <div style="padding: 0;">
                {''.join([f"""
                <div style="padding: 15px 20px; border-bottom: 1px solid #eee;">
                    <div style="font-weight: 500; color: #1e3a5f; margin-bottom: 5px;">
                        {t['fields'].get('TicketTitle', 'Untitled')}
                    </div>
                    <div style="display: flex; gap: 10px; font-size: 12px;">
                        <span style="background: {'#ffebee' if t['fields'].get('Priority') in ['High', 'Critical'] else '#fff3e0' if t['fields'].get('Priority') == 'Medium' else '#e8f5e9'};
                               color: {'#c62828' if t['fields'].get('Priority') in ['High', 'Critical'] else '#ef6c00' if t['fields'].get('Priority') == 'Medium' else '#2e7d32'};
                               padding: 2px 8px; border-radius: 10px;">
                            {t['fields'].get('Priority', 'Medium')}
                        </span>
                        <span style="color: #666;">{t['fields'].get('AssignedTo', 'Unassigned')}</span>
                    </div>
                </div>
                """ for t in tickets if t['fields'].get('Status') not in ['Resolved', 'Closed']][:5]) or '<div style="padding: 20px; color: #666; text-align: center;">No open tickets</div>'}
            </div>
        </div>

    </div>

    <!-- Quick Links -->
    <div style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px; text-align: center;">
        <a href="https://oberaconnect.sharepoint.com/sites/SOCTEAM-Engineering/Lists/Engineering%20Projects"
           style="display: inline-block; margin: 0 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: 500;">
            View All Projects
        </a>
        <a href="https://oberaconnect.sharepoint.com/sites/SOCTEAM-Engineering/Lists/Engineering%20Tickets"
           style="display: inline-block; margin: 0 10px; padding: 10px 20px; background: #1e3a5f; color: white; text-decoration: none; border-radius: 4px; font-weight: 500;">
            View All Tickets
        </a>
    </div>

</div>
'''
        return html

    def update_page(self):
        """Update the SharePoint page with new content"""
        if not self.find_site():
            print("Site not found")
            return False

        # Get data
        projects, tickets = self.get_list_data()
        print(f"Found {len(projects)} projects, {len(tickets)} tickets")

        # Generate summary
        html_content = self.generate_summary(projects, tickets)

        # Update page with web parts
        # First, get the page
        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/pages/{self.page_id}",
            headers=self.get_headers()
        )

        if resp.status_code != 200:
            print(f"Failed to get page: {resp.status_code}")
            return False

        # Update with canvas content
        update_data = {
            "title": "EE Team Dashboard",
            "canvasLayout": {
                "horizontalSections": [
                    {
                        "layout": "fullWidth",
                        "columns": [
                            {
                                "width": 12,
                                "webparts": [
                                    {
                                        "type": "d1d91016-032f-456d-98a4-721247c305e8",  # Text web part
                                        "data": {
                                            "innerHTML": html_content
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        resp = requests.patch(
            f"{self.base_url}/sites/{self.site_id}/pages/{self.page_id}",
            headers=self.get_headers(),
            json=update_data
        )

        if resp.status_code in [200, 204]:
            print("Page content updated")

            # Publish the page
            resp = requests.post(
                f"{self.base_url}/sites/{self.site_id}/pages/{self.page_id}/publish",
                headers=self.get_headers()
            )

            if resp.status_code in [200, 204]:
                print("Page published")
                print("\nDashboard URL:")
                print("https://oberaconnect.sharepoint.com/sites/SOCTEAM-Engineering/SitePages/EE-Team-Dashboard.aspx")
                return True
            else:
                print(f"Publish failed: {resp.status_code}")
        else:
            print(f"Update failed: {resp.status_code}")
            print(resp.text[:500])

        return False


def main():
    print("=" * 60)
    print("EE Team Dashboard - Daily Summary Generator")
    print("=" * 60)

    generator = DashboardGenerator()
    generator.update_page()

    print("\nTo set up automatic daily updates:")
    print("Add a cron job or scheduled task to run this script daily")
    print("Example cron: 0 8 * * * /home/mavrick/Projects/Secondbrain/venv/bin/python /home/mavrick/Projects/Secondbrain/ee_team_dashboard.py")


if __name__ == "__main__":
    main()
