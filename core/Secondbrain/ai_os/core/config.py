"""
AI Operating System - Configuration Management
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class LayerConfig:
    """Configuration for a single layer"""
    enabled: bool = True
    timeout: int = 300
    max_retries: int = 3
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIConfig:
    """
    Master configuration for the AI Operating System
    """
    # General settings
    name: str = "OberaConnect AI-OS"
    version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = True

    # Paths
    base_path: str = field(default_factory=lambda: str(Path.cwd()))
    data_path: str = "ai_os_data"
    log_path: str = "ai_os_logs"

    # Layer 1: Interface
    interface: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "cli": {"enabled": True, "prompt": "ai-os> "},
        "api": {"enabled": False, "host": "0.0.0.0", "port": 8080},
        "webhook": {"enabled": False, "secret": None}
    })

    # Layer 2: Intelligence
    intelligence: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "moe_router": {
            "model": "gemini-2.0-flash",
            "confidence_threshold": 0.7
        },
        "intent_parser": {
            "enabled": True
        },
        "context_manager": {
            "max_context_length": 32000,
            "history_depth": 10
        }
    })

    # Layer 3: Orchestration
    orchestration: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "max_parallel_pipelines": 5,
        "checkpoint_enabled": True,
        "retry_policy": {
            "max_retries": 3,
            "backoff": "exponential",
            "initial_delay": 1,
            "max_delay": 60
        },
        "timeout_default": 300
    })

    # Layer 4: Agents
    agents: Dict[str, Any] = field(default_factory=lambda: {
        "claude": {
            "enabled": True,
            "model": "claude-sonnet-4-20250514",
            "timeout": 300,
            "capabilities": ["code", "config", "reasoning", "analysis"]
        },
        "gemini": {
            "enabled": True,
            "model": "gemini-2.0-flash",
            "timeout": 600,
            "capabilities": ["large_docs", "video", "audio", "multimodal"]
        },
        "fara": {
            "enabled": True,
            "headless": True,
            "timeout": 300,
            "capabilities": ["web_ui", "portal", "scraping", "automation"]
        },
        "obsidian": {
            "enabled": True,
            "vault_path": None,
            "capabilities": ["knowledge", "notes", "search"]
        },
        "ba": {
            "enabled": True,
            "capabilities": ["analytics", "reporting", "quotes"]
        }
    })

    # Layer 5: Resources
    resources: Dict[str, Any] = field(default_factory=lambda: {
        "vector_db": {
            "provider": "chromadb",
            "persist_path": "./chromadb_data",
            "collection_name": "ai_os_knowledge"
        },
        "state_store": {
            "provider": "sqlite",
            "path": "./ai_os_state.db"
        },
        "mcp_servers": {
            "obsidian": {"enabled": True, "vault_path": None},
            "sharepoint": {"enabled": False},
            "keeper": {"enabled": False},
            "notebooklm": {"enabled": True}
        },
        "external_services": {
            "ninjaone": {"enabled": False, "api_key": None},
            "ms365": {"enabled": False, "tenant_id": None},
            "azure": {"enabled": False}
        }
    })

    # Logging
    logging: Dict[str, Any] = field(default_factory=lambda: {
        "level": "INFO",
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "file": True,
        "console": True,
        "structured": False  # JSON logging
    })

    def get_layer_config(self, layer: str) -> Dict[str, Any]:
        """Get configuration for a specific layer"""
        layer_map = {
            "interface": self.interface,
            "intelligence": self.intelligence,
            "orchestration": self.orchestration,
            "agents": self.agents,
            "resources": self.resources
        }
        return layer_map.get(layer, {})

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return self.agents.get(agent_name, {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "environment": self.environment,
            "debug": self.debug,
            "base_path": self.base_path,
            "data_path": self.data_path,
            "log_path": self.log_path,
            "interface": self.interface,
            "intelligence": self.intelligence,
            "orchestration": self.orchestration,
            "agents": self.agents,
            "resources": self.resources,
            "logging": self.logging
        }

    def save(self, path: Optional[str] = None):
        """Save configuration to file"""
        path = path or os.path.join(self.base_path, "ai_os_config.json")
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'AIConfig':
        """Load configuration from file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)


def load_config(config_path: Optional[str] = None) -> AIConfig:
    """
    Load configuration from file or create default
    """
    if config_path and Path(config_path).exists():
        return AIConfig.load(config_path)

    # Check default locations
    default_paths = [
        "./ai_os_config.json",
        "./ai_os/config.json",
        os.path.expanduser("~/.ai_os/config.json")
    ]

    for path in default_paths:
        if Path(path).exists():
            return AIConfig.load(path)

    # Return default config
    return AIConfig()


# Global config instance
_config: Optional[AIConfig] = None


def get_config() -> AIConfig:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: AIConfig):
    """Set global config instance"""
    global _config
    _config = config
