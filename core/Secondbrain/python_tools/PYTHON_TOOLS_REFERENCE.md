# Secondbrain Python Tools Reference

> **82 Python tools** for AI agents, SharePoint, engineering tracking, and knowledge management.
>
> Last updated: 2025-12-08

---

## AI Agents & Orchestration

| Tool | Description |
|------|-------------|
| `agent_ba.py` | Business Analytics agent - project health, metrics, quotes |
| `agent_notebooklm_analyst.py` | NotebookLM knowledge analyst |
| `agent_obsidian_manager.py` | Obsidian knowledge base manager |
| `agent_orchestrator.py` | MoE router coordinating all agents |
| `moe_router.py` | Mixture of Experts task routing |
| `claude_processor.py` | Claude API for content structuring |

---

## MCP Servers

| Tool | Description |
|------|-------------|
| `mcp_obsidian_server.py` | Obsidian vault operations |
| `mcp_sharepoint_server.py` | SharePoint list operations |
| `mcp_keeper_server.py` | Keeper vault credentials |
| `mcp_notebooklm_server.py` | NotebookLM analysis workflow |

---

## API Servers

| Tool | Description |
|------|-------------|
| `api_server_agents.py` | Agent orchestration endpoints |
| `api_server_data.py` | Data import trigger endpoints |
| `api_server_engineering.py` | Engineering tracking/reporting |
| `rag_web.py` | Web interface for RAG queries (port 5050) |
| `call_flow_web.py` | Call flow web interface |
| `call_flow_web_auth.py` | Call flow web with auth |

---

## SharePoint Tools

| Tool | Description |
|------|-------------|
| `sync_sharepoint.py` | Download new/updated docs from SharePoint |
| `upload_to_sharepoint.py` | Upload files back to SharePoint |
| `download_sharepoint.py` | Download from All Company site |
| `download_all_sharepoint.py` | Download ALL docs from ALL sites |
| `download_key_sites.py` | Download from key sites only |
| `list_sharepoint_data.py` | Fetch/display SharePoint list data |
| `sharepoint_importer.py` | Import SharePoint docs |
| `process_sharepoint.py` | Process SharePoint docs into vault |
| `process_sharepoint_structured.py` | Process preserving folder structure |
| `create_tasks_list.py` | Create Tasks list via Graph API |
| `create_employees_list.py` | Create Employees list via Graph API |
| `create_timeentries_list.py` | Create TimeEntries list |
| `add_comments_column.py` | Add comments column to lists |
| `sync_comments_to_md.py` | Sync SharePoint comments to markdown |
| `comment_utils.py` | Comment management utilities |
| `organize_sharepoint_structure.py` | Organize notes into folder structure |
| `move_sharepoint_to_subfolder.py` | Move SharePoint notes to subfolder |
| `reorganize_sharepoint_notes.py` | Reorganize existing notes |
| `process_all_sharepoint.py` | Process ALL SharePoint documents |
| `process_sharepoint_all_simple.py` | Simple processor using batch logic |

### SharePoint Usage Examples

```bash
# Download new/updated docs
./venv/bin/python3 sync_sharepoint.py

# Upload file to SharePoint
./venv/bin/python3 upload_to_sharepoint.py \
  "path/to/local/file.html" \
  --site-id "oberaconnect.sharepoint.com,..." \
  --folder "Documents/Customer/Folder"

# List SharePoint data
./venv/bin/python3 list_sharepoint_data.py
```

---

## Engineering & Project Tracking

| Tool | Description |
|------|-------------|
| `engineering_tracker.py` | Manage projects/tickets via SharePoint |
| `daily_engineering_summary.py` | Generate/email daily summary |
| `ecs_dashboard.py` | Export data for Power BI dashboard |
| `ee_team_dashboard.py` | EE Team daily summary generator |
| `update_ee_dashboard.py` | Update EE dashboard (cron job) |
| `project_automation.py` | Watch ECS for new installs, auto-create |
| `contract_tracker.py` | Track contracts, renewals, SLAs |

---

## Network & Customer Tools

| Tool | Description |
|------|-------------|
| `network_checklist.py` | Generate HTML network install checklist |
| `network_checklist_filler.py` | Pull customer data, fill checklist |
| `fill_spanish_fort_checklist.py` | Fill checklist for Spanish Fort |
| `new_site_install_automation.py` | New site install automation |
| `call_flow_generator.py` | Create customer call flows |
| `call_flow_processor.py` | Process existing call flow docs |

### Network Checklist Usage

```bash
# Generate checklist for a customer
./venv/bin/python3 network_checklist_filler.py --customer "Customer Name"

# Generate blank checklist template
./venv/bin/python3 network_checklist.py
```

---

## Obsidian Vault Tools

| Tool | Description |
|------|-------------|
| `obsidian_vault.py` | Vault manager stub |
| `cleanup_vault.py` | Remove verbose AI content |
| `suggest_links.py` | Suggest wiki links between notes |
| `add_links_for_graph.py` | Add links for Graph View |
| `create_master_canvas.py` | Master canvas with all 4 teams |
| `create_team_canvases.py` | Team-specific canvases |
| `team_link_clusters.py` | Link clusters by team |
| `rename_with_tags.py` | Rename notes with [tag] prefix |
| `rebuild_index.py` | Rebuild vector store index |

---

## Query & RAG

| Tool | Description |
|------|-------------|
| `query_brain.py` | Query vault with RAG |
| `query_brain_enhanced.py` | Enhanced with Obsidian URI links |
| `query_brain_html.py` | HTML output with clickable links |
| `vector_store.py` | Vector embeddings manager |

### Query Usage

```bash
# CLI query
./venv/bin/python3 query_brain.py "What is the network setup for Customer X?"

# Start web interface
./venv/bin/python3 rag_web.py
# Then visit http://localhost:5050
```

---

## Importers

| Tool | Description |
|------|-------------|
| `slab_importer.py` | Fetch from Slab via GraphQL |
| `slab_scraper.py` | Scrape Slab with Playwright |
| `process_slab.py` | Process Slab into vault |
| `process_slab_export.py` | Process Slab exported content |
| `slack_importer.py` | Import Slack messages/files |
| `document_processor.py` | Extract text from various formats |
| `metadata_extractor.py` | Extract operational metadata |
| `process_batch.py` | Batch document processor |

---

## Utilities

| Tool | Description |
|------|-------------|
| `config.py` | System configuration |
| `html_generator.py` | OberaConnect branded HTML docs |
| `gunicorn_config.py` | Gunicorn production config |
| `gunicorn_config_ssl.py` | Gunicorn SSL config |
| `convert.py` | Document conversion |
| `convert_v2.py` | Document conversion v2 |
| `list_employees.py` | Extract employee info from notes |
| `search_celebration.py` | Search Celebration Church docs |

---

## Cleanup Tools

| Tool | Description |
|------|-------------|
| `remove_copilot_content.py` | Remove copilot-buddy-bytes content |
| `remove_oberaconnect.py` | Remove OberaConnect/copilot content |
| `remove_platform_dev.py` | Remove platform dev files |

---

## Test Files

| Tool | Description |
|------|-------------|
| `test_chromadb.py` | Test ChromaDB persistence |
| `test_persistence.py` | Test persistence across sessions |

---

## AI-OS (5-Layer AI Operating System)

Located in `ai_os/` directory. Start with:

```bash
# Interactive CLI
./venv/bin/python3 ai_os/run.py

# Single query
./venv/bin/python3 -m ai_os.run "Your query here"

# API server
./venv/bin/python3 -m ai_os.run --api --port 8080
```

See `ai_os/ARCHITECTURE.md` for full documentation.

---

## Common SharePoint Site IDs

| Site | ID |
|------|-----|
| OberaConnect Technical | `oberaconnect.sharepoint.com,7c44e518-e9bd-4a53-b39b-036d1b30edb4,75282f0b-6bd7-437c-99e7-1cf44cff867d` |
| OberaConnect Admin | `oberaconnect.sharepoint.com,264e463d-b48b-485a-bb7d-8f1c908700be,bd344dc6-e8de-4089-bc5e-6ff921994375` |
| Engineering | `oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef` |
| EE Team | `oberaconnect.sharepoint.com,65a13881-1f98-41e7-9c59-331ac64e3773,aa08227f-8971-49bd-a3aa-0619149872e6` |

---

## Environment Variables Required

```bash
# Azure/SharePoint
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# Obsidian
OBSIDIAN_VAULT_PATH=/path/to/vault

# APIs
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```
