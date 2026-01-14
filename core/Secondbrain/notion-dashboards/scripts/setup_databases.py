#!/usr/bin/env python3
"""
Notion Database Setup - Create dashboard databases programmatically

Usage:
    python setup_databases.py --token YOUR_TOKEN --parent-page PAGE_ID
    python setup_databases.py --token YOUR_TOKEN --parent-page PAGE_ID --dry-run

Requirements:
    pip install notion-client --break-system-packages
"""

import argparse
import json
import logging
import sys

from notion_client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NotionDatabaseCreator:
    def __init__(self, token: str, dry_run: bool = False):
        self.token = token
        self.dry_run = dry_run
        self.client = Client(auth=token)
        self.created_databases = {}
    
    def create_database(self, parent_page_id: str, title: str, properties: dict) -> dict:
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create database: {title}")
            return {"id": f"dry-run-{title.lower().replace(' ', '-')}"}
        
        result = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties
        )
        logger.info(f"Created database: {title} ({result['id']})")
        return result
    
    def get_customer_status_schema(self) -> dict:
        return {
            "Site Name": {"title": {}},
            "Customer ID": {"rich_text": {}},
            "State": {"select": {"options": [
                {"name": s, "color": c} for s, c in [
                    ("Alabama", "red"), ("Arkansas", "orange"), ("Florida", "yellow"),
                    ("Georgia", "green"), ("Kentucky", "blue"), ("Louisiana", "purple"),
                    ("Mississippi", "pink"), ("Missouri", "red"), ("North Carolina", "orange"),
                    ("Oklahoma", "yellow"), ("South Carolina", "green"), ("Tennessee", "blue"),
                    ("Texas", "purple"), ("Virginia", "pink")
                ]
            ]}},
            "Device Count": {"number": {"format": "number"}},
            "Stack Type": {"multi_select": {"options": [
                {"name": "Ubiquiti", "color": "blue"}, {"name": "MikroTik", "color": "orange"},
                {"name": "SonicWall", "color": "red"}, {"name": "Azure", "color": "purple"}
            ]}},
            "Deployment Status": {"select": {"options": [
                {"name": "onboarding", "color": "yellow"}, {"name": "active", "color": "green"},
                {"name": "maintenance", "color": "blue"}, {"name": "needs attention", "color": "red"},
                {"name": "offboarding", "color": "gray"}
            ]}},
            "Health Score": {"number": {"format": "number"}},
            "Last Health Check": {"date": {}},
            "Open Tickets": {"number": {"format": "number"}},
            "Contract Renewal": {"date": {}},
            "Primary Contact": {"rich_text": {}},
            "Notes": {"rich_text": {}}
        }
    
    def get_daily_health_schema(self, customer_db_id: str = None) -> dict:
        schema = {
            "Date": {"title": {}},
            "Devices Online": {"number": {"format": "number"}},
            "Devices Offline": {"number": {"format": "number"}},
            "Devices Total": {"number": {"format": "number"}},
            "Availability Percentage": {"number": {"format": "percent"}},
            "WiFi Clients": {"number": {"format": "number"}},
            "Signal Warnings": {"number": {"format": "number"}},
            "Active Alerts": {"number": {"format": "number"}},
            "Alert Summary": {"rich_text": {}},
            "Config Drift Detected": {"checkbox": {}},
            "Backup Status": {"select": {"options": [
                {"name": "success", "color": "green"}, {"name": "partial", "color": "yellow"},
                {"name": "failed", "color": "red"}, {"name": "unknown", "color": "gray"}
            ]}},
            "Health Score": {"number": {"format": "number"}},
            "Notes": {"rich_text": {}}
        }
        if customer_db_id and not self.dry_run:
            schema["Site"] = {"relation": {"database_id": customer_db_id, "single_property": {}}}
        return schema
    
    def get_azure_pipeline_schema(self) -> dict:
        return {
            "Service Name": {"title": {}},
            "Category": {"select": {"options": [
                {"name": c, "color": ["blue", "green", "yellow", "orange", "red", "purple", "pink"][i % 7]}
                for i, c in enumerate([
                    "Compute", "Networking", "Storage", "Databases", "Identity", "Security",
                    "Management", "DevOps", "AI/ML", "Analytics", "Integration", "IoT",
                    "Migration", "Backup", "Monitoring"
                ])
            ]}},
            "Pipeline Stage": {"select": {"options": [
                {"name": "backlog", "color": "gray"}, {"name": "lab testing", "color": "yellow"},
                {"name": "production validation", "color": "orange"},
                {"name": "customer ready", "color": "green"}, {"name": "deprecated", "color": "red"}
            ]}},
            "Lab Status": {"select": {"options": [
                {"name": "not started", "color": "gray"}, {"name": "in progress", "color": "yellow"},
                {"name": "passed", "color": "green"}, {"name": "failed", "color": "red"}
            ]}},
            "Production Status": {"select": {"options": [
                {"name": "not started", "color": "gray"}, {"name": "in progress", "color": "yellow"},
                {"name": "deployed", "color": "green"}, {"name": "issues", "color": "red"}
            ]}},
            "Owner": {"rich_text": {}},
            "Customer Requests": {"number": {"format": "number"}},
            "Documentation Link": {"url": {}},
            "Security Review": {"checkbox": {}},
            "Target Date": {"date": {}},
            "Blockers": {"rich_text": {}},
            "Last Updated": {"date": {}},
            "Notes": {"rich_text": {}}
        }
    
    def get_config_changes_schema(self) -> dict:
        """Schema for logging all configuration changes from oberaconnect-tools."""
        return {
            "Change ID": {"title": {}},
            "Site Name": {"rich_text": {}},
            "Tool": {"select": {"options": [
                {"name": "mikrotik-config-builder", "color": "orange"},
                {"name": "sonicwall-scripts", "color": "red"},
                {"name": "unifi-deploy", "color": "blue"},
                {"name": "azure-automation", "color": "purple"},
                {"name": "network-troubleshooter", "color": "green"},
                {"name": "manual", "color": "gray"}
            ]}},
            "Vendor": {"select": {"options": [
                {"name": "MikroTik", "color": "orange"},
                {"name": "SonicWall", "color": "red"},
                {"name": "Ubiquiti", "color": "blue"},
                {"name": "Azure", "color": "purple"},
                {"name": "Multi", "color": "green"},
                {"name": "Manual", "color": "gray"}
            ]}},
            "Category": {"select": {"options": [
                {"name": "network", "color": "blue"},
                {"name": "security", "color": "red"},
                {"name": "cloud", "color": "purple"},
                {"name": "assessment", "color": "green"},
                {"name": "manual", "color": "gray"},
                {"name": "other", "color": "default"}
            ]}},
            "Action": {"select": {"options": [
                {"name": "deploy", "color": "green"},
                {"name": "update", "color": "blue"},
                {"name": "rollback", "color": "orange"},
                {"name": "backup", "color": "purple"},
                {"name": "restore", "color": "yellow"},
                {"name": "delete", "color": "red"},
                {"name": "create", "color": "green"},
                {"name": "modify", "color": "blue"},
                {"name": "assessment", "color": "gray"}
            ]}},
            "Summary": {"rich_text": {}},
            "Details": {"rich_text": {}},
            "Engineer": {"rich_text": {}},
            "Timestamp": {"date": {}},
            "Risk Level": {"select": {"options": [
                {"name": "low", "color": "green"},
                {"name": "medium", "color": "yellow"},
                {"name": "high", "color": "orange"},
                {"name": "critical", "color": "red"}
            ]}},
            "Ticket ID": {"rich_text": {}},
            "Rollback Plan": {"rich_text": {}},
            "Notes": {"rich_text": {}}
        }
    
    def get_devices_schema(self) -> dict:
        """Schema for network device inventory from discovery tools."""
        return {
            "Device Name": {"title": {}},
            "Device Type": {"select": {"options": [
                {"name": "AP", "color": "blue"},
                {"name": "Switch", "color": "green"},
                {"name": "Gateway", "color": "purple"},
                {"name": "Router", "color": "orange"},
                {"name": "Firewall", "color": "red"},
                {"name": "Server", "color": "gray"},
                {"name": "Endpoint", "color": "default"}
            ]}},
            "Vendor": {"select": {"options": [
                {"name": "Ubiquiti", "color": "blue"},
                {"name": "MikroTik", "color": "orange"},
                {"name": "SonicWall", "color": "red"},
                {"name": "Microsoft", "color": "green"},
                {"name": "Other", "color": "gray"}
            ]}},
            "MAC Address": {"rich_text": {}},
            "IP Address": {"rich_text": {}},
            "Firmware Version": {"rich_text": {}},
            "Status": {"select": {"options": [
                {"name": "online", "color": "green"},
                {"name": "offline", "color": "red"},
                {"name": "pending", "color": "yellow"},
                {"name": "unknown", "color": "gray"}
            ]}},
            "Last Seen": {"date": {}},
            "Uptime Days": {"number": {"format": "number"}},
            "Model": {"rich_text": {}},
            "Serial Number": {"rich_text": {}},
            "Discovery Source": {"select": {"options": [
                {"name": "UniFi API", "color": "blue"},
                {"name": "NinjaOne", "color": "green"},
                {"name": "Network Scan", "color": "orange"},
                {"name": "Manual", "color": "gray"}
            ]}},
            "Sync Timestamp": {"date": {}},
            "Notes": {"rich_text": {}}
        }
    
    def get_runbook_library_schema(self) -> dict:
        return {
            "Title": {"title": {}},
            "Category": {"select": {"options": [
                {"name": "network", "color": "blue"}, {"name": "security", "color": "red"},
                {"name": "cloud", "color": "purple"}, {"name": "hardware", "color": "orange"},
                {"name": "process", "color": "green"}
            ]}},
            "Vendor": {"multi_select": {"options": [
                {"name": "Ubiquiti", "color": "blue"}, {"name": "MikroTik", "color": "orange"},
                {"name": "SonicWall", "color": "red"}, {"name": "Azure", "color": "purple"},
                {"name": "M365", "color": "green"}
            ]}},
            "Document Type": {"select": {"options": [
                {"name": "SOP", "color": "blue"}, {"name": "runbook", "color": "green"},
                {"name": "troubleshooting guide", "color": "yellow"},
                {"name": "template", "color": "orange"}, {"name": "reference", "color": "purple"}
            ]}},
            "Complexity": {"select": {"options": [
                {"name": "basic", "color": "green"}, {"name": "intermediate", "color": "yellow"},
                {"name": "advanced", "color": "red"}
            ]}},
            "Automation Status": {"select": {"options": [
                {"name": "manual", "color": "gray"}, {"name": "partially automated", "color": "yellow"},
                {"name": "fully automated", "color": "green"}, {"name": "deprecated", "color": "red"}
            ]}},
            "Last Review Date": {"date": {}},
            "Next Review Due": {"date": {}},
            "Owner": {"rich_text": {}},
            "Tags": {"multi_select": {"options": []}},
            "Documentation Link": {"url": {}}
        }
    
    def setup_all_databases(self, parent_page_id: str) -> dict:
        results = {}
        
        logger.info("Creating Customer Status Board...")
        customer_db = self.create_database(parent_page_id, "Customer Status Board", self.get_customer_status_schema())
        results["customer_status"] = customer_db["id"]
        
        logger.info("Creating Daily Health Summaries...")
        health_db = self.create_database(parent_page_id, "Daily Health Summaries", 
                                         self.get_daily_health_schema(results["customer_status"]))
        results["daily_health"] = health_db["id"]
        
        logger.info("Creating Azure Migration Pipeline...")
        pipeline_db = self.create_database(parent_page_id, "Azure Migration Pipeline", self.get_azure_pipeline_schema())
        results["azure_pipeline"] = pipeline_db["id"]
        
        logger.info("Creating Runbook Library...")
        runbook_db = self.create_database(parent_page_id, "Runbook Library", self.get_runbook_library_schema())
        results["runbook_library"] = runbook_db["id"]
        
        logger.info("Creating Config Changes Log...")
        changes_db = self.create_database(parent_page_id, "Config Changes Log", self.get_config_changes_schema())
        results["config_changes"] = changes_db["id"]
        
        logger.info("Creating Network Devices Inventory...")
        devices_db = self.create_database(parent_page_id, "Network Devices", self.get_devices_schema())
        results["devices"] = devices_db["id"]
        
        self.created_databases = results
        return results
    
    def generate_config(self, output_path: str = None) -> str:
        config = {
            "notion_token": "YOUR_NOTION_TOKEN_HERE",
            "databases": self.created_databases,
            "unifi": {"site_manager_url": "https://unifi.ui.com", "api_token": "YOUR_UNIFI_TOKEN"},
            "ninjaone": {"api_url": "https://app.ninjarmm.com/api/v2", "client_id": "", "client_secret": ""},
            "settings": {"wifi_signal_threshold_dbm": -65, "health_score_warning_threshold": 70}
        }
        config_json = json.dumps(config, indent=4)
        if output_path:
            with open(output_path, 'w') as f:
                f.write(config_json)
            logger.info(f"Config written to {output_path}")
        return config_json


def main():
    parser = argparse.ArgumentParser(description="Create Notion databases for OberaConnect")
    parser.add_argument('--token', '-t', required=True, help='Notion integration token')
    parser.add_argument('--parent-page', '-p', required=True, help='Parent page ID')
    parser.add_argument('--output', '-o', help='Output config.json path')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    
    args = parser.parse_args()
    
    try:
        creator = NotionDatabaseCreator(args.token, dry_run=args.dry_run)
        results = creator.setup_all_databases(args.parent_page)
        
        print(f"\n{'=' * 50}")
        print("DATABASE SETUP COMPLETE")
        print(f"{'=' * 50}")
        for name, db_id in results.items():
            print(f"  {name}: {db_id}")
        
        if args.output:
            creator.generate_config(args.output)
        else:
            print("\nGenerated config:")
            print(creator.generate_config())
    
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
