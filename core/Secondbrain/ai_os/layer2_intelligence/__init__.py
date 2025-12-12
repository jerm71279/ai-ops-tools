"""
Layer 2: Intelligence Layer
Task classification, intent parsing, and MoE routing

Supports ML-based intent classification when sentence-transformers is available.
"""

from .intelligence import IntelligenceLayer
from .router import TaskRouter
from .classifier import TaskClassifier
from .context import ContextManager

# Optional ML classifier (may not be available)
try:
    from .ml_classifier import MLIntentClassifier, ML_AVAILABLE
except ImportError:
    MLIntentClassifier = None
    ML_AVAILABLE = False

__all__ = [
    'IntelligenceLayer',
    'TaskRouter',
    'TaskClassifier',
    'ContextManager',
    'MLIntentClassifier',
    'ML_AVAILABLE'
]
