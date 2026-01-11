#!/usr/bin/env python3
"""
Agent CLI Tool
List, inspect, and generate invocation commands for agents.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from loader import AgentLoader


def cmd_list(args, loader: AgentLoader):
    """List all available agents."""
    agents = loader.list_agents()

    if args.json:
        data = [{
            "name": a.name,
            "friendly_name": a.friendly_name or a.name,
            "description": a.user_description or a.description,
            "model": a.model
        } for a in agents]
        print(json.dumps(data, indent=2))
        return

    print("\nYour Agent Team")
    print("=" * 60)

    for agent in sorted(agents, key=lambda a: a.friendly_name or a.name):
        display_name = agent.friendly_name or agent.name
        desc = agent.user_description or agent.description
        print(f"\n  {display_name}")
        print(f"  {'-' * len(display_name)}")
        print(f"  {desc}")

        if args.verbose:
            if agent.invocation.examples:
                print(f"\n  Just say:")
                for ex in agent.invocation.examples[:2]:
                    plain = ex.get('plain_english', ex.get('description', ''))
                    print(f"    \"{plain}\"")

    print(f"\n  Total: {len(agents)} helpers")
    print("\n  Tip: Just describe what you need - Claude picks the right one.\n")


def cmd_show(args, loader: AgentLoader):
    """Show detailed information about an agent."""
    # Map friendly names to internal names
    name_map = {
        'explorer': 'explore',
        'planner': 'plan',
        'commander': 'bash',
        'researcher': 'general-purpose',
        'guide': 'claude-code-guide',
        'integrations': 'mcp-integration-overseer',
        'strategist': 'strategic-business-analyst'
    }
    lookup_name = name_map.get(args.name.lower(), args.name)
    agent = loader.get(lookup_name)

    if not agent:
        print(f"\nI don't recognize '{args.name}'")
        print(f"\nAvailable helpers:")
        for a in loader.list_agents():
            print(f"  - {a.friendly_name or a.name}")
        sys.exit(1)

    if args.json:
        print(json.dumps(agent.to_dict(), indent=2))
        return

    display_name = agent.friendly_name or agent.name
    desc = agent.user_description or agent.description

    print(f"\n{'=' * 60}")
    print(f"  {display_name}")
    print(f"{'=' * 60}")
    print(f"\n  {desc}")

    # Speed indicator
    speed_map = {'haiku': 'Fast', 'sonnet': 'Balanced', 'opus': 'Thorough'}
    print(f"\n  Speed: {speed_map.get(agent.model, agent.model)}")

    if agent.invocation.examples:
        print(f"\n  Just say things like:")
        for ex in agent.invocation.examples:
            plain = ex.get('plain_english', ex.get('prompt', ''))
            print(f"    \"{plain}\"")

    if agent.vendor_services:
        print(f"\n  Works with:")
        for svc in agent.vendor_services:
            print(f"    - {svc}")

    if args.prompt:
        print(f"\n  Technical Details:")
        print(f"  {'-' * 40}")
        for line in agent.system_prompt.split('\n')[:20]:
            print(f"    {line}")
        if len(agent.system_prompt.split('\n')) > 20:
            print(f"    ... (truncated)")

    print(f"\n  Tip: You don't need to remember this - just describe what you need.\n")


def cmd_invoke(args, loader: AgentLoader):
    """Generate Task tool invocation for an agent."""
    agent = loader.get(args.name)

    if not agent:
        print(f"Error: Agent '{args.name}' not found")
        sys.exit(1)

    prompt = args.task_prompt or f"[Your task for {agent.name}]"
    desc = args.desc or f"{agent.name} task"

    task_call = {
        "subagent_type": agent.invocation.subagent_type,
        "prompt": prompt,
        "description": desc
    }

    if agent.model and agent.model != "sonnet":
        task_call["model"] = agent.model

    if args.json:
        print(json.dumps(task_call, indent=2))
    else:
        print(f"\nTask Tool Invocation for '{agent.name}'")
        print("=" * 50)
        print(f"""
Task(
    subagent_type="{task_call['subagent_type']}",
    prompt="{task_call['prompt']}",
    description="{task_call['description']}"
)
""")

    # Also print natural language version
    print("Or ask Claude Code:")
    print(f'  "Use the {agent.name} agent to {prompt}"')
    print()


def cmd_suggest(args, loader: AgentLoader):
    """Suggest an agent for a task."""
    agent = loader.suggest_agent(args.task)

    if not agent:
        print("No agent suggestion available. Try 'general-purpose'.")
        return

    if args.json:
        print(json.dumps({
            "suggested": agent.name,
            "description": agent.description,
            "subagent_type": agent.invocation.subagent_type
        }, indent=2))
    else:
        print(f"\nSuggested Agent: {agent.name}")
        print(f"  {agent.description}")
        print(f"\n  Invoke with: subagent_type=\"{agent.invocation.subagent_type}\"")
        print()


def cmd_examples(args, loader: AgentLoader):
    """Show example prompts for all agents."""
    agents = loader.list_agents()

    print("\nAgent Example Prompts")
    print("=" * 60)

    for agent in sorted(agents, key=lambda a: a.name):
        if not agent.invocation.examples:
            continue

        print(f"\n  {agent.name}")
        print(f"  {'-' * len(agent.name)}")

        for ex in agent.invocation.examples:
            desc = ex.get('description', 'Example')
            prompt = ex.get('prompt', '')
            print(f"    {desc}:")
            print(f"      \"{prompt}\"")

    print()


def main():
    parser = argparse.ArgumentParser(
        prog='agent',
        description='CLI tool for managing Claude Code agents'
    )
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List all agents')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show more details')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show agent details')
    show_parser.add_argument('name', help='Agent name')
    show_parser.add_argument('-p', '--prompt', action='store_true', help='Show system prompt')

    # Invoke command
    invoke_parser = subparsers.add_parser('invoke', help='Generate invocation')
    invoke_parser.add_argument('name', help='Agent name')
    invoke_parser.add_argument('-t', '--task-prompt', help='Task prompt')
    invoke_parser.add_argument('-d', '--desc', help='Short description')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Suggest agent for task')
    suggest_parser.add_argument('task', help='Task description')

    # Examples command
    subparsers.add_parser('examples', help='Show example prompts')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize loader
    agents_dir = Path(__file__).parent
    loader = AgentLoader(agents_dir)
    loader.load_all()

    # Dispatch command
    commands = {
        'list': cmd_list,
        'show': cmd_show,
        'invoke': cmd_invoke,
        'suggest': cmd_suggest,
        'examples': cmd_examples
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args, loader)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
