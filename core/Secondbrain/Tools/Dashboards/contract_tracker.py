import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Contract Tracker - OberaConnect
Tracks customer contracts, renewal dates, and service terms

Based on 20+ contracts found in SharePoint
Provides alerts for upcoming renewals
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json
import csv


class ContractTracker:
    """Track OberaConnect customer contracts and renewal dates"""

    def __init__(self, data_file: str = "contracts_data.json"):
        self.data_dir = Path("contracts_tracking")
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / data_file
        self.contracts = self._load_contracts()
        print(f"✓ Contract Tracker initialized")
        print(f"  Data file: {self.data_file}")
        print(f"  Contracts loaded: {len(self.contracts)}")

    def _load_contracts(self) -> List[Dict[str, Any]]:
        """Load contracts from data file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []

    def _save_contracts(self):
        """Save contracts to data file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.contracts, f, indent=2, default=str)

    def add_contract(self, contract_data: Dict[str, Any]) -> str:
        """
        Add a new contract to tracking

        Required fields:
        - customer_name
        - contract_type (Managed Services/Voice/Network/Internet/etc)
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)

        Optional fields:
        - services (list)
        - monthly_value
        - renewal_terms (auto-renew, annual, month-to-month)
        - key_contacts
        - notes
        - source_document
        """

        # Generate unique ID
        contract_id = f"{contract_data.get('customer_name', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        contract_id = contract_id.replace(' ', '_').lower()

        # Build contract record
        contract = {
            "id": contract_id,
            "customer_name": contract_data.get("customer_name", "Unknown"),
            "contract_type": contract_data.get("contract_type", "General"),
            "start_date": contract_data.get("start_date", ""),
            "end_date": contract_data.get("end_date", ""),
            "services": contract_data.get("services", []),
            "monthly_value": contract_data.get("monthly_value", ""),
            "renewal_terms": contract_data.get("renewal_terms", "annual"),
            "key_contacts": contract_data.get("key_contacts", []),
            "notes": contract_data.get("notes", ""),
            "source_document": contract_data.get("source_document", ""),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        self.contracts.append(contract)
        self._save_contracts()

        print(f"✓ Contract added: {contract['customer_name']} - {contract['contract_type']}")
        return contract_id

    def update_contract(self, contract_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing contract"""
        for contract in self.contracts:
            if contract["id"] == contract_id:
                contract.update(updates)
                contract["updated_at"] = datetime.now().isoformat()
                self._save_contracts()
                print(f"✓ Contract updated: {contract_id}")
                return True
        print(f"⚠ Contract not found: {contract_id}")
        return False

    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific contract by ID"""
        for contract in self.contracts:
            if contract["id"] == contract_id:
                return contract
        return None

    def get_contracts_by_customer(self, customer_name: str) -> List[Dict[str, Any]]:
        """Get all contracts for a customer"""
        return [c for c in self.contracts
                if customer_name.lower() in c["customer_name"].lower()]

    def get_expiring_contracts(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get contracts expiring within specified days

        Args:
            days: Number of days to look ahead (default 90)

        Returns:
            List of contracts expiring soon, sorted by end_date
        """
        today = datetime.now().date()
        threshold = today + timedelta(days=days)

        expiring = []
        for contract in self.contracts:
            if contract.get("status") != "active":
                continue

            end_date_str = contract.get("end_date", "")
            if not end_date_str:
                continue

            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if today <= end_date <= threshold:
                    days_until = (end_date - today).days
                    contract_copy = contract.copy()
                    contract_copy["days_until_expiry"] = days_until
                    expiring.append(contract_copy)
            except ValueError:
                continue

        # Sort by expiry date
        expiring.sort(key=lambda x: x.get("end_date", ""))
        return expiring

    def get_renewal_alerts(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get contracts grouped by urgency

        Returns:
            {
                "critical": [],   # Expiring in 30 days or less
                "warning": [],    # Expiring in 31-60 days
                "upcoming": []    # Expiring in 61-90 days
            }
        """
        alerts = {
            "critical": [],
            "warning": [],
            "upcoming": []
        }

        for contract in self.get_expiring_contracts(90):
            days = contract.get("days_until_expiry", 999)
            if days <= 30:
                alerts["critical"].append(contract)
            elif days <= 60:
                alerts["warning"].append(contract)
            else:
                alerts["upcoming"].append(contract)

        return alerts

    def generate_report(self, output_format: str = "text") -> str:
        """
        Generate contract status report

        Args:
            output_format: "text", "csv", or "json"

        Returns:
            Report content as string
        """
        alerts = self.get_renewal_alerts()
        all_active = [c for c in self.contracts if c.get("status") == "active"]

        if output_format == "json":
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_active": len(all_active),
                    "critical": len(alerts["critical"]),
                    "warning": len(alerts["warning"]),
                    "upcoming": len(alerts["upcoming"])
                },
                "alerts": alerts,
                "all_contracts": self.contracts
            }
            return json.dumps(report_data, indent=2, default=str)

        elif output_format == "csv":
            output = []
            output.append("Customer,Contract Type,Start Date,End Date,Days Until Expiry,Status,Monthly Value")
            for contract in all_active:
                days = ""
                try:
                    end_date = datetime.strptime(contract.get("end_date", ""), "%Y-%m-%d").date()
                    days = (end_date - datetime.now().date()).days
                except:
                    days = "N/A"

                output.append(
                    f"{contract['customer_name']},{contract['contract_type']},"
                    f"{contract['start_date']},{contract['end_date']},{days},"
                    f"{contract['status']},{contract.get('monthly_value', '')}"
                )
            return "\n".join(output)

        else:  # text format
            lines = []
            lines.append("=" * 60)
            lines.append("OBERACONNECT CONTRACT STATUS REPORT")
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            lines.append("=" * 60)
            lines.append("")

            # Summary
            lines.append(f"Total Active Contracts: {len(all_active)}")
            lines.append("")

            # Critical alerts
            if alerts["critical"]:
                lines.append("🔴 CRITICAL - Expiring in 30 days or less:")
                lines.append("-" * 40)
                for c in alerts["critical"]:
                    lines.append(f"  • {c['customer_name']} - {c['contract_type']}")
                    lines.append(f"    Expires: {c['end_date']} ({c['days_until_expiry']} days)")
                lines.append("")

            # Warning alerts
            if alerts["warning"]:
                lines.append("🟡 WARNING - Expiring in 31-60 days:")
                lines.append("-" * 40)
                for c in alerts["warning"]:
                    lines.append(f"  • {c['customer_name']} - {c['contract_type']}")
                    lines.append(f"    Expires: {c['end_date']} ({c['days_until_expiry']} days)")
                lines.append("")

            # Upcoming
            if alerts["upcoming"]:
                lines.append("🟢 UPCOMING - Expiring in 61-90 days:")
                lines.append("-" * 40)
                for c in alerts["upcoming"]:
                    lines.append(f"  • {c['customer_name']} - {c['contract_type']}")
                    lines.append(f"    Expires: {c['end_date']} ({c['days_until_expiry']} days)")
                lines.append("")

            if not any(alerts.values()):
                lines.append("✅ No contracts expiring in the next 90 days")

            lines.append("=" * 60)
            return "\n".join(lines)

    def export_to_csv(self, filename: str = None) -> Path:
        """Export all contracts to CSV file"""
        if not filename:
            filename = f"contracts_export_{datetime.now().strftime('%Y%m%d')}.csv"

        output_path = self.data_dir / filename
        csv_content = self.generate_report("csv")

        with open(output_path, 'w') as f:
            f.write(csv_content)

        print(f"✓ Contracts exported to: {output_path}")
        return output_path

    def list_all(self) -> List[Dict[str, Any]]:
        """List all contracts"""
        return self.contracts

    def get_service_catalog(self) -> Dict[str, List[str]]:
        """
        Get catalog of services by customer

        Returns:
            {
                "Customer A": ["Managed Services", "Voice"],
                "Customer B": ["Network", "Internet"]
            }
        """
        catalog = {}
        for contract in self.contracts:
            if contract.get("status") != "active":
                continue
            customer = contract["customer_name"]
            if customer not in catalog:
                catalog[customer] = []
            catalog[customer].append(contract["contract_type"])
        return catalog


def main():
    """Example usage and demo"""
    tracker = ContractTracker()

    print("\n📋 Adding example contracts...")

    # Example contracts based on SharePoint documents found
    example_contracts = [
        {
            "customer_name": "City of Freeport",
            "contract_type": "Managed Services",
            "start_date": "2025-04-10",
            "end_date": "2026-04-10",
            "services": ["IT Support", "Network Monitoring", "Help Desk"],
            "monthly_value": "$3,500",
            "renewal_terms": "annual",
            "source_document": "City of Freeport Managed Services Obera Contract_2025-0410.pdf"
        },
        {
            "customer_name": "City of Freeport",
            "contract_type": "Voice Services",
            "start_date": "2025-04-10",
            "end_date": "2026-04-10",
            "services": ["VoIP", "Phone System", "SIP Trunks"],
            "monthly_value": "$1,200",
            "renewal_terms": "annual",
            "source_document": "City of Freeport Voice Obera Contract_2025-0410.pdf"
        },
        {
            "customer_name": "7 Brew Daphne",
            "contract_type": "Managed Services",
            "start_date": "2024-01-30",
            "end_date": "2025-01-30",
            "services": ["IT Support", "Network"],
            "monthly_value": "$800",
            "renewal_terms": "annual",
            "source_document": "7 Brew Daphne Obera Signed Contract_2024-0130.pdf"
        },
        {
            "customer_name": "FirstFour Staffing",
            "contract_type": "Managed Services",
            "start_date": "2024-06-27",
            "end_date": "2025-06-27",
            "services": ["IT Support", "Cloud Services"],
            "monthly_value": "$2,000",
            "renewal_terms": "annual",
            "source_document": "FirstFour Staffing Obera Signed Contract_2024-0627.pdf"
        },
        {
            "customer_name": "DC Lawn",
            "contract_type": "Managed Services",
            "start_date": "2024-10-17",
            "end_date": "2025-10-17",
            "services": ["IT Support"],
            "monthly_value": "$500",
            "renewal_terms": "annual",
            "source_document": "DC Lawn Obera Signed Contract_2024-1017.pdf"
        }
    ]

    for contract in example_contracts:
        tracker.add_contract(contract)

    # Generate and print report
    print("\n" + tracker.generate_report())

    # Export to CSV
    csv_path = tracker.export_to_csv()

    # Show service catalog
    print("\n📊 Service Catalog by Customer:")
    print("-" * 40)
    for customer, services in tracker.get_service_catalog().items():
        print(f"  {customer}: {', '.join(services)}")

    print("\n✅ Contract Tracker demo complete!")
    print(f"   Data file: {tracker.data_file}")
    print(f"   CSV export: {csv_path}")


if __name__ == "__main__":
    main()
