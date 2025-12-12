# Changelog

All notable changes to the OberaConnect Engineering Command Center are documented here.

---

## [2.0.0] - 2025-12-03

### BA Agent System Release

Major release introducing the Business Analytics Agent system with AI-powered project management capabilities.

### Added

#### Backend - AI Agents

- **`agent_ba.py`** - Business Analytics Agent
  - Project health analysis (schedule/budget variance, risk factors)
  - Resource utilization tracking (billable vs non-billable hours)
  - Time report generation (by project, employee, date, task)
  - Executive summary generation
  - Quote generation with complexity-based estimation
  - Natural language queries via Gemini AI
  - Configurable employee billable rates

- **`moe_router.py`** - Mixture of Experts Router
  - Intelligent task routing to appropriate agents
  - Category classification (knowledge management, analysis, business intelligence, etc.)
  - Gemini-powered smart classification with rule-based fallback
  - Agent capability scoring and load balancing
  - Routing history and statistics

- **`mcp_sharepoint_server.py`** - SharePoint MCP Server
  - Async Microsoft Graph API integration
  - CRUD operations for Projects, Tasks, Tickets, TimeEntries lists
  - List discovery and auto-creation
  - Search across lists
  - Analytics aggregation by field

#### Frontend - React Components

- **`src/components/TaskKanban.js`** - Task Board (NEW TAB)
  - Kanban board for TASKS (not projects) - drag-and-drop workflow
  - Columns: Not Started → In Progress → On Hold → Completed
  - Tasks linked to Projects via ProjectId/ProjectName
  - Filter by project, assignee, priority, search
  - Quick-add tasks to any column
  - Real-time sync with SharePoint Tasks list
  - Visual priority badges and due date indicators

- **`src/components/QuoteGenerator.js`** - Quote Generator
  - Complexity-based hour estimation (simple to enterprise)
  - Work type multipliers (development, design, consulting, support)
  - Employee billable rates ($125-$200/hr)
  - Buffer percentage option (default 15%)
  - Line items for detailed quotes
  - Export to text file

#### Configuration

- **`src/auth.js`** - Updated authentication
  - Added engineering team members (Mavrick, Patrick, Robbie)
  - Allow all @oberaconnect.com users
  - Improved error handling

### Changed

- **`agent_orchestrator.py`** - Enhanced orchestrator
  - Now supports BA Agent integration
  - MoE Router for intelligent task delegation
  - New `route_task()` method for automatic agent selection
  - New `execute_ba_task()` method for BA operations

- **`docker/agents/api_server.py`** - Updated API
  - Added BA Agent to available agents
  - Added MoE Router to available agents
  - Added SharePoint MCP server to available servers

- **`src/App.js`** - New "Task Board" tab
  - Added TaskKanban component as new navigation tab

### SharePoint Integration

The app syncs with the following SharePoint lists at:
`https://oberaconnect.sharepoint.com/sites/SOCTEAM-Engineering`

| List | Purpose | Key Fields |
|------|---------|------------|
| Projects | Project tracking | Title, Status, Priority, AssignedTo, Customer, BudgetHours, HoursSpent |
| Tasks | Task items linked to projects | Title, Status, Priority, ProjectId, ProjectName, DueDate, EstimatedHours |
| Tickets | Support tickets | Title, Status, Priority, Customer, SLAStatus |
| TimeEntries | Time logging | Employee, Hours, EntryDate, ProjectName, Billable |

### Employee Billable Rates

| Employee | Rate |
|----------|------|
| Mavrick Faison | $150/hr |
| Patrick McFarland | $135/hr |
| Robbie McFarland | $200/hr |
| Default | $125/hr |

---

## [1.0.0] - Previous

### Initial Release

- Projects management with cards and kanban views
- Time Reports with multiple views (by employee, project, task, billing)
- To-Do List with weekly planner
- Calendar component
- Tools Index
- Azure AD authentication via MSAL
- SharePoint List integration for data persistence

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React SPA)                      │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌────────────────┐  │
│  │Projects │ │TaskKanban│ │TimeReports│ │QuoteGenerator  │  │
│  └────┬────┘ └────┬─────┘ └─────┬─────┘ └───────┬────────┘  │
│       │           │             │               │            │
│       └───────────┴──────┬──────┴───────────────┘            │
│                          │                                    │
│                   ┌──────▼──────┐                            │
│                   │  Graph API  │                            │
│                   └──────┬──────┘                            │
└──────────────────────────┼───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   SharePoint Lists                            │
│  ┌─────────┐ ┌───────┐ ┌─────────┐ ┌─────────────┐          │
│  │Projects │ │ Tasks │ │Tickets  │ │ TimeEntries │          │
│  └─────────┘ └───────┘ └─────────┘ └─────────────┘          │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Backend Agents                            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    MoE Router                          │ │
│  │         (Intelligent Task Classification)              │ │
│  └───────────────────────┬────────────────────────────────┘ │
│              ┌───────────┼───────────┐                      │
│              ▼           ▼           ▼                      │
│  ┌───────────────┐ ┌───────────┐ ┌───────────────────────┐ │
│  │ Obsidian Mgr  │ │NotebookLM │ │      BA Agent         │ │
│  │ (Knowledge)   │ │(Analysis) │ │ (Business Analytics)  │ │
│  └───────────────┘ └───────────┘ └───────────────────────┘ │
│                                           │                  │
│                                    ┌──────▼──────┐          │
│                                    │   Gemini    │          │
│                                    │     AI      │          │
│                                    └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment

**Azure Static Web Apps**
- URL: https://jolly-island-06ade710f.3.azurestaticapps.net
- Region: Azure Global
- Authentication: Azure AD (MSAL)

**Deploy Command:**
```bash
npm run build
cp dist/bundle.js swa-build/dist/
SWA_CLI_DEPLOYMENT_TOKEN="..." npx @azure/static-web-apps-cli deploy ./swa-build --env production
```

---

## Files Created/Modified in 2.0.0

### New Files
| File | Lines | Description |
|------|-------|-------------|
| `agent_ba.py` | ~450 | Business Analytics Agent |
| `moe_router.py` | ~400 | Mixture of Experts Router |
| `mcp_sharepoint_server.py` | ~500 | SharePoint MCP Server |
| `src/components/TaskKanban.js` | ~500 | Task Kanban Board |
| `src/components/QuoteGenerator.js` | ~400 | Quote Generator |
| `list_sharepoint_data.py` | ~150 | CLI tool for SharePoint data |
| `browser_list_data.js` | ~100 | Browser console script |
| `CHANGELOG.md` | This file | Change documentation |

### Modified Files
| File | Changes |
|------|---------|
| `agent_orchestrator.py` | Added BA Agent, MoE integration |
| `docker/agents/api_server.py` | Added new agents to API |
| `src/App.js` | Added TaskKanban tab |
| `src/auth.js` | Added team members, domain check |
| `src/config.js` | No changes (already configured) |
