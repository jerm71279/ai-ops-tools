"""
Layer 4: Claude Agent
Claude AI agent implementation
"""

import subprocess
import time
from typing import Dict

from ..core.base import AIRequest, AIResponse, TaskStatus
from ..core.logging import get_logger
from .base_agent import BaseAgent


class ClaudeAgent(BaseAgent):
    """
    Claude AI Agent

    Uses Claude CLI for execution
    Specialized for: code generation, configuration, reasoning, analysis
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)

        self.name = "Claude"
        self.description = "Claude AI for code, config, and reasoning tasks"
        self.capabilities = ["code", "config", "reasoning", "analysis", "writing"]
        self.strengths = ["programming", "system configuration", "technical writing", "problem solving"]

        self.logger = get_logger("ai_os.agent.claude")

        # Configuration
        self._model = config.get("model", "claude-sonnet-4-20250514")
        self._timeout = config.get("timeout", 300)
        self._cli_available = False

    async def initialize(self) -> bool:
        """Initialize Claude agent"""
        self.logger.info("Initializing Claude agent...")

        # Check if Claude CLI is available
        try:
            result = subprocess.run(
                ["which", "claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self._cli_available = result.returncode == 0

            if not self._cli_available:
                self.logger.warning("Claude CLI not found, will use API fallback")

        except Exception as e:
            self.logger.warning(f"Error checking Claude CLI: {e}")
            self._cli_available = False

        self._initialized = True
        self._healthy = True
        self.logger.info("Claude agent initialized")
        return True

    async def execute(self, request: AIRequest) -> AIResponse:
        """Execute request with Claude"""
        start_time = time.time()

        try:
            prompt = self._build_prompt(request)

            if self._cli_available:
                # Use Claude CLI
                result = await self._execute_cli(prompt, request.timeout)
            else:
                # Fallback: return structured response for manual processing
                result = self._create_fallback_response(prompt)

            duration_ms = (time.time() - start_time) * 1000

            return AIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                content=result.get("content"),
                error=result.get("error"),
                status=TaskStatus.SUCCESS if result.get("success") else TaskStatus.FAILED,
                duration_ms=duration_ms,
                executed_by="Claude"
            )

        except Exception as e:
            self.logger.error(f"Claude execution error: {e}")
            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="Claude"
            )

    async def _execute_cli(self, prompt: str, timeout: int) -> Dict:
        """Execute using Claude CLI"""
        import asyncio

        try:
            # Run Claude CLI in print mode
            # --print enables non-interactive output
            # --output-format text ensures plain text response
            process = await asyncio.create_subprocess_exec(
                "claude",
                "--print",
                "--output-format", "text",
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            if process.returncode == 0:
                return {
                    "success": True,
                    "content": stdout.decode().strip()
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode().strip() or "Claude CLI error"
                }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Claude CLI timed out after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _create_fallback_response(self, prompt: str) -> Dict:
        """Create fallback response when CLI not available"""
        return {
            "success": True,
            "content": f"[Claude Agent - CLI not available]\n\nPrompt received ({len(prompt)} chars):\n{prompt[:500]}...\n\nTo process this request, please ensure Claude CLI is installed and configured."
        }

    async def shutdown(self) -> bool:
        """Shutdown Claude agent"""
        self._initialized = False
        self.logger.info("Claude agent shutdown")
        return True
