# Troubleshooting & Common Questions

## Quick Fixes

### "/agents command doesn't work"

**Are you in Claude Code?**
The slash commands only work inside Claude Code (the terminal/CLI app). They won't work on the Claude website.

**Try this:**
1. Open your terminal
2. Make sure Claude Code is running
3. Type `/agents` and press Enter

---

### "I don't know which agent to use"

**You don't have to pick one.**

Just describe what you want:
- "Find the login page"
- "Plan how to add a feature"
- "Run the tests"

Claude automatically picks the right helper.

**Still unsure?** Type `/agent-suggest` followed by what you want to do:
```
/agent-suggest find where errors are logged
```

---

### "Claude used the wrong agent"

That's okay - it happens. Just be more specific:

Instead of: "Look at the auth code"
Try: "Search for where we handle user login"

Or explicitly ask: "Use the Explorer to find authentication code"

---

### "What's the difference between agents?"

| If You Want To... | Use This |
|-------------------|----------|
| Find or search for something | Explorer |
| Plan before building | Planner |
| Run commands (git, npm, etc.) | Commander |
| Understand something complex | Researcher |
| Ask how Claude Code works | Guide |
| Fix service connections | Integrations |
| Make business decisions | Strategist |

---

### "What does 'haiku' or 'opus' mean?"

These are behind-the-scenes speed settings:
- **Haiku** = Faster, good for simple tasks
- **Sonnet** = Balanced
- **Opus** = More thorough, good for complex tasks

You don't need to pick these - Claude handles it automatically.

---

### "Do I need to install anything?"

**For basic use: No.**

The `/agents` command works immediately in Claude Code.

**For advanced use (CLI tool):**

```bash
cd ~/Projects/agents
pip install pyyaml
python3 cli.py list
```

---

### "I see weird terms like 'subagent_type'"

Ignore them! Those are technical details you don't need.

Just use plain language:
- Say: "Find the settings page"
- Not: "Use subagent_type Explore to search for settings"

---

## Still Stuck?

Type this in Claude Code:

```
Help me understand how to use agents
```

Claude will explain it in context of what you're working on.
