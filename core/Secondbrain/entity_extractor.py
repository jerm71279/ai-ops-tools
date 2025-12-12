#!/usr/bin/env python3
"""
Entity Extractor - Import structured data from SharePoint CSV exports into SQLite
Extracts Projects, Tickets, and other entities from SharePoint List exports
"""
import csv
import glob
from pathlib import Path
from datetime import datetime
from structured_store import StructuredStore
from config import INPUT_DOCUMENTS_DIR, CHROMA_DB_DIR


class EntityExtractor:
    """Extract structured entities from SharePoint CSV exports"""

    def __init__(self, store: StructuredStore):
        self.store = store

    def extract_all(self, sharepoint_dir: Path):
        """Extract all entities from SharePoint directory"""
        print("=" * 60)
        print("Entity Extraction")
        print("=" * 60)

        # Find all CSV files
        csv_files = list(sharepoint_dir.rglob("*.csv"))
        print(f"Found {len(csv_files)} CSV files")

        projects_imported = 0
        tickets_imported = 0

        for csv_path in csv_files:
            filename = csv_path.name.lower()

            # Project CSVs
            if filename.startswith('project'):
                count = self.extract_projects(csv_path)
                projects_imported += count

            # Ticket CSVs
            elif filename.startswith('ticket'):
                count = self.extract_tickets(csv_path)
                tickets_imported += count

        print(f"\nProjects imported: {projects_imported}")
        print(f"Tickets imported: {tickets_imported}")

        return projects_imported, tickets_imported

    def extract_projects(self, csv_path: Path) -> int:
        """Extract projects from a SharePoint Project List CSV"""
        count = 0
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip empty rows
                    if not row.get('Title') and not row.get('ProjectName'):
                        continue

                    project_data = {
                        'id': row.get('UniqueId') or row.get('GUID') or f"proj_{row.get('ID', '')}",
                        'title': row.get('ProjectName') or row.get('Title') or 'Untitled Project',
                        'customer': row.get('Customer', ''),
                        'status': row.get('Status', 'Unknown'),
                        'priority': row.get('Priority', 'Medium'),
                        'assigned_to': row.get('AssignedTo', ''),
                        'start_date': self._parse_date(row.get('StartDate')),
                        'due_date': self._parse_date(row.get('DueDate')),
                        'budget_hours': self._parse_float(row.get('BudgetHours') or row.get('Budget')),
                        'hours_spent': self._parse_float(row.get('HoursSpent')),
                        'percent_complete': self._parse_int(row.get('PercentComplete')),
                        'description': row.get('Description', ''),
                        'source_url': row.get('EncodedAbsUrl', ''),
                    }

                    if self.store.add_project(project_data):
                        count += 1

        except Exception as e:
            print(f"  Error reading {csv_path.name}: {e}")

        return count

    def extract_tickets(self, csv_path: Path) -> int:
        """Extract tickets from a SharePoint Ticket List CSV"""
        count = 0
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip empty rows
                    if not row.get('Title') and not row.get('TicketTitle'):
                        continue

                    ticket_id = row.get('UniqueId') or row.get('GUID') or row.get('TicketNumber') or f"tkt_{row.get('ID', '')}"

                    self.store.execute("""
                        INSERT INTO tickets (id, title, customer, status, priority, assigned_to, due_date, description, source, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            title = excluded.title,
                            status = excluded.status,
                            updated_at = excluded.updated_at
                    """, (
                        ticket_id,
                        row.get('TicketTitle') or row.get('Title') or 'Untitled Ticket',
                        row.get('Customer', ''),
                        row.get('Status', 'Open'),
                        row.get('Priority', 'Medium'),
                        row.get('AssignedTo', ''),
                        self._parse_date(row.get('DueDate')),
                        row.get('Description', ''),
                        row.get('Source', 'SharePoint'),
                        datetime.now().isoformat()
                    ))
                    count += 1

        except Exception as e:
            print(f"  Error reading {csv_path.name}: {e}")

        return count

    def extract_employees_from_assignments(self):
        """Extract unique employees from project/ticket assignments"""
        # Get unique assignees from projects
        project_assignees = self.store.query(
            "SELECT DISTINCT assigned_to FROM projects WHERE assigned_to IS NOT NULL AND assigned_to != ''"
        )

        # Get unique assignees from tickets
        ticket_assignees = self.store.query(
            "SELECT DISTINCT assigned_to FROM tickets WHERE assigned_to IS NOT NULL AND assigned_to != ''"
        )

        employees = set()
        for row in project_assignees + ticket_assignees:
            name = row['assigned_to'].strip()
            if name and len(name) > 2:
                employees.add(name)

        # Add employees to store
        for name in employees:
            self.store.execute("""
                INSERT INTO employees (name, source) VALUES (?, 'assignment')
                ON CONFLICT(name) DO NOTHING
            """, (name,))

        return len(employees)

    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats"""
        if not date_str:
            return None
        try:
            # Try common formats
            for fmt in ['%m/%d/%Y %I:%M:%S %p', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).isoformat()
                except ValueError:
                    continue
            return date_str
        except:
            return None

    def _parse_float(self, value: str) -> float:
        """Parse float value"""
        if not value:
            return None
        try:
            return float(value)
        except:
            return None

    def _parse_int(self, value: str) -> int:
        """Parse int value"""
        if not value:
            return None
        try:
            return int(float(value))
        except:
            return None


def main():
    """Run entity extraction"""
    db_path = CHROMA_DB_DIR.parent / "structured.db"
    store = StructuredStore(db_path)
    extractor = EntityExtractor(store)

    # Extract from SharePoint exports
    sharepoint_dir = INPUT_DOCUMENTS_DIR / "sharepoint_all"
    if sharepoint_dir.exists():
        projects, tickets = extractor.extract_all(sharepoint_dir)
    else:
        print(f"SharePoint directory not found: {sharepoint_dir}")

    # Extract employees from assignments
    print("\nExtracting employees from assignments...")
    emp_count = extractor.extract_employees_from_assignments()
    print(f"  Found {emp_count} unique employees")

    # Show summary
    print("\n" + "=" * 60)
    print("Final Statistics")
    print("=" * 60)
    stats = store.get_summary_stats()
    for key, value in stats.items():
        print(f"  {key.capitalize()}: {value}")


if __name__ == "__main__":
    main()
