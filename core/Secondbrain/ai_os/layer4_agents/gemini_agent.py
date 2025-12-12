"""
Layer 4: Gemini Agent
Google Gemini AI agent implementation
"""

import os
import time
from typing import Dict

from ..core.base import AIRequest, AIResponse, TaskStatus
from ..core.logging import get_logger
from .base_agent import BaseAgent


class GeminiAgent(BaseAgent):
    """
    Gemini AI Agent

    Uses Google Gemini API for execution
    Specialized for: large document analysis, multimodal processing
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)

        self.name = "Gemini"
        self.description = "Google Gemini for large docs and multimodal tasks"
        self.capabilities = ["large_docs", "video", "audio", "multimodal", "research"]
        self.strengths = ["document analysis", "multimedia processing", "web research", "summarization"]

        self.logger = get_logger("ai_os.agent.gemini")

        # Configuration
        self._model = config.get("model", "gemini-2.0-flash")
        self._timeout = config.get("timeout", 600)
        self._api_key = config.get("api_key") or os.environ.get("GEMINI_API_KEY")
        self._client = None

    async def initialize(self) -> bool:
        """Initialize Gemini agent"""
        self.logger.info("Initializing Gemini agent...")

        # Check for API key
        if not self._api_key:
            self.logger.warning("Gemini API key not found")

        # Try to initialize client
        try:
            import google.generativeai as genai

            if self._api_key:
                genai.configure(api_key=self._api_key)
                self._client = genai.GenerativeModel(self._model)
                self._initialized = True
                self._healthy = True
                self.logger.info("Gemini agent initialized with API")
            else:
                self._initialized = True
                self._healthy = False
                self.logger.warning("Gemini agent initialized without API key")

        except ImportError:
            self.logger.warning("google-generativeai package not installed")
            self._initialized = True
            self._healthy = False

        except Exception as e:
            self.logger.error(f"Error initializing Gemini: {e}")
            self._initialized = False
            self._healthy = False

        return self._initialized

    async def execute(self, request: AIRequest) -> AIResponse:
        """Execute request with Gemini"""
        start_time = time.time()

        try:
            prompt = self._build_prompt(request)

            if self._client and self._healthy:
                result = await self._execute_api(prompt)
            else:
                result = self._create_fallback_response(prompt)

            duration_ms = (time.time() - start_time) * 1000

            return AIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                content=result.get("content"),
                error=result.get("error"),
                status=TaskStatus.SUCCESS if result.get("success") else TaskStatus.FAILED,
                duration_ms=duration_ms,
                executed_by="Gemini"
            )

        except Exception as e:
            self.logger.error(f"Gemini execution error: {e}")
            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="Gemini"
            )

    async def _execute_api(self, prompt: str) -> Dict:
        """Execute using Gemini API"""
        try:
            response = self._client.generate_content(prompt)

            if response.text:
                return {
                    "success": True,
                    "content": response.text
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response from Gemini"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _create_fallback_response(self, prompt: str) -> Dict:
        """Create fallback response when API not available"""
        return {
            "success": True,
            "content": f"[Gemini Agent - API not configured]\n\nPrompt received ({len(prompt)} chars):\n{prompt[:500]}...\n\nTo process this request, please configure GEMINI_API_KEY environment variable."
        }

    async def shutdown(self) -> bool:
        """Shutdown Gemini agent"""
        self._client = None
        self._initialized = False
        self.logger.info("Gemini agent shutdown")
        return True
