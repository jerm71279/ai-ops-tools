"""
Unit tests for health score calculation.

Tests the unified HealthScoreCalculator to ensure consistent
scoring across all sync operations.
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from services.health_score import (
    HealthScoreCalculator,
    HealthMetrics,
    HealthWeights,
    HealthResult,
    HealthStatus,
    BackupStatus,
    calculate_health_score,
)
from core.errors import ValidationError


class TestHealthWeights:
    """Tests for HealthWeights configuration."""
    
    def test_default_weights_sum_to_100(self):
        """Default weights should sum to 100."""
        weights = HealthWeights.default()
        total = (
            weights.device_availability +
            weights.wifi_quality +
            weights.alerts +
            weights.backup +
            weights.config_compliance
        )
        assert total == 100
    
    def test_device_focused_weights_sum_to_100(self):
        """Device-focused preset should sum to 100."""
        weights = HealthWeights.device_focused()
        total = (
            weights.device_availability +
            weights.wifi_quality +
            weights.alerts +
            weights.backup +
            weights.config_compliance
        )
        assert total == 100
    
    def test_security_focused_weights_sum_to_100(self):
        """Security-focused preset should sum to 100."""
        weights = HealthWeights.security_focused()
        total = (
            weights.device_availability +
            weights.wifi_quality +
            weights.alerts +
            weights.backup +
            weights.config_compliance
        )
        assert total == 100
    
    def test_invalid_weights_raise_error(self):
        """Weights not summing to 100 should raise ValidationError."""
        with pytest.raises(ValidationError):
            HealthWeights(
                device_availability=50,
                wifi_quality=50,
                alerts=50,
                backup=50,
                config_compliance=50
            )


class TestHealthMetrics:
    """Tests for HealthMetrics data class."""
    
    def test_availability_ratio_all_online(self):
        """All devices online = 100% availability."""
        metrics = HealthMetrics(devices_online=10, devices_total=10)
        assert metrics.device_availability_ratio == 1.0
    
    def test_availability_ratio_half_online(self):
        """Half devices online = 50% availability."""
        metrics = HealthMetrics(devices_online=5, devices_total=10)
        assert metrics.device_availability_ratio == 0.5
    
    def test_availability_ratio_none_online(self):
        """No devices online = 0% availability."""
        metrics = HealthMetrics(devices_online=0, devices_total=10)
        assert metrics.device_availability_ratio == 0.0
    
    def test_availability_ratio_no_devices(self):
        """No devices = 100% availability (edge case)."""
        metrics = HealthMetrics(devices_online=0, devices_total=0)
        assert metrics.device_availability_ratio == 1.0
    
    def test_wifi_quality_ratio_no_weak(self):
        """No weak signal clients = 100% quality."""
        metrics = HealthMetrics(wifi_clients_total=50, wifi_clients_weak_signal=0)
        assert metrics.wifi_quality_ratio == 1.0
    
    def test_wifi_quality_ratio_half_weak(self):
        """Half weak signal = 50% quality."""
        metrics = HealthMetrics(wifi_clients_total=50, wifi_clients_weak_signal=25)
        assert metrics.wifi_quality_ratio == 0.5
    
    def test_backup_status_parsing(self):
        """Backup status string should parse to enum."""
        metrics = HealthMetrics(backup_status="success")
        assert metrics.parsed_backup_status == BackupStatus.SUCCESS
        
        metrics = HealthMetrics(backup_status="FAILED")  # Case insensitive
        assert metrics.parsed_backup_status == BackupStatus.FAILED
        
        metrics = HealthMetrics(backup_status="invalid")
        assert metrics.parsed_backup_status == BackupStatus.UNKNOWN


class TestHealthScoreCalculator:
    """Tests for HealthScoreCalculator."""
    
    def test_perfect_score(self, healthy_site_metrics):
        """All metrics healthy = score 100."""
        calculator = HealthScoreCalculator()
        result = calculator.calculate_from_dict(healthy_site_metrics)
        assert result.score == 100
        assert result.status == HealthStatus.HEALTHY
        assert not result.requires_review
    
    def test_all_devices_offline(self):
        """All devices offline = lose all availability points."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(
            devices_online=0, 
            devices_total=10,
            backup_status="success"  # Explicit to isolate test
        )
        result = calculator.calculate(metrics)
        
        # Default availability weight is 30, so score should be 100 - 30 = 70
        assert result.score == 70
        assert "device(s) offline" in result.review_reasons[0]
    
    def test_half_devices_offline(self):
        """Half devices offline = lose half availability points."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(
            devices_online=5, 
            devices_total=10,
            backup_status="success"  # Explicit to isolate test
        )
        result = calculator.calculate(metrics)
        
        # 50% availability = lose 15 of 30 points = 85
        assert result.score == 85
    
    def test_critical_alerts_penalty(self):
        """Critical alerts should deduct 10 points each."""
        calculator = HealthScoreCalculator()
        
        # 2 critical alerts = 20 points penalty (capped at 20 for alerts)
        metrics = HealthMetrics(alerts_critical=2, backup_status="success")
        result = calculator.calculate(metrics)
        assert result.score == 80
        
        # 3 critical alerts = 30 points but capped at 20
        metrics = HealthMetrics(alerts_critical=3, backup_status="success")
        result = calculator.calculate(metrics)
        assert result.score == 80  # Still 80 due to cap
    
    def test_warning_alerts_penalty(self):
        """Warning alerts should deduct 2 points each."""
        calculator = HealthScoreCalculator()
        
        # 5 warning alerts = 10 points penalty
        metrics = HealthMetrics(alerts_warning=5, backup_status="success")
        result = calculator.calculate(metrics)
        assert result.score == 90
    
    def test_backup_failed_penalty(self):
        """Failed backup = full backup weight penalty."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(backup_status="failed")
        result = calculator.calculate(metrics)
        
        # Default backup weight is 15
        assert result.score == 85
    
    def test_backup_partial_penalty(self):
        """Partial backup = half backup weight penalty."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(backup_status="partial")
        result = calculator.calculate(metrics)
        
        # Half of 15 = 7 (rounded)
        assert result.score == 93
    
    def test_backup_unknown_penalty(self):
        """Unknown backup = 33% of backup weight penalty."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(backup_status="unknown")
        result = calculator.calculate(metrics)
        
        # 33% of 15 ~= 4-5 points, so 95-96
        assert 95 <= result.score <= 96
    
    def test_config_drift_penalty(self):
        """Config drift = full compliance weight penalty."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(
            config_drift_detected=True, 
            backup_status="success"  # Explicit to isolate test
        )
        result = calculator.calculate(metrics)
        
        # Default config_compliance weight is 15
        assert result.score == 85
        assert result.requires_review
        assert "Config drift detected" in result.review_reasons
    
    def test_multiple_issues_compound(self):
        """Multiple issues should compound penalties."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(
            devices_online=8,
            devices_total=10,           # -6 points (20% of 30)
            alerts_warning=5,            # -10 points
            backup_status="partial",     # -7 points (50% of 15)
            config_drift_detected=True   # -15 points
        )
        result = calculator.calculate(metrics)
        
        # 100 - 6 - 10 - 7 - 15 = 62 (but int rounding may give 63)
        assert 62 <= result.score <= 63
        assert result.status == HealthStatus.WARNING
    
    def test_unhealthy_site(self, unhealthy_site_metrics):
        """Unhealthy site should have low score and require review."""
        calculator = HealthScoreCalculator()
        result = calculator.calculate_from_dict(unhealthy_site_metrics)
        
        assert result.score < 50
        assert result.status == HealthStatus.CRITICAL
        assert result.requires_review
        assert len(result.review_reasons) > 0
    
    def test_score_clamped_to_zero(self):
        """Score should never go below 0."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(
            devices_online=0,
            devices_total=100,
            alerts_critical=10,
            backup_status="failed",
            config_drift_detected=True
        )
        result = calculator.calculate(metrics)
        assert result.score >= 0
    
    def test_score_clamped_to_100(self):
        """Score should never exceed 100 (edge case)."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(backup_status="success")  # Explicit success
        result = calculator.calculate(metrics)
        assert result.score == 100
    
    def test_custom_weights(self):
        """Custom weights should affect scoring."""
        # Device-focused: 50 points for availability
        weights = HealthWeights.device_focused()
        calculator = HealthScoreCalculator(weights=weights)
        
        metrics = HealthMetrics(
            devices_online=5, 
            devices_total=10,
            backup_status="success"  # Explicit to isolate test
        )
        result = calculator.calculate(metrics)
        
        # 50% of 50 points = 25 point penalty
        assert result.score == 75
    
    def test_breakdown_included(self):
        """Result should include point breakdown."""
        calculator = HealthScoreCalculator()
        metrics = HealthMetrics(
            devices_online=10,
            devices_total=10,
            alerts_warning=5,
            backup_status="success"  # Explicit to isolate test
        )
        result = calculator.calculate(metrics)
        
        assert "device_availability" in result.breakdown
        assert "wifi_quality" in result.breakdown
        assert "alerts" in result.breakdown
        assert "backup" in result.breakdown
        assert "config_compliance" in result.breakdown
        
        # Full availability = 30 points
        assert result.breakdown["device_availability"] == 30


class TestConvenienceFunction:
    """Tests for the calculate_health_score convenience function."""
    
    def test_simple_call(self):
        """Convenience function should return integer score."""
        score = calculate_health_score(
            devices_online=10,
            devices_total=10,
            backup_status="success"  # Explicit to get 100
        )
        assert isinstance(score, int)
        assert score == 100
    
    def test_with_issues(self):
        """Convenience function should calculate correctly with issues."""
        score = calculate_health_score(
            devices_online=5,
            devices_total=10,
            alerts_critical=1,
            backup_status="failed"
        )
        assert isinstance(score, int)
        assert score < 100


class TestHealthStatus:
    """Tests for HealthStatus enum."""
    
    def test_healthy_threshold(self):
        """Score >= 80 should be HEALTHY."""
        assert HealthStatus.from_score(100) == HealthStatus.HEALTHY
        assert HealthStatus.from_score(80) == HealthStatus.HEALTHY
    
    def test_warning_threshold(self):
        """Score 50-79 should be WARNING."""
        assert HealthStatus.from_score(79) == HealthStatus.WARNING
        assert HealthStatus.from_score(50) == HealthStatus.WARNING
    
    def test_critical_threshold(self):
        """Score < 50 should be CRITICAL."""
        assert HealthStatus.from_score(49) == HealthStatus.CRITICAL
        assert HealthStatus.from_score(0) == HealthStatus.CRITICAL
