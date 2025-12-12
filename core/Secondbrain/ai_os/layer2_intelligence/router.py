"""
Layer 2: Task Router (MoE-style)
Routes tasks to optimal agents based on classification
"""

from typing import Any, Dict, List, Optional

from ..core.config import AIConfig
from ..core.base import AIRequest
from ..core.logging import get_logger


class TaskRouter:
    """
    Mixture of Experts (MoE) style router

    Selects the best agent(s) for a given task based on:
    - Task classification
    - Agent capabilities
    - Historical performance
    - Current agent availability
    """

    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.router")

        # Routing weights (learned over time)
        self._capability_weights: Dict[str, Dict[str, float]] = {}

        # Performance tracking
        self._agent_performance: Dict[str, Dict] = {}

    def route(
        self,
        request: AIRequest,
        classification: Dict,
        agents: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Route a request to the optimal agent(s)

        Args:
            request: The incoming request
            classification: Task classification from classifier
            agents: Available agents and their configurations

        Returns:
            Routing decision with primary and secondary agents
        """
        scores = {}

        for agent_id, agent_config in agents.items():
            score = self._calculate_agent_score(
                agent_id,
                agent_config,
                classification
            )
            scores[agent_id] = score

        # Sort by score
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_agents:
            return {
                "primary_agent": "claude",
                "secondary_agents": [],
                "confidence": 0.5,
                "routing_reason": "No agents available, defaulting to Claude"
            }

        primary_agent = sorted_agents[0][0]
        primary_score = sorted_agents[0][1]

        # Get secondary agents (those with score > 0.5 * primary)
        secondary_agents = [
            agent_id for agent_id, score in sorted_agents[1:]
            if score > 0.5 * primary_score
        ][:2]  # Max 2 secondary agents

        # Determine confidence
        confidence = min(1.0, primary_score)

        return {
            "primary_agent": primary_agent,
            "secondary_agents": secondary_agents,
            "confidence": confidence,
            "scores": dict(sorted_agents),
            "routing_reason": self._get_routing_reason(
                primary_agent,
                agents.get(primary_agent, {}),
                classification
            )
        }

    def _calculate_agent_score(
        self,
        agent_id: str,
        agent_config: Dict,
        classification: Dict
    ) -> float:
        """
        Calculate routing score for an agent

        Factors:
        - Capability match (0-1)
        - Domain expertise (0-1)
        - Complexity handling (0-1)
        - Historical performance (0-1)
        """
        score = 0.0

        # Get agent capabilities
        capabilities = set(agent_config.get("capabilities", []))
        strengths = set(agent_config.get("strengths", []))

        # Get classification info
        primary_category = classification.get("primary_category", "general")
        sub_category = classification.get("sub_category", "")
        complexity = classification.get("complexity", "simple")
        suggested = set(classification.get("suggested_agents", []))

        # Factor 1: Direct suggestion match (weight: 0.4)
        if agent_id in suggested:
            suggestion_score = 0.4
            # Higher score if first suggestion
            if suggested and list(suggested)[0] == agent_id:
                suggestion_score = 0.5
            score += suggestion_score

        # Factor 2: Capability match (weight: 0.3)
        capability_match = self._match_capabilities(
            capabilities,
            primary_category,
            sub_category
        )
        score += capability_match * 0.3

        # Factor 3: Strength match (weight: 0.2)
        strength_match = self._match_strengths(strengths, primary_category)
        score += strength_match * 0.2

        # Factor 4: Complexity handling (weight: 0.1)
        complexity_score = self._complexity_score(agent_id, complexity)
        score += complexity_score * 0.1

        # Apply historical performance modifier
        performance = self._agent_performance.get(agent_id, {})
        success_rate = performance.get("success_rate", 0.8)
        score *= (0.5 + success_rate * 0.5)  # Range 0.5-1.0

        return min(1.0, score)

    def _match_capabilities(
        self,
        capabilities: set,
        category: str,
        sub_category: str
    ) -> float:
        """Match capabilities to task category"""
        # Category to capability mapping (includes Secondbrain agents)
        category_capabilities = {
            "code": {"code", "reasoning", "analysis"},
            "network": {"config", "automation", "code"},
            "cloud": {"config", "automation", "code"},
            "document": {"large_docs", "analysis", "writing"},
            "web": {"web_ui", "portal", "scraping", "browser"},
            "knowledge": {"knowledge", "notes", "search", "organization", "tagging"},
            "business": {"analytics", "reporting", "metrics", "quotes", "project_health"},
            "analysis": {"analysis", "patterns", "feedback", "synthesis"},
            "general": {"reasoning", "analysis", "writing"}
        }

        required = category_capabilities.get(category, set())
        if not required:
            return 0.5

        matches = len(capabilities & required)
        return matches / len(required) if required else 0.5

    def _match_strengths(self, strengths: set, category: str) -> float:
        """Match strengths to category"""
        # Simple keyword matching (includes Secondbrain agents)
        category_keywords = {
            "code": ["programming", "coding", "development"],
            "network": ["network", "configuration", "firewall"],
            "cloud": ["cloud", "azure", "microsoft"],
            "document": ["document", "analysis", "writing"],
            "web": ["web", "automation", "browser"],
            "knowledge": ["knowledge", "search", "organization", "note", "semantic", "vault"],
            "business": ["business", "analytics", "reporting", "metrics", "project", "time"],
            "analysis": ["analysis", "pattern", "feedback", "synthesis"]
        }

        keywords = category_keywords.get(category, [])
        if not keywords:
            return 0.5

        strength_text = " ".join(strengths).lower()
        matches = sum(1 for kw in keywords if kw in strength_text)
        return matches / len(keywords) if keywords else 0.5

    def _complexity_score(self, agent_id: str, complexity: str) -> float:
        """Score agent's ability to handle complexity"""
        # Agent complexity handling ratings (includes Secondbrain agents)
        complexity_ratings = {
            "claude": {"simple": 1.0, "moderate": 1.0, "complex": 1.0},
            "gemini": {"simple": 0.8, "moderate": 1.0, "complex": 1.0},
            "fara": {"simple": 1.0, "moderate": 0.9, "complex": 0.7},
            "obsidian": {"simple": 1.0, "moderate": 0.9, "complex": 0.7},
            "ba": {"simple": 1.0, "moderate": 1.0, "complex": 0.9},
            "notebooklm": {"simple": 1.0, "moderate": 0.9, "complex": 0.8}
        }

        ratings = complexity_ratings.get(agent_id, {})
        return ratings.get(complexity, 0.7)

    def _get_routing_reason(
        self,
        agent_id: str,
        agent_config: Dict,
        classification: Dict
    ) -> str:
        """Generate human-readable routing reason"""
        agent_name = agent_config.get("name", agent_id)
        category = classification.get("primary_category", "general")
        sub_category = classification.get("sub_category", "")
        confidence = classification.get("confidence", 0.7)

        strengths = agent_config.get("strengths", [])
        strength_text = strengths[0] if strengths else "general tasks"

        return (
            f"Selected {agent_name} for {category}/{sub_category} task. "
            f"Best match for {strength_text}. "
            f"Confidence: {confidence:.0%}"
        )

    def update_performance(self, agent_id: str, success: bool, duration_ms: float):
        """Update agent performance metrics"""
        if agent_id not in self._agent_performance:
            self._agent_performance[agent_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "avg_duration_ms": 0
            }

        perf = self._agent_performance[agent_id]
        perf["total_requests"] += 1
        if success:
            perf["successful_requests"] += 1

        # Update rolling average duration
        n = perf["total_requests"]
        perf["avg_duration_ms"] = (
            perf["avg_duration_ms"] * (n - 1) + duration_ms
        ) / n

        # Calculate success rate
        perf["success_rate"] = perf["successful_requests"] / perf["total_requests"]

    def get_performance_stats(self) -> Dict[str, Dict]:
        """Get performance statistics for all agents"""
        return self._agent_performance.copy()
