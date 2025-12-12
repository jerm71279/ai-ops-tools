"""
Layer 1: Request Handler
Unified request handling and routing
"""

from typing import Callable, Dict, Optional

from ..core.base import AIRequest, AIResponse
from ..core.logging import get_logger


class RequestHandler:
    """
    Unified request handler for all interface types

    Routes requests from CLI, API, webhooks to the processing pipeline
    """

    def __init__(self):
        self.logger = get_logger("ai_os.request_handler")
        self._preprocessors: list = []
        self._postprocessors: list = []
        self._processor: Optional[Callable] = None

    def set_processor(self, callback: Callable):
        """Set the main request processor"""
        self._processor = callback

    def add_preprocessor(self, callback: Callable):
        """Add a request preprocessor"""
        self._preprocessors.append(callback)

    def add_postprocessor(self, callback: Callable):
        """Add a response postprocessor"""
        self._postprocessors.append(callback)

    async def handle(self, request: AIRequest) -> AIResponse:
        """
        Handle a request through the full pipeline

        1. Run preprocessors
        2. Process request
        3. Run postprocessors
        4. Return response
        """
        # Run preprocessors
        for preprocessor in self._preprocessors:
            try:
                request = await preprocessor(request) if asyncio.iscoroutinefunction(preprocessor) else preprocessor(request)
            except Exception as e:
                self.logger.error(f"Preprocessor error: {e}")

        # Process request
        if self._processor:
            try:
                import asyncio
                if asyncio.iscoroutinefunction(self._processor):
                    response = await self._processor(request)
                else:
                    response = self._processor(request)
            except Exception as e:
                self.logger.error(f"Processor error: {e}")
                response = AIResponse.error_response(
                    request_id=request.request_id,
                    error=str(e)
                )
        else:
            response = AIResponse.error_response(
                request_id=request.request_id,
                error="No processor configured"
            )

        # Run postprocessors
        for postprocessor in self._postprocessors:
            try:
                import asyncio
                response = await postprocessor(response) if asyncio.iscoroutinefunction(postprocessor) else postprocessor(response)
            except Exception as e:
                self.logger.error(f"Postprocessor error: {e}")

        return response


import asyncio  # Import at module level for the handler
