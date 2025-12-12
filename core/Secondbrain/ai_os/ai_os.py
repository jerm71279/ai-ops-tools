"""
AI Operating System - Main Entry Point
Unified 5-Layer AI Operating System
"""

import asyncio
from typing import Any, Dict, Optional

from .core.base import AIRequest, AIResponse
from .core.config import AIConfig, load_config
from .core.logging import AILogger, get_logger, configure_logging

# Import all layers
from .layer1_interface import InterfaceLayer, CLIInterface
from .layer2_intelligence import IntelligenceLayer
from .layer3_orchestration import OrchestrationLayer
from .layer4_agents import AgentLayer
from .layer5_resources import ResourceLayer


class AIOS:
    """
    AI Operating System

    Unified entry point for the 5-layer AI architecture.

    Usage:
        # Create and initialize
        ai_os = AIOS()
        await ai_os.initialize()

        # Process request
        response = await ai_os.process("Generate a Python function to sort a list")

        # Or run interactive CLI
        await ai_os.run_cli()

        # Shutdown
        await ai_os.shutdown()
    """

    def __init__(self, config: AIConfig = None):
        self.config = config or load_config()
        self.logger = get_logger("ai_os")

        # Initialize layers (not started yet)
        self._layer1: Optional[InterfaceLayer] = None
        self._layer2: Optional[IntelligenceLayer] = None
        self._layer3: Optional[OrchestrationLayer] = None
        self._layer4: Optional[AgentLayer] = None
        self._layer5: Optional[ResourceLayer] = None

        # CLI interface
        self._cli: Optional[CLIInterface] = None

        # State
        self._initialized = False

    async def initialize(self) -> bool:
        """
        Initialize all layers of the AI OS

        Initializes layers from bottom (L5) to top (L1)
        """
        self.logger.info("=" * 60)
        self.logger.info("AI Operating System Initializing...")
        self.logger.info("=" * 60)

        try:
            # Configure logging
            configure_logging(
                level=self.config.logging.get("level", "INFO"),
                log_path=self.config.log_path if self.config.logging.get("file") else None,
                structured=self.config.logging.get("structured", False)
            )

            # Layer 5: Resources (bottom layer)
            self.logger.info("[L5] Initializing Resource Layer...")
            self._layer5 = ResourceLayer(self.config)
            await self._layer5.initialize()

            # Layer 4: Agents
            self.logger.info("[L4] Initializing Agent Layer...")
            self._layer4 = AgentLayer(self.config)
            self._layer4.set_next_layer(self._layer5.process)
            await self._layer4.initialize()

            # Layer 3: Orchestration
            self.logger.info("[L3] Initializing Orchestration Layer...")
            self._layer3 = OrchestrationLayer(self.config)
            self._layer3.set_next_layer(self._layer4.process)
            await self._layer3.initialize()

            # Layer 2: Intelligence
            self.logger.info("[L2] Initializing Intelligence Layer...")
            self._layer2 = IntelligenceLayer(self.config)
            self._layer2.set_next_layer(self._layer3.process)
            await self._layer2.initialize()

            # Layer 1: Interface (top layer)
            self.logger.info("[L1] Initializing Interface Layer...")
            self._layer1 = InterfaceLayer(self.config)
            self._layer1.set_next_layer(self._layer2.process)
            await self._layer1.initialize()

            # Initialize CLI
            self._cli = CLIInterface(
                prompt="ai-os> ",
                process_callback=self._layer1.process
            )

            self._initialized = True
            self.logger.info("=" * 60)
            self.logger.info("AI Operating System Ready")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            await self.shutdown()
            raise

    async def shutdown(self) -> bool:
        """
        Shutdown all layers of the AI OS

        Shuts down layers from top (L1) to bottom (L5)
        """
        self.logger.info("Shutting down AI Operating System...")

        # Shutdown in reverse order
        if self._layer1:
            await self._layer1.shutdown()
        if self._layer2:
            await self._layer2.shutdown()
        if self._layer3:
            await self._layer3.shutdown()
        if self._layer4:
            await self._layer4.shutdown()
        if self._layer5:
            await self._layer5.shutdown()

        self._initialized = False
        self.logger.info("AI Operating System shutdown complete")
        return True

    async def process(self, content: str, **kwargs) -> AIResponse:
        """
        Process a request through the AI OS

        Args:
            content: The request content/prompt
            **kwargs: Additional request parameters

        Returns:
            AIResponse with results
        """
        if not self._initialized:
            raise RuntimeError("AI OS not initialized. Call initialize() first.")

        # Create request
        request = AIRequest(
            content=content,
            source=kwargs.get("source", "api"),
            request_type=kwargs.get("request_type", "general"),
            context=kwargs.get("context", {}),
            target_agent=kwargs.get("target_agent"),
            target_workflow=kwargs.get("target_workflow"),
            timeout=kwargs.get("timeout", 300),
            session_id=kwargs.get("session_id")
        )

        # Process through Layer 1 (cascades through all layers)
        return await self._layer1.process(request)

    async def run_cli(self):
        """Run the interactive CLI"""
        if not self._initialized:
            await self.initialize()

        await self._cli.run()

    def run_once(self, content: str, **kwargs) -> AIResponse:
        """
        Run a single request (synchronous wrapper)

        Useful for scripts and non-async code
        """
        async def _run():
            if not self._initialized:
                await self.initialize()
            response = await self.process(content, **kwargs)
            return response

        return asyncio.run(_run())

    # Status and health
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "initialized": self._initialized,
            "layers": {
                "L1:Interface": self._layer1.health_check() if self._layer1 else None,
                "L2:Intelligence": self._layer2.health_check() if self._layer2 else None,
                "L3:Orchestration": self._layer3.health_check() if self._layer3 else None,
                "L4:Agents": self._layer4.health_check() if self._layer4 else None,
                "L5:Resources": self._layer5.health_check() if self._layer5 else None
            }
        }

    def get_agents(self) -> Dict[str, Any]:
        """Get available agents"""
        if self._layer4:
            return self._layer4.get_agent_status()
        return {}

    def get_workflows(self) -> list:
        """Get available workflows"""
        if self._layer3:
            return self._layer3.list_workflows()
        return []


# Convenience function for quick usage
def create_aios(config_path: str = None) -> AIOS:
    """Create an AI OS instance"""
    config = load_config(config_path) if config_path else AIConfig()
    return AIOS(config)


# Main entry point
async def main():
    """Main entry point for running AI OS"""
    ai_os = AIOS()

    try:
        await ai_os.initialize()
        await ai_os.run_cli()
    finally:
        await ai_os.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
