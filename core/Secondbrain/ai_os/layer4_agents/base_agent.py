"""
Layer 4: Base Agent
Abstract base class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..core.base import AIRequest, AIResponse


class BaseAgent(ABC):
    """
    Abstract base class for AI agents

    All agents must implement:
    - initialize(): Setup agent (load models, connect to services)
    - execute(): Process a request
    - shutdown(): Cleanup resources

    Optional overrides:
    - health_check(): Check agent health
    - get_capabilities(): Return agent capabilities
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._initialized = False
        self._healthy = True

        # Agent metadata
        self.name: str = "BaseAgent"
        self.description: str = ""
        self.capabilities: List[str] = []
        self.strengths: List[str] = []

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    async def execute(self, request: AIRequest) -> AIResponse:
        """
        Execute a request

        Args:
            request: The AI request to process

        Returns:
            AIResponse with results
        """
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Shutdown and cleanup agent resources

        Returns:
            True if shutdown successful
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """Check agent health status"""
        return {
            "agent": self.name,
            "initialized": self._initialized,
            "healthy": self._healthy
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "strengths": self.strengths
        }

    def can_handle(self, request: AIRequest) -> bool:
        """
        Check if this agent can handle a request

        Override to implement custom logic
        """
        return True

    def _build_prompt(self, request: AIRequest) -> str:
        """Build prompt from request"""
        prompt = request.content

        # Add context if available
        if request.context:
            context_str = "\n".join(
                f"{k}: {v}" for k, v in request.context.items()
                if isinstance(v, (str, int, float, bool))
            )
            if context_str:
                prompt = f"Context:\n{context_str}\n\nRequest: {prompt}"

        return prompt
