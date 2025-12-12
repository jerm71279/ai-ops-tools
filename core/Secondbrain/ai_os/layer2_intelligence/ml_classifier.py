"""
Layer 2: ML-based Intent Classifier
Uses sentence embeddings for semantic intent classification
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..core.logging import get_logger

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    SentenceTransformer = None


class MLIntentClassifier:
    """
    ML-based intent classifier using sentence embeddings

    Uses semantic similarity to classify intents rather than keyword matching.
    This allows understanding of:
    - Synonyms and paraphrases
    - Context and nuance
    - New phrasings not seen before
    """

    # Pre-defined intent categories with example phrases
    INTENT_EXAMPLES = {
        "code": [
            "write a python function",
            "debug this script",
            "create an API endpoint",
            "fix the bug in my code",
            "implement a sorting algorithm",
            "refactor this class",
            "generate typescript code",
            "help with programming",
            "write unit tests",
            "create a REST API"
        ],
        "network": [
            "configure the firewall",
            "setup VPN connection",
            "troubleshoot network issues",
            "configure SonicWall rules",
            "setup UniFi access point",
            "create VLAN configuration",
            "check router settings",
            "diagnose connectivity problems",
            "configure MikroTik router",
            "setup port forwarding"
        ],
        "cloud": [
            "configure Azure settings",
            "setup Microsoft 365",
            "manage SharePoint site",
            "configure Intune policies",
            "setup Azure AD",
            "deploy to cloud",
            "manage Teams channels",
            "configure Entra ID",
            "setup cloud backup",
            "manage Azure subscriptions"
        ],
        "document": [
            "analyze this document",
            "summarize the PDF",
            "extract information from file",
            "review the report",
            "create documentation",
            "write a procedure",
            "generate SOP",
            "parse document content",
            "convert document format",
            "extract text from PDF"
        ],
        "web": [
            "scrape website data",
            "automate web form",
            "navigate to portal",
            "click through pages",
            "extract web content",
            "login to website",
            "automate browser actions",
            "fill out web form",
            "download from website",
            "interact with web page"
        ],
        "knowledge": [
            "search my notes",
            "find in knowledge base",
            "lookup information",
            "search Obsidian vault",
            "find related notes",
            "organize my knowledge",
            "tag and categorize notes",
            "search for concept",
            "find previous research",
            "query my vault"
        ],
        "business": [
            "generate project report",
            "analyze customer metrics",
            "create quote estimate",
            "track project hours",
            "calculate utilization",
            "review project health",
            "generate business report",
            "analyze KPIs",
            "create invoice",
            "track task progress",
            "check SharePoint folder",
            "find customer documents in SharePoint",
            "search SharePoint for checklist",
            "get files from customer folder",
            "look up onboarding documents"
        ],
        "analysis": [
            "analyze patterns",
            "synthesize information",
            "compare options",
            "evaluate trends",
            "provide insights",
            "analyze feedback",
            "generate analysis",
            "identify patterns",
            "deep dive analysis",
            "comprehensive review"
        ]
    }

    # Action intent examples
    ACTION_EXAMPLES = {
        "create": [
            "create a new",
            "generate code",
            "write a script",
            "build a feature",
            "make a report",
            "develop solution"
        ],
        "analyze": [
            "analyze this",
            "review the code",
            "check for issues",
            "examine the data",
            "evaluate options"
        ],
        "configure": [
            "configure settings",
            "setup the system",
            "install software",
            "deploy application",
            "provision resources"
        ],
        "search": [
            "search for",
            "find information",
            "look up",
            "locate file",
            "query database"
        ],
        "troubleshoot": [
            "fix the issue",
            "repair broken",
            "resolve error",
            "debug problem",
            "diagnose failure"
        ],
        "automate": [
            "automate process",
            "schedule task",
            "run workflow",
            "trigger action",
            "execute script"
        ]
    }

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: Path = None):
        self.logger = get_logger("ai_os.ml_classifier")
        self.model_name = model_name
        self.cache_dir = cache_dir or Path("./ai_os_cache/ml_models")

        self._model: Optional[SentenceTransformer] = None
        self._category_embeddings: Dict[str, np.ndarray] = {}
        self._action_embeddings: Dict[str, np.ndarray] = {}
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Check if ML classification is available"""
        return ML_AVAILABLE

    async def initialize(self) -> bool:
        """Initialize the ML classifier"""
        if not ML_AVAILABLE:
            self.logger.warning("sentence-transformers not installed - ML classification disabled")
            return False

        try:
            self.logger.info(f"Loading ML model: {self.model_name}")

            # Load model (will download if not cached)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._model = SentenceTransformer(self.model_name, cache_folder=str(self.cache_dir))

            # Pre-compute category embeddings
            self.logger.info("Computing category embeddings...")
            for category, examples in self.INTENT_EXAMPLES.items():
                embeddings = self._model.encode(examples)
                # Use mean of example embeddings as category representation
                self._category_embeddings[category] = np.mean(embeddings, axis=0)

            # Pre-compute action embeddings
            for action, examples in self.ACTION_EXAMPLES.items():
                embeddings = self._model.encode(examples)
                self._action_embeddings[action] = np.mean(embeddings, axis=0)

            self._initialized = True
            self.logger.info("ML classifier initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize ML classifier: {e}")
            return False

    def classify(self, content: str) -> Dict[str, Any]:
        """
        Classify content using semantic embeddings

        Args:
            content: The text to classify

        Returns:
            Classification with category, action, and confidence scores
        """
        if not self._initialized or not self._model:
            return self._fallback_classify(content)

        try:
            # Encode the query
            query_embedding = self._model.encode(content)

            # Calculate similarity to each category
            category_scores = {}
            for category, cat_embedding in self._category_embeddings.items():
                similarity = self._cosine_similarity(query_embedding, cat_embedding)
                category_scores[category] = float(similarity)

            # Get top category
            sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            primary_category = sorted_categories[0][0]
            primary_confidence = sorted_categories[0][1]

            # Calculate action similarity
            action_scores = {}
            for action, act_embedding in self._action_embeddings.items():
                similarity = self._cosine_similarity(query_embedding, act_embedding)
                action_scores[action] = float(similarity)

            # Get top action
            sorted_actions = sorted(action_scores.items(), key=lambda x: x[1], reverse=True)
            primary_action = sorted_actions[0][0]

            # Normalize confidence (similarity range is typically 0-1 for normalized embeddings)
            # but can be negative, so we map to 0.5-1.0 range
            confidence = (primary_confidence + 1) / 2  # Map from [-1,1] to [0,1]
            confidence = max(0.5, min(1.0, confidence))  # Clamp to reasonable range

            return {
                "primary_category": primary_category,
                "sub_category": primary_action,
                "confidence": confidence,
                "category_scores": category_scores,
                "action_scores": action_scores,
                "ml_classified": True,
                "top_categories": [
                    {"category": cat, "score": score}
                    for cat, score in sorted_categories[:3]
                ]
            }

        except Exception as e:
            self.logger.error(f"ML classification error: {e}")
            return self._fallback_classify(content)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _fallback_classify(self, content: str) -> Dict[str, Any]:
        """Fallback to simple keyword matching when ML unavailable"""
        content_lower = content.lower()

        # Simple keyword matching
        category_keywords = {
            "code": ["code", "script", "function", "python", "api"],
            "network": ["network", "firewall", "router", "vpn"],
            "cloud": ["azure", "microsoft", "sharepoint", "teams"],
            "document": ["document", "pdf", "report", "analyze"],
            "web": ["website", "browser", "scrape", "portal"],
            "knowledge": ["notes", "obsidian", "search", "find"],
            "business": ["project", "report", "metrics", "quote"],
            "analysis": ["analyze", "pattern", "insight", "compare"]
        }

        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[category] = score / len(keywords)

        if scores:
            primary = max(scores, key=scores.get)
            confidence = min(0.8, scores[primary] + 0.3)
        else:
            primary = "general"
            confidence = 0.5

        return {
            "primary_category": primary,
            "sub_category": "query",
            "confidence": confidence,
            "category_scores": scores,
            "ml_classified": False
        }

    def add_category_example(self, category: str, example: str):
        """Add a new example to a category (updates embedding)"""
        if category not in self.INTENT_EXAMPLES:
            self.INTENT_EXAMPLES[category] = []

        self.INTENT_EXAMPLES[category].append(example)

        # Recompute embedding if model is loaded
        if self._model and category in self._category_embeddings:
            embeddings = self._model.encode(self.INTENT_EXAMPLES[category])
            self._category_embeddings[category] = np.mean(embeddings, axis=0)

    def get_similar_queries(self, content: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """
        Find similar example queries

        Returns list of (category, example, similarity) tuples
        """
        if not self._initialized or not self._model:
            return []

        query_embedding = self._model.encode(content)

        similarities = []
        for category, examples in self.INTENT_EXAMPLES.items():
            for example in examples:
                example_embedding = self._model.encode(example)
                sim = self._cosine_similarity(query_embedding, example_embedding)
                similarities.append((category, example, float(sim)))

        # Sort by similarity
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:top_k]


# Singleton instance for reuse
_ml_classifier: Optional[MLIntentClassifier] = None


async def get_ml_classifier() -> MLIntentClassifier:
    """Get or create the ML classifier singleton"""
    global _ml_classifier

    if _ml_classifier is None:
        _ml_classifier = MLIntentClassifier()
        await _ml_classifier.initialize()

    return _ml_classifier
