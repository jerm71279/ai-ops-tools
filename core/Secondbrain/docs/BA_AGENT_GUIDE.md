# BA Agent System Guide

## Overview

The Business Analytics (BA) Agent is an AI-powered system for project management, resource tracking, and business intelligence. It integrates with SharePoint Lists and uses Gemini AI for intelligent analysis.

---

## Components

### 1. BA Agent (`agent_ba.py`)

The core analytics engine providing:

#### Analysis Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `analyze_project_health(project_id)` | Analyze health of all or specific projects | Health scores, risk factors, status |
| `analyze_resource_utilization(days)` | Team utilization metrics | Hours, billable %, capacity |
| `analyze_time_reports(group_by, days)` | Time entry analysis | Grouped totals, summaries |
| `generate_executive_summary()` | Combined executive report | All metrics + narrative |
| `generate_quote(description, complexity)` | Work estimation | Hours, costs, ranges |
| `query(question)` | Natural language queries (Gemini) | AI-generated answer |

#### Usage Example

```python
from agent_ba import BAAgent

# Initialize
agent = BAAgent(gemini_api_key="your-key")

# Load data from SharePoint
agent.set_data(
    projects=projects_list,
    tasks=tasks_list,
    time_entries=time_entries_list
)

# Analyze project health
result = agent.analyze_project_health()
print(result.insights)
print(result.recommendations)

# Generate quote
quote = agent.generate_quote(
    task_description="Implement Azure AD SSO",
    complexity="high",
    include_buffer=True
)
print(f"Estimated: {quote.data['estimated_hours']['typical']} hours")
print(f"Cost: ${quote.data['cost_estimates']['typical']}")
```

#### Health Score Calculation

Projects are scored 0-100 based on:
- Budget variance (-20 points if over budget)
- Overdue tasks (-10 to -25 points based on percentage)
- Schedule status (-15 to -30 points if behind)

| Score | Status |
|-------|--------|
| 80-100 | Healthy |
| 60-79 | At Risk |
| 0-59 | Critical |

---

### 2. MoE Router (`moe_router.py`)

Intelligent task routing to the best agent.

#### Categories

| Category | Routed To | Keywords |
|----------|-----------|----------|
| `knowledge_management` | Obsidian Manager | note, document, vault, wiki |
| `document_processing` | Obsidian Manager | process, upload, pdf, extract |
| `analysis` | NotebookLM Analyst | analyze, pattern, review, audit |
| `business_intelligence` | BA Agent | project, kpi, dashboard, metric |
| `project_management` | BA Agent | task, milestone, deadline, status |
| `time_tracking` | BA Agent | time, hour, billable, timesheet |
| `reporting` | BA Agent | report, summary, export |

#### Usage Example

```python
from moe_router import MoERouter

router = MoERouter()

# Route a task
result = router.route_to_best_agent("Generate project health report")
print(f"Agent: {result['agent_name']}")
print(f"Confidence: {result['confidence']}")

# With orchestrator
from agent_orchestrator import AgentOrchestrator
orchestrator = AgentOrchestrator()
result = orchestrator.route_task(
    "What's our team utilization this month?",
    data={"time_entries": entries}
)
```

---

### 3. SharePoint MCP Server (`mcp_sharepoint_server.py`)

Tools for SharePoint List operations.

#### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_projects` | Fetch projects | status_filter, limit |
| `get_tasks` | Fetch tasks | project_id, status_filter, assignee |
| `get_tickets` | Fetch tickets | status_filter, priority_filter |
| `get_time_entries` | Fetch time entries | date_from, date_to, employee |
| `get_project_with_tasks` | Project + related tasks | project_id |
| `create_task` | Create new task | title, project_id, assignee, due_date |
| `update_task_status` | Update status | task_id, status |
| `log_time_entry` | Log time | employee, hours, date, project_id |
| `search_items` | Search across lists | query, list_name |
| `get_list_analytics` | Aggregated stats | list_name, group_by |

#### Usage Example

```python
import asyncio
from mcp_sharepoint_server import SharePointMCPServer

async def main():
    server = SharePointMCPServer()
    server.set_access_token(token)

    # Discover lists
    await server.discover_lists()

    # Get projects
    result = await server.tool_get_projects(status_filter="In Progress")
    print(result['projects'])

    # Create task
    await server.tool_create_task(
        title="Review security audit",
        project_id="123",
        assignee="Mavrick Faison",
        priority="High"
    )

asyncio.run(main())
```

---

## Frontend Components

### Task Kanban Board (`TaskKanban.js`)

A drag-and-drop Kanban board for TASKS (not projects).

#### Features
- 4 columns: Not Started → In Progress → On Hold → Completed
- Tasks linked to projects via ProjectId
- Drag to change status (auto-saves to SharePoint)
- Filter by project, assignee, priority
- Quick-add to any column
- Due date indicators (overdue = red)

#### Props
None - self-contained component with internal state

### Quote Generator (`QuoteGenerator.js`)

Work estimation tool for quoting.

#### Complexity Levels

| Level | Hours Range |
|-------|-------------|
| Simple | 1-4 |
| Low | 2-8 |
| Medium | 4-16 |
| High | 8-40 |
| Complex | 24-80 |
| Enterprise | 40-160 |

#### Work Type Multipliers

| Type | Multiplier |
|------|------------|
| Development | 1.0x |
| Design | 0.9x |
| Consulting | 1.1x |
| Support | 0.8x |
| Training | 0.85x |
| Documentation | 0.7x |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | None |
| `SHAREPOINT_SITE_ID` | SharePoint site identifier | Configured in config.js |

### SharePoint Site

```javascript
// src/config.js
export const CONFIG = {
    siteId: 'oberaconnect.sharepoint.com,3894a9a1-...',
    GRAPH_API: 'https://graph.microsoft.com/v1.0'
};
```

### Billable Rates

```python
# agent_ba.py
BILLABLE_RATES = {
    'Mavrick Faison': 150,
    'Patrick McFarland': 135,
    'Robbie McFarland': 200,
    'Default': 125
}
```

---

## API Endpoints

### Docker Agents API (`/docker/agents/api_server.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/agents` | GET | List available agents |
| `/agents/{name}/run` | POST | Run an agent |
| `/orchestrate` | POST | Route task via orchestrator |
| `/jobs` | GET | List running jobs |
| `/jobs/{id}` | GET | Get job status |
| `/gemini/chat` | POST | Gemini chat completion |

---

## Deployment

### Build & Deploy

```bash
# Build
npm run build

# Copy bundle
cp dist/bundle.js swa-build/dist/

# Deploy
SWA_CLI_DEPLOYMENT_TOKEN="..." npx @azure/static-web-apps-cli deploy ./swa-build --env production
```

### URLs

- **Production**: https://jolly-island-06ade710f.3.azurestaticapps.net
- **SharePoint**: https://oberaconnect.sharepoint.com/sites/SOCTEAM-Engineering

---

## Troubleshooting

### "No lists found"
- Ensure user has Sites.ReadWrite.All permission
- Lists are auto-created on first use of each component

### "Token expired"
- The app refreshes tokens automatically
- If issues persist, log out and log back in

### "Task not saving"
- Check network tab for 429 (rate limited) - wait and retry
- Check for 412 (concurrent edit) - refresh and retry

### Gemini not working
- Set `GEMINI_API_KEY` environment variable
- Check API quota in Google Cloud Console
