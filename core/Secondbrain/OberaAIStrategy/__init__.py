"""
OberaConnect AI Strategy Framework
Implementation of the Five AI Shifts

The Five Shifts:
1. Leverage Charts - From org charts to leverage charts
   "What can we build to add more leverage?" 1 person + AI = 5-10x output

2. Director Mindset - From doer to director
   Flip from 90% doing to 80% directing AI. Your expertise becomes the vision.

3. Data Moats - From feature moats to data moats
   Your proprietary data and what you do with it is your competitive advantage.

4. Autonomous Back Office - The 98/2 principle
   AI handles 98% of patterns; humans audit 2% exceptions.

5. Distribution Advantage - From development to distribution
   When AI makes building easy, distribution is the differentiator.

This framework coordinates AI transformation across all OberaConnect projects
with unified feedback loops for continuous improvement.
"""

from .core.strategy_engine import (
    OberaAIStrategyEngine,
    AIShift,
    MaturityLevel,
    ShiftMetrics,
    ProjectIntegration,
    record_automation,
    get_dashboard
)

from .integrations.project_registry import (
    PROJECT_REGISTRY,
    register_all_projects,
    get_project_config,
    get_projects_by_shift,
    get_all_feedback_loops,
    get_data_moat_summary,
    get_shift_coverage
)

from .integrations.feedback_aggregator import (
    FeedbackAggregator,
    run_aggregation,
    get_status as get_aggregation_status
)

__version__ = "1.0.0"
__all__ = [
    # Core
    'OberaAIStrategyEngine',
    'AIShift',
    'MaturityLevel',
    'ShiftMetrics',
    'ProjectIntegration',
    # Convenience functions
    'record_automation',
    'get_dashboard',
    # Registry
    'PROJECT_REGISTRY',
    'register_all_projects',
    'get_project_config',
    'get_projects_by_shift',
    'get_all_feedback_loops',
    'get_data_moat_summary',
    'get_shift_coverage',
    # Feedback Aggregation
    'FeedbackAggregator',
    'run_aggregation',
    'get_aggregation_status'
]
