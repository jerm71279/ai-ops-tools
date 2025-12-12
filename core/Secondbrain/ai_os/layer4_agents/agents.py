"""
Layer 4: Agent Layer - Main Implementation
Manages and coordinates specialized AI agents
"""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional

from ..core.base import AIRequest, AIResponse, LayerInterface, TaskStatus
from ..core.config import AIConfig
from ..core.logging import get_logger
from ..core.exceptions import AgentError, AgentUnavailableError, AgentTimeoutError


class AgentLayer(LayerInterface):
    """
    Layer 4: Agent Layer

    Responsibilities:
    - Manage pool of specialized AI agents
    - Execute tasks with appropriate agent
    - Handle agent lifecycle (init, execute, cleanup)
    - Provide unified interface over heterogeneous providers
    """

    def __init__(self, config: AIConfig = None):
        super().__init__("agents", config.agents if config else {})
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.layer4")

        # Next layer callback (Layer 5: Resources)
        self._next_layer: Optional[Callable] = None

        # Agent registry
        self._agents: Dict[str, 'BaseAgent'] = {}

        # Agent status
        self._agent_status: Dict[str, Dict] = {}

        # Execution stats
        self._execution_stats: Dict[str, Dict] = {}

    async def initialize(self) -> bool:
        """Initialize the agent layer"""
        self.logger.info("Initializing Agent Layer...")

        # Initialize configured agents
        await self._initialize_agents()

        self._initialized = True
        self._healthy = True
        self.logger.info("Agent Layer initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the agent layer"""
        self.logger.info("Shutting down Agent Layer...")

        # Shutdown all agents
        for agent_id, agent in self._agents.items():
            try:
                await agent.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down agent {agent_id}: {e}")

        self._initialized = False
        return True

    def set_next_layer(self, callback: Callable):
        """Set the callback to the next layer (Layer 5: Resources)"""
        self._next_layer = callback

    async def _initialize_agents(self):
        """Initialize all configured agents"""
        from .base_agent import BaseAgent
        from .claude_agent import ClaudeAgent
        from .gemini_agent import GeminiAgent
        from .secondbrain_agents import ObsidianManagerAgent, BAAgent, NotebookLMAgent

        agents_config = self.config.agents

        # Initialize Claude agent
        if agents_config.get("claude", {}).get("enabled", True):
            try:
                claude = ClaudeAgent(agents_config.get("claude", {}))
                await claude.initialize()
                self._agents["claude"] = claude
                self._agent_status["claude"] = {"available": True, "last_check": time.time()}
                self.logger.info("Claude agent initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Claude agent: {e}")
                self._agent_status["claude"] = {"available": False, "error": str(e)}

        # Initialize Gemini agent
        if agents_config.get("gemini", {}).get("enabled", True):
            try:
                gemini = GeminiAgent(agents_config.get("gemini", {}))
                await gemini.initialize()
                self._agents["gemini"] = gemini
                self._agent_status["gemini"] = {"available": True, "last_check": time.time()}
                self.logger.info("Gemini agent initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Gemini agent: {e}")
                self._agent_status["gemini"] = {"available": False, "error": str(e)}

        # Initialize Secondbrain Agents
        await self._initialize_secondbrain_agents(agents_config)

    async def _initialize_secondbrain_agents(self, agents_config: Dict):
        """Initialize Secondbrain integration agents"""
        from .secondbrain_agents import ObsidianManagerAgent, BAAgent, NotebookLMAgent

        # Initialize Obsidian Manager Agent
        if agents_config.get("obsidian", {}).get("enabled", True):
            try:
                obsidian = ObsidianManagerAgent(agents_config.get("obsidian", {}))
                await obsidian.initialize()
                self._agents["obsidian"] = obsidian
                self._agent_status["obsidian"] = {
                    "available": obsidian._healthy,
                    "last_check": time.time(),
                    "capabilities": obsidian.capabilities
                }
                self.logger.info(f"Obsidian Manager agent initialized (healthy: {obsidian._healthy})")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Obsidian agent: {e}")
                self._agent_status["obsidian"] = {"available": False, "error": str(e)}

        # Initialize Business Analyst Agent
        if agents_config.get("ba", {}).get("enabled", True):
            try:
                ba = BAAgent(agents_config.get("ba", {}))
                await ba.initialize()
                self._agents["ba"] = ba
                self._agent_status["ba"] = {
                    "available": ba._healthy,
                    "last_check": time.time(),
                    "capabilities": ba.capabilities
                }
                self.logger.info(f"Business Analyst agent initialized (healthy: {ba._healthy})")
            except Exception as e:
                self.logger.warning(f"Failed to initialize BA agent: {e}")
                self._agent_status["ba"] = {"available": False, "error": str(e)}

        # Initialize NotebookLM Analyst Agent
        if agents_config.get("notebooklm", {}).get("enabled", True):
            try:
                notebooklm = NotebookLMAgent(agents_config.get("notebooklm", {}))
                await notebooklm.initialize()
                self._agents["notebooklm"] = notebooklm
                self._agent_status["notebooklm"] = {
                    "available": notebooklm._healthy,
                    "last_check": time.time(),
                    "capabilities": notebooklm.capabilities
                }
                self.logger.info(f"NotebookLM Analyst agent initialized (healthy: {notebooklm._healthy})")
            except Exception as e:
                self.logger.warning(f"Failed to initialize NotebookLM agent: {e}")
                self._agent_status["notebooklm"] = {"available": False, "error": str(e)}

    def register_agent(self, agent_id: str, agent: 'BaseAgent'):
        """Register a custom agent"""
        self._agents[agent_id] = agent
        self._agent_status[agent_id] = {"available": True, "last_check": time.time()}
        self.logger.info(f"Registered agent: {agent_id}")

    async def process(self, request: AIRequest) -> AIResponse:
        """
        Process a request through the agent layer

        Steps:
        1. Select target agent
        2. Validate agent availability
        3. Execute with agent
        4. Handle response and stats
        """
        start_time = time.time()
        agent_id = request.target_agent or "claude"

        self.logger.layer_start("L4:Agents", request.request_id, f"Agent: {agent_id}")
        self.logger.agent_start(agent_id, request.request_id, request.content[:50])

        try:
            # Step 1: Validate agent
            if agent_id not in self._agents:
                # Try fallback to Claude
                if "claude" in self._agents:
                    self.logger.warning(f"Agent {agent_id} not available, falling back to Claude")
                    agent_id = "claude"
                else:
                    raise AgentUnavailableError(agent_id, "Agent not registered")

            agent = self._agents[agent_id]

            if not self._agent_status.get(agent_id, {}).get("available", False):
                raise AgentUnavailableError(agent_id, "Agent not available")

            # Step 2: Execute with timeout
            try:
                response = await asyncio.wait_for(
                    agent.execute(request),
                    timeout=request.timeout
                )
            except asyncio.TimeoutError:
                raise AgentTimeoutError(agent_id, request.timeout)

            # Step 3: Update stats
            self._update_execution_stats(agent_id, response.success, time.time() - start_time)

            # Add layer trace
            response.layer_trace.insert(0, f"L4:Agent:{agent_id}")
            response.executed_by = f"L4:Agent:{agent_id}"

            duration_ms = (time.time() - start_time) * 1000
            self._update_stats(response.success, duration_ms)

            self.logger.agent_end(agent_id, request.request_id, response.success, duration_ms)
            self.logger.layer_end("L4:Agents", request.request_id, response.success, duration_ms)

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._update_stats(False, duration_ms)
            self.logger.error(f"Agent Layer error: {e}")

            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by=f"L4:Agent:{agent_id}"
            )

    def _update_execution_stats(self, agent_id: str, success: bool, duration: float):
        """Update agent execution statistics"""
        if agent_id not in self._execution_stats:
            self._execution_stats[agent_id] = {
                "total": 0,
                "success": 0,
                "failed": 0,
                "total_duration": 0
            }

        stats = self._execution_stats[agent_id]
        stats["total"] += 1
        stats["total_duration"] += duration

        if success:
            stats["success"] += 1
        else:
            stats["failed"] += 1

    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        return {
            agent_id: {
                "available": status.get("available", False),
                "stats": self._execution_stats.get(agent_id, {}),
                **{k: v for k, v in status.items() if k != "available"}
            }
            for agent_id, status in self._agent_status.items()
        }

    def list_agents(self) -> List[str]:
        """List available agents"""
        return [
            agent_id for agent_id, status in self._agent_status.items()
            if status.get("available", False)
        ]
