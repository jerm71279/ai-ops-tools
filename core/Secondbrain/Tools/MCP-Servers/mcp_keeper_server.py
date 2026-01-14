import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
MCP Server: Keeper Vault Operations (Session-Based)
Uses persistent keeper shell session for SSO authentication
"""
import subprocess
import threading
import queue
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class KeeperSession:
    """
    Manages a persistent Keeper Commander shell session
    Handles SSO authentication and command execution
    """

    def __init__(self):
        self.process = None
        self.output_queue = queue.Queue()
        self.authenticated = False
        self.prompt_pattern = re.compile(r'(My Vault|Not logged in)>\s*$')
        self._reader_thread = None

    def start(self) -> bool:
        """Start the keeper shell process"""
        try:
            self.process = subprocess.Popen(
                ['keeper', 'shell'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Start reader thread
            self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self._reader_thread.start()

            # Wait for initial prompt
            time.sleep(2)
            initial = self._get_output(timeout=5)

            if 'Not logged in' in initial:
                self.authenticated = False
                return True
            elif 'My Vault' in initial:
                self.authenticated = True
                return True

            return True

        except Exception as e:
            print(f"Error starting keeper shell: {e}")
            return False

    def _read_output(self):
        """Continuously read output from the process"""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(line)
            except:
                break

    def _get_output(self, timeout: float = 10) -> str:
        """Get accumulated output with timeout"""
        output_lines = []
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                line = self.output_queue.get(timeout=0.5)
                output_lines.append(line)

                # Check if we hit a prompt
                full_output = ''.join(output_lines)
                if self.prompt_pattern.search(full_output):
                    break

            except queue.Empty:
                if output_lines:
                    # Check if last output looks complete
                    full_output = ''.join(output_lines)
                    if self.prompt_pattern.search(full_output):
                        break

        return ''.join(output_lines)

    def send_command(self, command: str, timeout: float = 30) -> str:
        """Send a command and return the output"""
        if not self.process or self.process.poll() is not None:
            return "Error: Keeper session not running"

        # Clear any pending output
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except:
                break

        # Send command
        try:
            self.process.stdin.write(command + '\n')
            self.process.stdin.flush()
        except Exception as e:
            return f"Error sending command: {e}"

        # Get response
        time.sleep(0.5)  # Brief delay for command processing
        output = self._get_output(timeout=timeout)

        # Update authentication status
        if 'My Vault>' in output:
            self.authenticated = True

        # Clean up output (remove command echo and prompt)
        lines = output.split('\n')
        cleaned = []
        for line in lines:
            # Skip command echo
            if line.strip() == command.strip():
                continue
            # Skip prompt lines
            if re.match(r'^(My Vault|Not logged in)>\s*$', line.strip()):
                continue
            cleaned.append(line)

        return '\n'.join(cleaned).strip()

    def is_authenticated(self) -> bool:
        """Check if session is authenticated"""
        return self.authenticated

    def close(self):
        """Close the keeper session"""
        if self.process:
            try:
                self.process.stdin.write('quit\n')
                self.process.stdin.flush()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None


class KeeperMCPServer:
    """
    MCP Server for Keeper Vault operations using persistent session
    """

    def __init__(self):
        self.session = KeeperSession()
        self._started = False

    def start_session(self) -> Dict[str, Any]:
        """Start the keeper session - call this first"""
        if self._started:
            return {"success": True, "message": "Session already started"}

        success = self.session.start()
        if success:
            self._started = True
            return {
                "success": True,
                "authenticated": self.session.is_authenticated(),
                "message": "Session started. Run 'login' if not authenticated."
            }
        return {"success": False, "error": "Failed to start keeper session"}

    def login(self, email: str = "jeremy.smith@oberaconnect.com") -> Dict[str, Any]:
        """
        Initiate login - returns SSO URL for browser authentication
        After browser auth, call complete_sso_login with the token
        """
        if not self._started:
            self.start_session()

        output = self.session.send_command(f"login {email}", timeout=10)

        # Check for SSO URL
        if "SSO Login URL:" in output:
            # Extract URL
            url_match = re.search(r'(https://keepersecurity\.com/api/rest/sso/saml/login/[^\s]+)', output)
            if url_match:
                return {
                    "success": True,
                    "sso_required": True,
                    "sso_url": url_match.group(1),
                    "instructions": "Open URL in browser, complete login, copy token, then call complete_sso_login"
                }

        if "My Vault>" in output or self.session.is_authenticated():
            return {
                "success": True,
                "authenticated": True,
                "message": "Already authenticated"
            }

        return {
            "success": False,
            "output": output
        }

    def complete_sso_login(self, token: str) -> Dict[str, Any]:
        """Complete SSO login by pasting the token"""
        # Select paste option
        self.session.send_command("p", timeout=5)
        time.sleep(0.5)

        # Paste token
        output = self.session.send_command(token, timeout=15)

        if "My Vault>" in output or self.session.is_authenticated():
            return {
                "success": True,
                "authenticated": True,
                "message": "Successfully authenticated"
            }

        return {
            "success": False,
            "output": output
        }

    def get_tools(self) -> List[Dict]:
        """Return MCP tool definitions"""
        return [
            {
                "name": "keeper_start_session",
                "description": "Start Keeper Commander session (call first)",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "keeper_login",
                "description": "Initiate Keeper login (returns SSO URL if needed)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "default": "jeremy.smith@oberaconnect.com"}
                    }
                }
            },
            {
                "name": "keeper_sso_token",
                "description": "Complete SSO login with token from browser",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string", "description": "SSO token from browser"}
                    },
                    "required": ["token"]
                }
            },
            {
                "name": "keeper_list_folders",
                "description": "List folders and records in vault",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Folder path (empty for root)"}
                    }
                }
            },
            {
                "name": "keeper_list_records",
                "description": "List records in a specific folder",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "folder": {"type": "string", "description": "Folder name"}
                    },
                    "required": ["folder"]
                }
            },
            {
                "name": "keeper_get_record",
                "description": "Get record details (passwords masked)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "string", "description": "Record title or UID"}
                    },
                    "required": ["record"]
                }
            },
            {
                "name": "keeper_search",
                "description": "Search for records",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "keeper_create_record",
                "description": "Create a new record",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "folder": {"type": "string"},
                        "title": {"type": "string"},
                        "notes": {"type": "string"}
                    },
                    "required": ["folder", "title"]
                }
            },
            {
                "name": "keeper_upload_attachment",
                "description": "Upload file to a record",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "record": {"type": "string", "description": "Record title or UID"},
                        "file_path": {"type": "string", "description": "Full path to file"}
                    },
                    "required": ["record", "file_path"]
                }
            },
            {
                "name": "keeper_raw_command",
                "description": "Execute raw keeper command",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"}
                    },
                    "required": ["command"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Execute a tool and return results"""

        # Session management tools
        if tool_name == "keeper_start_session":
            return self.start_session()

        if tool_name == "keeper_login":
            return self.login(arguments.get("email", "jeremy.smith@oberaconnect.com"))

        if tool_name == "keeper_sso_token":
            return self.complete_sso_login(arguments["token"])

        # Ensure session is started for other commands
        if not self._started:
            self.start_session()

        if not self.session.is_authenticated():
            return {
                "success": False,
                "error": "Not authenticated. Call keeper_login first."
            }

        try:
            if tool_name == "keeper_list_folders":
                path = arguments.get("path", "")
                if path:
                    output = self.session.send_command(f'ls "{path}"')
                else:
                    output = self.session.send_command("ls")

                # Parse output
                folders = []
                records = []
                for line in output.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if line.endswith('/'):
                        folders.append(line.rstrip('/'))
                    else:
                        records.append(line)

                return {
                    "success": True,
                    "folders": folders,
                    "records": records,
                    "raw": output
                }

            elif tool_name == "keeper_list_records":
                folder = arguments["folder"]
                output = self.session.send_command(f'cd "{folder}"')
                output = self.session.send_command("ls")

                records = [l.strip() for l in output.split('\n') if l.strip() and not l.strip().endswith('/')]

                return {
                    "success": True,
                    "folder": folder,
                    "records": records,
                    "count": len(records)
                }

            elif tool_name == "keeper_get_record":
                record = arguments["record"]
                output = self.session.send_command(f'get "{record}"')

                return {
                    "success": True,
                    "record": output
                }

            elif tool_name == "keeper_search":
                query = arguments["query"]
                output = self.session.send_command(f'search "{query}"')

                return {
                    "success": True,
                    "query": query,
                    "results": output
                }

            elif tool_name == "keeper_create_record":
                folder = arguments["folder"]
                title = arguments["title"]
                notes = arguments.get("notes", "")

                # Navigate to folder
                self.session.send_command(f'cd "{folder}"')

                # Create record
                cmd = f'add-record --title "{title}"'
                if notes:
                    notes_escaped = notes.replace('"', '\\"')
                    cmd += f' --notes "{notes_escaped}"'

                output = self.session.send_command(cmd)

                return {
                    "success": "created" in output.lower() or "added" in output.lower(),
                    "message": f"Record '{title}' created in '{folder}'",
                    "output": output
                }

            elif tool_name == "keeper_upload_attachment":
                record = arguments["record"]
                file_path = arguments["file_path"]

                if not Path(file_path).exists():
                    return {"success": False, "error": f"File not found: {file_path}"}

                output = self.session.send_command(
                    f'upload-attachment "{record}" --file "{file_path}"',
                    timeout=120
                )

                return {
                    "success": True,
                    "message": f"File uploaded to '{record}'",
                    "output": output
                }

            elif tool_name == "keeper_raw_command":
                output = self.session.send_command(arguments["command"])
                return {
                    "success": True,
                    "output": output
                }

            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()


# Global server instance for MCP
_server_instance = None

def get_server() -> KeeperMCPServer:
    """Get or create the global server instance"""
    global _server_instance
    if _server_instance is None:
        _server_instance = KeeperMCPServer()
    return _server_instance

def create_server() -> KeeperMCPServer:
    """Create and return a new MCP server instance"""
    return KeeperMCPServer()


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Keeper MCP Server (Session-Based)")
    print("=" * 60)

    server = create_server()

    print(f"\nAvailable tools: {len(server.get_tools())}")
    for tool in server.get_tools():
        print(f"  - {tool['name']}: {tool['description']}")

    print("\n" + "=" * 60)
    print("Starting Keeper session...")
    print("=" * 60)

    result = server.start_session()
    print(f"Session: {result}")

    if not server.session.is_authenticated():
        print("\nNot authenticated. Initiating login...")
        result = server.login()
        print(f"Login result: {result}")

        if result.get("sso_required"):
            print(f"\nSSO URL: {result['sso_url']}")
            print("\n1. Open the URL above in your browser")
            print("2. Complete the SSO login")
            print("3. Copy the token")
            print("4. Paste it below:\n")

            token = input("SSO Token: ").strip()
            if token:
                result = server.complete_sso_login(token)
                print(f"SSO Result: {result}")

    if server.session.is_authenticated():
        print("\n" + "=" * 60)
        print("Testing commands...")
        print("=" * 60)

        # Test ls
        result = server.execute_tool("keeper_list_folders", {})
        print(f"\nFolders: {result.get('folders', [])}")
        print(f"Records at root: {len(result.get('records', []))}")

        # Test Firewalls folder
        result = server.execute_tool("keeper_list_records", {"folder": "Firewalls"})
        print(f"\nFirewalls folder: {result.get('count', 0)} records")

    print("\nClosing session...")
    server.close()
    print("Done.")
