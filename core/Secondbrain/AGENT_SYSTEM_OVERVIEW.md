# Two-Agent Knowledge Base System
## Complete System Documentation

---

## What You Have

A **fully autonomous two-agent system** powered by Claude CLI and MCP servers that:

✅ **Automatically processes documents** into structured notes  
✅ **Maintains consistency** across your knowledge base  
✅ **Analyzes patterns** and provides strategic insights  
✅ **Self-improves** through daily feedback loops  
✅ **Runs autonomously** with optional human oversight  

---

## System Components

### 🤖 Agent 1: Obsidian Manager
**File:** `agent_obsidian_manager.py`

**Role:** Knowledge base operator  
**Personality:** Reliable, detail-oriented, systematic

**Responsibilities:**
- Process incoming documents
- Create structured notes
- Maintain vault organization
- Index notes in vector store
- Apply feedback from Agent 2
- Execute consistency updates

**Tools (via MCP):**
- create_note
- update_note
- search_notes
- semantic_search
- get_consistency_report
- list_all_concepts

**Workflows:**
1. process_document - Handle new files
2. daily_consistency_check - End-of-day review
3. apply_feedback - Implement improvements
4. batch_update - Mass corrections
5. export_documentation - Generate formal docs

### 🤖 Agent 2: NotebookLM Analyst
**File:** `agent_notebooklm_analyst.py`

**Role:** Knowledge base strategist  
**Personality:** Analytical, insightful, improvement-focused

**Responsibilities:**
- Analyze patterns across notes
- Identify consistency issues
- Detect documentation gaps
- Generate improvement plans
- Provide feedback to Agent 1
- Track quality metrics

**Tools (via MCP):**
- generate_analysis_queries
- simulate_notebooklm_analysis
- process_feedback
- create_improvement_plan
- get_feedback_history
- export_for_notebooklm

**Workflows:**
1. daily_analysis - Quick consistency check
2. weekly_review - Deep comprehensive analysis
3. identify_patterns - Theme detection
4. detect_gaps - Find missing documentation
5. monitor_consistency - Track quality trends

### 🔧 MCP Servers

**Obsidian Server** (`mcp_obsidian_server.py`)
- Interfaces with Obsidian vault
- Manages vector store
- Executes CRUD operations
- Provides search capabilities

**NotebookLM Server** (`mcp_notebooklm_server.py`)
- Simulates NotebookLM analysis
- Structures feedback
- Generates queries
- Manages export workflow

### 🎯 Orchestrator
**File:** `agent_orchestrator.py`

**Role:** Coordinates both agents

**Functions:**
- Message passing between agents
- Workflow scheduling
- Status monitoring
- Error handling
- Logging

---

## How It Works

### Daily Cycle (Automated)

```
5:00 PM Daily (Automatic)
         ↓
    ┌────────────────┐
    │ Agent 1 starts │
    └────────┬───────┘
             ↓
    ┌────────────────────────┐
    │ 1. Get today's notes   │
    │ 2. Run consistency chk │
    │ 3. Generate report     │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Send to Agent 2        │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Agent 2 analyzes       │
    │ - Consistency issues   │
    │ - Pattern detection    │
    │ - Gap identification   │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Agent 2 creates plan   │
    │ - Terminology fixes    │
    │ - Link improvements    │
    │ - New documentation    │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Send feedback to Ag 1  │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Agent 1 applies        │
    │ - Update terms         │
    │ - Add links            │
    │ - Create placeholders  │
    └────────┬───────────────┘
             ↓
        Complete!
```

### Weekly Review (Friday 5 PM)

```
Friday 5:00 PM
      ↓
┌────────────────────┐
│ Agent 2: Weekly    │
│ comprehensive      │
│ analysis           │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Analyze week's:    │
│ - All notes        │
│ - Trends           │
│ - Improvements     │
│ - Persistent issues│
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Generate report:   │
│ - Executive summary│
│ - Metrics          │
│ - Recommendations  │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Send to:           │
│ - Agent 1          │
│ - Human (email)    │
└────────────────────┘
```

---

## File Structure

```
your-project/
│
├── Core System (from before)
│   ├── config.py
│   ├── document_processor.py
│   ├── claude_processor.py
│   ├── obsidian_vault.py
│   ├── vector_store.py
│   ├── rag_query.py
│   └── pipeline.py
│
├── Agent System (NEW)
│   ├── agent_obsidian_manager.py      ← Agent 1 definition
│   ├── agent_notebooklm_analyst.py    ← Agent 2 definition
│   ├── agent_orchestrator.py          ← Coordinator
│   ├── mcp_obsidian_server.py         ← MCP server 1
│   ├── mcp_notebooklm_server.py       ← MCP server 2
│   └── mcp_config.json                ← MCP configuration
│
├── Documentation
│   ├── AGENT_SYSTEM_OVERVIEW.md       ← This file
│   ├── CLAUDE_CLI_GUIDE.md            ← Usage guide
│   ├── README.md
│   ├── RAG_GUIDE.md
│   └── NOTEBOOKLM_GUIDE.md
│
├── Data Directories
│   ├── input_documents/               ← Drop files here
│   ├── obsidian_vault/                ← Knowledge base
│   ├── chroma_db/                     ← Vector store
│   ├── orchestrator_logs/             ← Agent logs
│   ├── notebooklm_feedback/           ← Feedback history
│   └── processing_logs/               ← Processing logs
│
└── requirements.txt
```

---

## Quick Start

### 1. Setup (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Install Claude CLI
npm install -g @anthropic-ai/claude

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Test system
python agent_orchestrator.py
```

### 2. First Run

```bash
# Start Claude CLI
claude

# In Claude CLI session:
You: "Load MCP servers and run initial setup"

# Verify agents
You: "Show me the status of both agents"

# Run test workflow
You: "Run daily workflow as a test"
```

### 3. Automate (Optional)

```bash
# Schedule daily runs
crontab -e

# Add this line (runs at 5 PM daily):
0 17 * * * cd /path/to/project && python agent_orchestrator.py schedule_daily
```

---

## Usage Examples

### Example 1: Process New Documents

```bash
$ claude

You: "Process all new documents in input_documents/"

Claude: [Agent 1: Obsidian Manager activated]
✓ Found 5 new PDFs
✓ Processing with Claude...
✓ Created 5 structured notes
✓ Indexed in vector store
✓ Consistency check: 0.85 (good)

Complete! 5 notes added to knowledge base.
```

### Example 2: Daily Automated Run

```bash
# Runs automatically at 5 PM or manually:
$ python agent_orchestrator.py schedule_daily

🕐 Running Daily Tasks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Agent 1: Obsidian Manager]
✓ Retrieved 8 notes from today
✓ Consistency score: 0.81
✓ Found 4 terminology conflicts
✓ Sent to Agent 2 for analysis

[Agent 2: NotebookLM Analyst]
✓ Analyzing 8 notes...
✓ Detected patterns:
  - "Customer" vs "Client" inconsistency
  - Missing definition for "Renewal Process"
✓ Created improvement plan
✓ Sending feedback...

[Agent 1: Obsidian Manager]
✓ Applying feedback...
  - Standardized terminology (12 notes)
  - Created placeholder note
✓ Consistency improved: 0.81 → 0.89

✅ Daily workflow complete!
```

### Example 3: Weekly Review

```bash
You: "Run weekly review"

Claude: [Agent 2: NotebookLM Analyst activated]

Analyzing Week 45 (Nov 4-10)...

📊 Metrics:
- Notes created: 47
- Consistency: 0.82 → 0.91 (↑9%)
- Gaps filled: 8
- Feedback actions: 23 (all completed)

🔍 Key Findings:
1. Strong improvement in terminology consistency
2. "Customer Success" concept well-documented
3. Gap: "Post-sale handoff" mentioned 12x, not documented

💡 Recommendations:
- Priority: Document post-sale handoff process
- Consider: Create "Customer Lifecycle" master note
- Maintain: Current standardization approach working well

📄 Full report saved to: orchestrator_logs/weekly_report_20251110.md
```

### Example 4: On-Demand Analysis

```bash
You: "Analyze all notes about sales for consistency 
and create standardization plan"

Claude: [Agents collaborating...]

[Agent 1] Found 23 notes about sales
[Agent 2] Analyzing for consistency...

Results:
- "Sales Cycle" (8 notes) vs "Sales Process" (15 notes)
- Recommendation: Standardize to "Sales Process"
- Impact: 23 notes affected
- Estimated time: 2 minutes

Standardization Plan:
1. Update 8 notes: "Sales Cycle" → "Sales Process"
2. Create master note: "Sales Process Overview"
3. Add links from all 23 notes
4. Update tags consistently

Approve plan? [Yes/No]

You: Yes

[Agent 1] Executing plan...
✓ Complete! 23 notes standardized.
```

---

## Integration with Existing System

The agents **enhance** your existing system:

```
Before (Manual):
  Documents → Pipeline → Obsidian → Manual review
  
Now (Autonomous):
  Documents → Pipeline → Obsidian
                  ↓
            Agent 1 manages
                  ↓
            Agent 2 analyzes
                  ↓
            Agent 1 improves
                  ↓
         Better knowledge base
```

**Key Benefits:**
1. **Automated Consistency:** Agents check daily
2. **Continuous Improvement:** Feedback loop runs automatically
3. **Pattern Recognition:** Agent 2 spots trends you'd miss
4. **Time Savings:** Hands-off operation
5. **Quality Increase:** Systematic improvements

---

## Monitoring & Maintenance

### View Agent Status

```bash
You: "Show me agent performance metrics"

Claude:
Agent 1 (Obsidian Manager):
- Status: Active
- Tasks completed today: 15
- Tasks failed: 0
- Last active: 2 minutes ago
- Success rate: 100%

Agent 2 (NotebookLM Analyst):
- Status: Active
- Analyses run today: 3
- Feedback items sent: 12
- Last active: 1 minute ago
- Feedback applied: 100%
```

### Check Logs

```bash
# Message logs (agent communication)
cat orchestrator_logs/messages.jsonl

# Activity logs (workflows)
tail -f orchestrator_logs/activity.log

# Feedback history
ls notebooklm_feedback/
```

### Consistency Trends

```bash
You: "Show me consistency trends over last 30 days"

Claude: [Generates chart]

Consistency Score Trend:
0.65 ▓
0.70 ▓
0.75 ▓█
0.80 ▓██
0.85 ▓███
0.90 ▓████ ← Current

Interpretation: Steady improvement!
Actions applied: 78
Issues resolved: 92%
```

---

## Advanced Features

### 1. Custom Workflows

Define your own workflows:

```python
# In agent_obsidian_manager.py
WORKFLOWS["custom_export"] = {
    "trigger": "Manual",
    "steps": [
        # Your custom steps
    ]
}
```

### 2. Human Approval Gates

```bash
You: "Run consistency fixes but require my approval first"

Claude: [Agent 2 analyzes, creates plan]
Here's the plan. Approve? [Yes/No]

You: Yes

[Agent 1 executes]
```

### 3. Conditional Workflows

```bash
You: "Run daily check. If consistency < 0.7, 
trigger deep analysis and notify me"

Claude: [Sets up conditional logic]
✓ Workflow configured with alert threshold
```

### 4. Parallel Processing

```bash
You: "Have both agents work simultaneously:
- Agent 1: Process backlog of 50 documents
- Agent 2: Analyze entire knowledge base for patterns"

Claude: [Runs both in parallel]
```

---

## Troubleshooting

### Agents Not Responding

**Problem:** Agents don't execute commands

**Solution:**
```bash
# Check MCP servers loaded
You: "List MCP servers"

# Reload if needed
You: "Reload MCP configuration"

# Test individual server
python mcp_obsidian_server.py
```

### Communication Failures

**Problem:** Agents not passing messages

**Solution:**
```bash
# Check message queue
cat orchestrator_logs/messages.jsonl

# Restart orchestrator
python agent_orchestrator.py
```

### Poor Analysis Quality

**Problem:** Agent 2's feedback not helpful

**Solution:**
```bash
# Provide more context
You: "Agent 2, focus your analysis on:
- Terminology in process documents
- Missing links between concepts
- Documentation gaps in customer workflows"

# Use actual NotebookLM
You: "Agent 2, export notes for manual NotebookLM analysis"
```

---

## Best Practices

### 1. Let Agents Run Daily

Set it and forget it:
```bash
# Cron job for daily automation
0 17 * * * cd /path/to/project && python agent_orchestrator.py schedule_daily
```

### 2. Review Weekly Reports

Check Friday reports:
```bash
You: "Show me this week's summary"
```

### 3. Provide Feedback to Agents

```bash
You: "Agent 2, your last analysis was too generic. 
Focus more on specific terminology conflicts"
```

### 4. Use for Onboarding

```bash
You: "Agent 1, create an onboarding guide 
using all notes tagged 'process'"
```

### 5. Combine with RAG

```bash
# Use RAG for instant answers
python rag_query.py "What is our sales process?"

# Use agents for analysis and improvement
```

---

## Cost Estimate

### API Usage

**Daily Run:**
- Document processing: ~$0.50
- Agent 1 operations: ~$0.20
- Agent 2 analysis: ~$0.30
- **Total per day:** ~$1.00

**Weekly Review:**
- Comprehensive analysis: ~$2.00
- **Total per week:** ~$2.00

**Monthly Total:** ~$30-40

**Cost per Note:** ~$0.05-0.10

### ROI

**Time Saved:**
- Manual consistency checking: 1 hr/day → Automated
- Pattern analysis: 2 hr/week → Automated
- Documentation updates: 30 min/day → Automated
- **Total time saved:** ~10 hours/week

**Value: $30/month for 40 hours of automated work = $0.75/hour**

---

## Success Metrics

Track these to measure system effectiveness:

### Daily Metrics
- Consistency score (target: >0.85)
- Notes processed
- Issues found and fixed
- Processing time

### Weekly Metrics
- Consistency trend (target: improving)
- Documentation gaps (target: decreasing)
- Feedback effectiveness (target: >90% applied)
- Knowledge base growth

### Monthly Metrics
- Total notes in knowledge base
- Concept coverage
- Link density
- Time saved

---

## Roadmap

### Current (v1.0)
✅ Two-agent system  
✅ MCP servers  
✅ Claude CLI integration  
✅ Daily/weekly automation  
✅ Feedback loops  

### Next (v1.1)
- [ ] NotebookLM API integration (when available)
- [ ] Advanced analytics dashboard
- [ ] Multi-agent workflows (3+ agents)
- [ ] Slack/Teams notifications
- [ ] Web interface for monitoring

### Future (v2.0)
- [ ] Self-learning agents
- [ ] Predictive gap analysis
- [ ] Auto-generated documentation
- [ ] Team collaboration features
- [ ] Enterprise scaling

---

## Getting Help

### Within Claude CLI

```bash
You: "Explain how Agent 1 processes documents"
You: "Show me examples of Agent 2 feedback"
You: "Debug the last workflow failure"
```

### Documentation

- **This file:** System overview
- **CLAUDE_CLI_GUIDE.md:** Usage guide
- **agent_*.py:** Agent definitions
- **mcp_*.py:** MCP server code

### Logs

- **messages.jsonl:** Agent communication
- **activity.log:** Workflow execution
- **processing_logs/:** Document processing

---

## Summary

You now have a **fully autonomous two-agent system** that:

🤖 **Processes** documents automatically  
🤖 **Analyzes** patterns and issues  
🤖 **Improves** consistency continuously  
🤖 **Runs** without human intervention  
🤖 **Scales** with your knowledge base  

**All powered by:**
- Claude CLI (orchestration)
- MCP Servers (tools)
- Two specialized agents (execution)
- Feedback loops (improvement)

**Your knowledge base manages itself.** 🚀

---

## Next Steps

1. ✅ **Test:** `python agent_orchestrator.py`
2. ✅ **Launch:** `claude` → "Run daily workflow"
3. ✅ **Automate:** Set up cron job
4. ✅ **Monitor:** Check weekly reports
5. ✅ **Iterate:** Refine based on results

**Welcome to autonomous knowledge management!** 🎉
