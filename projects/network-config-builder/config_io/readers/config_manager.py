#!/usr/bin/env python3
"""
Configuration Management
Helpers for loading and managing configuration files (JSON, YAML, INI, ENV).
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from configparser import ConfigParser


class Config:
    """Configuration manager supporting multiple formats."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (JSON, YAML, INI, or .env)
        """
        self.data: Dict[str, Any] = {}
        if config_file:
            self.load(config_file)
    
    def load(self, config_file: str) -> 'Config':
        """Load configuration from file based on extension."""
        path = Path(config_file)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        ext = path.suffix.lower()
        
        if ext == '.json':
            self.data = self._load_json(path)
        elif ext in ['.yaml', '.yml']:
            self.data = self._load_yaml(path)
        elif ext == '.ini':
            self.data = self._load_ini(path)
        elif ext == '.env':
            self.data = self._load_env(path)
        else:
            raise ValueError(f"Unsupported config file format: {ext}")
        
        return self
    
    def _load_json(self, path: Path) -> Dict:
        """Load JSON configuration."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML configuration."""
        try:
            import yaml
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
    
    def _load_ini(self, path: Path) -> Dict:
        """Load INI configuration."""
        parser = ConfigParser()
        parser.read(path)
        return {section: dict(parser.items(section)) for section in parser.sections()}
    
    def _load_env(self, path: Path) -> Dict:
        """Load .env file configuration."""
        config = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support.
        
        Example:
            config.get('database.host', 'localhost')
        """
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support."""
        keys = key.split('.')
        data = self.data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self, config_file: str) -> None:
        """Save configuration to file."""
        path = Path(config_file)
        ext = path.suffix.lower()
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if ext == '.json':
            with open(path, 'w') as f:
                json.dump(self.data, f, indent=2)
        elif ext in ['.yaml', '.yml']:
            try:
                import yaml
                with open(path, 'w') as f:
                    yaml.dump(self.data, f, default_flow_style=False)
            except ImportError:
                raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
        elif ext == '.ini':
            parser = ConfigParser()
            for section, values in self.data.items():
                parser.add_section(str(section))
                for key, value in values.items():
                    parser.set(str(section), str(key), str(value))
            with open(path, 'w') as f:
                parser.write(f)
        else:
            raise ValueError(f"Unsupported save format: {ext}")
    
    def merge_env(self, prefix: str = "") -> 'Config':
        """
        Merge environment variables into config.
        
        Args:
            prefix: Only include env vars starting with this prefix
        
        Example:
            config.merge_env("MYAPP_")  # Includes MYAPP_DATABASE_HOST, etc.
        """
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue
            
            # Remove prefix and convert to lowercase dot notation
            config_key = key[len(prefix):].lower().replace('_', '.')
            self.set(config_key, value)
        
        return self
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-style assignment."""
        self.set(key, value)


# Example usage
if __name__ == "__main__":
    # Load JSON config
    config = Config('config.json')
    db_host = config.get('database.host', 'localhost')
    
    # Load with env override
    config = Config('config.json').merge_env('MYAPP_')
    
    # Set and save
    config.set('api.timeout', 30)
    config.save('config_updated.json')
    
    # Dict-style access
    timeout = config['api.timeout']
