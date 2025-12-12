"""
Layer 4: Agent Layer
Specialized AI agents for task execution
"""

from .agents import AgentLayer
from .base_agent import BaseAgent
from .claude_agent import ClaudeAgent
from .gemini_agent import GeminiAgent
from .secondbrain_agents import ObsidianManagerAgent, BAAgent, NotebookLMAgent

__all__ = [
    'AgentLayer',
    'BaseAgent',
    'ClaudeAgent',
    'GeminiAgent',
    'ObsidianManagerAgent',
    'BAAgent',
    'NotebookLMAgent'
]
