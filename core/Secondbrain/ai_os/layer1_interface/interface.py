"""
Layer 1: Interface Layer - Main Implementation
Handles all entry points to the AI Operating System
"""

import asyncio
import time
from typing import Any, Callable, Dict, Optional

from ..core.base import AIRequest, AIResponse, LayerInterface, TaskStatus
from ..core.config import AIConfig
from ..core.logging import get_logger
from ..core.exceptions import InterfaceLayerError, ValidationError


class InterfaceLayer(LayerInterface):
    """
    Layer 1: Interface Layer

    Responsibilities:
    - Parse and validate incoming requests
    - Route to appropriate handler (CLI, API, Webhook)
    - Manage authentication/authorization
    - Rate limiting
    - Request/response logging
    """

    def __init__(self, config: AIConfig = None):
        super().__init__("interface", config.interface if config else {})
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.layer1")

        # Next layer callback (set by AI OS)
        self._next_layer: Optional[Callable] = None

        # Request handlers
        self._handlers: Dict[str, Callable] = {}

        # Rate limiting
        self._rate_limits: Dict[str, list] = {}
        self._rate_window = 60  # seconds
        self._rate_max = 100  # requests per window

        # Request history for tracing
        self._request_history: list = []
        self._max_history = 1000

    async def initialize(self) -> bool:
        """Initialize the interface layer"""
        self.logger.info("Initializing Interface Layer...")

        # Register default handlers
        self._register_default_handlers()

        self._initialized = True
        self._healthy = True
        self.logger.info("Interface Layer initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the interface layer"""
        self.logger.info("Shutting down Interface Layer...")
        self._initialized = False
        return True

    def set_next_layer(self, callback: Callable):
        """Set the callback to the next layer (Layer 2: Intelligence)"""
        self._next_layer = callback

    def _register_default_handlers(self):
        """Register default request handlers"""
        self._handlers["general"] = self._handle_general
        self._handlers["query"] = self._handle_query
        self._handlers["command"] = self._handle_command
        self._handlers["workflow"] = self._handle_workflow
        self._handlers["status"] = self._handle_status

    async def process(self, request: AIRequest) -> AIResponse:
        """
        Process an incoming request

        Steps:
        1. Validate request
        2. Check rate limits
        3. Log request
        4. Route to handler or next layer
        5. Return response
        """
        start_time = time.time()
        self.logger.layer_start("L1:Interface", request.request_id, request.content[:50])

        try:
            # Step 1: Validate request
            self._validate_request(request)

            # Step 2: Check rate limits
            self._check_rate_limit(request.user_id or request.source)

            # Step 3: Log request
            self._log_request(request)

            # Step 4: Route to appropriate handler or next layer
            if request.request_type in self._handlers:
                response = await self._handlers[request.request_type](request)
            elif self._next_layer:
                response = await self._next_layer(request)
            else:
                raise InterfaceLayerError("No handler or next layer configured")

            # Add layer trace
            response.layer_trace.insert(0, "L1:Interface")

            duration_ms = (time.time() - start_time) * 1000
            response.duration_ms = duration_ms
            self._update_stats(response.success, duration_ms)

            self.logger.layer_end("L1:Interface", request.request_id, response.success, duration_ms)
            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._update_stats(False, duration_ms)
            self.logger.error(f"Interface Layer error: {e}")

            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="L1:Interface"
            )

    def _validate_request(self, request: AIRequest):
        """Validate incoming request"""
        if not request.content and not request.context:
            raise ValidationError("Request must have content or context", field="content")

        if request.timeout < 0:
            raise ValidationError("Timeout must be positive", field="timeout")

        if request.max_retries < 0:
            raise ValidationError("Max retries must be non-negative", field="max_retries")

    def _check_rate_limit(self, identifier: str):
        """Check and enforce rate limits"""
        now = time.time()

        # Initialize if needed
        if identifier not in self._rate_limits:
            self._rate_limits[identifier] = []

        # Remove old entries
        self._rate_limits[identifier] = [
            t for t in self._rate_limits[identifier]
            if now - t < self._rate_window
        ]

        # Check limit
        if len(self._rate_limits[identifier]) >= self._rate_max:
            from ..core.exceptions import RateLimitError
            raise RateLimitError(retry_after=self._rate_window)

        # Add current request
        self._rate_limits[identifier].append(now)

    def _log_request(self, request: AIRequest):
        """Log request for tracing"""
        entry = {
            "request_id": request.request_id,
            "timestamp": request.timestamp,
            "type": request.request_type,
            "source": request.source,
            "user_id": request.user_id
        }

        self._request_history.append(entry)

        # Trim history
        if len(self._request_history) > self._max_history:
            self._request_history = self._request_history[-self._max_history:]

    # ========================================================================
    # Request Handlers
    # ========================================================================

    async def _handle_general(self, request: AIRequest) -> AIResponse:
        """Handle general requests - forward to next layer"""
        if self._next_layer:
            return await self._next_layer(request)

        return AIResponse(
            request_id=request.request_id,
            success=True,
            content="General request received",
            executed_by="L1:Interface"
        )

    async def _handle_query(self, request: AIRequest) -> AIResponse:
        """Handle query requests"""
        if self._next_layer:
            return await self._next_layer(request)

        return AIResponse(
            request_id=request.request_id,
            success=True,
            content="Query request received",
            executed_by="L1:Interface"
        )

    async def _handle_command(self, request: AIRequest) -> AIResponse:
        """Handle command requests"""
        content = request.content.strip().lower()

        # Built-in commands
        if content == "status":
            return await self._handle_status(request)
        elif content == "help":
            return self._get_help_response(request)
        elif content == "history":
            return self._get_history_response(request)

        # Forward to next layer
        if self._next_layer:
            return await self._next_layer(request)

        return AIResponse(
            request_id=request.request_id,
            success=True,
            content="Command received",
            executed_by="L1:Interface"
        )

    async def _handle_workflow(self, request: AIRequest) -> AIResponse:
        """Handle workflow requests"""
        if self._next_layer:
            request.request_type = "workflow"
            return await self._next_layer(request)

        return AIResponse(
            request_id=request.request_id,
            success=True,
            content="Workflow request received",
            executed_by="L1:Interface"
        )

    async def _handle_status(self, request: AIRequest) -> AIResponse:
        """Handle status requests"""
        status = self.health_check()

        return AIResponse(
            request_id=request.request_id,
            success=True,
            content=status,
            executed_by="L1:Interface",
            artifacts={"health": status}
        )

    def _get_help_response(self, request: AIRequest) -> AIResponse:
        """Get help information"""
        help_text = """
AI Operating System - Help

Commands:
  status    - Show system status
  help      - Show this help message
  history   - Show recent requests

Request Types:
  general   - General AI requests
  query     - Query knowledge base
  command   - Execute system command
  workflow  - Run a workflow pipeline

For more information, see the documentation.
"""
        return AIResponse(
            request_id=request.request_id,
            success=True,
            content=help_text.strip(),
            executed_by="L1:Interface"
        )

    def _get_history_response(self, request: AIRequest) -> AIResponse:
        """Get request history"""
        recent = self._request_history[-10:]  # Last 10 requests

        return AIResponse(
            request_id=request.request_id,
            success=True,
            content=f"Recent requests: {len(recent)}",
            executed_by="L1:Interface",
            artifacts={"history": recent}
        )

    # ========================================================================
    # Convenience Methods
    # ========================================================================

    def create_request(
        self,
        content: str,
        request_type: str = "general",
        source: str = "cli",
        **kwargs
    ) -> AIRequest:
        """Create a new request with proper defaults"""
        return AIRequest(
            content=content,
            request_type=request_type,
            source=source,
            **kwargs
        )
