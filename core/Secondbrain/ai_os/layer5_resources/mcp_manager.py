"""
Layer 5: MCP Server Manager
Manages Model Context Protocol server connections
Integrates with existing Secondbrain MCP servers
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent path for Secondbrain imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..core.config import AIConfig
from ..core.logging import get_logger


class MCPManager:
    """
    MCP Server Manager

    Manages connections to MCP servers:
    - Obsidian (mcp_obsidian_server.py)
    - SharePoint (mcp_sharepoint_server.py)
    - Keeper (mcp_keeper_server.py)
    - NotebookLM (mcp_notebooklm_server.py)
    - Custom servers
    """

    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.mcp")

        # Server instances (actual MCP server objects)
        self._servers: Dict[str, Any] = {}
        self._server_status: Dict[str, Dict] = {}

    async def initialize(self) -> bool:
        """Initialize MCP servers"""
        self.logger.info("Initializing MCP Manager...")

        mcp_config = self.config.resources.get("mcp_servers", {})

        # Always try to initialize Secondbrain servers
        await self._init_secondbrain_servers(mcp_config)

        # Initialize any additional configured servers
        for server_name, server_config in mcp_config.items():
            if server_name not in self._server_status and server_config.get("enabled", False):
                try:
                    await self._init_server(server_name, server_config)
                except Exception as e:
                    self.logger.warning(f"Failed to init MCP server {server_name}: {e}")
                    self._server_status[server_name] = {"available": False, "error": str(e)}

        available_count = sum(1 for s in self._server_status.values() if s.get("available"))
        self.logger.info(f"MCP Manager initialized with {available_count} servers available")
        return True

    async def _init_secondbrain_servers(self, mcp_config: Dict):
        """Initialize Secondbrain MCP servers"""

        # Initialize Obsidian MCP Server
        try:
            from mcp_obsidian_server import ObsidianMCPServer
            obsidian_server = ObsidianMCPServer()
            self._servers["obsidian"] = obsidian_server
            self._server_status["obsidian"] = {
                "available": True,
                "server_class": "ObsidianMCPServer",
                "tools": [t["name"] for t in obsidian_server.get_tools()]
            }
            self.logger.info("Obsidian MCP server initialized (Secondbrain integration)")
        except ImportError as e:
            self.logger.warning(f"Obsidian MCP server not available: {e}")
            self._server_status["obsidian"] = {"available": False, "error": str(e)}

        # Initialize SharePoint MCP Server
        try:
            from mcp_sharepoint_server import SharePointMCPServer
            sharepoint_server = SharePointMCPServer()
            self._servers["sharepoint"] = sharepoint_server
            self._server_status["sharepoint"] = {
                "available": True,
                "server_class": "SharePointMCPServer",
                "tools": self._get_server_tools("sharepoint")
            }
            self.logger.info("SharePoint MCP server initialized (Secondbrain integration)")
        except ImportError as e:
            self.logger.warning(f"SharePoint MCP server not available: {e}")
            self._server_status["sharepoint"] = {"available": False, "error": str(e)}

        # Initialize Keeper MCP Server
        try:
            from mcp_keeper_server import KeeperMCPServer
            keeper_server = KeeperMCPServer()
            self._servers["keeper"] = keeper_server
            self._server_status["keeper"] = {
                "available": True,
                "server_class": "KeeperMCPServer",
                "tools": self._get_server_tools("keeper")
            }
            self.logger.info("Keeper MCP server initialized (Secondbrain integration)")
        except ImportError as e:
            self.logger.warning(f"Keeper MCP server not available: {e}")
            self._server_status["keeper"] = {"available": False, "error": str(e)}

        # Initialize NotebookLM MCP Server
        try:
            from mcp_notebooklm_server import NotebookLMMCPServer
            notebooklm_server = NotebookLMMCPServer()
            self._servers["notebooklm"] = notebooklm_server
            self._server_status["notebooklm"] = {
                "available": True,
                "server_class": "NotebookLMMCPServer",
                "tools": self._get_server_tools("notebooklm")
            }
            self.logger.info("NotebookLM MCP server initialized (Secondbrain integration)")
        except ImportError as e:
            self.logger.warning(f"NotebookLM MCP server not available: {e}")
            self._server_status["notebooklm"] = {"available": False, "error": str(e)}

    async def shutdown(self) -> bool:
        """Shutdown all MCP servers"""
        self.logger.info("Shutting down MCP Manager...")

        for server_name in list(self._servers.keys()):
            try:
                await self._shutdown_server(server_name)
            except Exception as e:
                self.logger.error(f"Error shutting down {server_name}: {e}")

        return True

    async def _init_server(self, name: str, config: Dict):
        """Initialize a specific MCP server (for custom servers)"""
        self.logger.info(f"Initializing MCP server: {name}")

        # For non-Secondbrain servers, create stub status
        self._server_status[name] = {
            "available": True,
            "config": config,
            "tools": self._get_server_tools(name)
        }

        self.logger.info(f"MCP server {name} initialized")

    async def _shutdown_server(self, name: str):
        """Shutdown a specific MCP server"""
        if name in self._servers:
            del self._servers[name]
        if name in self._server_status:
            self._server_status[name]["available"] = False

    def _get_server_tools(self, name: str) -> List[str]:
        """Get available tools for a server"""
        # Define tools for each known server type
        server_tools = {
            "obsidian": [
                "create_note",
                "read_note",
                "search_notes",
                "list_notes",
                "update_note",
                "delete_note",
                "get_tags",
                "get_links"
            ],
            "sharepoint": [
                "list_sites",
                "list_files",
                "read_file",
                "upload_file",
                "search"
            ],
            "keeper": [
                "get_secret",
                "list_secrets",
                "search_secrets"
            ],
            "notebooklm": [
                "create_notebook",
                "add_source",
                "query",
                "summarize"
            ]
        }
        return server_tools.get(name, [])

    async def call_tool(self, server: str, tool: str, args: Dict) -> Dict:
        """
        Call a tool on an MCP server

        Args:
            server: Server name
            tool: Tool name
            args: Tool arguments

        Returns:
            Tool execution result
        """
        status = self._server_status.get(server)

        if not status or not status.get("available"):
            return {
                "success": False,
                "error": f"MCP server '{server}' not available"
            }

        available_tools = status.get("tools", [])
        if tool not in available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool}' not available on server '{server}'"
            }

        self.logger.info(f"MCP call: {server}.{tool}({args})")

        # Use actual MCP server instance if available
        server_instance = self._servers.get(server)
        if server_instance:
            try:
                # Check for execute_tool method (Secondbrain pattern)
                if hasattr(server_instance, 'execute_tool'):
                    result = server_instance.execute_tool(tool, args)
                    return {
                        "success": True,
                        "content": result,
                        "server": server,
                        "tool": tool
                    }
                # Check for direct method call (alternative pattern)
                elif hasattr(server_instance, tool):
                    method = getattr(server_instance, tool)
                    result = await method(**args) if asyncio.iscoroutinefunction(method) else method(**args)
                    return {
                        "success": True,
                        "content": result,
                        "server": server,
                        "tool": tool
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Tool '{tool}' implementation not found on server '{server}'"
                    }
            except Exception as e:
                self.logger.error(f"MCP tool execution error: {server}.{tool}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "server": server,
                    "tool": tool
                }

        # Fallback for servers without instances (stub behavior)
        return {
            "success": True,
            "content": f"[MCP Stub] Called {server}.{tool} with args: {args}",
            "server": server,
            "tool": tool
        }

    def list_servers(self) -> List[str]:
        """List available servers"""
        return [
            name for name, status in self._server_status.items()
            if status.get("available")
        ]

    def get_server_status(self, server: str) -> Optional[Dict]:
        """Get status of a specific server"""
        return self._server_status.get(server)

    def get_server_tools(self, server: str) -> List[str]:
        """Get available tools for a server"""
        status = self._server_status.get(server)
        return status.get("tools", []) if status else []
