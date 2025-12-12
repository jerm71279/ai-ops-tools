#!/usr/bin/env python3
"""
Keeper Config Puller
Pull MikroTik and SonicWall config files from Keeper Security for analysis

Usage:
    # Interactive mode (prompts for SSO)
    ./venv/bin/python3 keeper_config_puller.py

    # Search only (list matching records)
    ./venv/bin/python3 keeper_config_puller.py --search-only

    # Download specific record
    ./venv/bin/python3 keeper_config_puller.py --record "SFWB MikroTik"
"""

import subprocess
import time
import re
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


class KeeperConfigPuller:
    """Pull network config files from Keeper vault"""

    def __init__(self, output_dir: str = None):
        self.process = None
        self.authenticated = False
        self.output_dir = Path(output_dir or "/home/mavrick/Projects/Secondbrain/keeper_configs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Config search patterns
        self.search_terms = [
            "mikrotik",
            "sonicwall",
            "router config",
            "firewall config",
            "network config",
            ".rsc",  # MikroTik export extension
            ".exp",  # SonicWall export extension
        ]

    def start_session(self) -> bool:
        """Start keeper shell session"""
        print("Starting Keeper Commander session...")

        try:
            self.process = subprocess.Popen(
                ['keeper', 'shell'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            time.sleep(2)
            output = self._read_output(timeout=5)
            print(output)

            if 'My Vault' in output:
                self.authenticated = True
                print("Already authenticated!")
                return True
            elif 'Not logged in' in output:
                print("Session started, need to login...")
                return True
            return True

        except FileNotFoundError:
            print("ERROR: Keeper Commander not found. Install with: pip install keepercommander")
            return False
        except Exception as e:
            print(f"ERROR starting session: {e}")
            return False

    def login(self, email: str = "jeremy.smith@oberaconnect.com") -> dict:
        """Initiate login - returns SSO URL if needed"""
        print(f"\nLogging in as {email}...")

        self._send_command(f"login {email}")
        time.sleep(3)
        output = self._read_output(timeout=30)

        if 'SSO' in output or 'https://' in output:
            # Extract SSO URL
            urls = re.findall(r'https://[^\s]+', output)
            if urls:
                print("\n" + "=" * 60)
                print("SSO LOGIN REQUIRED")
                print("=" * 60)
                print(f"\n1. Open this URL in your browser:\n   {urls[0]}")
                print("\n2. Complete login in browser")
                print("\n3. Copy the token/code from the browser")
                print("=" * 60)
                return {"status": "sso_required", "url": urls[0], "output": output}

        if 'My Vault' in output or 'Logged in' in output:
            self.authenticated = True
            return {"status": "success", "output": output}

        return {"status": "unknown", "output": output}

    def complete_sso(self, token: str) -> bool:
        """Complete SSO with token from browser"""
        print(f"\nSubmitting SSO token...")
        self._send_command(token)
        time.sleep(5)
        output = self._read_output(timeout=10)

        if 'My Vault' in output or 'Successfully' in output:
            self.authenticated = True
            print("SSO login successful!")
            return True

        print(f"SSO result: {output}")
        return 'error' not in output.lower()

    def search_configs(self, query: str = None) -> list:
        """Search for config records"""
        results = []

        search_queries = [query] if query else self.search_terms

        for term in search_queries:
            print(f"Searching for: {term}...")
            self._send_command(f"search {term}")
            time.sleep(2)
            output = self._read_output(timeout=10)

            # Parse search results
            lines = output.strip().split('\n')
            for line in lines:
                # Look for record UIDs (22 char base64-like strings)
                if re.search(r'[A-Za-z0-9_-]{20,}', line) and 'search' not in line.lower():
                    results.append({"query": term, "line": line.strip()})

        return results

    def list_folders(self, path: str = "") -> str:
        """List folders in vault"""
        cmd = f"ls {path}" if path else "ls"
        self._send_command(cmd)
        time.sleep(2)
        return self._read_output(timeout=5)

    def get_record(self, record: str) -> str:
        """Get record details"""
        self._send_command(f"get {record}")
        time.sleep(2)
        return self._read_output(timeout=5)

    def download_attachment(self, record: str, output_path: str = None) -> bool:
        """Download attachments from a record"""
        if not output_path:
            output_path = str(self.output_dir)

        print(f"Downloading attachments from: {record}")
        print(f"Saving to: {output_path}")

        # Use download-attachment command
        self._send_command(f"download-attachment --record \"{record}\" --out-dir \"{output_path}\"")
        time.sleep(5)
        output = self._read_output(timeout=30)
        print(output)

        return 'error' not in output.lower()

    def download_all_configs(self) -> dict:
        """Download all MikroTik and SonicWall configs"""
        results = {
            "mikrotik": [],
            "sonicwall": [],
            "errors": []
        }

        # Search for MikroTik configs
        print("\n" + "=" * 60)
        print("Searching for MikroTik configs...")
        print("=" * 60)

        mikrotik_terms = ["mikrotik", ".rsc", "routeros"]
        for term in mikrotik_terms:
            self._send_command(f"search {term}")
            time.sleep(2)
            output = self._read_output(timeout=10)
            print(f"Results for '{term}':\n{output}\n")

        # Search for SonicWall configs
        print("\n" + "=" * 60)
        print("Searching for SonicWall configs...")
        print("=" * 60)

        sonicwall_terms = ["sonicwall", ".exp", "firewall"]
        for term in sonicwall_terms:
            self._send_command(f"search {term}")
            time.sleep(2)
            output = self._read_output(timeout=10)
            print(f"Results for '{term}':\n{output}\n")

        return results

    def interactive_download(self):
        """Interactive mode to browse and download"""
        print("\n" + "=" * 60)
        print("INTERACTIVE MODE")
        print("=" * 60)
        print("Commands: ls, cd <folder>, search <term>, get <record>,")
        print("          download <record>, quit")
        print("=" * 60 + "\n")

        while True:
            try:
                cmd = input("keeper> ").strip()

                if not cmd:
                    continue

                if cmd.lower() in ['quit', 'exit', 'q']:
                    break

                if cmd.startswith('download '):
                    record = cmd[9:].strip()
                    self.download_attachment(record)
                elif cmd.startswith('get '):
                    record = cmd[4:].strip()
                    print(self.get_record(record))
                else:
                    self._send_command(cmd)
                    time.sleep(2)
                    print(self._read_output(timeout=5))

            except KeyboardInterrupt:
                print("\nExiting...")
                break

    def _send_command(self, cmd: str):
        """Send command to keeper shell"""
        if self.process and self.process.stdin:
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()

    def _read_output(self, timeout: float = 5) -> str:
        """Read output from keeper shell"""
        import select

        output = []
        end_time = time.time() + timeout

        while time.time() < end_time:
            if self.process and self.process.stdout:
                # Check if data available
                ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                if ready:
                    line = self.process.stdout.readline()
                    if line:
                        output.append(line)
                    else:
                        break
                else:
                    # No data, check if we have enough output
                    if output and time.time() > end_time - (timeout * 0.5):
                        break
            else:
                break

        return ''.join(output)

    def close(self):
        """Close the keeper session"""
        if self.process:
            try:
                self._send_command("quit")
                self.process.terminate()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description="Pull network configs from Keeper")
    parser.add_argument("--search-only", action="store_true", help="Only search, don't download")
    parser.add_argument("--record", type=str, help="Download specific record")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--query", "-q", type=str, help="Custom search query")

    args = parser.parse_args()

    print("=" * 60)
    print("Keeper Config Puller")
    print("Pull MikroTik & SonicWall configs for analysis")
    print("=" * 60)

    puller = KeeperConfigPuller(output_dir=args.output)

    try:
        # Start session
        if not puller.start_session():
            sys.exit(1)

        # Login if needed
        if not puller.authenticated:
            result = puller.login()

            if result["status"] == "sso_required":
                token = input("\nPaste SSO token here: ").strip()
                if not puller.complete_sso(token):
                    print("SSO login failed")
                    sys.exit(1)

        # Execute requested operation
        if args.interactive:
            puller.interactive_download()

        elif args.search_only or args.query:
            print("\nSearching vault...")
            results = puller.search_configs(args.query)
            print(f"\nFound {len(results)} potential matches")
            for r in results:
                print(f"  [{r['query']}] {r['line']}")

        elif args.record:
            print(f"\nDownloading: {args.record}")
            puller.download_attachment(args.record)

        else:
            # Default: search and list all configs
            puller.download_all_configs()

            print("\n" + "=" * 60)
            print("To download a specific record, use:")
            print(f"  python3 keeper_config_puller.py --record \"Record Name\"")
            print("\nOr use interactive mode:")
            print(f"  python3 keeper_config_puller.py --interactive")
            print("=" * 60)

    finally:
        puller.close()

    print(f"\nConfigs saved to: {puller.output_dir}")


if __name__ == "__main__":
    main()
