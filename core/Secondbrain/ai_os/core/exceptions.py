"""
AI Operating System - Exception Classes
"""

from typing import Any, Dict, Optional


class AIError(Exception):
    """Base exception for all AI OS errors"""

    def __init__(
        self,
        message: str,
        code: str = "AI_ERROR",
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.recoverable = recoverable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable
        }


class LayerError(AIError):
    """Error in a specific layer"""

    def __init__(
        self,
        layer: str,
        message: str,
        code: str = "LAYER_ERROR",
        details: Optional[Dict] = None,
        recoverable: bool = True
    ):
        super().__init__(message, code, details, recoverable)
        self.layer = layer
        self.details["layer"] = layer


class InterfaceLayerError(LayerError):
    """Layer 1: Interface errors"""

    def __init__(self, message: str, code: str = "INTERFACE_ERROR", **kwargs):
        super().__init__("interface", message, code, **kwargs)


class IntelligenceLayerError(LayerError):
    """Layer 2: Intelligence errors"""

    def __init__(self, message: str, code: str = "INTELLIGENCE_ERROR", **kwargs):
        super().__init__("intelligence", message, code, **kwargs)


class OrchestrationError(LayerError):
    """Layer 3: Orchestration errors"""

    def __init__(self, message: str, code: str = "ORCHESTRATION_ERROR", **kwargs):
        super().__init__("orchestration", message, code, **kwargs)


class PipelineError(OrchestrationError):
    """Pipeline execution error"""

    def __init__(
        self,
        message: str,
        pipeline_name: str,
        step_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, code="PIPELINE_ERROR", **kwargs)
        self.pipeline_name = pipeline_name
        self.step_name = step_name
        self.details["pipeline"] = pipeline_name
        if step_name:
            self.details["step"] = step_name


class AgentError(LayerError):
    """Layer 4: Agent errors"""

    def __init__(
        self,
        agent_name: str,
        message: str,
        code: str = "AGENT_ERROR",
        **kwargs
    ):
        super().__init__("agents", message, code, **kwargs)
        self.agent_name = agent_name
        self.details["agent"] = agent_name


class AgentUnavailableError(AgentError):
    """Agent is not available or not configured"""

    def __init__(self, agent_name: str, reason: str = ""):
        message = f"Agent '{agent_name}' is unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(agent_name, message, code="AGENT_UNAVAILABLE", recoverable=False)


class AgentTimeoutError(AgentError):
    """Agent execution timed out"""

    def __init__(self, agent_name: str, timeout: int):
        super().__init__(
            agent_name,
            f"Agent '{agent_name}' timed out after {timeout}s",
            code="AGENT_TIMEOUT"
        )
        self.timeout = timeout
        self.details["timeout"] = timeout


class ResourceError(LayerError):
    """Layer 5: Resource errors"""

    def __init__(
        self,
        resource_name: str,
        message: str,
        code: str = "RESOURCE_ERROR",
        **kwargs
    ):
        super().__init__("resources", message, code, **kwargs)
        self.resource_name = resource_name
        self.details["resource"] = resource_name


class MCPServerError(ResourceError):
    """MCP Server error"""

    def __init__(self, server_name: str, message: str, **kwargs):
        super().__init__(
            f"mcp_{server_name}",
            f"MCP Server '{server_name}' error: {message}",
            code="MCP_ERROR",
            **kwargs
        )


class DataStoreError(ResourceError):
    """Data store error"""

    def __init__(self, store_type: str, message: str, **kwargs):
        super().__init__(
            store_type,
            f"Data store '{store_type}' error: {message}",
            code="DATA_STORE_ERROR",
            **kwargs
        )


class RoutingError(IntelligenceLayerError):
    """MoE routing error"""

    def __init__(self, message: str, task: str = "", **kwargs):
        super().__init__(message, code="ROUTING_ERROR", **kwargs)
        if task:
            self.details["task"] = task[:100]


class ValidationError(InterfaceLayerError):
    """Request validation error"""

    def __init__(self, message: str, field: str = "", **kwargs):
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class AuthenticationError(InterfaceLayerError):
    """Authentication error"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, code="AUTH_ERROR", recoverable=False, **kwargs)


class RateLimitError(InterfaceLayerError):
    """Rate limit exceeded"""

    def __init__(self, retry_after: int = 60, **kwargs):
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s",
            code="RATE_LIMIT",
            **kwargs
        )
        self.retry_after = retry_after
        self.details["retry_after"] = retry_after
