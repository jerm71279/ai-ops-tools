"""
Layer 2: Task Classifier
Classifies tasks by domain, complexity, and requirements

Supports both rule-based and ML-based classification:
- Rule-based: Fast keyword matching (always available)
- ML-based: Semantic understanding via sentence embeddings (optional)
"""

from typing import Any, Dict, List, Optional

from ..core.config import AIConfig
from ..core.logging import get_logger


class TaskClassifier:
    """
    Task classification engine

    Analyzes task content to determine:
    - Primary category (domain)
    - Sub-category (action type)
    - Complexity level
    - Required capabilities
    - Suggested agents
    """

    def __init__(self, config: AIConfig = None, use_ml: bool = True):
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.classifier")
        self._use_ml = use_ml
        self._ml_classifier: Optional['MLIntentClassifier'] = None
        self._ml_initialized = False

        # Category definitions
        self._categories = {
            "code": {
                "keywords": ["code", "script", "function", "program", "python", "javascript",
                            "typescript", "api", "endpoint", "class", "method", "bug", "error"],
                "agents": ["claude"],
                "complexity_boost": 0.2
            },
            "network": {
                "keywords": ["network", "firewall", "router", "switch", "vlan", "vpn",
                            "sonicwall", "mikrotik", "unifi", "ubiquiti", "cisco", "port"],
                "agents": ["claude", "fara"],
                "complexity_boost": 0.1
            },
            "cloud": {
                "keywords": ["azure", "aws", "microsoft", "m365", "teams",
                            "intune", "entra", "active directory", "tenant", "subscription"],
                "agents": ["claude", "fara"],
                "complexity_boost": 0.15
            },
            "document": {
                "keywords": ["document", "pdf", "report", "sop", "procedure", "manual",
                            "analyze", "summarize", "extract", "review"],
                "agents": ["gemini", "claude"],
                "complexity_boost": 0.0
            },
            "web": {
                "keywords": ["portal", "website", "browser", "web", "page", "click",
                            "navigate", "form", "login", "scrape", "extract"],
                "agents": ["fara", "gemini"],
                "complexity_boost": 0.05
            },
            "knowledge": {
                "keywords": ["knowledge", "note", "obsidian", "search", "find", "lookup",
                            "remember", "store", "organize", "vault", "concept", "tag"],
                "agents": ["obsidian", "claude"],
                "complexity_boost": -0.1
            },
            "business": {
                "keywords": ["project", "task", "ticket", "report", "metrics", "kpi",
                            "quote", "estimate", "customer", "client", "schedule", "hours",
                            "utilization", "health", "sharepoint", "folder", "checklist",
                            "document library", "site", "onboarding", "new customer"],
                "agents": ["ba", "claude"],
                "complexity_boost": 0.1
            },
            "analysis": {
                "keywords": ["analyze", "pattern", "insight", "synthesis", "feedback",
                            "notebooklm", "compare", "evaluate", "trend"],
                "agents": ["notebooklm", "gemini", "claude"],
                "complexity_boost": 0.1
            }
        }

        # Action definitions
        self._actions = {
            "create": ["create", "generate", "write", "build", "make", "develop", "implement"],
            "analyze": ["analyze", "review", "check", "examine", "evaluate", "assess"],
            "configure": ["configure", "setup", "install", "deploy", "provision", "enable"],
            "search": ["search", "find", "look for", "locate", "query", "fetch"],
            "troubleshoot": ["fix", "repair", "resolve", "troubleshoot", "debug", "diagnose"],
            "automate": ["automate", "schedule", "run", "execute", "trigger", "workflow"]
        }

    async def initialize_ml(self) -> bool:
        """Initialize ML classifier (call once at startup)"""
        if not self._use_ml:
            return False

        try:
            from .ml_classifier import MLIntentClassifier
            self._ml_classifier = MLIntentClassifier()
            self._ml_initialized = await self._ml_classifier.initialize()

            if self._ml_initialized:
                self.logger.info("ML classifier initialized - using semantic classification")
            else:
                self.logger.info("ML classifier unavailable - using rule-based classification")

            return self._ml_initialized
        except ImportError:
            self.logger.debug("ML classifier module not available")
            return False
        except Exception as e:
            self.logger.warning(f"Failed to initialize ML classifier: {e}")
            return False

    async def classify(self, content: str, intent: Dict = None) -> Dict[str, Any]:
        """
        Classify a task based on content

        Uses ML classification if available, falls back to rule-based.

        Args:
            content: The task content/description
            intent: Pre-parsed intent (optional)

        Returns:
            Classification dictionary
        """
        # Try ML classification first
        ml_result = None
        if self._ml_initialized and self._ml_classifier:
            try:
                ml_result = self._ml_classifier.classify(content)
                self.logger.debug(f"ML classification: {ml_result.get('primary_category')} "
                                  f"(confidence: {ml_result.get('confidence', 0):.2f})")
            except Exception as e:
                self.logger.warning(f"ML classification failed: {e}")

        # Rule-based classification
        content_lower = content.lower()
        words = set(content_lower.split())

        # Calculate category scores
        category_scores = {}
        for category, config in self._categories.items():
            score = self._calculate_category_score(content_lower, words, config)
            if score > 0:
                category_scores[category] = score

        # Determine primary category (combine ML and rule-based)
        if ml_result and ml_result.get("ml_classified"):
            # Use ML result but boost with rule-based matches
            ml_category = ml_result["primary_category"]
            ml_confidence = ml_result["confidence"]

            # If rule-based agrees, boost confidence
            if ml_category in category_scores:
                rule_score = category_scores[ml_category]
                combined_confidence = (ml_confidence * 0.7) + (rule_score * 0.3)
            else:
                combined_confidence = ml_confidence * 0.85  # Slight penalty if rules don't match

            primary_category = ml_category
            confidence = min(1.0, combined_confidence)

            # Merge category scores
            if ml_result.get("category_scores"):
                for cat, score in ml_result["category_scores"].items():
                    if cat in category_scores:
                        category_scores[cat] = (category_scores[cat] + score) / 2
                    else:
                        category_scores[cat] = score

        elif category_scores:
            primary_category = max(category_scores, key=category_scores.get)
            confidence = min(1.0, category_scores[primary_category])
        else:
            primary_category = intent.get("domain", "general") if intent else "general"
            confidence = 0.5

        # Determine action/sub-category
        if ml_result and ml_result.get("sub_category"):
            sub_category = ml_result["sub_category"]
        else:
            sub_category = self._determine_action(content_lower)

        # Calculate complexity
        complexity = self._calculate_complexity(content, primary_category)

        # Get suggested agents
        suggested_agents = self._get_suggested_agents(primary_category, sub_category)

        result = {
            "primary_category": primary_category,
            "sub_category": sub_category,
            "complexity": complexity,
            "confidence": confidence,
            "category_scores": category_scores,
            "suggested_agents": suggested_agents,
            "requires_multi_agent": complexity == "complex" or len(suggested_agents) > 1,
            "ml_enhanced": ml_result is not None and ml_result.get("ml_classified", False)
        }

        # Add top categories from ML if available
        if ml_result and ml_result.get("top_categories"):
            result["top_categories"] = ml_result["top_categories"]

        return result

    def _calculate_category_score(
        self,
        content: str,
        words: set,
        category_config: Dict
    ) -> float:
        """Calculate score for a category"""
        keywords = category_config.get("keywords", [])
        matches = 0

        for keyword in keywords:
            if " " in keyword:
                # Multi-word keyword
                if keyword in content:
                    matches += 2  # Bonus for phrase match
            elif keyword in words:
                matches += 1

        if not keywords:
            return 0.0

        # Normalize score
        score = matches / (len(keywords) * 0.5)  # Allow score > 1 for multiple matches
        score = min(1.0, score)

        return score

    def _determine_action(self, content: str) -> str:
        """Determine the action type"""
        for action, keywords in self._actions.items():
            for keyword in keywords:
                if keyword in content:
                    return action
        return "query"

    def _calculate_complexity(self, content: str, category: str) -> str:
        """
        Calculate task complexity

        Factors:
        - Content length
        - Number of distinct requirements
        - Category-specific boost
        - Explicit complexity keywords
        """
        # Base score from length
        word_count = len(content.split())

        if word_count < 10:
            base_complexity = 0.2
        elif word_count < 30:
            base_complexity = 0.4
        elif word_count < 60:
            base_complexity = 0.6
        else:
            base_complexity = 0.8

        # Category boost
        category_config = self._categories.get(category, {})
        complexity_boost = category_config.get("complexity_boost", 0.0)
        base_complexity += complexity_boost

        # Explicit keywords
        content_lower = content.lower()
        if any(w in content_lower for w in ["simple", "basic", "quick", "just"]):
            base_complexity -= 0.2
        if any(w in content_lower for w in ["complex", "detailed", "comprehensive", "full"]):
            base_complexity += 0.2
        if any(w in content_lower for w in ["multiple", "several", "all", "complete"]):
            base_complexity += 0.1

        # Clamp and categorize
        base_complexity = max(0.0, min(1.0, base_complexity))

        if base_complexity < 0.35:
            return "simple"
        elif base_complexity < 0.65:
            return "moderate"
        else:
            return "complex"

    def _get_suggested_agents(self, category: str, action: str) -> List[str]:
        """Get suggested agents for category and action"""
        category_config = self._categories.get(category, {})
        primary_agents = category_config.get("agents", ["claude"])

        # Action-specific additions (includes Secondbrain agents)
        action_additions = {
            "analyze": ["notebooklm", "gemini"],
            "automate": ["fara"],
            "search": ["obsidian"],
            "create": ["claude", "obsidian"],
            "troubleshoot": ["claude", "ba"]
        }

        additional = action_additions.get(action, [])

        # Combine and deduplicate while preserving order
        all_agents = primary_agents + [a for a in additional if a not in primary_agents]

        return all_agents[:3]  # Max 3 suggestions
