"""
Layer 5: Resource Layer - Main Implementation
Manages data stores, MCP servers, and external integrations
"""

import time
from typing import Any, Callable, Dict, List, Optional

from ..core.base import AIRequest, AIResponse, LayerInterface, TaskStatus
from ..core.config import AIConfig
from ..core.logging import get_logger
from ..core.exceptions import ResourceError


class ResourceLayer(LayerInterface):
    """
    Layer 5: Resource Layer

    Responsibilities:
    - Manage MCP server connections
    - Provide data storage abstraction
    - Handle external service integrations
    - Manage credentials and connections
    """

    def __init__(self, config: AIConfig = None):
        super().__init__("resources", config.resources if config else {})
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.layer5")

        # MCP servers
        self._mcp_manager: Optional['MCPManager'] = None

        # Data store
        self._data_store: Optional['DataStore'] = None

        # External services
        self._external_services: Dict[str, Any] = {}

    async def initialize(self) -> bool:
        """Initialize the resource layer"""
        self.logger.info("Initializing Resource Layer...")

        # Initialize MCP manager
        from .mcp_manager import MCPManager
        self._mcp_manager = MCPManager(self.config)
        await self._mcp_manager.initialize()

        # Initialize data store
        from .data_store import DataStore
        self._data_store = DataStore(self.config)
        await self._data_store.initialize()

        self._initialized = True
        self._healthy = True
        self.logger.info("Resource Layer initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the resource layer"""
        self.logger.info("Shutting down Resource Layer...")

        if self._mcp_manager:
            await self._mcp_manager.shutdown()

        if self._data_store:
            await self._data_store.shutdown()

        self._initialized = False
        return True

    async def process(self, request: AIRequest) -> AIResponse:
        """
        Process a resource request

        This layer typically doesn't process requests directly,
        but provides services to other layers.
        """
        start_time = time.time()

        try:
            # Handle resource-specific operations
            operation = request.context.get("resource_operation")

            if operation == "store":
                result = await self._handle_store(request)
            elif operation == "retrieve":
                result = await self._handle_retrieve(request)
            elif operation == "mcp_call":
                result = await self._handle_mcp_call(request)
            else:
                result = {
                    "success": True,
                    "content": "Resource layer active",
                    "services": self.get_status()
                }

            duration_ms = (time.time() - start_time) * 1000

            return AIResponse(
                request_id=request.request_id,
                success=result.get("success", True),
                content=result.get("content"),
                error=result.get("error"),
                status=TaskStatus.SUCCESS if result.get("success") else TaskStatus.FAILED,
                duration_ms=duration_ms,
                executed_by="L5:Resources",
                layer_trace=["L5:Resources"]
            )

        except Exception as e:
            self.logger.error(f"Resource Layer error: {e}")
            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="L5:Resources"
            )

    async def _handle_store(self, request: AIRequest) -> Dict:
        """Handle data storage request"""
        if self._data_store:
            key = request.context.get("key", request.request_id)
            data = request.context.get("data", request.content)
            await self._data_store.store(key, data)
            return {"success": True, "content": f"Stored data with key: {key}"}
        return {"success": False, "error": "Data store not available"}

    async def _handle_retrieve(self, request: AIRequest) -> Dict:
        """Handle data retrieval request"""
        if self._data_store:
            key = request.context.get("key")
            if key:
                data = await self._data_store.retrieve(key)
                return {"success": True, "content": data}
            return {"success": False, "error": "Key not specified"}
        return {"success": False, "error": "Data store not available"}

    async def _handle_mcp_call(self, request: AIRequest) -> Dict:
        """Handle MCP server call"""
        if self._mcp_manager:
            server = request.context.get("mcp_server")
            tool = request.context.get("mcp_tool")
            args = request.context.get("mcp_args", {})

            if server and tool:
                result = await self._mcp_manager.call_tool(server, tool, args)
                return result
            return {"success": False, "error": "Server and tool must be specified"}
        return {"success": False, "error": "MCP manager not available"}

    def get_status(self) -> Dict[str, Any]:
        """Get resource layer status"""
        return {
            "mcp_servers": self._mcp_manager.list_servers() if self._mcp_manager else [],
            "data_store": self._data_store.get_status() if self._data_store else {},
            "external_services": list(self._external_services.keys())
        }

    # Convenience methods for other layers
    async def store_data(self, key: str, data: Any):
        """Store data (convenience method)"""
        if self._data_store:
            await self._data_store.store(key, data)

    async def retrieve_data(self, key: str) -> Any:
        """Retrieve data (convenience method)"""
        if self._data_store:
            return await self._data_store.retrieve(key)
        return None

    async def call_mcp_tool(self, server: str, tool: str, args: Dict = None) -> Dict:
        """Call MCP tool (convenience method)"""
        if self._mcp_manager:
            return await self._mcp_manager.call_tool(server, tool, args or {})
        return {"success": False, "error": "MCP manager not available"}
