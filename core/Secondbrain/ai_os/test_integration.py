#!/usr/bin/env python3
"""
AI OS Integration Test
Tests Secondbrain integration with the 5-layer AI Operating System
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_os import AIOS, AIConfig


async def test_initialization():
    """Test AI OS initialization with Secondbrain agents"""
    print("=" * 60)
    print("AI OS Integration Test")
    print("=" * 60)

    # Create AI OS instance
    config = AIConfig()
    ai_os = AIOS(config)

    try:
        # Initialize
        print("\n[1] Testing Initialization...")
        success = await ai_os.initialize()
        print(f"    Initialization: {'✓ Success' if success else '✗ Failed'}")

        # Get status
        print("\n[2] System Status:")
        status = ai_os.get_status()
        print(f"    Initialized: {status['initialized']}")
        for layer, health in status['layers'].items():
            if health:
                healthy = health.get('healthy', False)
                print(f"    {layer}: {'✓ Healthy' if healthy else '⚠ Degraded'}")

        # List agents
        print("\n[3] Available Agents:")
        agents = ai_os.get_agents()
        for agent_id, agent_info in agents.items():
            available = agent_info.get('available', False)
            capabilities = agent_info.get('capabilities', [])
            status_icon = '✓' if available else '✗'
            print(f"    {status_icon} {agent_id}")
            if capabilities:
                print(f"      Capabilities: {', '.join(capabilities[:3])}...")

        # List workflows
        print("\n[4] Available Workflows:")
        workflows = ai_os.get_workflows()
        if workflows:
            for wf in workflows[:5]:
                print(f"    - {wf}")
        else:
            print("    No workflows registered")

        # Test request processing
        print("\n[5] Testing Request Processing:")
        test_requests = [
            ("Search my knowledge base for Python tips", "knowledge"),
            ("Generate a project health report", "business"),
            ("Analyze the patterns in my notes", "analysis"),
            ("Create a Python function to sort data", "code"),
        ]

        for content, expected_category in test_requests:
            print(f"\n    Request: '{content[:40]}...'")
            try:
                response = await ai_os.process(content, timeout=30)
                print(f"    Status: {'✓ Success' if response.success else '✗ Failed'}")
                print(f"    Executed by: {response.executed_by}")
                if response.layer_trace:
                    print(f"    Layer trace: {' → '.join(response.layer_trace[:3])}")
            except Exception as e:
                print(f"    Error: {e}")

        print("\n" + "=" * 60)
        print("Integration Test Complete")
        print("=" * 60)

    finally:
        # Shutdown
        await ai_os.shutdown()


async def test_layer_isolation():
    """Test individual layer functionality"""
    print("\n[Layer Isolation Tests]")

    # Test Layer 2 - Intelligence
    from ai_os.layer2_intelligence import IntelligenceLayer
    from ai_os.core.base import AIRequest

    config = AIConfig()
    layer2 = IntelligenceLayer(config)
    await layer2.initialize()

    # Test classification
    request = AIRequest(content="Search for notes about project management")
    response = await layer2.process(request)

    print(f"\n    Layer 2 Classification Test:")
    print(f"    Input: 'Search for notes about project management'")
    # Classification info is in response.content when L2 processes without orchestration layer
    if isinstance(response.content, dict):
        classification = response.content.get('classification', {})
    else:
        classification = response.metadata.get('classification', {})
    print(f"    Category: {classification.get('primary_category', 'unknown')}")
    print(f"    Suggested agents: {classification.get('suggested_agents', [])}")

    await layer2.shutdown()


async def test_mcp_servers():
    """Test MCP server connections"""
    print("\n[MCP Server Connection Tests]")

    from ai_os.layer5_resources.mcp_manager import MCPManager

    config = AIConfig()
    mcp = MCPManager(config)
    await mcp.initialize()

    servers = mcp.list_servers()
    print(f"\n    Available MCP Servers:")
    for server in servers:
        status = mcp.get_server_status(server)
        tools = mcp.get_server_tools(server)
        print(f"    - {server}: {len(tools)} tools")
        if tools:
            print(f"      Tools: {', '.join(tools[:3])}...")


async def main():
    """Run all integration tests"""
    try:
        await test_initialization()
        await test_layer_isolation()
        await test_mcp_servers()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
