"""
OberaConnect Assessment Framework
Aligned with OberaAI Strategy

Feedback Loops:
1. Score Tracking - Monitor improvement over time
2. Remediation - Track and verify fixes
3. Pattern Learning - Build proprietary data moat
4. Benchmark - Compare against peers

Principles:
- 98/2: AI handles patterns, humans handle exceptions
- Director Mode: AI analyzes, humans approve
- Data Moat: Every assessment makes the system smarter
- Leverage: One engineer can assess many customers
"""

from .core.assessment_engine import (
    AssessmentEngine,
    AssessmentResult,
    AssessmentType,
    Finding,
    SeverityLevel,
    RemediationStatus,
    quick_security_assessment
)

from .analyzers.ai_analyzer import (
    AIAnalyzer,
    AnalysisRequest,
    AnalysisResult,
    AssessmentDirector
)

from .feedback.feedback_loops import (
    FeedbackLoopOrchestrator,
    ScoreTrackingLoop,
    RemediationLoop,
    PatternLearningLoop,
    BenchmarkLoop
)

__version__ = "1.0.0"
__all__ = [
    # Core
    'AssessmentEngine',
    'AssessmentResult',
    'AssessmentType',
    'Finding',
    'SeverityLevel',
    'RemediationStatus',
    'quick_security_assessment',
    # Analyzers
    'AIAnalyzer',
    'AnalysisRequest',
    'AnalysisResult',
    'AssessmentDirector',
    # Feedback Loops
    'FeedbackLoopOrchestrator',
    'ScoreTrackingLoop',
    'RemediationLoop',
    'PatternLearningLoop',
    'BenchmarkLoop',
]
