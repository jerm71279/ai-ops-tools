"""
Layer 1: CLI Interface
Command-line interface for the AI Operating System
"""

import asyncio
import sys
from typing import Callable, Optional

from ..core.base import AIRequest, AIResponse
from ..core.logging import get_logger


class CLIInterface:
    """
    Command Line Interface for AI OS

    Provides interactive terminal access to the AI Operating System
    """

    def __init__(
        self,
        prompt: str = "ai-os> ",
        process_callback: Callable = None
    ):
        self.prompt = prompt
        self.process_callback = process_callback
        self.logger = get_logger("ai_os.cli")
        self._running = False
        self._history: list = []

    def set_processor(self, callback: Callable):
        """Set the callback for processing requests"""
        self.process_callback = callback

    async def run(self):
        """Run the interactive CLI loop"""
        self._running = True
        self._print_banner()

        while self._running:
            try:
                # Get user input
                user_input = await self._get_input()

                if user_input is None:
                    continue

                # Handle built-in commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self._running = False
                    print("\nGoodbye!")
                    break

                if user_input.lower() == 'clear':
                    self._clear_screen()
                    continue

                if not user_input.strip():
                    continue

                # Add to history
                self._history.append(user_input)

                # Create request
                request = self._create_request(user_input)

                # Process request
                if self.process_callback:
                    response = await self.process_callback(request)
                    self._display_response(response)
                else:
                    print("No processor configured")

            except KeyboardInterrupt:
                print("\n^C")
                continue
            except EOFError:
                self._running = False
                break
            except Exception as e:
                self.logger.error(f"CLI error: {e}")
                print(f"Error: {e}")

    async def _get_input(self) -> Optional[str]:
        """Get input from user (async-compatible)"""
        try:
            # Use asyncio-compatible input
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: input(self.prompt))
        except (EOFError, KeyboardInterrupt):
            return None

    def _create_request(self, content: str) -> AIRequest:
        """Create a request from CLI input"""
        # Detect request type from input
        request_type = "general"

        if content.startswith('/'):
            request_type = "command"
            content = content[1:]
        elif content.startswith('?'):
            request_type = "query"
            content = content[1:]
        elif content.startswith('!'):
            request_type = "workflow"
            content = content[1:]

        return AIRequest(
            content=content.strip(),
            request_type=request_type,
            source="cli"
        )

    def _display_response(self, response: AIResponse):
        """Display response to user"""
        print()

        if response.success:
            if isinstance(response.content, dict):
                import json
                print(json.dumps(response.content, indent=2))
            elif isinstance(response.content, str):
                print(response.content)
            else:
                print(str(response.content))

            # Show artifacts if present
            if response.artifacts:
                print("\n--- Artifacts ---")
                for key, value in response.artifacts.items():
                    if isinstance(value, dict):
                        import json
                        print(f"{key}: {json.dumps(value, indent=2)}")
                    else:
                        print(f"{key}: {value}")
        else:
            print(f"Error: {response.error}")

        # Show execution info
        print(f"\n[{response.executed_by}] {response.duration_ms:.0f}ms")
        print()

    def _print_banner(self):
        """Print welcome banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    AI OPERATING SYSTEM                       ║
║                       OberaConnect                           ║
╠══════════════════════════════════════════════════════════════╣
║  Type your request or use:                                   ║
║    /command  - Execute system command                        ║
║    ?query    - Query knowledge base                          ║
║    !workflow - Run a workflow                                ║
║    exit      - Exit the system                               ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)

    def _clear_screen(self):
        """Clear the terminal screen"""
        import os
        os.system('clear' if os.name != 'nt' else 'cls')

    def run_once(self, content: str) -> AIResponse:
        """Run a single command (non-interactive)"""
        request = self._create_request(content)

        if self.process_callback:
            return asyncio.run(self.process_callback(request))

        return AIResponse.error_response(
            request_id=request.request_id,
            error="No processor configured"
        )
