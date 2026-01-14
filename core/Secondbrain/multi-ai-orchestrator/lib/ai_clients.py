#!/usr/bin/env python3
"""
Multi-AI CLI Client Wrappers
Unified interface for Claude CLI, Gemini CLI, and Fara-7B

Author: OberaConnect Engineering
Version: 1.0.0
"""

import subprocess
import json
import os
import tempfile
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROK = "grok"
    FARA = "fara"


@dataclass
class AIResponse:
    """Standardized response from any AI CLI"""
    provider: AIProvider
    success: bool
    content: str
    raw_output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "success": self.success,
            "content": self.content,
            "error": self.error,
            "metadata": self.metadata
        }


class BaseAIClient(ABC):
    """Abstract base class for AI CLI clients"""
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.is_available = self._check_availability()
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """Check if the CLI tool is installed and accessible"""
        pass
    
    @abstractmethod
    def execute(self, prompt: str, **kwargs) -> AIResponse:
        """Execute a prompt and return standardized response"""
        pass
    
    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        pass
    
    def _run_command(self, cmd: List[str], input_text: Optional[str] = None) -> tuple:
        """Run a shell command and return stdout, stderr, returncode"""
        try:
            result = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1
        except Exception as e:
            return "", str(e), -1


class ClaudeCLI(BaseAIClient):
    """
    Claude CLI wrapper
    
    Best for:
    - Code generation and refactoring
    - Agentic coding (multi-file edits)
    - Complex reasoning and planning
    - Configuration file generation
    - Documentation writing
    """
    
    def __init__(self, timeout: int = 300, model: str = "sonnet"):
        self.model = model
        super().__init__(timeout)
    
    @property
    def provider(self) -> AIProvider:
        return AIProvider.CLAUDE
    
    def _check_availability(self) -> bool:
        stdout, stderr, code = self._run_command(["which", "claude"])
        return code == 0
    
    def execute(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        files: Optional[List[str]] = None,
        output_format: str = "text",
        allowedTools: Optional[List[str]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Execute Claude CLI with prompt
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            files: List of file paths to include as context
            output_format: "text" or "json"
            allowedTools: List of allowed tools (e.g., ["Bash", "Read", "Write"])
        """
        cmd = ["claude", "-p", prompt]
        
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])
        
        if output_format == "json":
            cmd.append("--output-format=json")
        
        if allowedTools:
            cmd.extend(["--allowedTools", ",".join(allowedTools)])
        
        if files:
            for f in files:
                if Path(f).exists():
                    cmd.extend(["--file", f])
        
        logger.debug(f"Executing Claude CLI: {' '.join(cmd)}")
        stdout, stderr, code = self._run_command(cmd)
        
        success = code == 0 and stdout
        content = stdout.strip() if success else ""
        
        return AIResponse(
            provider=self.provider,
            success=success,
            content=content,
            raw_output=stdout,
            error=stderr if not success else None,
            metadata={"model": self.model, "files_included": files or []}
        )
    
    def execute_with_tools(
        self,
        prompt: str,
        tools: List[str] = ["Bash", "Read", "Write", "Edit"],
        working_dir: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Execute Claude in agentic mode with tool access"""
        cmd = ["claude", "-p", prompt, "--allowedTools", ",".join(tools)]
        
        if working_dir:
            cmd = ["cd", working_dir, "&&"] + cmd
        
        stdout, stderr, code = self._run_command(cmd)
        
        return AIResponse(
            provider=self.provider,
            success=code == 0,
            content=stdout.strip(),
            raw_output=stdout,
            error=stderr if code != 0 else None,
            metadata={"tools": tools, "working_dir": working_dir}
        )


class GeminiCLI(BaseAIClient):
    """
    Gemini CLI wrapper
    
    Best for:
    - Long document analysis (1M+ tokens)
    - Video/audio analysis
    - Large log file processing
    - Multi-modal tasks
    """
    
    def __init__(self, timeout: int = 600, model: str = "gemini-2.5-pro"):
        self.model = model
        super().__init__(timeout)
    
    @property
    def provider(self) -> AIProvider:
        return AIProvider.GEMINI
    
    def _check_availability(self) -> bool:
        stdout, stderr, code = self._run_command(["which", "gemini"])
        return code == 0
    
    def execute(
        self,
        prompt: str,
        files: Optional[List[str]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Execute Gemini CLI with prompt
        
        Args:
            prompt: The user prompt
            files: List of file paths (supports large files, video, audio)
        """
        # Gemini CLI uses @./path syntax for file references in the prompt
        full_prompt = prompt
        if files:
            file_refs = []
            for f in files:
                if Path(f).exists():
                    # Use @ syntax for file inclusion
                    file_refs.append(f"@{f}")
            if file_refs:
                full_prompt = f"{prompt}\n\nFiles: {' '.join(file_refs)}"
        
        cmd = ["gemini", "-p", full_prompt]
        
        logger.debug(f"Executing Gemini CLI: {' '.join(cmd)}")
        stdout, stderr, code = self._run_command(cmd)
        
        success = code == 0 and stdout
        
        return AIResponse(
            provider=self.provider,
            success=success,
            content=stdout.strip() if success else "",
            raw_output=stdout,
            error=stderr if not success else None,
            metadata={"model": self.model, "files_included": files or []}
        )
    
    def analyze_large_file(
        self,
        file_path: str,
        analysis_prompt: str,
        **kwargs
    ) -> AIResponse:
        """Specialized method for large file analysis"""
        if not Path(file_path).exists():
            return AIResponse(
                provider=self.provider,
                success=False,
                content="",
                raw_output="",
                error=f"File not found: {file_path}"
            )
        
        file_size = Path(file_path).stat().st_size
        return self.execute(
            prompt=analysis_prompt,
            files=[file_path],
            metadata={"file_size_bytes": file_size}
        )


class FaraCLI(BaseAIClient):
    """
    Fara-7B CLI wrapper
    
    Best for:
    - Web UI automation (clicks, forms, navigation)
    - RPA-style browser tasks
    - Portal automation (no API access)
    - Visual web scraping
    - Local/air-gapped execution
    - Sensitive data workflows (on-device)
    """
    
    def __init__(self, timeout: int = 600, sandbox: bool = True):
        self.sandbox = sandbox
        self.fara_dir = Path.home() / "fara"
        super().__init__(timeout)
    
    @property
    def provider(self) -> AIProvider:
        return AIProvider.FARA
    
    def _check_availability(self) -> bool:
        # Check if fara is installed
        fara_cli = self.fara_dir / ".venv" / "bin" / "python"
        return fara_cli.exists() or shutil.which("fara-cli") is not None
    
    def execute(
        self,
        task: str,
        url: Optional[str] = None,
        screenshot_dir: Optional[str] = None,
        max_steps: int = 50,
        **kwargs
    ) -> AIResponse:
        """
        Execute Fara-7B for web automation task
        
        Args:
            task: Natural language description of the task
            url: Starting URL for the task
            screenshot_dir: Directory to save screenshots
            max_steps: Maximum number of steps before stopping
        """
        # Build command for fara-cli
        cmd = [
            str(self.fara_dir / ".venv" / "bin" / "python"),
            "-m", "fara.cli",
            "--task", task,
            "--max-steps", str(max_steps)
        ]
        
        if url:
            cmd.extend(["--url", url])
        
        if screenshot_dir:
            cmd.extend(["--screenshot-dir", screenshot_dir])
        
        if self.sandbox:
            cmd.append("--sandbox")
        
        logger.debug(f"Executing Fara CLI: {' '.join(cmd)}")
        stdout, stderr, code = self._run_command(cmd)
        
        return AIResponse(
            provider=self.provider,
            success=code == 0,
            content=stdout.strip(),
            raw_output=stdout,
            error=stderr if code != 0 else None,
            metadata={
                "url": url,
                "max_steps": max_steps,
                "sandbox": self.sandbox
            }
        )
    
    def automate_portal(
        self,
        portal_url: str,
        task_description: str,
        credentials_env: Optional[Dict[str, str]] = None,
        approval_required: bool = True,
        **kwargs
    ) -> AIResponse:
        """
        Automate a web portal task with optional credential injection
        
        Note: Fara-7B will pause at "Critical Points" requiring user approval
        """
        task = task_description
        if approval_required:
            task += " (Wait for my approval before submitting any forms or making purchases)"
        
        # Set environment variables for credentials if provided
        env = os.environ.copy()
        if credentials_env:
            env.update(credentials_env)
        
        return self.execute(
            task=task,
            url=portal_url,
            **kwargs
        )


class GrokCLI(BaseAIClient):
    """
    Grok CLI wrapper (xAI)

    Best for:
    - Real-time information (X/Twitter integration)
    - Conversational responses
    - Current events analysis
    - Alternative perspective on technical decisions
    """

    def __init__(self, timeout: int = 300):
        super().__init__(timeout)

    @property
    def provider(self) -> AIProvider:
        return AIProvider.GROK

    def _check_availability(self) -> bool:
        stdout, stderr, code = self._run_command(["which", "grok"])
        return code == 0

    def execute(
        self,
        prompt: str,
        files: Optional[List[str]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Execute Grok CLI with prompt

        Args:
            prompt: The user prompt
            files: List of file paths to include
        """
        cmd = ["grok", "-p", prompt]

        if files:
            for f in files:
                if Path(f).exists():
                    cmd.extend(["--file", f])

        logger.debug(f"Executing Grok CLI: {' '.join(cmd)}")
        stdout, stderr, code = self._run_command(cmd)

        success = code == 0 and stdout

        return AIResponse(
            provider=self.provider,
            success=success,
            content=stdout.strip() if success else "",
            raw_output=stdout,
            error=stderr if not success else None,
            metadata={"files_included": files or []}
        )


class AIClientFactory:
    """Factory for creating AI clients"""

    _clients: Dict[AIProvider, BaseAIClient] = {}

    @classmethod
    def get_client(cls, provider: AIProvider, **kwargs) -> BaseAIClient:
        """Get or create an AI client for the specified provider"""
        if provider not in cls._clients:
            if provider == AIProvider.CLAUDE:
                cls._clients[provider] = ClaudeCLI(**kwargs)
            elif provider == AIProvider.GEMINI:
                cls._clients[provider] = GeminiCLI(**kwargs)
            elif provider == AIProvider.GROK:
                cls._clients[provider] = GrokCLI(**kwargs)
            elif provider == AIProvider.FARA:
                cls._clients[provider] = FaraCLI(**kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        return cls._clients[provider]
    
    @classmethod
    def get_available_clients(cls) -> List[AIProvider]:
        """Return list of available AI providers"""
        available = []
        for provider in AIProvider:
            client = cls.get_client(provider)
            if client.is_available:
                available.append(provider)
        return available


def select_best_client(task_type: str) -> AIProvider:
    """
    Select the best AI provider for a given task type
    
    Task types:
    - code_generation, code_refactoring, agentic_coding
    - long_document_analysis, video_analysis, audio_analysis
    - web_automation, portal_automation, rpa, web_scraping
    - config_generation, documentation
    - reasoning, planning
    - local_execution, sensitive_data
    """
    task_mapping = {
        # Claude excels at
        "code_generation": AIProvider.CLAUDE,
        "code_refactoring": AIProvider.CLAUDE,
        "agentic_coding": AIProvider.CLAUDE,
        "config_generation": AIProvider.CLAUDE,
        "documentation": AIProvider.CLAUDE,
        "reasoning": AIProvider.CLAUDE,
        "planning": AIProvider.CLAUDE,
        "network_scripting": AIProvider.CLAUDE,
        
        # Gemini excels at
        "long_document_analysis": AIProvider.GEMINI,
        "video_analysis": AIProvider.GEMINI,
        "audio_analysis": AIProvider.GEMINI,
        "large_log_analysis": AIProvider.GEMINI,
        "multimodal": AIProvider.GEMINI,
        
        # Fara excels at
        "web_automation": AIProvider.FARA,
        "portal_automation": AIProvider.FARA,
        "rpa": AIProvider.FARA,
        "web_scraping": AIProvider.FARA,
        "form_filling": AIProvider.FARA,
        "local_execution": AIProvider.FARA,
        "sensitive_data": AIProvider.FARA,
        "browser_task": AIProvider.FARA,
    }
    
    return task_mapping.get(task_type.lower(), AIProvider.CLAUDE)
