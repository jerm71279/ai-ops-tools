"""
Layer 2: Intelligence Layer - Main Implementation
Handles task classification, intent parsing, and agent routing
"""

import time
from typing import Any, Callable, Dict, List, Optional

from ..core.base import AIRequest, AIResponse, LayerInterface, TaskStatus
from ..core.config import AIConfig
from ..core.logging import get_logger
from ..core.exceptions import IntelligenceLayerError, RoutingError


class IntelligenceLayer(LayerInterface):
    """
    Layer 2: Intelligence Layer

    Responsibilities:
    - Parse user intent from natural language
    - Classify tasks by domain and complexity
    - Maintain conversation/session context
    - Route to optimal agent(s) via MoE
    """

    def __init__(self, config: AIConfig = None):
        super().__init__("intelligence", config.intelligence if config else {})
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.layer2")

        # Next layer callback (set by AI OS)
        self._next_layer: Optional[Callable] = None

        # Components
        self._router: Optional['TaskRouter'] = None
        self._classifier: Optional['TaskClassifier'] = None
        self._context_manager: Optional['ContextManager'] = None

        # Agent registry
        self._agents: Dict[str, Dict] = {}

        # Classification cache
        self._classification_cache: Dict[str, Dict] = {}
        self._cache_ttl = 300  # 5 minutes

    async def initialize(self) -> bool:
        """Initialize the intelligence layer"""
        self.logger.info("Initializing Intelligence Layer...")

        # Initialize components
        from .router import TaskRouter
        from .classifier import TaskClassifier
        from .context import ContextManager

        self._router = TaskRouter(self.config)
        self._classifier = TaskClassifier(self.config, use_ml=True)
        self._context_manager = ContextManager(self.config)

        # Initialize ML classifier (optional, won't fail if unavailable)
        try:
            ml_ready = await self._classifier.initialize_ml()
            if ml_ready:
                self.logger.info("ML-based intent classification enabled")
        except Exception as e:
            self.logger.debug(f"ML classification not available: {e}")

        # Register default agents
        self._register_default_agents()

        self._initialized = True
        self._healthy = True
        self.logger.info("Intelligence Layer initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the intelligence layer"""
        self.logger.info("Shutting down Intelligence Layer...")
        self._initialized = False
        return True

    def set_next_layer(self, callback: Callable):
        """Set the callback to the next layer (Layer 3: Orchestration)"""
        self._next_layer = callback

    def register_agent(self, agent_id: str, agent_config: Dict):
        """Register an agent for routing"""
        self._agents[agent_id] = agent_config
        self.logger.info(f"Registered agent: {agent_id}")

    def _register_default_agents(self):
        """Register default agent configurations"""
        default_agents = {
            "claude": {
                "name": "Claude",
                "capabilities": ["code", "config", "reasoning", "analysis", "writing"],
                "strengths": ["programming", "system configuration", "technical writing"],
                "priority": 1
            },
            "gemini": {
                "name": "Gemini",
                "capabilities": ["large_docs", "video", "audio", "multimodal", "research"],
                "strengths": ["document analysis", "multimedia processing", "web research"],
                "priority": 2
            },
            "fara": {
                "name": "Fara",
                "capabilities": ["web_ui", "portal", "scraping", "automation", "browser"],
                "strengths": ["web automation", "portal interaction", "data extraction"],
                "priority": 3
            },
            "obsidian": {
                "name": "Obsidian Manager",
                "capabilities": ["knowledge", "notes", "search", "organization"],
                "strengths": ["knowledge management", "note organization", "search"],
                "priority": 4
            },
            "ba": {
                "name": "Business Analyst",
                "capabilities": ["analytics", "reporting", "quotes", "metrics"],
                "strengths": ["business analytics", "report generation", "project metrics"],
                "priority": 5
            }
        }

        for agent_id, config in default_agents.items():
            self.register_agent(agent_id, config)

    async def process(self, request: AIRequest) -> AIResponse:
        """
        Process a request through the intelligence layer

        Steps:
        1. Parse intent
        2. Classify task
        3. Enrich with context
        4. Route to best agent(s)
        5. Forward to orchestration layer
        """
        start_time = time.time()
        self.logger.layer_start("L2:Intelligence", request.request_id, request.content[:50])

        try:
            # Step 1: Parse intent
            intent = self._parse_intent(request)
            self.logger.debug(f"Intent: {intent}")

            # Step 2: Classify task
            classification = await self._classify_task(request, intent)
            request.classification = classification
            self.logger.debug(f"Classification: {classification}")

            # Step 3: Enrich with context
            if self._context_manager:
                context = self._context_manager.get_context(request.session_id)
                request.context.update(context)

            # Step 4: Route to best agent(s)
            routing = self._route_request(request, classification)
            request.target_agent = routing.get("primary_agent")
            self.logger.info(f"Routed to: {routing.get('primary_agent')} (confidence: {routing.get('confidence', 0):.2f})")

            # Step 5: Forward to orchestration layer
            if self._next_layer:
                response = await self._next_layer(request)
            else:
                # If no orchestration layer, return routing info
                response = AIResponse(
                    request_id=request.request_id,
                    success=True,
                    content={
                        "intent": intent,
                        "classification": classification,
                        "routing": routing
                    },
                    executed_by="L2:Intelligence"
                )

            # Update context with this interaction
            if self._context_manager and request.session_id:
                self._context_manager.add_interaction(
                    request.session_id,
                    request.content,
                    response.content
                )

            # Add layer trace
            response.layer_trace.insert(0, "L2:Intelligence")

            duration_ms = (time.time() - start_time) * 1000
            self._update_stats(response.success, duration_ms)
            self.logger.layer_end("L2:Intelligence", request.request_id, response.success, duration_ms)

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._update_stats(False, duration_ms)
            self.logger.error(f"Intelligence Layer error: {e}")

            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="L2:Intelligence"
            )

    def _parse_intent(self, request: AIRequest) -> Dict[str, Any]:
        """
        Parse user intent from request

        Returns structured intent information
        """
        content = request.content.lower()

        # Determine action type
        action = "query"  # default
        if any(w in content for w in ["create", "generate", "write", "build", "make"]):
            action = "create"
        elif any(w in content for w in ["analyze", "review", "check", "examine"]):
            action = "analyze"
        elif any(w in content for w in ["configure", "setup", "install", "deploy"]):
            action = "configure"
        elif any(w in content for w in ["search", "find", "look for", "locate"]):
            action = "search"
        elif any(w in content for w in ["fix", "repair", "resolve", "troubleshoot"]):
            action = "troubleshoot"
        elif any(w in content for w in ["automate", "schedule", "run"]):
            action = "automate"

        # Determine domain
        domain = "general"
        if any(w in content for w in ["code", "script", "function", "program", "python", "javascript"]):
            domain = "code"
        elif any(w in content for w in ["network", "firewall", "router", "sonicwall", "mikrotik", "unifi"]):
            domain = "network"
        elif any(w in content for w in ["azure", "microsoft", "m365", "sharepoint", "teams"]):
            domain = "cloud"
        elif any(w in content for w in ["document", "pdf", "report", "sop"]):
            domain = "document"
        elif any(w in content for w in ["portal", "website", "browser", "web"]):
            domain = "web"
        elif any(w in content for w in ["knowledge", "note", "obsidian", "search"]):
            domain = "knowledge"
        elif any(w in content for w in ["project", "task", "ticket", "report", "metrics"]):
            domain = "business"

        # Determine complexity
        complexity = "simple"
        word_count = len(content.split())
        if word_count > 50 or any(w in content for w in ["complex", "detailed", "comprehensive"]):
            complexity = "complex"
        elif word_count > 20 or any(w in content for w in ["multiple", "several", "workflow"]):
            complexity = "moderate"

        return {
            "action": action,
            "domain": domain,
            "complexity": complexity,
            "requires_context": any(w in content for w in ["this", "that", "previous", "last"]),
            "is_question": content.strip().endswith("?") or content.startswith(("what", "how", "why", "when", "where", "who"))
        }

    async def _classify_task(self, request: AIRequest, intent: Dict) -> Dict[str, Any]:
        """
        Classify the task for routing

        Returns classification with confidence scores
        """
        # Check cache
        cache_key = f"{request.content[:100]}_{intent['domain']}"
        if cache_key in self._classification_cache:
            cached = self._classification_cache[cache_key]
            if time.time() - cached.get("timestamp", 0) < self._cache_ttl:
                return cached.get("classification", {})

        if self._classifier:
            classification = await self._classifier.classify(request.content, intent)
        else:
            # Fallback classification
            classification = {
                "primary_category": intent["domain"],
                "sub_category": intent["action"],
                "complexity": intent["complexity"],
                "confidence": 0.7,
                "suggested_agents": self._get_suggested_agents(intent)
            }

        # Cache result
        self._classification_cache[cache_key] = {
            "classification": classification,
            "timestamp": time.time()
        }

        return classification

    def _get_suggested_agents(self, intent: Dict) -> List[str]:
        """Get suggested agents based on intent"""
        domain = intent.get("domain", "general")
        action = intent.get("action", "query")

        # Domain to agent mapping
        domain_agents = {
            "code": ["claude"],
            "network": ["claude", "fara"],
            "cloud": ["claude", "fara"],
            "document": ["gemini", "claude"],
            "web": ["fara", "gemini"],
            "knowledge": ["obsidian", "claude"],
            "business": ["ba", "claude"],
            "general": ["claude"]
        }

        # Action to agent mapping
        action_agents = {
            "create": ["claude"],
            "analyze": ["gemini", "claude"],
            "configure": ["claude"],
            "search": ["obsidian", "gemini"],
            "troubleshoot": ["claude"],
            "automate": ["fara", "claude"]
        }

        # Combine suggestions
        suggested = set(domain_agents.get(domain, ["claude"]))
        suggested.update(action_agents.get(action, []))

        return list(suggested)

    def _route_request(self, request: AIRequest, classification: Dict) -> Dict[str, Any]:
        """
        Route request to optimal agent(s)

        Uses MoE-style routing based on classification
        """
        if self._router:
            return self._router.route(request, classification, self._agents)

        # Fallback routing
        suggested = classification.get("suggested_agents", ["claude"])
        primary = suggested[0] if suggested else "claude"

        return {
            "primary_agent": primary,
            "secondary_agents": suggested[1:] if len(suggested) > 1 else [],
            "confidence": classification.get("confidence", 0.7),
            "routing_reason": f"Domain: {classification.get('primary_category')}, Action: {classification.get('sub_category')}"
        }

    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get information about a registered agent"""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return [
            {"id": agent_id, **config}
            for agent_id, config in self._agents.items()
        ]
