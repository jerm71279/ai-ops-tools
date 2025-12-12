# Claude CLI Agent System Guide

## Complete guide for running the two-agent knowledge base system with Claude CLI (Claude Code)

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Claude CLI (Claude Code)               │
│           Orchestrates both agents                  │
└────────────────┬────────────────────────────────────┘
                 │
       ┌─────────┴──────────┐
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│  Agent 1:   │◄────►│  Agent 2:   │
│  Obsidian   │      │  NotebookLM │
│  Manager    │      │  Analyst    │
└──────┬──────┘      └──────┬──────┘
       │                    │
   ┌───┴────┐          ┌────┴────┐
   ↓        ↓          ↓         ↓
[MCP:    [MCP:      [MCP:     [MCP:
Vault]   Vector]    NBL]      Feedback]
```

---

## Prerequisites

### 1. Install Claude CLI (Claude Code)

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude

# Or using Homebrew on macOS
brew install anthropic/tap/claude
```

Verify installation:
```bash
claude --version
```

### 2. Set Up API Key

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Quick Start

### 1. Initialize the System

```bash
# Run the orchestrator test
python agent_orchestrator.py
```

This will:
- Initialize both MCP servers
- Test agent communication
- Run a sample daily workflow

### 2. Start Claude CLI in Project Directory

```bash
cd /path/to/your/project
claude
```

### 3. Load MCP Configuration

Within Claude CLI session:
```
Load MCP servers from mcp_config.json
```

Claude CLI will automatically detect and load the configuration.

---

## Using the Agents

### Agent 1: Obsidian Manager

**Role:** Manages the knowledge base

**How to invoke:**

```bash
# In Claude CLI
You: "Run the Obsidian Manager agent to process new documents"

# Or more specific
You: "Agent 1, run daily consistency check"
```

**Available Commands:**

1. **Process Documents:**
```
Process all new documents in the input_documents folder
```

2. **Consistency Check:**
```
Run daily consistency check and prepare notes for analysis
```

3. **Apply Feedback:**
```
Apply the feedback from NotebookLM Analyst regarding terminology standardization
```

4. **Batch Update:**
```
Batch update all notes: replace "Customer Setup" with "Customer Onboarding"
```

5. **Search and Report:**
```
Search for all notes about "sales process" and generate a consistency report
```

### Agent 2: NotebookLM Analyst

**Role:** Analyzes knowledge base and provides feedback

**How to invoke:**

```bash
# In Claude CLI
You: "Run the NotebookLM Analyst to analyze today's notes"

# Or more specific
You: "Agent 2, perform weekly review and generate improvement recommendations"
```

**Available Commands:**

1. **Daily Analysis:**
```
Analyze today's notes for consistency issues and gaps
```

2. **Weekly Review:**
```
Perform comprehensive weekly analysis with trend reporting
```

3. **Pattern Recognition:**
```
Identify patterns and themes across the knowledge base
```

4. **Gap Analysis:**
```
Find all documentation gaps and prioritize them
```

5. **Generate Queries:**
```
Generate smart analysis queries for manual NotebookLM review
```

---

## Example Workflows

### Workflow 1: Daily Automated Cycle

**Morning:**
```bash
claude

You: "Run daily workflow:
1. Agent 1: Check for new documents and process them
2. Agent 1: Run consistency check on today's work
3. Agent 2: Analyze today's notes and provide feedback
4. Agent 1: Apply high-priority feedback items"
```

Claude CLI will:
- Orchestrate both agents
- Pass messages between them
- Execute workflows in sequence
- Provide status updates

### Workflow 2: Weekly Deep Dive

**Friday afternoon:**
```bash
You: "Run weekly review workflow:
1. Agent 2: Analyze the entire week's notes
2. Agent 2: Generate comprehensive report with trends
3. Agent 2: Create improvement plan
4. Agent 1: Preview the changes that would be made"
```

### Workflow 3: Manual NotebookLM Integration

**When you want to use actual NotebookLM:**
```bash
You: "Agent 2: Export this week's notes for NotebookLM upload
with analysis queries included"
```

Agent will:
- Export notes to `./notebooklm_exports/`
- Generate query list
- Create upload instructions

Then:
1. Upload files to NotebookLM manually
2. Run queries in NotebookLM
3. Copy responses back

```bash
You: "Agent 2: Process this NotebookLM feedback:
[paste the feedback from NotebookLM]"
```

Agent will:
- Structure the feedback
- Create improvement plan
- Send to Agent 1 for execution

### Workflow 4: On-Demand Analysis

```bash
You: "Analyze all notes about 'customer success' for consistency
and create a standardization plan"
```

Claude CLI will:
- Direct Agent 1 to search notes
- Pass to Agent 2 for analysis
- Generate recommendations
- Return action plan

---

## Advanced Usage

### Custom Workflows

You can define custom workflows for agents:

```bash
You: "Create a new workflow for Agent 1:
1. Search for all process documents
2. Check if they follow standard template
3. Flag non-conforming docs
4. Generate report"
```

### Parallel Operations

Run both agents simultaneously:

```bash
You: "In parallel:
- Agent 1: Process new documents
- Agent 2: Analyze last week for trends"
```

### Conditional Logic

```bash
You: "Run daily check. If consistency score drops below 0.7,
immediately trigger Agent 2 deep analysis and flag for my review"
```

---

## MCP Tools Reference

### Obsidian Manager Tools

**create_note(structured_data, note_type)**
- Creates new note in vault
- Auto-indexes in vector store
- Returns note ID

**search_notes(query, tags, concepts, semantic)**
- Search vault by various criteria
- Can use semantic vector search
- Returns matching notes

**get_consistency_report()**
- Generates consistency metrics
- Identifies issues
- Returns report object

**get_recent_notes(days)**
- Get notes from last N days
- Returns note list with metadata

**semantic_search(query, n_results)**
- Vector-based semantic search
- Returns similar notes with scores

### NotebookLM Analyst Tools

**generate_analysis_queries(note_summaries, focus_areas)**
- Creates smart analysis questions
- Tailored to note content
- Returns query list

**simulate_notebooklm_analysis(notes_content, analysis_type)**
- Claude-based analysis simulation
- Until NotebookLM API available
- Returns structured analysis

**process_feedback(raw_feedback)**
- Structures raw feedback
- Creates actionable items
- Returns processed feedback

**create_improvement_plan(feedback_items, priority)**
- Builds implementation plan
- Prioritizes actions
- Returns plan object

---

## Prompting Patterns

### Pattern 1: Sequential Agent Tasks

```
Agent 1: [task]
Then Agent 2: [task]
Finally Agent 1: [task]
```

Claude CLI handles sequencing automatically.

### Pattern 2: Agent Collaboration

```
Have both agents collaborate on:
[high-level goal]

Agent 1 should: [specific role]
Agent 2 should: [specific role]
```

### Pattern 3: Feedback Loop

```
Start feedback loop:
1. Agent 1: Check consistency
2. Agent 2: Analyze issues
3. Agent 1: Apply fixes
4. Repeat until consistency > 0.9
```

### Pattern 4: Human-in-the-Loop

```
Agent 2: Analyze and create plan
Then show me the plan for approval
If I approve, Agent 1: Execute plan
```

---

## Monitoring and Debugging

### View Agent Status

```bash
You: "Show me the status of both agents"
```

Returns:
- Tasks completed
- Tasks failed
- Last active time
- Message queue status

### View Logs

```bash
# Message logs
cat orchestrator_logs/messages.jsonl

# Activity logs
tail -f orchestrator_logs/activity.log

# Agent-specific logs
cat processing_logs/processing_history.json
```

### Debug Mode

```bash
You: "Enable debug mode and run daily workflow"
```

Shows:
- Each tool call
- Message passing
- Decision points
- Errors

---

## Best Practices

### 1. Clear Task Definition

✅ **Good:**
```
Agent 1: Process all PDFs in input_documents/ 
and create structured notes with auto-linking
```

❌ **Bad:**
```
Process stuff
```

### 2. Specify Success Criteria

✅ **Good:**
```
Run consistency check. Success means:
- All notes have concepts defined
- Consistency score > 0.85
- No critical gaps
```

### 3. Use Agent Strengths

- **Agent 1** for operations (create, update, search)
- **Agent 2** for analysis (patterns, insights, recommendations)

### 4. Leverage MCP Tools Directly

```
Using Obsidian MCP: search for all notes tagged "process" 
created in last 7 days
```

### 5. Chain Workflows

```
Run these workflows in sequence:
1. process_document (Agent 1)
2. daily_analysis (Agent 2)
3. apply_feedback (Agent 1)

Stop if any workflow fails
```

---

## Troubleshooting

### Issue: Agents not responding

**Solution:**
```bash
# Check MCP servers are loaded
You: "List available MCP servers"

# Restart if needed
You: "Reload MCP configuration"
```

### Issue: Agent communication failure

**Solution:**
```bash
# Check orchestrator logs
cat orchestrator_logs/messages.jsonl

# Verify message queue
You: "Show message queue status"
```

### Issue: Tool execution fails

**Solution:**
```bash
# Test tool directly
You: "Test Obsidian MCP tool: list_all_concepts"

# Check error logs
tail -f orchestrator_logs/activity.log
```

### Issue: Consistency not improving

**Solution:**
```bash
You: "Agent 2: Analyze why consistency isn't improving
and create detailed remediation plan"
```

---

## Scheduling Automated Runs

### Option 1: Cron Job

```bash
# Edit crontab
crontab -e

# Add daily task (5 PM)
0 17 * * * cd /path/to/project && python agent_orchestrator.py schedule_daily

# Add weekly task (Friday 5 PM)
0 17 * * 5 cd /path/to/project && python agent_orchestrator.py schedule_weekly
```

### Option 2: Claude CLI Script

Create `daily_run.sh`:
```bash
#!/bin/bash
cd /path/to/project
claude run <<EOF
Run daily workflow:
1. Agent 1: Process new documents
2. Agent 1: Run consistency check
3. Agent 2: Analyze and provide feedback
4. Agent 1: Apply high-priority items
Generate summary report
EOF
```

Make executable:
```bash
chmod +x daily_run.sh
```

Schedule with cron:
```bash
0 17 * * * /path/to/daily_run.sh
```

---

## Example: Complete Daily Session

```bash
$ claude

Claude: Hello! I'm ready to help. I see MCP servers for Obsidian 
and NotebookLM are loaded.

You: Run complete daily workflow

Claude: I'll orchestrate both agents for the daily workflow:

[Agent 1: Obsidian Manager]
✓ Scanning for new documents... Found 3 PDFs
✓ Processing documents with Claude...
✓ Created 3 structured notes
✓ Indexed in vector store
✓ Running consistency check...
  - Consistency score: 0.82
  - Issues found: 5 terminology conflicts
✓ Sending to Agent 2 for analysis

[Agent 2: NotebookLM Analyst]
✓ Received 3 notes for analysis
✓ Simulating NotebookLM analysis...
✓ Found patterns:
  - "Client" vs "Customer" used inconsistently
  - 2 documentation gaps identified
✓ Creating improvement plan...
✓ Sending feedback to Agent 1

[Agent 1: Obsidian Manager]
✓ Received feedback from Agent 2
✓ Applying changes:
  - Standardizing to "Customer" (12 notes updated)
  - Created placeholder for "Renewal Process"
✓ Changes complete

Summary:
- Documents processed: 3
- Notes created: 3
- Consistency improved: 0.82 → 0.88
- Feedback items: 5 (all applied)

You: Generate the weekly report

Claude: [Running weekly review workflow...]

[Full detailed report generated]

You: Perfect! Save this and schedule to run daily at 5pm

Claude: I'll create a cron job for you...
[Provides setup instructions]

Done! The system will now run automatically daily at 5pm.
```

---

## Tips for Maximum Effectiveness

1. **Be Specific**: Clear instructions = better results
2. **Use Workflows**: Pre-defined workflows are more reliable
3. **Monitor Metrics**: Track consistency score trends
4. **Review Feedback**: Check Agent 2's recommendations
5. **Iterate**: Refine prompts based on results
6. **Combine Tools**: Use MCP tools directly when needed
7. **Leverage Memory**: Agents remember context within session
8. **Save Patterns**: Document working prompts for reuse

---

## Next Steps

1. **Run Test:** `python agent_orchestrator.py`
2. **Start Claude CLI:** `claude`
3. **Run First Workflow:** "Run daily workflow"
4. **Review Results:** Check generated notes and logs
5. **Iterate:** Refine based on results
6. **Automate:** Schedule regular runs

---

## Getting Help

**View available commands:**
```
You: "Show me all available workflows for both agents"
```

**Get agent documentation:**
```
You: "Explain the Obsidian Manager's daily_consistency_check workflow"
```

**Debug issues:**
```
You: "Why did the last workflow fail? Show me the logs"
```

---

## Reference Files

- **Agent 1 Definition:** `agent_obsidian_manager.py`
- **Agent 2 Definition:** `agent_notebooklm_analyst.py`
- **Orchestrator:** `agent_orchestrator.py`
- **MCP Config:** `mcp_config.json`
- **Obsidian MCP:** `mcp_obsidian_server.py`
- **NotebookLM MCP:** `mcp_notebooklm_server.py`

---

**Your knowledge base is now managed by AI agents. Let them work!** 🤖
