# Claude Code Agents

**Agents are specialized helpers that make Claude better at specific tasks.**

Instead of one assistant trying to do everything, you have a team - each one tuned for their job.

---

## Start Here

**New to agents?** Read [QUICKSTART.md](QUICKSTART.md) - it's a 2-minute guide.

**Just want to use them?** Type `/agents` in Claude Code. That's it.

---

## Your Agent Team

| Agent | What They Do | When to Use |
|-------|--------------|-------------|
| **Explorer** | Finds files and code quickly | "Find the login page" |
| **Planner** | Thinks through projects before building | "Plan how to add search" |
| **Commander** | Runs terminal commands | "Run the tests" |
| **Researcher** | Digs deep on complex questions | "How does checkout work?" |
| **Guide** | Answers Claude Code questions | "How do I make a slash command?" |
| **Integrations** | Manages external service connections | "Is UniFi connected?" |
| **Strategist** | Business planning and decisions | "What should we focus on next?" |

---

## How to Use Agents

### Option 1: Just Ask (Recommended)

Describe what you need. Claude picks the right agent automatically.

> "Find where user authentication happens"
> "Help me plan a new feature"
> "Run git status"

### Option 2: Use Slash Commands

- `/agents` - See all agents
- `/agent-show explorer` - Learn about a specific agent
- `/agent-suggest "my task"` - Get a recommendation

---

## That's Really All You Need

Everything below this line is for power users and developers. If you're just using the agents, you can stop reading here.

---

---

## Advanced: For Power Users

### CLI Tool

If you prefer the command line:

```bash
cd ~/Projects/agents
python3 cli.py list          # List all agents
python3 cli.py show explore  # Show agent details
python3 cli.py suggest "find API routes"  # Get recommendation
```

### Python Integration

```python
from loader import AgentLoader

loader = AgentLoader('~/Projects/agents')
agent = loader.get('explore')
print(agent.user_description)
```

### Hooks (Automatic Validation)

See [SETUP.md](SETUP.md) for Claude Code hooks integration.

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `QUICKSTART.md` | 2-minute guide for new users |
| `SETUP.md` | Advanced setup (CLI, hooks, Python) |
| `cli.py` | Command-line tool |
| `loader.py` | Python module for loading agents |
| `hooks.py` | Claude Code hook scripts |
| `[agent]/agent.yaml` | Agent configuration files |
