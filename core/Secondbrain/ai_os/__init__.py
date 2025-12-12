"""
AI Operating System
5-Layer Architecture for Autonomous AI Orchestration

Layers:
1. Interface - CLI, API, Webhooks
2. Intelligence - MoE Routing, Classification
3. Orchestration - Pipelines, Workflows
4. Agents - Claude, Gemini, Fara, Custom
5. Resources - MCP Servers, Data Stores
"""

from .ai_os import AIOS
from .core.config import AIConfig, load_config

__version__ = "1.0.0"
__all__ = ['AIOS', 'AIConfig', 'load_config']
