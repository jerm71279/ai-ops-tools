import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
ECS Dashboard Data Generator
Exports Engineering Projects and Tasks data for Power BI or local visualization.
Also provides a terminal-based dashboard view.

Run: python ecs_dashboard.py [--export] [--terminal]
"""
import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class ECSDashboard:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = None

        # Site and list IDs
        self.site_id = None
        self.projects_list_id = 'a310c2d1-634f-44d0-862b-6750bf8788ce'
        self.tasks_list_id = '92c85920-31bd-49ae-a4ae-8cee71ee5f39'

        self.output_dir = Path(__file__).parent / "output" / "dashboard"
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        if response.status_code != 200:
            raise Exception(f"Failed to get token: {response.text}")

        self.token = response.json().get('access_token')
        return self.token

    def get_headers(self):
        """Get auth headers"""
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/json'
        }

    def find_site(self):
        """Find SOC TEAM site"""
        resp = requests.get(
            f"{self.base_url}/sites?search=SOCTEAM",
            headers=self.get_headers()
        )
        for site in resp.json().get('value', []):
            if 'SOCTEAM' in site.get('webUrl', ''):
                self.site_id = site['id']
                return True
        return False

    def get_projects(self):
        """Get all projects"""
        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/lists/{self.projects_list_id}/items?expand=fields",
            headers=self.get_headers()
        )
        projects = []
        for item in resp.json().get('value', []):
            fields = item.get('fields', {})
            projects.append({
                'id': item['id'],
                'name': fields.get('ProjectName', fields.get('Title', '')),
                'customer': fields.get('Customer', ''),
                'status': fields.get('Status', 'Not Started'),
                'priority': fields.get('Priority', 'Medium'),
                'assigned_to': fields.get('AssignedTo', ''),
                'team': fields.get('Team', ''),
                'phase': fields.get('ProjectPhase', ''),
                'start_date': fields.get('StartDate', ''),
                'due_date': fields.get('DueDate', ''),
                'percent_complete': fields.get('PercentComplete', 0),
                'budget_hours': fields.get('BudgetHours', 0),
                'hours_spent': fields.get('HoursSpent', 0),
                'created': fields.get('Created', ''),
                'modified': fields.get('Modified', '')
            })
        return projects

    def get_tasks(self):
        """Get all tasks"""
        resp = requests.get(
            f"{self.base_url}/sites/{self.site_id}/lists/{self.tasks_list_id}/items?expand=fields",
            headers=self.get_headers()
        )
        tasks = []
        for item in resp.json().get('value', []):
            fields = item.get('fields', {})
            tasks.append({
                'id': item['id'],
                'title': fields.get('TaskTitle', fields.get('Title', '')),
                'description': fields.get('TaskDescription', ''),
                'project_id': fields.get('ProjectID', ''),
                'ticket_id': fields.get('TicketID', ''),
                'status': fields.get('Status', 'Not Started'),
                'priority': fields.get('Priority', 'Medium'),
                'assigned_to': fields.get('AssignedTo', ''),
                'phase': fields.get('Phase', ''),
                'estimated_hours': fields.get('EstimatedHours', 0),
                'actual_hours': fields.get('ActualHours', 0),
                'start_date': fields.get('StartDate', ''),
                'due_date': fields.get('DueDate', ''),
                'created': fields.get('Created', ''),
                'modified': fields.get('Modified', '')
            })
        return tasks

    def export_to_json(self, projects, tasks):
        """Export data to JSON for Power BI"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'projects': projects,
            'tasks': tasks,
            'summary': self.calculate_summary(projects, tasks)
        }

        output_file = self.output_dir / f"ecs_data_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Exported to: {output_file}")
        return output_file

    def export_to_csv(self, projects, tasks):
        """Export data to CSV for Power BI"""
        import csv

        # Export projects
        projects_file = self.output_dir / f"projects_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(projects_file, 'w', newline='') as f:
            if projects:
                writer = csv.DictWriter(f, fieldnames=projects[0].keys())
                writer.writeheader()
                writer.writerows(projects)

        # Export tasks
        tasks_file = self.output_dir / f"tasks_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(tasks_file, 'w', newline='') as f:
            if tasks:
                writer = csv.DictWriter(f, fieldnames=tasks[0].keys())
                writer.writeheader()
                writer.writerows(tasks)

        print(f"Exported to: {projects_file}")
        print(f"Exported to: {tasks_file}")
        return projects_file, tasks_file

    def calculate_summary(self, projects, tasks):
        """Calculate dashboard summary metrics"""
        # Project metrics
        project_statuses = {}
        for p in projects:
            status = p['status']
            project_statuses[status] = project_statuses.get(status, 0) + 1

        # Task metrics
        task_statuses = {}
        tasks_by_assignee = {}
        tasks_due_soon = 0
        overdue_tasks = 0
        today = datetime.now().date()

        for t in tasks:
            # Status counts
            status = t['status']
            task_statuses[status] = task_statuses.get(status, 0) + 1

            # Assignee counts
            assignee = t['assigned_to'] or 'Unassigned'
            if assignee not in tasks_by_assignee:
                tasks_by_assignee[assignee] = {'total': 0, 'complete': 0, 'in_progress': 0}
            tasks_by_assignee[assignee]['total'] += 1
            if status == 'Complete':
                tasks_by_assignee[assignee]['complete'] += 1
            elif status == 'In Progress':
                tasks_by_assignee[assignee]['in_progress'] += 1

            # Due date analysis
            if t['due_date']:
                try:
                    due = datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')).date()
                    if due < today and status != 'Complete':
                        overdue_tasks += 1
                    elif due <= today + timedelta(days=7) and status != 'Complete':
                        tasks_due_soon += 1
                except:
                    pass

        return {
            'total_projects': len(projects),
            'total_tasks': len(tasks),
            'project_statuses': project_statuses,
            'task_statuses': task_statuses,
            'tasks_by_assignee': tasks_by_assignee,
            'tasks_due_this_week': tasks_due_soon,
            'overdue_tasks': overdue_tasks
        }

    def print_terminal_dashboard(self, projects, tasks):
        """Print a terminal-based dashboard"""
        summary = self.calculate_summary(projects, tasks)

        print()
        print("=" * 70)
        print("  ENGINEERING COMMAND SYSTEM - DASHBOARD")
        print("=" * 70)
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()

        # Summary Cards
        print("  SUMMARY")
        print("  " + "-" * 66)
        print(f"  | Active Projects: {summary['total_projects']:3} | Total Tasks: {summary['total_tasks']:3} | Due This Week: {summary['tasks_due_this_week']:3} | Overdue: {summary['overdue_tasks']:3} |")
        print("  " + "-" * 66)
        print()

        # Project Status
        print("  PROJECTS BY STATUS")
        print("  " + "-" * 40)
        for status, count in summary['project_statuses'].items():
            bar = "█" * count + "░" * (10 - min(count, 10))
            print(f"  {status:15} [{bar}] {count}")
        print()

        # Task Status (Kanban Overview)
        print("  TASKS BY STATUS (Kanban)")
        print("  " + "-" * 40)
        status_order = ['Not Started', 'Scheduled', 'In Progress', 'Need to Reschedule', 'Complete']
        for status in status_order:
            count = summary['task_statuses'].get(status, 0)
            bar = "█" * count + "░" * (10 - min(count, 10))
            print(f"  {status:20} [{bar}] {count}")
        print()

        # Workload by Assignee
        print("  WORKLOAD BY TEAM MEMBER")
        print("  " + "-" * 50)
        print(f"  {'Assignee':20} {'Total':>6} {'Active':>8} {'Done':>6}")
        print("  " + "-" * 50)
        for assignee, counts in summary['tasks_by_assignee'].items():
            active = counts['in_progress'] + (counts['total'] - counts['complete'] - counts['in_progress'])
            print(f"  {assignee:20} {counts['total']:>6} {active:>8} {counts['complete']:>6}")
        print()

        # Upcoming Tasks
        print("  UPCOMING TASKS (Next 7 Days)")
        print("  " + "-" * 66)
        today = datetime.now().date()
        upcoming = []
        for t in tasks:
            if t['due_date'] and t['status'] != 'Complete':
                try:
                    due = datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')).date()
                    if due <= today + timedelta(days=7):
                        upcoming.append((due, t))
                except:
                    pass

        upcoming.sort(key=lambda x: x[0])
        for due, t in upcoming[:5]:
            status_icon = "🔴" if due < today else "🟡" if due == today else "🟢"
            print(f"  {status_icon} {due.strftime('%m/%d')} | {t['title'][:35]:35} | {t['assigned_to']:15}")

        if not upcoming:
            print("  No tasks due in the next 7 days")
        print()

        # Projects List
        print("  ACTIVE PROJECTS")
        print("  " + "-" * 66)
        active_projects = [p for p in projects if p['status'] not in ['Complete', 'Archived']]
        for p in active_projects[:5]:
            pct = int(p['percent_complete'] or 0)
            pct_bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"  {p['name'][:30]:30} [{pct_bar}] {pct:>3}% | {p['status']}")
        print()

        print("=" * 70)
        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='ECS Dashboard - View and export project/task data')
    parser.add_argument('--export', action='store_true', help='Export data to JSON and CSV')
    parser.add_argument('--terminal', action='store_true', help='Show terminal dashboard')
    parser.add_argument('--json', action='store_true', help='Output summary as JSON')
    args = parser.parse_args()

    # Default to terminal view if no args
    if not any([args.export, args.terminal, args.json]):
        args.terminal = True

    dashboard = ECSDashboard()

    if not dashboard.find_site():
        print("ERROR: Could not find SOC TEAM site")
        return

    projects = dashboard.get_projects()
    tasks = dashboard.get_tasks()

    if args.export:
        dashboard.export_to_json(projects, tasks)
        dashboard.export_to_csv(projects, tasks)

    if args.terminal:
        dashboard.print_terminal_dashboard(projects, tasks)

    if args.json:
        summary = dashboard.calculate_summary(projects, tasks)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
