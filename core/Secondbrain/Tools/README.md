# Secondbrain Tools

Organized collection of automation tools for OberaConnect MSP operations.

---

## Directory Structure

```
Tools/
├── Agents/              # AI agents and orchestrators
├── Call-Flow/           # Phone system call flow automation
├── Dashboards/          # Engineering and operations dashboards
├── Data-Processing/     # Data import and processing tools
├── MCP-Servers/         # Model Context Protocol servers
├── Network-Checklists/  # Network configuration tools
├── Obsidian-Management/ # Knowledge base management
├── RAG-Query/           # Retrieval-Augmented Generation tools
├── SharePoint-Sync/     # SharePoint document synchronization
└── UniFi-Automation/    # UniFi network bulk configuration
```

---

## Tool Categories

### Agents (`Agents/`)
AI agent implementations for automated task handling.

| Tool | Description |
|------|-------------|
| `agent_orchestrator.py` | Multi-agent coordination |
| `agent_ba.py` | Business Analyst agent |
| `agent_notebooklm_analyst.py` | NotebookLM integration |
| `agent_obsidian_manager.py` | Obsidian vault management agent |
| `moe_router.py` | Mixture of Experts router |

### Call Flow (`Call-Flow/`)
Automated phone system call flow generation.

| Tool | Description |
|------|-------------|
| `call_flow_generator.py` | Generate call flow documentation |
| `call_flow_processor.py` | Process call flow data |
| `call_flow_web.py` | Web interface for call flows |
| `call_flow_web_auth.py` | Authenticated call flow web app |

### Dashboards (`Dashboards/`)
Operations and engineering dashboards.

| Tool | Description |
|------|-------------|
| `daily_engineering_summary.py` | Daily engineering email report |
| `engineering_tracker.py` | Project tracking dashboard |
| `ecs_dashboard.py` | Engineering Command System |
| `ee_team_dashboard.py` | EE team status dashboard |
| `update_ee_dashboard.py` | Dashboard data updater |
| `contract_tracker.py` | Contract management tracking |

### Data Processing (`Data-Processing/`)
Data import and transformation tools.

| Tool | Description |
|------|-------------|
| `process_all_sharepoint.py` | Bulk SharePoint processing |
| `process_batch.py` | Batch document processing |
| `slab_importer.py` | Slab wiki importer |
| `slab_scraper.py` | Slab content scraper |
| `slack_importer.py` | Slack history importer |
| `metadata_extractor.py` | Document metadata extraction |

### MCP Servers (`MCP-Servers/`)
Model Context Protocol servers for Claude integration.

| Tool | Description |
|------|-------------|
| `mcp_keeper_server.py` | Keeper Security MCP |
| `mcp_sharepoint_server.py` | SharePoint MCP |
| `mcp_obsidian_server.py` | Obsidian vault MCP |
| `mcp_notebooklm_server.py` | NotebookLM MCP |

### Network Checklists (`Network-Checklists/`)
Network installation and configuration automation.

| Tool | Description |
|------|-------------|
| `network_checklist.py` | Generate network checklists |
| `network_checklist_filler.py` | Auto-fill checklist data |
| `fill_spanish_fort_checklist.py` | Spanish Fort site automation |
| `sync_customer_checklists.py` | Sync checklists from SharePoint |
| `config_complexity_analyzer.py` | Analyze config complexity |

### Obsidian Management (`Obsidian-Management/`)
Knowledge base maintenance tools.

| Tool | Description |
|------|-------------|
| `cleanup_vault.py` | Clean orphaned notes |
| `organize_notes_by_tags.py` | Tag-based organization |
| `rename_with_tags.py` | Bulk rename by tags |
| `suggest_links.py` | Auto-suggest wiki links |
| `add_links_for_graph.py` | Graph view link creation |

### RAG Query (`RAG-Query/`)
Retrieval-Augmented Generation tools.

| Tool | Description |
|------|-------------|
| `query_brain.py` | CLI knowledge base query |
| `query_brain_enhanced.py` | Enhanced query with context |
| `query_brain_html.py` | HTML output queries |
| `rag_web.py` | Web-based RAG interface |
| `agentic_rag.py` | Agent-based RAG pipeline |
| `rebuild_index.py` | Rebuild vector index |
| `entity_extractor.py` | Extract entities from docs |
| `query_classifier.py` | Query type classification |

### SharePoint Sync (`SharePoint-Sync/`)
SharePoint document synchronization.

| Tool | Description |
|------|-------------|
| `sync_sharepoint.py` | Daily SharePoint sync (cron) |
| `download_sharepoint.py` | Download SharePoint files |
| `download_all_sharepoint.py` | Full SharePoint download |
| `upload_to_sharepoint.py` | Upload files to SharePoint |
| `sharepoint_importer.py` | Import to knowledge base |
| `list_sharepoint_data.py` | List SharePoint contents |
| `process_sharepoint.py` | Process SharePoint docs |

### UniFi Automation (`UniFi-Automation/`)
UniFi network bulk configuration via API.

| Tool | Description | SOP |
|------|-------------|-----|
| `udm_pro_bulk_config.py` | Bulk VLAN creation | SOP-NET-008 |
| `enable_network_isolation.py` | Toggle network isolation |
| `delete_units_zone.py` | Delete firewall zones |
| `find_zone_api.py` | API endpoint discovery |

---

## Core Libraries

Shared libraries in `/core/`:

| Library | Description |
|---------|-------------|
| `config.py` | Configuration and environment |
| `vector_store.py` | ChromaDB vector operations |
| `obsidian_vault.py` | Obsidian note management |
| `document_processor.py` | Document parsing/processing |
| `structured_store.py` | SQLite structured data |
| `comment_utils.py` | Comment system utilities |
| `claude_processor.py` | Claude API integration |
| `html_generator.py` | HTML document generation |

---

## Usage

All tools support the project root as their working directory:

```bash
cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate

# Run a tool
python3 Tools/RAG-Query/query_brain.py "search query"

# Run SharePoint sync
python3 Tools/SharePoint-Sync/sync_sharepoint.py
```

---

## Cron Jobs (Active)

| Schedule | Tool | Description |
|----------|------|-------------|
| 5:00 AM | `Tools/SharePoint-Sync/sync_sharepoint.py` | Daily SharePoint sync |
| 5:15 AM | `Tools/Network-Checklists/sync_customer_checklists.py` | Checklist sync |
| 5:30 AM | `Tools/Obsidian-Management/organize_notes_by_tags.py` | Organize notes |
| 6:00 AM | `OberaAIStrategy/run_strategy.py` | AI strategy aggregation |
| 6:30 AM | `project_automation.py` | Project automation |
| 7:00 AM | `scripts/azure_backup_report.py` | Azure backup report |

---

## Related SOPs

| SOP ID | Title | Tool Folder |
|--------|-------|-------------|
| SOP-NET-008 | UniFi Bulk Deployment | `UniFi-Automation/` |

---

## Last Updated
2025-12-30 - Full reorganization from root-level scripts
