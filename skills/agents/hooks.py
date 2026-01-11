#!/usr/bin/env python3
"""
Claude Code Hooks Integration
Hooks that integrate with the agent system.
"""

import json
import sys
import os
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from loader import AgentLoader


def pre_tool_hook():
    """
    Pre-tool hook for Task tool calls.
    Can validate or suggest agents before invocation.

    Hook type: PreToolUse
    Tool: Task

    Returns JSON with:
      - "decision": "allow" | "block" | "modify"
      - "reason": explanation
      - "modification": (optional) modified parameters
    """
    # Read hook input from stdin
    input_data = json.loads(sys.stdin.read())

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only process Task tool
    if tool_name != "Task":
        print(json.dumps({"decision": "allow"}))
        return

    subagent_type = tool_input.get("subagent_type", "")
    prompt = tool_input.get("prompt", "")

    # Load agents to validate
    loader = AgentLoader(Path(__file__).parent)
    loader.load_all()

    # Check if agent exists
    agent = loader.get(subagent_type)

    if not agent:
        # Suggest an alternative
        suggested = loader.suggest_agent(prompt)
        if suggested:
            print(json.dumps({
                "decision": "allow",
                "reason": f"Agent '{subagent_type}' not in registry. Suggested: {suggested.name}"
            }))
        else:
            print(json.dumps({"decision": "allow"}))
        return

    # Log the agent being used
    print(json.dumps({
        "decision": "allow",
        "reason": f"Using {agent.name} agent ({agent.model})"
    }))


def post_tool_hook():
    """
    Post-tool hook for logging agent completions.

    Hook type: PostToolUse
    Tool: Task
    """
    input_data = json.loads(sys.stdin.read())

    tool_name = input_data.get("tool_name", "")
    tool_output = input_data.get("tool_output", "")

    if tool_name != "Task":
        return

    # Could log agent completions, metrics, etc.
    # For now, just pass through


def notification_hook():
    """
    Notification hook - triggered on agent events.

    Hook type: Notification
    """
    input_data = json.loads(sys.stdin.read())
    event = input_data.get("event", "")

    # Handle specific events
    if event == "agent_started":
        agent_type = input_data.get("agent_type", "unknown")
        # Could send desktop notification, log, etc.

    elif event == "agent_completed":
        agent_type = input_data.get("agent_type", "unknown")
        # Could track metrics, send notification


def list_agents_hook():
    """
    Hook to list available agents.
    Can be triggered by a custom slash command.
    """
    loader = AgentLoader(Path(__file__).parent)
    agents = loader.load_all()

    output = ["Available Agents:", ""]
    for name, agent in sorted(agents.items()):
        output.append(f"  {agent.name} [{agent.model}]")
        output.append(f"    {agent.description}")
        output.append("")

    print("\n".join(output))


if __name__ == "__main__":
    # Determine which hook to run based on argument
    if len(sys.argv) < 2:
        print("Usage: hooks.py [pre|post|notify|list]")
        sys.exit(1)

    hook_type = sys.argv[1]

    hooks = {
        "pre": pre_tool_hook,
        "post": post_tool_hook,
        "notify": notification_hook,
        "list": list_agents_hook
    }

    hook_func = hooks.get(hook_type)
    if hook_func:
        hook_func()
    else:
        print(f"Unknown hook type: {hook_type}")
        sys.exit(1)
