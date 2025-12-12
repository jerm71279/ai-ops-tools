#!/usr/bin/env python3
"""
Structured Store - SQLite database for SharePoint List data
Optimized for aggregation queries (counts, sums, filters)
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re


class StructuredStore:
    """SQLite store for structured SharePoint data - optimized for analytical queries"""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Create tables for structured business data"""
        cursor = self.conn.cursor()

        # Customers table - extracted from folders and documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                folder_path TEXT,
                document_count INTEGER DEFAULT 0,
                project_count INTEGER DEFAULT 0,
                ticket_count INTEGER DEFAULT 0,
                last_activity TEXT,
                tags TEXT,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                title TEXT,
                customer TEXT,
                status TEXT,
                priority TEXT,
                assigned_to TEXT,
                start_date TEXT,
                due_date TEXT,
                budget_hours REAL,
                hours_spent REAL,
                percent_complete INTEGER,
                description TEXT,
                source_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT,
                customer TEXT,
                status TEXT,
                priority TEXT,
                assigned_to TEXT,
                due_date TEXT,
                time_spent REAL,
                description TEXT,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                department TEXT,
                role TEXT,
                project_count INTEGER DEFAULT 0,
                ticket_count INTEGER DEFAULT 0,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Documents metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                file_path TEXT UNIQUE,
                customer TEXT,
                doc_type TEXT,
                tags TEXT,
                entities TEXT,
                indexed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_customer ON projects(customer)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_customer ON documents(customer)")

        self.conn.commit()

    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute SQL query and return results as dicts"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"SQL Error: {e}")
            return []

    def execute(self, sql: str, params: tuple = ()) -> bool:
        """Execute SQL statement (INSERT, UPDATE, DELETE)"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"SQL Error: {e}")
            return False

    # ==================== Customer Methods ====================

    def add_customer(self, name: str, folder_path: str = None, source: str = 'manual') -> bool:
        """Add or update a customer"""
        return self.execute("""
            INSERT INTO customers (name, folder_path, source, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                folder_path = COALESCE(excluded.folder_path, folder_path),
                updated_at = excluded.updated_at
        """, (name, folder_path, source, datetime.now().isoformat()))

    def count_customers(self) -> int:
        """Get total customer count"""
        result = self.query("SELECT COUNT(*) as count FROM customers")
        return result[0]['count'] if result else 0

    def get_customers(self, limit: int = None, status: str = None) -> List[Dict]:
        """Get customer list with optional filters"""
        sql = """
            SELECT name, folder_path, document_count, project_count,
                   ticket_count, last_activity, source
            FROM customers
            ORDER BY name ASC
        """
        if limit:
            sql += f" LIMIT {limit}"
        return self.query(sql)

    def get_customer_details(self, customer_name: str) -> Optional[Dict]:
        """Get detailed info for a specific customer"""
        customers = self.query(
            "SELECT * FROM customers WHERE name = ?",
            (customer_name,)
        )
        if not customers:
            return None

        customer = customers[0]

        # Get related projects
        projects = self.query(
            "SELECT * FROM projects WHERE customer = ?",
            (customer_name,)
        )

        # Get related tickets
        tickets = self.query(
            "SELECT * FROM tickets WHERE customer = ?",
            (customer_name,)
        )

        # Get related documents
        documents = self.query(
            "SELECT * FROM documents WHERE customer = ?",
            (customer_name,)
        )

        return {
            'customer': customer,
            'projects': projects,
            'tickets': tickets,
            'documents': documents
        }

    def update_customer_counts(self, customer_name: str):
        """Update aggregated counts for a customer"""
        project_count = self.query(
            "SELECT COUNT(*) as c FROM projects WHERE customer = ?",
            (customer_name,)
        )[0]['c']

        ticket_count = self.query(
            "SELECT COUNT(*) as c FROM tickets WHERE customer = ?",
            (customer_name,)
        )[0]['c']

        doc_count = self.query(
            "SELECT COUNT(*) as c FROM documents WHERE customer = ?",
            (customer_name,)
        )[0]['c']

        self.execute("""
            UPDATE customers
            SET project_count = ?, ticket_count = ?, document_count = ?,
                updated_at = ?
            WHERE name = ?
        """, (project_count, ticket_count, doc_count, datetime.now().isoformat(), customer_name))

    # ==================== Project Methods ====================

    def add_project(self, project_data: Dict[str, Any]) -> bool:
        """Add or update a project"""
        return self.execute("""
            INSERT INTO projects
            (id, title, customer, status, priority, assigned_to,
             start_date, due_date, budget_hours, hours_spent,
             percent_complete, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                customer = excluded.customer,
                status = excluded.status,
                updated_at = excluded.updated_at
        """, (
            project_data.get('id'),
            project_data.get('title'),
            project_data.get('customer'),
            project_data.get('status'),
            project_data.get('priority'),
            project_data.get('assigned_to'),
            project_data.get('start_date'),
            project_data.get('due_date'),
            project_data.get('budget_hours'),
            project_data.get('hours_spent'),
            project_data.get('percent_complete'),
            project_data.get('description'),
            datetime.now().isoformat()
        ))

    def count_projects(self, status: str = None) -> int:
        """Get project count with optional status filter"""
        if status:
            result = self.query(
                "SELECT COUNT(*) as count FROM projects WHERE status = ?",
                (status,)
            )
        else:
            result = self.query("SELECT COUNT(*) as count FROM projects")
        return result[0]['count'] if result else 0

    def get_project_stats(self) -> Dict[str, Any]:
        """Get project statistics"""
        return {
            'total_projects': self.count_projects(),
            'by_status': self.query("""
                SELECT status, COUNT(*) as count
                FROM projects
                GROUP BY status
                ORDER BY count DESC
            """),
            'by_customer': self.query("""
                SELECT customer, COUNT(*) as count
                FROM projects
                WHERE customer IS NOT NULL
                GROUP BY customer
                ORDER BY count DESC
                LIMIT 10
            """)
        }

    # ==================== Indexing Methods ====================

    def index_customer_folders(self, sharepoint_dir: Path):
        """Extract customers from SharePoint folder structure"""
        # Look for customer folders in various locations
        customer_paths = [
            sharepoint_dir / "oberaconnect_shared_directory" / "Documents" / "Customers",
            sharepoint_dir / "shared" / "documents" / "Customers",
            sharepoint_dir / "Customers",
        ]

        customers_found = 0

        for customers_dir in customer_paths:
            if customers_dir.exists():
                print(f"  Scanning: {customers_dir}")
                for item in customers_dir.iterdir():
                    if item.is_dir():
                        customer_name = item.name
                        # Skip system folders
                        if customer_name.startswith('.') or customer_name in ['Templates', 'Archive']:
                            continue

                        self.add_customer(customer_name, str(item), 'folder')
                        customers_found += 1

        return customers_found

    def index_customers_from_documents(self, notes_dir: Path):
        """Extract customer names from document metadata/content"""
        customer_patterns = [
            r'customer[:\s]+([A-Z][A-Za-z0-9\s&\-\.]+)',
            r'client[:\s]+([A-Z][A-Za-z0-9\s&\-\.]+)',
            r'# ([A-Z][A-Za-z0-9\s&\-\.]+)\s*\n',  # Markdown headers as potential customer names
        ]

        customers_found = set()

        for note_path in notes_dir.rglob("*.md"):
            try:
                content = note_path.read_text(encoding='utf-8', errors='ignore')[:2000]

                # Check for customer folder indicators in path
                path_parts = note_path.parts
                for i, part in enumerate(path_parts):
                    if part.lower() in ['customers', 'clients'] and i + 1 < len(path_parts):
                        customer_name = path_parts[i + 1]
                        if customer_name and not customer_name.endswith('.md'):
                            customers_found.add(customer_name)

                # Extract from content patterns
                for pattern in customer_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        name = match.strip()
                        if len(name) > 3 and len(name) < 100:
                            customers_found.add(name)

            except Exception as e:
                continue

        # Add found customers
        for name in customers_found:
            self.add_customer(name, source='document')

        return len(customers_found)

    def add_document(self, title: str, file_path: str, customer: str = None,
                     doc_type: str = None, tags: List[str] = None, entities: Dict = None):
        """Add document metadata"""
        return self.execute("""
            INSERT INTO documents (title, file_path, customer, doc_type, tags, entities, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                title = excluded.title,
                customer = excluded.customer,
                tags = excluded.tags,
                entities = excluded.entities,
                indexed_at = excluded.indexed_at
        """, (
            title,
            file_path,
            customer,
            doc_type,
            json.dumps(tags) if tags else None,
            json.dumps(entities) if entities else None,
            datetime.now().isoformat()
        ))

    # ==================== Analytics Methods ====================

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics"""
        return {
            'customers': self.count_customers(),
            'projects': self.count_projects(),
            'tickets': self.query("SELECT COUNT(*) as count FROM tickets")[0]['count'],
            'documents': self.query("SELECT COUNT(*) as count FROM documents")[0]['count'],
            'employees': self.query("SELECT COUNT(*) as count FROM employees")[0]['count'],
        }

    def search_customers(self, search_term: str) -> List[Dict]:
        """Search customers by name"""
        return self.query(
            "SELECT * FROM customers WHERE name LIKE ? ORDER BY name",
            (f"%{search_term}%",)
        )

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recently updated records across all tables"""
        # Combine recent updates from all tables
        results = []

        recent_customers = self.query(
            "SELECT 'customer' as type, name as title, updated_at FROM customers ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        )
        results.extend(recent_customers)

        recent_projects = self.query(
            "SELECT 'project' as type, title, updated_at FROM projects ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        )
        results.extend(recent_projects)

        # Sort by date and return top N
        results.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return results[:limit]


def main():
    """Test the structured store"""
    from config import CHROMA_DB_DIR, INPUT_DOCUMENTS_DIR, OBSIDIAN_VAULT_PATH

    print("=" * 60)
    print("Structured Store - Initialization")
    print("=" * 60)

    db_path = CHROMA_DB_DIR.parent / "structured.db"
    store = StructuredStore(db_path)

    print(f"\nDatabase: {db_path}")

    # Index customers from folders
    print("\nIndexing customers from SharePoint folders...")
    sharepoint_dir = INPUT_DOCUMENTS_DIR / "sharepoint_all"
    if sharepoint_dir.exists():
        count = store.index_customer_folders(sharepoint_dir)
        print(f"  Found {count} customers from folders")

    # Index customers from vault
    print("\nIndexing customers from vault documents...")
    vault_notes = OBSIDIAN_VAULT_PATH / "notes"
    if vault_notes.exists():
        count = store.index_customers_from_documents(vault_notes)
        print(f"  Found {count} customers from documents")

    # Show summary
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    stats = store.get_summary_stats()
    for key, value in stats.items():
        print(f"  {key.capitalize()}: {value}")

    # List customers
    print("\nCustomers:")
    customers = store.get_customers(limit=15)
    for c in customers:
        print(f"  - {c['name']}")

    if len(customers) >= 15:
        total = store.count_customers()
        print(f"  ... and {total - 15} more")


if __name__ == "__main__":
    main()
