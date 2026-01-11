#!/usr/bin/env python3
"""
Agent Loader Module
Loads and parses agent descriptors from YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AgentInvocation:
    """Invocation details for an agent."""
    subagent_type: str
    examples: List[Dict[str, str]] = field(default_factory=list)
    thoroughness_levels: Optional[Dict[str, str]] = None
    resume_behavior: Optional[str] = None


@dataclass
class Agent:
    """Represents a loaded agent configuration."""
    name: str
    description: str
    model: str
    tools: List[str]
    system_prompt: str
    invocation: AgentInvocation
    path: Path
    vendor_services: Optional[List[str]] = None
    friendly_name: Optional[str] = None
    user_description: Optional[str] = None

    def get_task_call(self, prompt: str, description: str = None) -> Dict:
        """Generate Task tool parameters for this agent."""
        return {
            "subagent_type": self.invocation.subagent_type,
            "prompt": prompt,
            "description": description or f"{self.name} task",
            "model": self.model if self.model != "default" else None
        }

    def to_dict(self) -> Dict:
        """Convert agent to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "tools": self.tools,
            "system_prompt": self.system_prompt,
            "invocation": {
                "subagent_type": self.invocation.subagent_type,
                "examples": self.invocation.examples
            }
        }


class AgentLoader:
    """Loads agent configurations from YAML files."""

    def __init__(self, agents_dir: str = None):
        """
        Initialize the loader.

        Args:
            agents_dir: Path to agents directory. Defaults to ./agents
        """
        if agents_dir is None:
            agents_dir = Path(__file__).parent
        self.agents_dir = Path(agents_dir)
        self._agents: Dict[str, Agent] = {}
        self._loaded = False

    def load_all(self, force: bool = False) -> Dict[str, Agent]:
        """
        Load all agent configurations.

        Args:
            force: Force reload even if already loaded

        Returns:
            Dictionary of agent name -> Agent
        """
        if self._loaded and not force:
            return self._agents

        self._agents = {}

        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            yaml_file = agent_dir / "agent.yaml"
            if yaml_file.exists():
                agent = self._load_agent(yaml_file)
                if agent:
                    self._agents[agent.name.lower()] = agent

        self._loaded = True
        return self._agents

    def _load_agent(self, yaml_path: Path) -> Optional[Agent]:
        """Load a single agent from YAML file."""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)

            invocation_data = data.get('invocation', {})
            invocation = AgentInvocation(
                subagent_type=invocation_data.get('subagent_type', data['name']),
                examples=invocation_data.get('examples', []),
                thoroughness_levels=invocation_data.get('thoroughness_levels'),
                resume_behavior=invocation_data.get('resume_behavior')
            )

            return Agent(
                name=data['name'],
                description=data['description'],
                model=data.get('model', 'sonnet'),
                tools=data.get('tools', []),
                system_prompt=data.get('system_prompt', ''),
                invocation=invocation,
                path=yaml_path,
                vendor_services=data.get('vendor_services'),
                friendly_name=data.get('friendly_name'),
                user_description=data.get('user_description')
            )
        except Exception as e:
            print(f"Error loading {yaml_path}: {e}")
            return None

    def get(self, name: str) -> Optional[Agent]:
        """Get an agent by name (case-insensitive)."""
        if not self._loaded:
            self.load_all()
        return self._agents.get(name.lower())

    def list_agents(self) -> List[Agent]:
        """Get all loaded agents."""
        if not self._loaded:
            self.load_all()
        return list(self._agents.values())

    def find_by_capability(self, keyword: str) -> List[Agent]:
        """Find agents whose description or tools match a keyword."""
        if not self._loaded:
            self.load_all()

        keyword = keyword.lower()
        matches = []

        for agent in self._agents.values():
            if (keyword in agent.description.lower() or
                keyword in agent.system_prompt.lower() or
                any(keyword in tool.lower() for tool in agent.tools)):
                matches.append(agent)

        return matches

    def suggest_agent(self, task: str) -> Optional[Agent]:
        """Suggest the best agent for a given task description."""
        if not self._loaded:
            self.load_all()

        task_lower = task.lower()

        # Simple keyword matching for suggestions
        suggestions = {
            'explore': ['find', 'search', 'where', 'locate', 'look for'],
            'plan': ['plan', 'design', 'architect', 'strategy', 'implement'],
            'bash': ['run', 'execute', 'git', 'npm', 'docker', 'command'],
            'claude-code-guide': ['claude', 'api', 'hook', 'mcp server', 'sdk'],
            'mcp-integration-overseer': ['integration', 'ninjaone', 'unifi', 'vendor', 'api'],
            'strategic-business-analyst': ['business', 'strategy', 'market', 'quarterly']
        }

        for agent_name, keywords in suggestions.items():
            if any(kw in task_lower for kw in keywords):
                return self._agents.get(agent_name)

        # Default to general-purpose
        return self._agents.get('general-purpose')


# Convenience function
def load_agents(agents_dir: str = None) -> Dict[str, Agent]:
    """Load all agents from the specified directory."""
    loader = AgentLoader(agents_dir)
    return loader.load_all()


if __name__ == "__main__":
    # Test loading
    loader = AgentLoader()
    agents = loader.load_all()

    print(f"Loaded {len(agents)} agents:\n")
    for name, agent in agents.items():
        print(f"  {agent.name}: {agent.description}")
        print(f"    Model: {agent.model}")
        print(f"    Tools: {', '.join(agent.tools[:3])}{'...' if len(agent.tools) > 3 else ''}")
        print()
