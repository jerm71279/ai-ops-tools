"""
Unified health score calculation for OberaConnect.

Single source of truth for site health scoring with configurable weights.
Eliminates duplication between customer_status_sync and daily_health_sync.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum

from core.logging_config import get_logger
from core.errors import ValidationError

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health status categories based on score thresholds."""
    HEALTHY = "healthy"           # 80-100
    WARNING = "warning"           # 50-79
    CRITICAL = "critical"         # 0-49
    
    @classmethod
    def from_score(cls, score: int) -> 'HealthStatus':
        """Determine status from numeric score."""
        if score >= 80:
            return cls.HEALTHY
        elif score >= 50:
            return cls.WARNING
        else:
            return cls.CRITICAL


class BackupStatus(Enum):
    """Backup status values with associated penalties."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    UNKNOWN = "unknown"
    
    @property
    def penalty_ratio(self) -> float:
        """Return penalty as ratio of max backup points."""
        ratios = {
            BackupStatus.SUCCESS: 0.0,
            BackupStatus.PARTIAL: 0.5,
            BackupStatus.FAILED: 1.0,
            BackupStatus.UNKNOWN: 0.33,
        }
        return ratios.get(self, 0.33)


@dataclass
class HealthWeights:
    """
    Configurable weights for health score components.
    
    All weights must sum to 100. Default weights are balanced
    for typical MSP monitoring priorities.
    
    Attributes:
        device_availability: Points for device uptime (0-100% online)
        wifi_quality: Points for WiFi signal quality
        alerts: Points deducted for active alerts
        backup: Points for backup status
        config_compliance: Points for configuration compliance
    """
    device_availability: int = 30
    wifi_quality: int = 20
    alerts: int = 20
    backup: int = 15
    config_compliance: int = 15
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """Ensure weights sum to 100."""
        total = (
            self.device_availability +
            self.wifi_quality +
            self.alerts +
            self.backup +
            self.config_compliance
        )
        if total != 100:
            raise ValidationError(
                "weights",
                f"Weights must sum to 100, got {total}",
                {"total": total, "weights": self.__dict__}
            )
    
    @classmethod
    def default(cls) -> 'HealthWeights':
        """Return default weights."""
        return cls()
    
    @classmethod
    def device_focused(cls) -> 'HealthWeights':
        """Weights emphasizing device availability."""
        return cls(
            device_availability=50,
            wifi_quality=15,
            alerts=15,
            backup=10,
            config_compliance=10
        )
    
    @classmethod
    def security_focused(cls) -> 'HealthWeights':
        """Weights emphasizing security/compliance."""
        return cls(
            device_availability=25,
            wifi_quality=15,
            alerts=20,
            backup=15,
            config_compliance=25
        )


@dataclass
class HealthMetrics:
    """
    Input metrics for health score calculation.
    
    All fields optional with sensible defaults.
    """
    # Device metrics
    devices_online: int = 0
    devices_total: int = 0
    
    # WiFi metrics
    wifi_clients_total: int = 0
    wifi_clients_weak_signal: int = 0
    
    # Alert metrics
    alerts_critical: int = 0
    alerts_warning: int = 0
    alerts_info: int = 0
    
    # Backup status
    backup_status: str = "unknown"
    
    # Config compliance
    config_drift_detected: bool = False
    config_violations: List[str] = field(default_factory=list)
    
    # Optional: open tickets (from RMM)
    open_tickets: int = 0
    
    @property
    def device_availability_ratio(self) -> float:
        """Calculate device availability as ratio (0.0 - 1.0)."""
        if self.devices_total == 0:
            return 1.0  # No devices = 100% available
        return self.devices_online / self.devices_total
    
    @property
    def wifi_quality_ratio(self) -> float:
        """Calculate WiFi quality as ratio (0.0 - 1.0, higher is better)."""
        if self.wifi_clients_total == 0:
            return 1.0  # No clients = perfect quality
        weak_ratio = self.wifi_clients_weak_signal / self.wifi_clients_total
        return 1.0 - weak_ratio
    
    @property
    def parsed_backup_status(self) -> BackupStatus:
        """Parse backup status string to enum."""
        try:
            return BackupStatus(self.backup_status.lower())
        except ValueError:
            return BackupStatus.UNKNOWN


@dataclass
class HealthResult:
    """
    Result of health score calculation.
    
    Contains score, status, and detailed breakdown.
    """
    score: int
    status: HealthStatus
    breakdown: Dict[str, int]
    requires_review: bool
    review_reasons: List[str]
    
    @property
    def status_name(self) -> str:
        """Return status as string for Notion."""
        return self.status.value


class HealthScoreCalculator:
    """
    Calculate health scores from site metrics.
    
    Provides unified scoring across all sync operations.
    
    Example:
        calculator = HealthScoreCalculator()
        
        metrics = HealthMetrics(
            devices_online=10,
            devices_total=12,
            alerts_warning=2,
            backup_status="success"
        )
        
        result = calculator.calculate(metrics)
        print(f"Score: {result.score}, Status: {result.status_name}")
    """
    
    def __init__(
        self,
        weights: Optional[HealthWeights] = None,
        warning_threshold: int = 70,
        critical_threshold: int = 50
    ):
        """
        Initialize calculator with weights and thresholds.
        
        Args:
            weights: Custom weights or None for defaults
            warning_threshold: Score below which status is WARNING
            critical_threshold: Score below which status is CRITICAL
        """
        self.weights = weights or HealthWeights.default()
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
    
    def calculate(self, metrics: HealthMetrics) -> HealthResult:
        """
        Calculate health score from metrics.
        
        Args:
            metrics: Input metrics for calculation
        
        Returns:
            HealthResult with score, status, and breakdown
        """
        breakdown = {}
        review_reasons = []
        
        # Start with perfect score
        score = 100
        
        # Device availability (deduct from max weight based on unavailability)
        availability_penalty = int(
            (1 - metrics.device_availability_ratio) * self.weights.device_availability
        )
        score -= availability_penalty
        breakdown["device_availability"] = self.weights.device_availability - availability_penalty
        
        if metrics.devices_total > 0 and metrics.devices_online < metrics.devices_total:
            offline_count = metrics.devices_total - metrics.devices_online
            review_reasons.append(f"{offline_count} device(s) offline")
        
        # WiFi quality (deduct based on weak signal ratio)
        wifi_penalty = int(
            (1 - metrics.wifi_quality_ratio) * self.weights.wifi_quality
        )
        score -= wifi_penalty
        breakdown["wifi_quality"] = self.weights.wifi_quality - wifi_penalty
        
        if metrics.wifi_clients_weak_signal > 0:
            review_reasons.append(
                f"{metrics.wifi_clients_weak_signal} client(s) with weak signal"
            )
        
        # Alerts (critical = 10pts each, warning = 2pts each, capped at max weight)
        alert_penalty = min(
            metrics.alerts_critical * 10 + metrics.alerts_warning * 2,
            self.weights.alerts
        )
        score -= alert_penalty
        breakdown["alerts"] = self.weights.alerts - alert_penalty
        
        if metrics.alerts_critical > 0:
            review_reasons.append(f"{metrics.alerts_critical} critical alert(s)")
        
        # Backup status
        backup_penalty = int(
            metrics.parsed_backup_status.penalty_ratio * self.weights.backup
        )
        score -= backup_penalty
        breakdown["backup"] = self.weights.backup - backup_penalty
        
        if metrics.parsed_backup_status != BackupStatus.SUCCESS:
            review_reasons.append(f"Backup status: {metrics.backup_status}")
        
        # Config compliance
        if metrics.config_drift_detected:
            score -= self.weights.config_compliance
            breakdown["config_compliance"] = 0
            review_reasons.append("Config drift detected")
            if metrics.config_violations:
                review_reasons.extend(metrics.config_violations[:3])  # Top 3
        else:
            breakdown["config_compliance"] = self.weights.config_compliance
        
        # Clamp score to 0-100
        score = max(0, min(100, score))
        
        # Determine status
        status = HealthStatus.from_score(score)
        
        # Determine if review required
        requires_review = (
            score < self.warning_threshold or
            metrics.alerts_critical > 0 or
            metrics.config_drift_detected
        )
        
        return HealthResult(
            score=score,
            status=status,
            breakdown=breakdown,
            requires_review=requires_review,
            review_reasons=review_reasons
        )
    
    def calculate_from_dict(self, data: Dict) -> HealthResult:
        """
        Calculate health score from dictionary input.
        
        Convenience method for raw API data.
        
        Args:
            data: Dictionary with metric values
        
        Returns:
            HealthResult
        """
        metrics = HealthMetrics(
            devices_online=data.get("devices_online", 0),
            devices_total=data.get("devices_total", 0),
            wifi_clients_total=data.get("wifi_clients", 0),
            wifi_clients_weak_signal=data.get("signal_warnings", 0),
            alerts_critical=data.get("critical_alerts", 0),
            alerts_warning=data.get("warning_alerts", data.get("active_alerts", 0)),
            backup_status=data.get("backup_status", "unknown"),
            config_drift_detected=data.get("config_drift", False),
            config_violations=data.get("config_violations", []),
            open_tickets=data.get("open_tickets", 0),
        )
        return self.calculate(metrics)


# Module-level convenience instance
_default_calculator: Optional[HealthScoreCalculator] = None


def get_calculator() -> HealthScoreCalculator:
    """Get or create default calculator instance."""
    global _default_calculator
    if _default_calculator is None:
        _default_calculator = HealthScoreCalculator()
    return _default_calculator


def calculate_health_score(
    devices_online: int = 0,
    devices_total: int = 0,
    wifi_clients_total: int = 0,
    wifi_clients_weak_signal: int = 0,
    alerts_critical: int = 0,
    alerts_warning: int = 0,
    backup_status: str = "unknown",
    config_drift: bool = False,
    **kwargs
) -> int:
    """
    Calculate health score with simple function interface.
    
    Convenience function for backward compatibility.
    Returns just the score integer.
    """
    metrics = HealthMetrics(
        devices_online=devices_online,
        devices_total=devices_total,
        wifi_clients_total=wifi_clients_total,
        wifi_clients_weak_signal=wifi_clients_weak_signal,
        alerts_critical=alerts_critical,
        alerts_warning=alerts_warning,
        backup_status=backup_status,
        config_drift_detected=config_drift,
    )
    result = get_calculator().calculate(metrics)
    return result.score
