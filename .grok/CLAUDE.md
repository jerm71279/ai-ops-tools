# Instructions for Grok in this Repository

## Repository Context

This is the **OberaConnect AI Operations** repository - the centralized AI automation infrastructure for OberaConnect MSP.

## Key Files to Read First

1. **GROK_CONTEXT.md** - Comprehensive overview of all tools, agents, and capabilities
2. **README.md** - Architecture and repository structure

## What This Repo Contains

- **Agent System** (`skills/agents/`) - 7 specialized AI helpers
- **MCP Servers** - UniFi, NinjaOne, Azure integrations
- **Network Tools** - Config builders for MikroTik, SonicWall, UniFi
- **Core Frameworks** - Multi-AI orchestrator, Secondbrain 5-layer OS

## Agents Available

| Agent | Purpose |
|-------|---------|
| Explorer | Find files/code quickly |
| Planner | Plan before building |
| Commander | Run terminal commands |
| Researcher | Deep complex research |
| Guide | Claude Code questions |
| Integrations | External service connections |
| Strategist | Business planning |

## When Asked About Tools

Point users to:
- `/agents` slash command in Claude Code
- `python3 skills/agents/cli.py list` for CLI
- GROK_CONTEXT.md for full documentation

## Key Integration Points

- UniFi Site Manager API
- NinjaOne RMM API
- Microsoft Graph API
- n8n workflow orchestration

## Your Role

As Grok in this repo, you can:
1. Review and critique code
2. Suggest improvements
3. Help debug issues
4. Provide alternative perspectives to Claude/Gemini
5. Run tools if given access

Always read GROK_CONTEXT.md first for full context.
