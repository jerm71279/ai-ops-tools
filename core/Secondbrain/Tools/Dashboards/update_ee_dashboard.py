import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Update EE Team Dashboard - Run daily via cron
Regenerates the dashboard HTML with current project/ticket data
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/mavrick/Projects/Secondbrain/.env')

def main():
    # Get token
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')

    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    token_resp = requests.post(token_url, data=token_data)
    token = token_resp.json().get('access_token')

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    base_url = 'https://graph.microsoft.com/v1.0'

    # Get EE TEAM site (SOCTEAM)
    resp = requests.get(f'{base_url}/sites?search=SOCTEAM', headers=headers)
    sites = resp.json().get('value', [])
    site_id = None
    for site in sites:
        if site.get('webUrl') == 'https://oberaconnect.sharepoint.com/sites/SOCTEAM':
            site_id = site['id']
            break

    if not site_id:
        print("Site not found")
        return

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

    # Get items
    resp = requests.get(f'{base_url}/sites/{site_id}/lists/{projects_id}/items?expand=fields', headers=headers)
    projects = resp.json().get('value', [])

    resp = requests.get(f'{base_url}/sites/{site_id}/lists/{tickets_id}/items?expand=fields', headers=headers)
    tickets = resp.json().get('value', [])

    # Stats
    total_projects = len(projects)
    projects_in_progress = len([p for p in projects if p['fields'].get('Status') == 'In Progress'])
    total_tickets = len(tickets)
    tickets_high = len([t for t in tickets if t['fields'].get('Priority') in ['High', 'Critical']])

    today = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    # Generate HTML
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>EE Team Dashboard</title>
    <style>
        body {{ font-family: Segoe UI, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header p {{ margin: 0; opacity: 0.9; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-card .number {{ font-size: 32px; font-weight: bold; color: #1e3a5f; }}
        .stat-card .label {{ color: #666; font-size: 14px; }}
        .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
        .card-header {{ background: #1e3a5f; color: white; padding: 15px 20px; font-weight: 600; }}
        .item {{ padding: 15px 20px; border-bottom: 1px solid #eee; }}
        .item-title {{ font-weight: 500; color: #1e3a5f; margin-bottom: 5px; }}
        .item-meta {{ display: flex; gap: 10px; font-size: 12px; }}
        .badge {{ padding: 2px 8px; border-radius: 10px; }}
        .badge-progress {{ background: #fff3e0; color: #ef6c00; }}
        .badge-high {{ background: #ffebee; color: #c62828; }}
        .badge-medium {{ background: #fff3e0; color: #ef6c00; }}
        .badge-low {{ background: #e8f5e9; color: #2e7d32; }}
        .links {{ margin-top: 30px; padding: 20px; background: white; border-radius: 8px; text-align: center; }}
        .links a {{ display: inline-block; margin: 0 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: 500; }}
        .links a.secondary {{ background: #1e3a5f; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>EE Team Daily Summary</h1>
            <p>Last updated: {today}</p>
        </div>

        <div class="stats">
            <div class="stat-card" style="border-left: 4px solid #4CAF50;">
                <div class="number">{total_projects}</div>
                <div class="label">Total Projects</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #ff9800;">
                <div class="number">{projects_in_progress}</div>
                <div class="label">In Progress</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #2196F3;">
                <div class="number">{total_tickets}</div>
                <div class="label">Total Tickets</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #f44336;">
                <div class="number">{tickets_high}</div>
                <div class="label">High Priority</div>
            </div>
        </div>

        <div class="two-col">
            <div class="card">
                <div class="card-header">Active Projects</div>
                {''.join([f"""
                <div class="item">
                    <div class="item-title">{p['fields'].get('ProjectName', 'Untitled')}</div>
                    <div class="item-meta">
                        <span class="badge badge-progress">{p['fields'].get('Status', 'Not Started')}</span>
                        <span style="color: #666;">{p['fields'].get('Team', '')}</span>
                    </div>
                </div>
                """ for p in projects if p['fields'].get('Status') != 'Completed'][:5]) or '<div class="item" style="color: #666;">No active projects</div>'}
            </div>

            <div class="card">
                <div class="card-header">Open Tickets</div>
                {''.join([f"""
                <div class="item">
                    <div class="item-title">{t['fields'].get('TicketTitle', 'Untitled')}</div>
                    <div class="item-meta">
                        <span class="badge badge-{'high' if t['fields'].get('Priority') in ['High', 'Critical'] else 'medium' if t['fields'].get('Priority') == 'Medium' else 'low'}">{t['fields'].get('Priority', 'Medium')}</span>
                        <span style="color: #666;">{t['fields'].get('AssignedTo', 'Unassigned')}</span>
                    </div>
                </div>
                """ for t in tickets if t['fields'].get('Status') not in ['Resolved', 'Closed']][:5]) or '<div class="item" style="color: #666;">No open tickets</div>'}
            </div>
        </div>

        <div class="links">
            <a href="https://oberaconnect.sharepoint.com/sites/SOCTEAM/Lists/Engineering%20Projects">View All Projects</a>
            <a href="https://oberaconnect.sharepoint.com/sites/SOCTEAM/Lists/Engineering%20Tickets" class="secondary">View All Tickets</a>
        </div>
    </div>
</body>
</html>'''

    # Upload to SharePoint
    resp = requests.get(f'{base_url}/sites/{site_id}/drives', headers={'Authorization': f'Bearer {token}'})
    drives = resp.json().get('value', [])
    drive_id = None
    for drive in drives:
        if drive['name'] == 'Documents':
            drive_id = drive['id']
            break

    upload_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/octet-stream'
    }

    url = f'{base_url}/sites/{site_id}/drives/{drive_id}/root:/EE_Team_Dashboard.html:/content'
    response = requests.put(url, headers=upload_headers, data=html.encode('utf-8'))

    if response.status_code in [200, 201]:
        print(f'{datetime.now()}: Dashboard updated successfully')
    else:
        print(f'{datetime.now()}: Update failed - {response.status_code}')


if __name__ == "__main__":
    main()
