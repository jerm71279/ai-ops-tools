import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Mixture of Experts (MoE) Router
Intelligent task routing system for multi-agent orchestration

Routes tasks to the most appropriate agent based on:
- Task classification
- Agent capabilities
- Current workload
- Historical performance
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Optional Gemini for advanced classification
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class TaskCategory(Enum):
    """Categories of tasks the system handles"""
    KNOWLEDGE_MANAGEMENT = "knowledge_management"
    DOCUMENT_PROCESSING = "document_processing"
    ANALYSIS = "analysis"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    PROJECT_MANAGEMENT = "project_management"
    TIME_TRACKING = "time_tracking"
    REPORTING = "reporting"
    SUPPORT = "support"
    UNKNOWN = "unknown"


@dataclass
class AgentCapability:
    """Defines an agent's capabilities"""
    agent_id: str
    name: str
    description: str
    categories: List[TaskCategory]
    keywords: List[str]
    priority: int  # Higher = preferred for ties
    max_concurrent_tasks: int
    current_load: int = 0


@dataclass
class RoutingDecision:
    """Result of routing a task"""
    task_id: str
    task_description: str
    classified_category: str
    selected_agent: str
    confidence: float
    reasoning: str
    alternative_agents: List[str]
    timestamp: str


class MoERouter:
    """
    Mixture of Experts Router

    Intelligently routes tasks to the most appropriate agent
    based on task content, agent capabilities, and system state.
    """

    def __init__(self, gemini_api_key: str = None):
        self.router_id = "moe_router"
        self.routing_history = []

        # Initialize Gemini for advanced classification
        self.gemini_model = None
        if GEMINI_AVAILABLE and gemini_api_key:
            import os
            api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')

        # Define agent capabilities
        self.agents: Dict[str, AgentCapability] = {
            "agent_obsidian": AgentCapability(
                agent_id="agent_obsidian",
                name="Obsidian Manager",
                description="Knowledge base operator - processes documents, creates notes, maintains vault",
                categories=[
                    TaskCategory.KNOWLEDGE_MANAGEMENT,
                    TaskCategory.DOCUMENT_PROCESSING
                ],
                keywords=[
                    "note", "document", "vault", "obsidian", "knowledge",
                    "create note", "update note", "search notes", "wiki",
                    "documentation", "markdown", "link", "tag", "template"
                ],
                priority=2,
                max_concurrent_tasks=5
            ),
            "agent_notebooklm": AgentCapability(
                agent_id="agent_notebooklm",
                name="NotebookLM Analyst",
                description="Knowledge base strategist - analyzes patterns, identifies gaps, generates insights",
                categories=[
                    TaskCategory.ANALYSIS,
                    TaskCategory.KNOWLEDGE_MANAGEMENT
                ],
                keywords=[
                    "analyze", "pattern", "consistency", "gap", "review",
                    "insight", "trend", "recommendation", "feedback",
                    "quality", "improvement", "audit"
                ],
                priority=2,
                max_concurrent_tasks=3
            ),
            "agent_ba": AgentCapability(
                agent_id="agent_ba",
                name="Business Analytics Agent",
                description="Business intelligence - project health, resource utilization, time tracking, quotes",
                categories=[
                    TaskCategory.BUSINESS_INTELLIGENCE,
                    TaskCategory.PROJECT_MANAGEMENT,
                    TaskCategory.TIME_TRACKING,
                    TaskCategory.REPORTING
                ],
                keywords=[
                    "project", "health", "status", "budget", "hours",
                    "time", "billable", "utilization", "capacity",
                    "quote", "estimate", "cost", "report", "summary",
                    "executive", "dashboard", "kpi", "metric", "sla",
                    "resource", "workload", "forecast", "employee"
                ],
                priority=3,  # Higher priority for business queries
                max_concurrent_tasks=10
            )
        }

        # Classification patterns (rule-based fallback)
        self.classification_patterns = {
            TaskCategory.KNOWLEDGE_MANAGEMENT: [
                r"note|document|vault|obsidian|wiki|markdown",
                r"create.*note|update.*note|search.*note",
                r"knowledge.*base|documentation"
            ],
            TaskCategory.DOCUMENT_PROCESSING: [
                r"process.*document|upload|import|extract",
                r"pdf|excel|word|file"
            ],
            TaskCategory.ANALYSIS: [
                r"analyze|analysis|pattern|trend|insight",
                r"review|audit|assess|evaluate"
            ],
            TaskCategory.BUSINESS_INTELLIGENCE: [
                r"project.*health|resource.*utilization",
                r"kpi|metric|dashboard|executive.*summary",
                r"business.*intelligence|bi\s"
            ],
            TaskCategory.PROJECT_MANAGEMENT: [
                r"project|task|milestone|deadline",
                r"status|progress|completion|overdue"
            ],
            TaskCategory.TIME_TRACKING: [
                r"time|hour|billable|timesheet",
                r"log.*time|track.*time|time.*entry"
            ],
            TaskCategory.REPORTING: [
                r"report|summary|export|generate.*report",
                r"weekly|monthly|quarterly"
            ],
            TaskCategory.SUPPORT: [
                r"ticket|support|help|issue|incident",
                r"customer|client.*request"
            ]
        }

    def classify_task(self, task_description: str) -> Tuple[TaskCategory, float]:
        """
        Classify a task into a category

        Returns: (category, confidence)
        """
        task_lower = task_description.lower()

        # Try Gemini classification first if available
        if self.gemini_model:
            try:
                gemini_result = self._classify_with_gemini(task_description)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                print(f"Gemini classification failed, falling back to rules: {e}")

        # Rule-based classification
        category_scores: Dict[TaskCategory, float] = {}

        for category, patterns in self.classification_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, task_lower))
                score += matches * 0.2

            # Check against agent keywords
            for agent in self.agents.values():
                if category in agent.categories:
                    keyword_matches = sum(
                        1 for kw in agent.keywords
                        if kw.lower() in task_lower
                    )
                    score += keyword_matches * 0.15

            category_scores[category] = min(score, 1.0)

        # Get best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]

            if confidence > 0:
                return best_category, min(confidence, 0.95)

        return TaskCategory.UNKNOWN, 0.3

    def _classify_with_gemini(self, task_description: str) -> Optional[Tuple[TaskCategory, float]]:
        """Use Gemini for intelligent classification"""
        categories_list = [c.value for c in TaskCategory if c != TaskCategory.UNKNOWN]

        prompt = f"""
        Classify this task into exactly one category.

        Task: {task_description}

        Available categories:
        {json.dumps(categories_list, indent=2)}

        Respond with JSON only:
        {{"category": "category_name", "confidence": 0.0-1.0}}
        """

        response = self.gemini_model.generate_content(prompt)
        text = response.text.strip()

        # Parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                category_str = result.get("category", "unknown")
                confidence = float(result.get("confidence", 0.5))

                # Map string to enum
                for cat in TaskCategory:
                    if cat.value == category_str:
                        return cat, confidence

        except (json.JSONDecodeError, ValueError):
            pass

        return None

    def select_agent(
        self,
        task_description: str,
        category: TaskCategory = None,
        preferred_agent: str = None
    ) -> Tuple[str, float, str]:
        """
        Select the best agent for a task

        Returns: (agent_id, confidence, reasoning)
        """
        # Classify if not provided
        if category is None:
            category, _ = self.classify_task(task_description)

        task_lower = task_description.lower()

        # Score each agent
        agent_scores: Dict[str, Dict[str, Any]] = {}

        for agent_id, agent in self.agents.items():
            score = 0.0
            reasons = []

            # Category match (primary factor)
            if category in agent.categories:
                score += 0.4
                reasons.append(f"Handles {category.value}")

            # Keyword matching
            keyword_matches = sum(
                1 for kw in agent.keywords
                if kw.lower() in task_lower
            )
            if keyword_matches > 0:
                keyword_score = min(keyword_matches * 0.1, 0.3)
                score += keyword_score
                reasons.append(f"{keyword_matches} keyword matches")

            # Priority boost
            score += agent.priority * 0.05
            reasons.append(f"Priority {agent.priority}")

            # Load penalty
            if agent.current_load >= agent.max_concurrent_tasks:
                score -= 0.3
                reasons.append("At capacity")
            elif agent.current_load > agent.max_concurrent_tasks * 0.7:
                score -= 0.1
                reasons.append("High load")

            # Preferred agent boost
            if preferred_agent and agent_id == preferred_agent:
                score += 0.2
                reasons.append("User preferred")

            agent_scores[agent_id] = {
                "score": score,
                "reasons": reasons
            }

        # Select best agent
        best_agent = max(agent_scores, key=lambda x: agent_scores[x]["score"])
        best_score = agent_scores[best_agent]["score"]
        reasoning = "; ".join(agent_scores[best_agent]["reasons"])

        return best_agent, min(best_score, 0.95), reasoning

    def route_task(
        self,
        task_id: str,
        task_description: str,
        preferred_agent: str = None,
        context: Dict = None
    ) -> RoutingDecision:
        """
        Route a task to the appropriate agent

        Main entry point for the router
        """
        # Classify task
        category, classification_confidence = self.classify_task(task_description)

        # Select agent
        agent_id, selection_confidence, reasoning = self.select_agent(
            task_description,
            category,
            preferred_agent
        )

        # Get alternative agents
        alternatives = [
            a.agent_id for a in self.agents.values()
            if a.agent_id != agent_id and category in a.categories
        ]

        # Combined confidence
        confidence = (classification_confidence + selection_confidence) / 2

        decision = RoutingDecision(
            task_id=task_id,
            task_description=task_description[:200],
            classified_category=category.value,
            selected_agent=agent_id,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            alternative_agents=alternatives,
            timestamp=datetime.now().isoformat()
        )

        # Store history
        self.routing_history.append(asdict(decision))

        return decision

    def route_to_best_agent(
        self,
        task_description: str,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Convenience method for simple routing

        Returns dict with agent_id and routing info
        """
        task_id = f"task_{datetime.now().timestamp()}"
        decision = self.route_task(task_id, task_description, context=context)

        return {
            "agent_id": decision.selected_agent,
            "agent_name": self.agents[decision.selected_agent].name,
            "category": decision.classified_category,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "alternatives": decision.alternative_agents
        }

    def update_agent_load(self, agent_id: str, delta: int):
        """Update an agent's current load"""
        if agent_id in self.agents:
            self.agents[agent_id].current_load = max(
                0,
                self.agents[agent_id].current_load + delta
            )

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_id: {
                "name": agent.name,
                "current_load": agent.current_load,
                "max_load": agent.max_concurrent_tasks,
                "available_capacity": agent.max_concurrent_tasks - agent.current_load,
                "categories": [c.value for c in agent.categories]
            }
            for agent_id, agent in self.agents.items()
        }

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        if not self.routing_history:
            return {"total_routed": 0}

        agent_counts = {}
        category_counts = {}
        avg_confidence = 0

        for decision in self.routing_history:
            agent = decision["selected_agent"]
            category = decision["classified_category"]

            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            avg_confidence += decision["confidence"]

        return {
            "total_routed": len(self.routing_history),
            "by_agent": agent_counts,
            "by_category": category_counts,
            "average_confidence": round(avg_confidence / len(self.routing_history), 2)
        }


# ============================================================================
# INTEGRATION WITH ORCHESTRATOR
# ============================================================================

class MoEOrchestrator:
    """
    Enhanced orchestrator with MoE routing

    Wraps the existing AgentOrchestrator with intelligent routing
    """

    def __init__(self, gemini_api_key: str = None):
        self.router = MoERouter(gemini_api_key)

        # Import agents (lazy to avoid circular imports)
        self._agents = {}
        self._initialized = False

    def _initialize_agents(self):
        """Initialize agent instances"""
        if self._initialized:
            return

        try:
            from agent_ba import BAAgent
            self._agents["agent_ba"] = BAAgent()
        except ImportError:
            print("Warning: BAAgent not available")

        # Add other agents as needed
        self._initialized = True

    def execute_task(
        self,
        task_description: str,
        data: Dict = None,
        preferred_agent: str = None
    ) -> Dict[str, Any]:
        """
        Execute a task using intelligent routing

        1. Routes task to best agent
        2. Executes with appropriate agent
        3. Returns results
        """
        self._initialize_agents()

        # Route the task
        routing = self.router.route_to_best_agent(task_description, context=data)
        agent_id = routing["agent_id"]

        print(f"\n{'='*60}")
        print(f"MoE Router Decision")
        print(f"{'='*60}")
        print(f"Task: {task_description[:100]}...")
        print(f"Routed to: {routing['agent_name']} ({agent_id})")
        print(f"Category: {routing['category']}")
        print(f"Confidence: {routing['confidence']}")
        print(f"Reasoning: {routing['reasoning']}")
        print(f"{'='*60}\n")

        # Update load
        self.router.update_agent_load(agent_id, 1)

        result = {
            "routing": routing,
            "success": False,
            "result": None,
            "error": None
        }

        try:
            # Execute with appropriate agent
            if agent_id == "agent_ba" and "agent_ba" in self._agents:
                agent = self._agents["agent_ba"]

                # Set data if provided
                if data:
                    agent.set_data(
                        projects=data.get("projects"),
                        tasks=data.get("tasks"),
                        tickets=data.get("tickets"),
                        time_entries=data.get("time_entries")
                    )

                # Determine which analysis to run based on category
                if routing["category"] == "project_health":
                    result["result"] = agent.analyze_project_health()
                elif routing["category"] == "resource_utilization":
                    result["result"] = agent.analyze_resource_utilization()
                elif routing["category"] == "time_tracking":
                    result["result"] = agent.analyze_time_reports()
                elif routing["category"] == "reporting":
                    result["result"] = agent.generate_executive_summary()
                else:
                    # Default to executive summary
                    result["result"] = agent.generate_executive_summary()

                result["success"] = True

            else:
                result["error"] = f"Agent {agent_id} not available or not implemented"

        except Exception as e:
            result["error"] = str(e)
            result["success"] = False

        finally:
            # Update load
            self.router.update_agent_load(agent_id, -1)

        return result

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator and router status"""
        return {
            "router_status": self.router.get_agent_status(),
            "routing_stats": self.router.get_routing_stats(),
            "agents_initialized": list(self._agents.keys())
        }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """CLI entry point for MoE Router"""
    import argparse

    parser = argparse.ArgumentParser(description="Mixture of Experts Router")
    parser.add_argument("--task", type=str, help="Task description to route")
    parser.add_argument("--status", action="store_true", help="Show router status")

    args = parser.parse_args()

    router = MoERouter()

    if args.status:
        print("Router Status:")
        print(json.dumps(router.get_agent_status(), indent=2))
        print("\nRouting Stats:")
        print(json.dumps(router.get_routing_stats(), indent=2))

    elif args.task:
        print(f"\nRouting task: {args.task}\n")
        result = router.route_to_best_agent(args.task)
        print(json.dumps(result, indent=2))

    else:
        # Demo routing
        test_tasks = [
            "Generate a project health report for all active projects",
            "Create a new note about network configuration",
            "Analyze the consistency of documentation",
            "What's our team utilization this month?",
            "Generate a quote for implementing Azure AD authentication",
            "Export time entries for billing",
            "Review the knowledge base for gaps"
        ]

        print("MoE Router Demo")
        print("=" * 60)

        for task in test_tasks:
            result = router.route_to_best_agent(task)
            print(f"\nTask: {task}")
            print(f"  -> Agent: {result['agent_name']}")
            print(f"  -> Category: {result['category']}")
            print(f"  -> Confidence: {result['confidence']}")


if __name__ == "__main__":
    main()
