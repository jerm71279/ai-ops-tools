"""
Layer 5: Resource Layer
Data stores, MCP servers, and external service integrations
"""

from .resources import ResourceLayer
from .mcp_manager import MCPManager
from .data_store import DataStore

__all__ = [
    'ResourceLayer',
    'MCPManager',
    'DataStore'
]
