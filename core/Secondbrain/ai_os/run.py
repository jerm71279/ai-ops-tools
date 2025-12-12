#!/usr/bin/env python3
"""
AI Operating System - Runner Script

Usage:
    # Interactive CLI mode
    python -m ai_os.run

    # Single query mode
    python -m ai_os.run "Search for Python notes"

    # Start API server
    python -m ai_os.run --api

    # Start with webhooks
    python -m ai_os.run --api --webhooks
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_os import AIOS, AIConfig


async def run_cli(ai_os: AIOS):
    """Run interactive CLI"""
    await ai_os.run_cli()


async def run_single(ai_os: AIOS, query: str):
    """Run a single query"""
    print(f"Processing: {query}")
    print("-" * 50)

    response = await ai_os.process(query)

    if response.success:
        print(f"Result:\n{response.content}")
    else:
        print(f"Error: {response.error}")

    print("-" * 50)
    print(f"Executed by: {response.executed_by}")
    print(f"Duration: {response.duration_ms:.2f}ms")


async def run_api(ai_os: AIOS, host: str, port: int, enable_webhooks: bool):
    """Run API server"""
    from ai_os.layer1_interface.api import APIInterface

    # Create API interface
    api = APIInterface(host=host, port=port, process_callback=ai_os.process)
    api.set_status_callback(ai_os.get_status)
    api.set_agents_callback(ai_os.get_agents)
    api.set_workflows_callback(ai_os.get_workflows)

    # Add webhook routes if enabled
    if enable_webhooks:
        from ai_os.layer1_interface.webhooks import WebhookHandler, register_webhook_routes
        webhook_handler = WebhookHandler(process_callback=ai_os.process)

        # Register after app is created
        if api._app:
            register_webhook_routes(api._app, webhook_handler)
            print(f"Webhooks enabled at: /webhooks/github, /webhooks/slack, /webhooks/ninjaone")

    # Start server
    await api.start_server()

    print(f"API server running on http://{host}:{port}")
    print("Endpoints:")
    print("  GET  /           - API info")
    print("  GET  /health     - Health check")
    print("  GET  /status     - System status")
    print("  POST /process    - Process request (sync)")
    print("  POST /process/async - Process request (async)")
    print("  GET  /jobs       - List jobs")
    print("  GET  /agents     - List agents")
    print("  GET  /workflows  - List workflows")
    print("  GET  /ws         - WebSocket streaming")
    print("  GET  /openapi.json - OpenAPI spec")
    print()
    print("Press Ctrl+C to stop")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        await api.stop_server()


async def main():
    parser = argparse.ArgumentParser(
        description="AI Operating System Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive CLI
  %(prog)s "Search for notes"       # Single query
  %(prog)s --api                    # Start API server
  %(prog)s --api --port 9000        # API on custom port
  %(prog)s --api --webhooks         # API with webhooks enabled
"""
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query to process (if not provided, starts interactive CLI)"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server instead of CLI"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="API server port (default: 8080)"
    )
    parser.add_argument(
        "--webhooks",
        action="store_true",
        help="Enable webhook endpoints (requires --api)"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    # Load configuration
    config = AIConfig()
    if args.config:
        from ai_os.core.config import load_config
        config = load_config(args.config)

    # Create AI OS instance
    ai_os = AIOS(config)

    try:
        # Initialize
        await ai_os.initialize()

        if args.api:
            # Run API server
            await run_api(ai_os, args.host, args.port, args.webhooks)
        elif args.query:
            # Run single query
            await run_single(ai_os, args.query)
        else:
            # Run interactive CLI
            await run_cli(ai_os)

    finally:
        await ai_os.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
