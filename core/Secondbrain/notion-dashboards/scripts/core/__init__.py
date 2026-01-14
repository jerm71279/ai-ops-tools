"""
Core modules for OberaConnect Notion integration.

This package provides shared infrastructure:
- Configuration management
- Error handling
- Logging
- Retry logic
- Base sync class
"""

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

from core.config import (
    Config,
    DatabaseIds,
    SyncSettings,
    MakerCheckerConfig,
    load_config,
)

from core.logging_config import (
    setup_logging,
    get_logger,
    enable_debug,
    enable_quiet,
)

from core.retry import (
    retry_on_exception,
    retry_notion_api,
    RetryBudget,
    RetryBudgetExhausted,
)

from core.base_sync import BaseSyncClient

__all__ = [
    # Errors
    "NotionSyncError",
    "ConfigurationError",
    "DatabaseNotFoundError",
    "RateLimitError",
    "ValidationError",
    "PageNotFoundError",
    "RelationError",
    "DataSourceError",
    "MakerCheckerError",
    "map_notion_api_error",
    # Config
    "Config",
    "DatabaseIds",
    "SyncSettings",
    "MakerCheckerConfig",
    "load_config",
    # Logging
    "setup_logging",
    "get_logger",
    "enable_debug",
    "enable_quiet",
    # Retry
    "retry_on_exception",
    "retry_notion_api",
    "RetryBudget",
    "RetryBudgetExhausted",
    # Base class
    "BaseSyncClient",
]
