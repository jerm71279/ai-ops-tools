#!/usr/bin/env python3
"""
Daily Engineering Summary Generator
Generates and emails daily summary of projects and tickets
Runs at 4 PM Monday-Friday
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv('/home/mavrick/Projects/Secondbrain/.env')

# Configuration
RECIPIENTS = [
    'Security@oberaconnect.com',
    'Devon.harris@oberaconnect.com',
    'philip.durant@oberaconnect.com'
]

SITE_ID = 'oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef'

class EngineeringSummaryGenerator:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.base_url = 'https://graph.microsoft.com/v1.0'
        self.token = self._get_token()
        self.projects_list_id = None
        self.tickets_list_id = None
        self.tasks_list_id = None
        self.projects = []
        self.tickets = []
        self.tasks = []

    def _get_token(self):
        """Get OAuth token"""
        token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        response = requests.post(token_url, data=data)
        return response.json().get('access_token')

    def _get_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def get_list_ids(self):
        """Get SharePoint list IDs"""
        url = f'{self.base_url}/sites/{SITE_ID}/lists'
        response = requests.get(url, headers=self._get_headers())
        lists = response.json().get('value', [])

        for lst in lists:
            if lst['displayName'] == 'Engineering Projects':
                self.projects_list_id = lst['id']
            elif lst['displayName'] == 'Engineering Tickets':
                self.tickets_list_id = lst['id']
            elif lst['displayName'] == 'Engineering Tasks':
                self.tasks_list_id = lst['id']

    def fetch_data(self):
        """Fetch all projects, tickets, and tasks"""
        # Fetch projects
        url = f'{self.base_url}/sites/{SITE_ID}/lists/{self.projects_list_id}/items?expand=fields'
        response = requests.get(url, headers=self._get_headers())
        self.projects = response.json().get('value', [])

        # Fetch tickets
        url = f'{self.base_url}/sites/{SITE_ID}/lists/{self.tickets_list_id}/items?expand=fields'
        response = requests.get(url, headers=self._get_headers())
        self.tickets = response.json().get('value', [])

        # Fetch tasks
        if self.tasks_list_id:
            url = f'{self.base_url}/sites/{SITE_ID}/lists/{self.tasks_list_id}/items?expand=fields'
            response = requests.get(url, headers=self._get_headers())
            self.tasks = response.json().get('value', [])

    def parse_comments(self, comments_json):
        """Parse comments from JSON string stored in SharePoint"""
        import json
        if not comments_json:
            return []
        try:
            return json.loads(comments_json)
        except:
            return []

    def parse_documentation_log(self, log_json):
        """Parse documentation log from JSON string stored in SharePoint"""
        import json
        if not log_json:
            return []
        try:
            return json.loads(log_json)
        except:
            return []

    def get_recent_documentation(self, hours=24):
        """Get documentation entries from the last N hours across all tickets"""
        from datetime import timezone
        recent = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for ticket in self.tickets:
            log_json = ticket['fields'].get('DocumentationLog', '')
            entries = self.parse_documentation_log(log_json)
            ticket_title = ticket['fields'].get('TicketTitle', 'Untitled Ticket')
            project_id = ticket['fields'].get('ProjectID', '')

            # Find parent project name
            project_name = None
            for project in self.projects:
                if project['id'] == project_id:
                    project_name = project['fields'].get('ProjectName', '')
                    break

            for entry in entries:
                try:
                    entry_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                    if entry_time > cutoff:
                        recent.append({
                            'project_name': project_name,
                            'ticket_title': ticket_title,
                            'type': entry.get('type', 'note'),
                            'author': entry.get('author', 'System'),
                            'text': entry.get('text', ''),
                            'timestamp': entry_time
                        })
                except:
                    pass

        # Sort by timestamp descending
        recent.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent

    def get_linked_ticket(self, project_id):
        """Get the linked ticket for a project"""
        for ticket in self.tickets:
            if ticket['fields'].get('ProjectID') == project_id:
                return ticket
        return None

    def get_ticket_tasks(self, ticket_id):
        """Get all tasks for a ticket"""
        return [t for t in self.tasks if t['fields'].get('TicketID') == ticket_id]

    def calculate_project_progress(self, project_id):
        """Calculate project progress from tasks"""
        linked_ticket = self.get_linked_ticket(project_id)
        if not linked_ticket:
            return 0

        tasks = self.get_ticket_tasks(linked_ticket['id'])
        if not tasks:
            return 0

        done_tasks = len([t for t in tasks if t['fields'].get('Status') == 'Done'])
        return round((done_tasks / len(tasks)) * 100)

    def get_recent_comments(self, hours=24):
        """Get comments from the last N hours across all items"""
        from datetime import timezone
        import json
        recent = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for item in self.projects:
            comments_json = item['fields'].get('Comments', '')
            comments = self.parse_comments(comments_json)
            item_name = item['fields'].get('ProjectName', 'Untitled Project')
            for c in comments:
                try:
                    comment_time = datetime.strptime(c.get('time', ''), '%m/%d/%Y, %I:%M:%S %p')
                    comment_time = comment_time.replace(tzinfo=timezone.utc)
                    if comment_time > cutoff:
                        recent.append({
                            'item_type': 'Project',
                            'item_name': item_name,
                            'author': c.get('author', 'Unknown'),
                            'text': c.get('text', ''),
                            'time': c.get('time', '')
                        })
                except:
                    # If time parsing fails, include if text exists
                    if c.get('text'):
                        recent.append({
                            'item_type': 'Project',
                            'item_name': item_name,
                            'author': c.get('author', 'Unknown'),
                            'text': c.get('text', ''),
                            'time': c.get('time', 'Recently')
                        })

        for item in self.tickets:
            comments_json = item['fields'].get('Comments', '')
            comments = self.parse_comments(comments_json)
            item_name = item['fields'].get('TicketTitle', 'Untitled Ticket')
            for c in comments:
                try:
                    comment_time = datetime.strptime(c.get('time', ''), '%m/%d/%Y, %I:%M:%S %p')
                    comment_time = comment_time.replace(tzinfo=timezone.utc)
                    if comment_time > cutoff:
                        recent.append({
                            'item_type': 'Ticket',
                            'item_name': item_name,
                            'author': c.get('author', 'Unknown'),
                            'text': c.get('text', ''),
                            'time': c.get('time', '')
                        })
                except:
                    if c.get('text'):
                        recent.append({
                            'item_type': 'Ticket',
                            'item_name': item_name,
                            'author': c.get('author', 'Unknown'),
                            'text': c.get('text', ''),
                            'time': c.get('time', 'Recently')
                        })

        return recent

    def calculate_stats(self):
        """Calculate summary statistics"""
        stats = {}

        # Project stats
        stats['total_projects'] = len(self.projects)
        stats['in_progress_projects'] = len([p for p in self.projects if p['fields'].get('Status') == 'In Progress'])
        stats['not_started_projects'] = len([p for p in self.projects if p['fields'].get('Status') == 'Not Started'])
        stats['completed_projects'] = len([p for p in self.projects if p['fields'].get('Status') == 'Completed'])
        stats['high_priority_projects'] = len([p for p in self.projects if p['fields'].get('Priority') == 'High'])

        # Ticket stats (note: tickets are now linked to projects)
        stats['total_tickets'] = len(self.tickets)
        stats['open_tickets'] = len([t for t in self.tickets if t['fields'].get('Status') == 'Open'])
        stats['in_progress_tickets'] = len([t for t in self.tickets if t['fields'].get('Status') == 'In Progress'])
        stats['pending_tickets'] = len([t for t in self.tickets if t['fields'].get('Status') == 'Pending'])
        stats['resolved_tickets'] = len([t for t in self.tickets if t['fields'].get('Status') in ['Resolved', 'Closed']])
        stats['high_priority_tickets'] = len([t for t in self.tickets if t['fields'].get('Priority') == 'High'])

        # Task stats
        stats['total_tasks'] = len(self.tasks)
        stats['todo_tasks'] = len([t for t in self.tasks if t['fields'].get('Status') == 'To Do'])
        stats['in_progress_tasks'] = len([t for t in self.tasks if t['fields'].get('Status') == 'In Progress'])
        stats['done_tasks'] = len([t for t in self.tasks if t['fields'].get('Status') == 'Done'])

        # Combined stats
        stats['total_high_priority'] = stats['high_priority_projects'] + stats['high_priority_tickets']

        # Recently completed (last 24 hours)
        from datetime import timezone
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        stats['completed_today'] = 0
        stats['tasks_completed_today'] = 0
        for item in self.projects + self.tickets:
            try:
                modified = datetime.fromisoformat(item['fields'].get('Modified', '').replace('Z', '+00:00'))
                status = item['fields'].get('Status', '')
                if modified > yesterday and status in ['Completed', 'Resolved', 'Closed']:
                    stats['completed_today'] += 1
            except:
                pass  # Skip items with invalid dates

        for task in self.tasks:
            try:
                modified = datetime.fromisoformat(task['fields'].get('Modified', '').replace('Z', '+00:00'))
                if modified > yesterday and task['fields'].get('Status') == 'Done':
                    stats['tasks_completed_today'] += 1
            except:
                pass

        # Get recent documentation entries count
        recent_docs = self.get_recent_documentation(24)
        stats['recent_documentation'] = len(recent_docs)

        # Get recent comments count (legacy)
        recent_comments = self.get_recent_comments(24)
        stats['recent_comments'] = len(recent_comments)

        return stats

    def generate_html_report(self, stats):
        """Generate HTML email report"""
        date_str = datetime.now().strftime('%B %d, %Y')

        # Sort projects and tickets by priority (High > Medium > Low) and status
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        sorted_projects = sorted(self.projects, key=lambda x: (
            priority_order.get(x['fields'].get('Priority', 'Low'), 2),
            x['fields'].get('Status', '')
        ))
        sorted_tickets = sorted(self.tickets, key=lambda x: (
            priority_order.get(x['fields'].get('Priority', 'Low'), 2),
            x['fields'].get('Status', '')
        ))

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 30px;
            border-bottom: 4px solid #f59e0b;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .logo-connect {{
            color: #f59e0b;
        }}
        .header h1 {{
            margin: 10px 0 0 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .date {{
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #1e3a8a;
        }}
        .stat-card.warning {{
            border-left-color: #f59e0b;
        }}
        .stat-card.danger {{
            border-left-color: #ef4444;
        }}
        .stat-card.success {{
            border-left-color: #10b981;
        }}
        .stat-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
            margin-top: 5px;
        }}
        .stat-subtitle {{
            font-size: 12px;
            color: #9ca3af;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .item {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 3px solid #ef4444;
        }}
        .item-title {{
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 5px;
        }}
        .item-meta {{
            font-size: 13px;
            color: #6b7280;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 5px;
        }}
        .badge-high {{
            background: #fee2e2;
            color: #dc2626;
        }}
        .badge-status {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .footer {{
            background: #f9fafb;
            padding: 20px 30px;
            text-align: center;
            color: #6b7280;
            font-size: 13px;
            border-top: 1px solid #e5e7eb;
        }}
        .button {{
            display: inline-block;
            background: #1e3a8a;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <span>Obera</span><span class="logo-connect">Connect</span>
            </div>
            <h1>Engineering Daily Summary</h1>
        </div>

        <div class="content">
            <div class="date">{date_str}</div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Projects</div>
                    <div class="stat-value">{stats['total_projects']}</div>
                    <div class="stat-subtitle">{stats['in_progress_projects']} in progress</div>
                </div>

                <div class="stat-card warning">
                    <div class="stat-label">Active Tasks</div>
                    <div class="stat-value">{stats['total_tasks']}</div>
                    <div class="stat-subtitle">{stats['in_progress_tasks']} in progress, {stats['todo_tasks']} to do</div>
                </div>

                <div class="stat-card danger">
                    <div class="stat-label">High Priority</div>
                    <div class="stat-value">{stats['total_high_priority']}</div>
                    <div class="stat-subtitle">Requires attention</div>
                </div>

                <div class="stat-card success">
                    <div class="stat-label">Tasks Done Today</div>
                    <div class="stat-value">{stats['tasks_completed_today']}</div>
                    <div class="stat-subtitle">Last 24 hours</div>
                </div>

                <div class="stat-card" style="border-left-color: #8b5cf6;">
                    <div class="stat-label">Documentation Updates</div>
                    <div class="stat-value">{stats['recent_documentation']}</div>
                    <div class="stat-subtitle">Last 24 hours</div>
                </div>
            </div>
'''

        # Add Recent Documentation section if any exist
        recent_docs = self.get_recent_documentation(24)
        if recent_docs:
            html += '''
            <div class="section">
                <div class="section-title">📝 Recent Documentation</div>
                <ul style="list-style: none; padding: 0;">
'''
            for doc in recent_docs[:10]:  # Limit to 10 most recent
                type_icons = {
                    'created': '🆕',
                    'task_created': '✅',
                    'task_updated': '🔄',
                    'note': '📝',
                    'status_change': '📊'
                }
                icon = type_icons.get(doc['type'], '📝')
                project_info = f" ({doc['project_name']})" if doc['project_name'] else ""
                time_str = doc['timestamp'].strftime('%I:%M %p')
                html += f'''
                    <li style="padding: 12px; margin-bottom: 8px; background: #f9fafb; border-left: 3px solid #8b5cf6; border-radius: 4px;">
                        <strong>{icon} {doc['ticket_title']}{project_info}</strong><br>
                        <span style="font-size: 13px; color: #1f2937; margin: 8px 0; display: block;">
                            {doc['text']}
                        </span>
                        <span style="font-size: 12px; color: #6b7280;">
                            — {doc['author']} • {time_str}
                        </span>
                    </li>
'''
            html += '''
                </ul>
            </div>
'''

        # Add ALL Projects List with Progress and Tasks
        html += '''
            <div class="section">
                <div class="section-title">📋 Active Projects</div>
                <ul style="list-style: none; padding: 0;">
'''
        # Only show active (non-completed) projects
        active_projects = [p for p in sorted_projects if p['fields'].get('Status') != 'Completed']
        for project in active_projects:
            fields = project['fields']
            priority_icon = '🔴' if fields.get('Priority') == 'High' else '🟡' if fields.get('Priority') == 'Medium' else '🟢'
            status_icon = '🔄' if fields.get('Status') == 'In Progress' else '⏸️' if fields.get('Status') == 'On Hold' else '📋'

            # Calculate progress from tasks
            progress = self.calculate_project_progress(project['id'])
            linked_ticket = self.get_linked_ticket(project['id'])
            task_count = len(self.get_ticket_tasks(linked_ticket['id'])) if linked_ticket else 0
            done_count = len([t for t in self.get_ticket_tasks(linked_ticket['id']) if t['fields'].get('Status') == 'Done']) if linked_ticket else 0

            progress_bar = f'''<div style="background:#e5e7eb;height:6px;border-radius:3px;width:100%;margin-top:8px;"><div style="background:#10b981;height:6px;border-radius:3px;width:{progress}%;"></div></div>'''
            task_info = f"{done_count}/{task_count} tasks" if task_count > 0 else "No tasks"

            html += f'''
                    <li style="padding: 12px; margin-bottom: 10px; background: #f9fafb; border-left: 3px solid {'#ef4444' if fields.get('Priority') == 'High' else '#f59e0b' if fields.get('Priority') == 'Medium' else '#10b981'}; border-radius: 4px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <strong>{priority_icon} {fields.get('ProjectName', 'Untitled')}</strong>
                            <span style="font-size:12px;background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:10px;">{progress}%</span>
                        </div>
                        <span style="font-size: 13px; color: #6b7280; display:block; margin-top:4px;">
                            {status_icon} {fields.get('Status', 'N/A')} •
                            Assigned: {fields.get('AssignedTo', 'Unassigned')} •
                            {task_info}
                        </span>
                        {progress_bar}
                    </li>
'''
        html += '''
                </ul>
            </div>
'''

        # Add Active Tasks section
        active_tasks = [t for t in self.tasks if t['fields'].get('Status') != 'Done']
        if active_tasks:
            html += '''
            <div class="section">
                <div class="section-title">✅ Active Tasks</div>
                <ul style="list-style: none; padding: 0;">
'''
            # Sort by priority then status
            priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
            active_tasks_sorted = sorted(active_tasks, key=lambda x: (
                priority_order.get(x['fields'].get('Priority', 'Low'), 3),
                0 if x['fields'].get('Status') == 'In Progress' else 1
            ))
            for task in active_tasks_sorted[:15]:  # Limit to 15 tasks
                fields = task['fields']
                priority_icon = '🔴' if fields.get('Priority') in ['High', 'Critical'] else '🟡' if fields.get('Priority') == 'Medium' else '🟢'
                status_icon = '🔄' if fields.get('Status') == 'In Progress' else '📋'
                html += f'''
                    <li style="padding: 10px 12px; margin-bottom: 6px; background: #f9fafb; border-left: 3px solid {'#ef4444' if fields.get('Priority') in ['High', 'Critical'] else '#f59e0b' if fields.get('Priority') == 'Medium' else '#10b981'}; border-radius: 4px;">
                        <strong>{priority_icon} {fields.get('TaskTitle', 'Untitled')}</strong>
                        <span style="font-size: 12px; color: #6b7280; display:block; margin-top:2px;">
                            {status_icon} {fields.get('Status', 'To Do')} •
                            {fields.get('AssignedTo', 'Unassigned')}
                            {' • ' + fields.get('Phase', '') if fields.get('Phase') else ''}
                        </span>
                    </li>
'''
            html += '''
                </ul>
            </div>
'''

        html += '''
        </div>

        <div class="footer">
            <p>This is an automated daily summary generated at 4:00 PM</p>
            <p>OberaConnect Engineering Team | ''' + str(datetime.now().year) + '''</p>
        </div>
    </div>
</body>
</html>
'''
        return html

    def send_email(self, html_content):
        """Send email via Microsoft Graph API"""
        url = f'{self.base_url}/users/Security@oberaconnect.com/sendMail'

        email_data = {
            'message': {
                'subject': f'Engineering Daily Summary - {datetime.now().strftime("%B %d, %Y")}',
                'body': {
                    'contentType': 'HTML',
                    'content': html_content
                },
                'toRecipients': [
                    {'emailAddress': {'address': email}} for email in RECIPIENTS
                ]
            },
            'saveToSentItems': 'true'
        }

        response = requests.post(url, headers=self._get_headers(), json=email_data)

        if response.status_code == 202:
            print(f'✅ Email sent successfully to {len(RECIPIENTS)} recipients')
            return True
        else:
            print(f'❌ Email failed: {response.status_code}')
            print(f'   Error: {response.text}')
            return False

    def save_report_to_sharepoint(self, html_content):
        """Save daily report to SharePoint Reports folder"""
        # Get Documents drive
        url = f'{self.base_url}/sites/{SITE_ID}/drives'
        response = requests.get(url, headers={'Authorization': f'Bearer {self.token}'})
        drives = response.json().get('value', [])

        drive_id = None
        for drive in drives:
            if drive['name'] == 'Documents':
                drive_id = drive['id']
                break

        if not drive_id:
            print('❌ Documents drive not found')
            return False

        # Create filename with date
        filename = f"Daily_Summary_{datetime.now().strftime('%Y-%m-%d')}.html"

        # Save to both locations: archive and Engineering channel Files tab
        folder_paths = [
            "Reports/Daily Summaries",           # Archive location
            "Engineering/Daily Reports"          # Teams Engineering channel Files tab
        ]

        upload_headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/octet-stream'
        }

        for folder_path in folder_paths:
            upload_url = f'{self.base_url}/sites/{SITE_ID}/drives/{drive_id}/root:/{folder_path}/{filename}:/content'
            response = requests.put(upload_url, headers=upload_headers, data=html_content.encode('utf-8'))

            if response.status_code in [200, 201]:
                print(f'✅ Report saved to: {folder_path}/{filename}')
            else:
                print(f'⚠️  Failed to save to {folder_path}: {response.status_code}')

        return True

    def generate_and_send(self):
        """Main method to generate and send daily summary"""
        print(f'Starting daily summary generation at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        try:
            # Get list IDs
            self.get_list_ids()

            # Fetch data
            print('Fetching data from SharePoint...')
            self.fetch_data()

            # Calculate stats
            print('Calculating statistics...')
            stats = self.calculate_stats()

            # Generate HTML report
            print('Generating HTML report...')
            html_content = self.generate_html_report(stats)

            # Send email
            print('Sending email...')
            email_sent = self.send_email(html_content)

            # Save to SharePoint
            print('Saving report to SharePoint...')
            report_saved = self.save_report_to_sharepoint(html_content)

            print(f'✅ Daily summary complete!')
            print(f'   Projects: {stats["total_projects"]} ({stats["in_progress_projects"]} in progress)')
            print(f'   Tickets: {stats["total_tickets"]} ({stats["open_tickets"] + stats["in_progress_tickets"]} open)')
            print(f'   High Priority: {stats["total_high_priority"]}')

            return True

        except Exception as e:
            print(f'❌ Error generating summary: {e}')
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    generator = EngineeringSummaryGenerator()
    generator.generate_and_send()
