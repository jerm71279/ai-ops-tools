"""
Unit tests for custom exception hierarchy.

Tests error classes and mapping functions.
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.errors import (
    NotionSyncError,
    ConfigurationError,
    DatabaseNotFoundError,
    RateLimitError,
    ValidationError,
    PageNotFoundError,
    RelationError,
    DataSourceError,
    MakerCheckerError,
    map_notion_api_error,
)


class TestNotionSyncError:
    """Tests for base NotionSyncError."""
    
    def test_basic_message(self):
        """Error should store and display message."""
        error = NotionSyncError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
    
    def test_with_details(self):
        """Error should include details in string representation."""
        error = NotionSyncError(
            "Failed to sync",
            {"site": "Acme Corp", "reason": "timeout"}
        )
        assert "Failed to sync" in str(error)
        assert "site" in str(error)
        assert error.details["site"] == "Acme Corp"
    
    def test_inheritance(self):
        """All custom errors should inherit from NotionSyncError."""
        assert issubclass(ConfigurationError, NotionSyncError)
        assert issubclass(DatabaseNotFoundError, NotionSyncError)
        assert issubclass(RateLimitError, NotionSyncError)
        assert issubclass(ValidationError, NotionSyncError)
        assert issubclass(PageNotFoundError, NotionSyncError)


class TestConfigurationError:
    """Tests for ConfigurationError."""
    
    def test_basic_error(self):
        """Should create configuration error."""
        error = ConfigurationError("Missing token")
        assert "Missing token" in str(error)
    
    def test_with_details(self):
        """Should include configuration details."""
        error = ConfigurationError(
            "Invalid config",
            {"path": "/etc/config.json", "field": "token"}
        )
        assert error.details["path"] == "/etc/config.json"


class TestDatabaseNotFoundError:
    """Tests for DatabaseNotFoundError."""
    
    def test_with_name_only(self):
        """Should create error with just database name."""
        error = DatabaseNotFoundError("customer_status")
        assert "customer_status" in str(error)
        assert error.db_name == "customer_status"
        assert error.db_id is None
    
    def test_with_name_and_id(self):
        """Should include database ID when provided."""
        error = DatabaseNotFoundError("customer_status", "db_123456")
        assert error.db_name == "customer_status"
        assert error.db_id == "db_123456"
        assert "db_123456" in str(error.details)


class TestRateLimitError:
    """Tests for RateLimitError."""
    
    def test_basic_error(self):
        """Should create rate limit error."""
        error = RateLimitError()
        assert "rate limit" in str(error).lower()
    
    def test_with_retry_after(self):
        """Should include retry-after hint."""
        error = RateLimitError(retry_after=30.0)
        assert error.retry_after == 30.0
        assert "30" in str(error.details)


class TestValidationError:
    """Tests for ValidationError."""
    
    def test_basic_error(self):
        """Should create validation error."""
        error = ValidationError("email", "Invalid format")
        assert "email" in str(error)
        assert error.field == "email"
    
    def test_with_invalid_value(self):
        """Should include the invalid value."""
        error = ValidationError("score", "Must be 0-100", 150)
        assert error.invalid_value == 150
        assert "150" in str(error.details)
    
    def test_truncates_long_values(self):
        """Should truncate very long invalid values."""
        long_value = "x" * 200
        error = ValidationError("field", "Too long", long_value)
        # Should truncate to 100 chars
        assert len(error.details.get("invalid_value", "")) <= 100


class TestPageNotFoundError:
    """Tests for PageNotFoundError."""
    
    def test_basic_error(self):
        """Should create page not found error."""
        error = PageNotFoundError("Acme Corp")
        assert "Acme Corp" in str(error)
    
    def test_with_database(self):
        """Should include database context."""
        error = PageNotFoundError("Acme Corp", "customer_status")
        assert error.details["database"] == "customer_status"


class TestRelationError:
    """Tests for RelationError."""
    
    def test_basic_error(self):
        """Should describe relation failure."""
        error = RelationError(
            source="health_snapshot",
            target="customer_site",
            reason="Site not found"
        )
        assert "health_snapshot" in str(error)
        assert "customer_site" in str(error)
        assert "Site not found" in str(error)


class TestDataSourceError:
    """Tests for DataSourceError."""
    
    def test_basic_error(self):
        """Should identify data source."""
        error = DataSourceError("UniFi", "Connection timeout")
        assert "UniFi" in str(error)
        assert error.source == "UniFi"
    
    def test_with_original_error(self):
        """Should preserve original exception."""
        original = ConnectionError("Network unreachable")
        error = DataSourceError("NinjaOne", "API failed", original)
        assert error.original_error == original


class TestMakerCheckerError:
    """Tests for MakerCheckerError."""
    
    def test_basic_error(self):
        """Should describe maker/checker failure."""
        error = MakerCheckerError("Bulk operation exceeds threshold")
        assert "Bulk operation" in str(error)
    
    def test_with_threshold(self):
        """Should include threshold value."""
        error = MakerCheckerError("Too many changes", threshold=10)
        assert error.threshold == 10
        assert "10" in str(error.details)


class TestMapNotionApiError:
    """Tests for API error mapping function."""
    
    def test_rate_limit_detection(self):
        """Should detect rate limit errors."""
        
        class MockApiError(Exception):
            pass
        
        # 429 in message
        mock_error = MockApiError("HTTP 429 Too Many Requests")
        result = map_notion_api_error(mock_error)
        assert isinstance(result, RateLimitError)
    
    def test_not_found_detection(self):
        """Should detect not found errors."""
        
        class MockApiError(Exception):
            pass
        
        mock_error = MockApiError("HTTP 404 Not Found")
        result = map_notion_api_error(mock_error)
        assert isinstance(result, PageNotFoundError)
    
    def test_validation_detection(self):
        """Should detect validation errors."""
        
        class MockApiError(Exception):
            pass
        
        mock_error = MockApiError("HTTP 400 Bad Request: validation failed")
        result = map_notion_api_error(mock_error)
        assert isinstance(result, ValidationError)
    
    def test_generic_fallback(self):
        """Unknown errors should map to base NotionSyncError."""
        
        class MockApiError(Exception):
            pass
        
        mock_error = MockApiError("Something unexpected")
        result = map_notion_api_error(mock_error)
        assert isinstance(result, NotionSyncError)
        assert not isinstance(result, RateLimitError)
