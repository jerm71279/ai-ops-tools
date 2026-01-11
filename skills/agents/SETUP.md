# Agent System Setup

## Quick Start

### 1. Install Dependencies

```bash
cd /home/mavrick/Projects/agents
pip install -r requirements.txt
```

### 2. Make CLI Executable

```bash
chmod +x cli.py
```

### 3. Test It

```bash
# List all agents
./cli.py list

# Show agent details
./cli.py show explore

# Get invocation help
./cli.py invoke plan -t "Design a caching system"

# Suggest an agent for a task
./cli.py suggest "find all API routes"

# Show example prompts
./cli.py examples
```

---

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list` | List all agents | `./cli.py list -v` |
| `show <name>` | Show agent details | `./cli.py show plan --prompt` |
| `invoke <name>` | Generate invocation | `./cli.py invoke explore -t "Find auth code"` |
| `suggest <task>` | Suggest agent for task | `./cli.py suggest "run the tests"` |
| `examples` | Show example prompts | `./cli.py examples` |

### Global Options

- `--json` - Output as JSON (useful for scripting)

---

## Claude Code Hooks Integration

### Option A: Add to claude_code_config.json

Create or edit `~/.claude/claude_code_config.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "command": "python /home/mavrick/Projects/agents/hooks.py pre"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Task",
        "command": "python /home/mavrick/Projects/agents/hooks.py post"
      }
    ]
  }
}
```

### Option B: Project-Level Hooks

Create `.claude/hooks.json` in your project:

```json
{
  "PreToolUse": [
    {
      "matcher": "Task",
      "command": "python /home/mavrick/Projects/agents/hooks.py pre"
    }
  ]
}
```

### What the Hooks Do

- **PreToolUse**: Validates agent exists, logs which agent is being invoked
- **PostToolUse**: Can log completions, track metrics

---

## Add to PATH (Optional)

Add an alias for easier access:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias agent='/home/mavrick/Projects/agents/cli.py'
```

Then use:
```bash
agent list
agent show explore
agent invoke plan -t "Design the feature"
```

---

## Programmatic Usage

```python
from loader import AgentLoader, load_agents

# Quick load
agents = load_agents('/home/mavrick/Projects/agents')

# Or use the loader class
loader = AgentLoader('/home/mavrick/Projects/agents')
loader.load_all()

# Get specific agent
explore = loader.get('explore')
print(explore.system_prompt)

# Find by capability
git_agents = loader.find_by_capability('git')

# Suggest agent for task
suggested = loader.suggest_agent('find all TODO comments')
print(f"Use: {suggested.name}")

# Generate Task tool call
task_params = explore.get_task_call(
    prompt="Find all React components",
    description="Find components"
)
```

---

## Adding New Agents

1. Create directory: `mkdir /home/mavrick/Projects/agents/my-agent`

2. Create `agent.yaml`:

```yaml
name: my-agent
description: What this agent does
model: sonnet  # haiku, sonnet, or opus

tools:
  - Tool1
  - Tool2

invocation:
  subagent_type: my-agent
  examples:
    - description: Example task
      prompt: "Do something specific"

system_prompt: |
  You are a specialized agent for...

  ## Capabilities
  - Capability 1
  - Capability 2

  ## Guidelines
  - Guideline 1
  - Guideline 2
```

3. Test: `./cli.py show my-agent`

---

## Directory Structure

```
/agents
├── README.md              # Overview
├── SETUP.md               # This file
├── requirements.txt       # Python dependencies
├── loader.py              # YAML loader module
├── cli.py                 # CLI tool
├── hooks.py               # Claude Code hooks
├── explore/
│   └── agent.yaml
├── plan/
│   └── agent.yaml
├── bash/
│   └── agent.yaml
├── general-purpose/
│   └── agent.yaml
├── claude-code-guide/
│   └── agent.yaml
├── mcp-integration-overseer/
│   └── agent.yaml
└── strategic-business-analyst/
    └── agent.yaml
```
