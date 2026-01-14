"""
Data models for OberaConnect Notion integration.

Provides typed dataclasses for:
- Site data
- Health metrics
- Config changes
- Network devices
"""

# Re-export health models from services (they're closely related)
from services.health_score import (
    HealthMetrics,
    HealthResult,
    HealthStatus,
    HealthWeights,
    BackupStatus,
)

__all__ = [
    "HealthMetrics",
    "HealthResult",
    "HealthStatus",
    "HealthWeights",
    "BackupStatus",
]
