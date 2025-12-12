#!/usr/bin/env python3
"""
Keeper Vault Workflow Implementations
Automated backup and secrets management workflows

Author: OberaConnect Engineering
Version: 1.0.0
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import Keeper MCP Server
from mcp_keeper_server import KeeperMCPServer, create_server


# =============================================================================
# SONICWALL CONFIG BACKUP WORKFLOW
# =============================================================================

class SonicWallBackupWorkflow:
    """
    Automates SonicWall configuration backup to Keeper vault

    Features:
    - Watch for new .exp files in specified directory
    - Parse customer code from filename
    - Upload to correct Keeper folder
    - Add metadata to record
    """

    # Default folder for all firewall/router configs
    DEFAULT_FOLDER = "Router-Firewall Customer Sites"

    # Customer code to folder mapping (for future per-customer folders)
    CUSTOMER_FOLDERS = {
        "SFWB": "Router-Firewall Customer Sites",   # Spanish Fort Water Board
        "SETC": "Router-Firewall Customer Sites",   # Setco
        "GRLE": "Router-Firewall Customer Sites",   # G Real Estate
        "FRPT": "Router-Firewall Customer Sites",   # Freeport
        "OBERA": "Router-Firewall Customer Sites",  # Obera internal
        "DEFAULT": "Router-Firewall Customer Sites" # Default folder
    }

    # Pattern to extract info from SonicWall export filename
    # Example: sonicwall-TZ 270-SonicOS 7.0.1-5161-R6164-2025-12-05T14_05_24.264Z.exp
    SONICWALL_FILENAME_PATTERN = re.compile(
        r'sonicwall-([^-]+)-SonicOS\s*([\d\.]+)-(\d+)-R(\d+)-(.+)\.exp',
        re.IGNORECASE
    )

    def __init__(self, keeper_server: KeeperMCPServer = None):
        self.keeper = keeper_server or create_server()
        self.authenticated = False

    def start_session(self) -> Dict[str, Any]:
        """Start Keeper session"""
        result = self.keeper.start_session()
        if result.get("authenticated"):
            self.authenticated = True
        return result

    def authenticate_sso(self, token: str) -> Dict[str, Any]:
        """Complete SSO authentication with token"""
        result = self.keeper.complete_sso_login(token)
        if result.get("authenticated"):
            self.authenticated = True
        return result

    def parse_sonicwall_filename(self, filename: str) -> Dict[str, Any]:
        """
        Parse SonicWall export filename to extract metadata

        Returns:
            Dict with model, firmware, serial, date info
        """
        # Try standard SonicWall export format
        match = self.SONICWALL_FILENAME_PATTERN.match(filename)
        if match:
            return {
                "model": match.group(1).strip(),
                "firmware": match.group(2),
                "build": match.group(3),
                "release": match.group(4),
                "timestamp": match.group(5),
                "parsed": True
            }

        # Try custom naming format: SFWB_TZ270_2025-12-05_preshipment.exp
        custom_match = re.match(
            r'([A-Z]{4})_([^_]+)_(\d{4}-\d{2}-\d{2})_(\w+)\.exp',
            filename
        )
        if custom_match:
            return {
                "customer_code": custom_match.group(1),
                "model": custom_match.group(2),
                "date": custom_match.group(3),
                "backup_type": custom_match.group(4),
                "parsed": True
            }

        return {"parsed": False, "filename": filename}

    def determine_keeper_folder(self, customer_code: str = None) -> str:
        """Determine the correct Keeper folder for the config"""
        if customer_code and customer_code.upper() in self.CUSTOMER_FOLDERS:
            return self.CUSTOMER_FOLDERS[customer_code.upper()]
        return self.CUSTOMER_FOLDERS["DEFAULT"]

    def generate_record_title(
        self,
        customer_code: str,
        model: str,
        date: str = None,
        backup_type: str = "backup"
    ) -> str:
        """Generate standardized record title"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        return f"{customer_code} - SonicWall {model} Config - {date}"

    def generate_notes(self, metadata: Dict[str, Any], file_path: str) -> str:
        """Generate notes field for Keeper record"""
        notes = []

        if metadata.get("customer_code"):
            notes.append(f"Customer: {metadata['customer_code']}")

        if metadata.get("model"):
            notes.append(f"Device: SonicWall {metadata['model']}")

        if metadata.get("firmware"):
            notes.append(f"Firmware: {metadata['firmware']}")

        if metadata.get("backup_type"):
            notes.append(f"Backup Type: {metadata['backup_type']}")

        notes.append(f"Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        notes.append(f"Source File: {Path(file_path).name}")
        notes.append(f"Verified: Pending")

        return "\n".join(notes)

    def backup_config(
        self,
        file_path: str,
        customer_code: str = None,
        backup_type: str = "backup",
        folder: str = None
    ) -> Dict[str, Any]:
        """
        Backup a SonicWall config file to Keeper

        Args:
            file_path: Path to the .exp file
            customer_code: 4-letter customer code (e.g., SFWB)
            backup_type: Type of backup (preshipment, postinstall, prechange, scheduled)
            folder: Override target folder (default: auto-detect)

        Returns:
            Result dict with success status and details
        """
        if not self.authenticated:
            return {
                "success": False,
                "error": "Not authenticated. Call start_session() and authenticate_sso() first."
            }

        file_path = Path(file_path)
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        # Parse filename for metadata
        metadata = self.parse_sonicwall_filename(file_path.name)

        # Use provided customer_code or try to extract from filename
        if not customer_code:
            customer_code = metadata.get("customer_code", "UNKNOWN")

        # Determine folder
        target_folder = folder or self.determine_keeper_folder(customer_code)

        # Generate record title
        model = metadata.get("model", "Unknown")
        date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
        title = self.generate_record_title(customer_code, model, date, backup_type)

        # Generate notes
        metadata["customer_code"] = customer_code
        metadata["backup_type"] = backup_type
        notes = self.generate_notes(metadata, str(file_path))

        # Create record in Keeper
        create_result = self.keeper.execute_tool(
            "keeper_create_record",
            {
                "folder": target_folder,
                "title": title,
                "notes": notes
            }
        )

        if not create_result.get("success"):
            return {
                "success": False,
                "error": f"Failed to create record: {create_result.get('error', create_result.get('output'))}",
                "step": "create_record"
            }

        # Upload attachment
        upload_result = self.keeper.execute_tool(
            "keeper_upload_attachment",
            {
                "record": title,
                "file_path": str(file_path.absolute())
            }
        )

        return {
            "success": upload_result.get("success", False),
            "record_title": title,
            "folder": target_folder,
            "file": str(file_path),
            "metadata": metadata,
            "create_result": create_result,
            "upload_result": upload_result
        }

    def batch_backup(
        self,
        directory: str,
        pattern: str = "*.exp",
        customer_code: str = None
    ) -> Dict[str, Any]:
        """
        Backup all matching config files from a directory

        Args:
            directory: Directory to scan for .exp files
            pattern: Glob pattern (default: *.exp)
            customer_code: Override customer code for all files

        Returns:
            Batch result with individual file results
        """
        directory = Path(directory)
        if not directory.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}

        files = list(directory.glob(pattern))
        if not files:
            return {"success": True, "message": "No matching files found", "count": 0}

        results = []
        success_count = 0

        for file_path in files:
            result = self.backup_config(
                str(file_path),
                customer_code=customer_code
            )
            results.append({
                "file": file_path.name,
                **result
            })
            if result.get("success"):
                success_count += 1

        return {
            "success": success_count == len(files),
            "total": len(files),
            "successful": success_count,
            "failed": len(files) - success_count,
            "results": results
        }

    def close(self):
        """Close Keeper session"""
        if self.keeper:
            self.keeper.close()


# =============================================================================
# FILE WATCHER FOR AUTOMATIC BACKUP
# =============================================================================

class SonicWallConfigWatcher:
    """
    Watch a directory for new SonicWall config files and auto-backup to Keeper

    Usage:
        watcher = SonicWallConfigWatcher("/path/to/downloads")
        watcher.start()  # Runs continuously
    """

    def __init__(
        self,
        watch_dir: str,
        keeper_server: KeeperMCPServer = None,
        poll_interval: int = 30
    ):
        self.watch_dir = Path(watch_dir)
        self.workflow = SonicWallBackupWorkflow(keeper_server)
        self.poll_interval = poll_interval
        self.processed_files = set()
        self._running = False

    def _is_sonicwall_config(self, filename: str) -> bool:
        """Check if file is a SonicWall config export"""
        return (
            filename.endswith('.exp') and
            ('sonicwall' in filename.lower() or
             re.match(r'[A-Z]{4}_[^_]+_\d{4}-\d{2}-\d{2}_\w+\.exp', filename))
        )

    def scan_for_new_files(self) -> List[Path]:
        """Scan directory for new SonicWall config files"""
        new_files = []

        for file_path in self.watch_dir.glob("*.exp"):
            if file_path.name not in self.processed_files:
                if self._is_sonicwall_config(file_path.name):
                    new_files.append(file_path)

        return new_files

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single config file"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing: {file_path.name}")

        result = self.workflow.backup_config(str(file_path))

        if result.get("success"):
            self.processed_files.add(file_path.name)
            print(f"  ✓ Uploaded to Keeper: {result.get('record_title')}")
        else:
            print(f"  ✗ Failed: {result.get('error')}")

        return result

    def start(self, sso_token: str = None):
        """
        Start watching for files

        Args:
            sso_token: SSO token for Keeper authentication
        """
        import time

        print(f"Starting SonicWall Config Watcher")
        print(f"Watch directory: {self.watch_dir}")
        print(f"Poll interval: {self.poll_interval}s")
        print("-" * 50)

        # Start Keeper session
        result = self.workflow.start_session()
        print(f"Keeper session: {result}")

        if not self.workflow.authenticated:
            if sso_token:
                result = self.workflow.authenticate_sso(sso_token)
                print(f"SSO auth: {result}")
            else:
                print("ERROR: Not authenticated and no SSO token provided")
                return

        self._running = True

        try:
            while self._running:
                new_files = self.scan_for_new_files()

                for file_path in new_files:
                    self.process_file(file_path)

                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\nStopping watcher...")
        finally:
            self.workflow.close()

    def stop(self):
        """Stop the watcher"""
        self._running = False


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI for SonicWall Config Backup"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SonicWall Config Backup to Keeper Vault"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Single file backup
    backup_parser = subparsers.add_parser("backup", help="Backup a single config file")
    backup_parser.add_argument("file", help="Path to .exp file")
    backup_parser.add_argument("--customer", "-c", help="Customer code (e.g., SFWB)")
    backup_parser.add_argument("--type", "-t", default="backup",
                               choices=["preshipment", "postinstall", "prechange", "scheduled", "backup"],
                               help="Backup type")
    backup_parser.add_argument("--folder", "-f", help="Target Keeper folder")
    backup_parser.add_argument("--token", help="SSO token for authentication")

    # Batch backup
    batch_parser = subparsers.add_parser("batch", help="Backup all configs in a directory")
    batch_parser.add_argument("directory", help="Directory containing .exp files")
    batch_parser.add_argument("--customer", "-c", help="Customer code for all files")
    batch_parser.add_argument("--token", help="SSO token for authentication")

    # Watch mode
    watch_parser = subparsers.add_parser("watch", help="Watch directory for new configs")
    watch_parser.add_argument("directory", help="Directory to watch")
    watch_parser.add_argument("--interval", "-i", type=int, default=30, help="Poll interval in seconds")
    watch_parser.add_argument("--token", help="SSO token for authentication")

    args = parser.parse_args()

    if args.command == "backup":
        workflow = SonicWallBackupWorkflow()
        workflow.start_session()

        if args.token:
            workflow.authenticate_sso(args.token)
        else:
            result = workflow.keeper.login()
            if result.get("sso_required"):
                print(f"\nSSO URL: {result['sso_url']}")
                token = input("Paste SSO token: ").strip()
                workflow.authenticate_sso(token)

        result = workflow.backup_config(
            args.file,
            customer_code=args.customer,
            backup_type=args.type,
            folder=args.folder
        )

        print(json.dumps(result, indent=2))
        workflow.close()

    elif args.command == "batch":
        workflow = SonicWallBackupWorkflow()
        workflow.start_session()

        if args.token:
            workflow.authenticate_sso(args.token)
        else:
            result = workflow.keeper.login()
            if result.get("sso_required"):
                print(f"\nSSO URL: {result['sso_url']}")
                token = input("Paste SSO token: ").strip()
                workflow.authenticate_sso(token)

        result = workflow.batch_backup(
            args.directory,
            customer_code=args.customer
        )

        print(json.dumps(result, indent=2))
        workflow.close()

    elif args.command == "watch":
        watcher = SonicWallConfigWatcher(
            args.directory,
            poll_interval=args.interval
        )
        watcher.start(sso_token=args.token)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
