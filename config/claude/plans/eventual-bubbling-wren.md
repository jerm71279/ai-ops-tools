# WSL File Tree Reorganization - Optimal Hybrid Plan

## Overview
**Strategy:** Symlink-bridge migration with phased execution
**Estimated Space Savings:** ~16GB immediate, ~22GB total
**Risk Level:** Minimal (symlinks provide instant rollback)

---

## Phase 0: Audit & Backup

### 0.1 Run wsl_organizer.py analysis
```bash
python3 ~/wsl_organizer.py analyze ~ -o ~/wsl_analysis/
```

### 0.2 Grep ALL hardcoded paths (supplements tool gaps)
```bash
grep -rn "/home/mavrick" ~/Projects --include="*.py" | grep -v ".git" | grep -v "venv" | grep -v "__pycache__"
```

### 0.3 System checks
```bash
crontab -l                          # Check scheduled tasks
grep -r "mavrick" ~/.bashrc         # Check aliases
find ~ -maxdepth 3 -name ".git" -type d 2>/dev/null | head -20  # Git repos
```

### 0.4 Document .env locations
```bash
find ~ -name ".env" -type f 2>/dev/null | head -20
```

---

## Phase 1: Quick Wins (Reclaim ~16GB)

### 1.1 Clear caches
```bash
rm -rf ~/.cache/*                   # 6.6 GB
npm cache clean --force             # 1.5 GB
```

### 1.2 Delete orphan ZIPs (verify first)
```bash
ls -la ~/*.zip                      # Check what's there
# After verification:
rm ~/3da521c8-e248-4269-b61f-861ed6c20ab1-api.zip
rm ~/3da521c8-e248-4269-b61f-861ed6c20ab1-app.zip
rm ~/multi-ai-orchestrator.zip
rm "~/5 step AI.zip"
```

### 1.3 Delete recreatable venv
```bash
rm -rf ~/Projects/Secondbrain/venv  # 7.6 GB - will recreate in Phase 6
```

### 1.4 Remove backup/temp files
```bash
rm -f ~/ECC_APP/*.backup
rm -f ~/.claude.json.backup
find ~ -name "*.Zone.Identifier" -delete 2>/dev/null
rmdir ~/claude-test 2>/dev/null
```

---

## Phase 2: Create New Structure with Forward Symlinks

### 2.1 Create directory structure
```bash
mkdir -p ~/active ~/tools ~/archive ~/data ~/config
```

### 2.2 Create forward symlinks (new paths -> old locations)
```bash
# Active projects
ln -s ~/copilot-buddy-bytes ~/active/oberaconnect
ln -s ~/Projects/Secondbrain ~/active/secondbrain
ln -s ~/multi-ai-orchestrator ~/active/multi-ai-orchestrator
ln -s ~/Projects/network-config-builder ~/active/network-config-builder
ln -s ~/fara ~/active/fara
ln -s ~/AZ_Subs ~/active/az-subs

# Tools
ln -s ~/ECC_APP ~/tools/ecc-app
ln -s ~/Projects/Nmap_Project ~/tools/nmap-scanner

# Data
ln -s ~/input_documents ~/data/sharepoint
ln -s ~/logs ~/data/logs

# Config
ln -s ~/Projects/Secondbrain/.env ~/config/shared.env
```

### 2.3 Verify new structure works
```bash
ls -la ~/active/
ls -la ~/tools/
cat ~/config/shared.env | head -5  # Should show .env contents
```

---

## Phase 3: Deduplicate Projects

### 3.1 Compare multi-ai-orchestrator copies
```bash
# Compare root vs Secondbrain copy
diff -rq ~/multi-ai-orchestrator ~/Projects/Secondbrain/multi-ai-orchestrator 2>/dev/null | head -20

# Check for nested duplicate
ls ~/multi-ai-orchestrator/multi-ai-orchestrator 2>/dev/null
```

### 3.2 Compare copilot-buddy-bytes copies
```bash
diff -rq ~/copilot-buddy-bytes ~/Projects/Secondbrain/separate_projects/copilot-buddy-bytes-2 2>/dev/null | head -20
```

### 3.3 Delete confirmed duplicates (after diff verification)
```bash
# Nested duplicate inside multi-ai-orchestrator
rm -rf ~/multi-ai-orchestrator/multi-ai-orchestrator

# Secondbrain embedded copies
rm -rf ~/Projects/Secondbrain/multi-ai-orchestrator
rm -rf ~/Projects/Secondbrain/separate_projects/copilot-buddy-bytes-2
rm -rf ~/Projects/Secondbrain/separate_projects/copilot-buddy-bytes-main
```

---

## Phase 4: Gradual Code Updates

### 4.1 Add environment variable to .bashrc
```bash
echo 'export OBERA_HOME="$HOME"' >> ~/.bashrc
source ~/.bashrc
```

### 4.2 Files to update (priority order)

| Priority | File | Hardcoded Paths |
|----------|------|-----------------|
| 1 | `Projects/Secondbrain/OberaAIStrategy/integrations/project_registry.py` | Central registry - 8+ paths |
| 2 | `Projects/Secondbrain/call_flow_web_auth.py` | 6 paths + sys.path.insert |
| 3 | `Projects/Secondbrain/new_site_install_automation.py` | 7 paths |
| 4 | `Projects/Secondbrain/network_checklist.py` | .env path, logo path, template |
| 5 | `Projects/Secondbrain/gunicorn_config.py` | Log paths |
| 6 | `Projects/Secondbrain/gunicorn_config_ssl.py` | SSL + log paths |
| 7 | `Projects/Secondbrain/process_sharepoint.py` | CHROMA_DB_DIR |
| 8 | `Projects/Secondbrain/sync_comments_to_md.py` | .env, COMMENTS_DIR |
| 9 | `Projects/Secondbrain/comment_utils.py` | .env, COMMENTS_DIR |
| 10 | `Projects/Secondbrain/fill_spanish_fort_checklist.py` | Template, output paths |
| 11 | `Projects/Secondbrain/config_complexity_analyzer.py` | keeper_configs, input_documents |
| 12 | `Projects/Secondbrain/test_persistence.py` | CHROMA_DIR |
| 13 | `Projects/Secondbrain/test_chromadb.py` | CHROMA_DIR |
| 14 | `Projects/Secondbrain/add_comments_column.py` | .env path |
| 15 | `Projects/Secondbrain/update_ee_dashboard.py` | .env path |
| 16 | `Projects/Secondbrain/scripts/convert_sop_to_docx.py` | sops_dir, output_dir |
| 17 | `Projects/Secondbrain/OberaAIStrategy/integrations/feedback_aggregator.py` | data path |
| 18 | `AZ_Subs/Obera/.env` | AZURE_CONFIG_DIR |

### 4.3 Update pattern
```python
# BEFORE
SOME_PATH = Path("/home/mavrick/Projects/Secondbrain/data")

# AFTER
import os
OBERA_HOME = Path(os.environ.get('OBERA_HOME', os.path.expanduser('~')))
SOME_PATH = OBERA_HOME / "active" / "secondbrain" / "data"
```

### 4.4 Test after each file update
```bash
python3 -c "import sys; sys.path.insert(0, '.'); from <module> import *; print('OK')"
```

---

## Phase 5: Flip Symlinks (Physical Moves)

### 5.1 Move files to new structure, create backward-compat symlinks
```bash
# Example for copilot-buddy-bytes -> oberaconnect
rm ~/active/oberaconnect                           # Remove forward symlink
mv ~/copilot-buddy-bytes ~/active/oberaconnect     # Physical move
ln -s ~/active/oberaconnect ~/copilot-buddy-bytes  # Backward compat symlink

# Repeat for each project...
```

### 5.2 Full move sequence
```bash
# Active projects
rm ~/active/oberaconnect && mv ~/copilot-buddy-bytes ~/active/oberaconnect && ln -s ~/active/oberaconnect ~/copilot-buddy-bytes
rm ~/active/secondbrain && mv ~/Projects/Secondbrain ~/active/secondbrain && ln -s ~/active/secondbrain ~/Projects/Secondbrain
rm ~/active/multi-ai-orchestrator && mv ~/multi-ai-orchestrator ~/active/multi-ai-orchestrator && ln -s ~/active/multi-ai-orchestrator ~/multi-ai-orchestrator
rm ~/active/network-config-builder && mv ~/Projects/network-config-builder ~/active/network-config-builder && ln -s ~/active/network-config-builder ~/Projects/network-config-builder
rm ~/active/fara && mv ~/fara ~/active/fara && ln -s ~/active/fara ~/fara
rm ~/active/az-subs && mv ~/AZ_Subs ~/active/az-subs && ln -s ~/active/az-subs ~/AZ_Subs

# Tools
rm ~/tools/ecc-app && mv ~/ECC_APP ~/tools/ecc-app && ln -s ~/tools/ecc-app ~/ECC_APP
rm ~/tools/nmap-scanner && mv ~/Projects/Nmap_Project ~/tools/nmap-scanner && ln -s ~/tools/nmap-scanner ~/Projects/Nmap_Project

# Data
rm ~/data/sharepoint && mv ~/input_documents ~/data/sharepoint && ln -s ~/data/sharepoint ~/input_documents
rm ~/data/logs && mv ~/logs ~/data/logs && ln -s ~/data/logs ~/logs
```

---

## Phase 6: Validation & Final Cleanup

### 6.1 Recreate Python virtual environment
```bash
cd ~/active/secondbrain
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6.2 Test critical functionality
```bash
# Test Flask app
cd ~/active/secondbrain && python3 call_flow_web_auth.py --help

# Test project registry
python3 -c "from OberaAIStrategy.integrations.project_registry import PROJECT_REGISTRY; print(PROJECT_REGISTRY)"

# Test SharePoint sync (if applicable)
python3 process_sharepoint.py --dry-run
```

### 6.3 Archive large data (optional - external storage)
```bash
# Nmap scan results (~6GB)
tar -czf /mnt/external/nmap-scans-backup.tar.gz ~/tools/nmap-scanner/scans/
rm -rf ~/tools/nmap-scanner/scans/*
```

### 6.4 Remove backward-compat symlinks (after 1-2 weeks stable)
```bash
rm ~/copilot-buddy-bytes
rm ~/multi-ai-orchestrator
rm ~/fara
rm ~/AZ_Subs
rm ~/ECC_APP
rm ~/Projects/Secondbrain
rm ~/Projects/network-config-builder
rm ~/Projects/Nmap_Project
rm ~/input_documents
rm ~/logs
```

### 6.5 Clean up empty directories
```bash
rmdir ~/Projects 2>/dev/null  # Only if empty
```

---

## Final Structure

```
/home/mavrick/
├── active/                      # Active development
│   ├── oberaconnect/            # React SaaS platform
│   ├── secondbrain/             # Main AI/automation hub
│   ├── multi-ai-orchestrator/   # AI orchestration CLI
│   ├── network-config-builder/  # Network automation
│   ├── fara/                    # Microsoft Fara-7B
│   └── az-subs/                 # Azure MCP server
│
├── tools/                       # Utilities
│   ├── ecc-app/                 # Engineering Command Center
│   └── nmap-scanner/            # Network scanning
│
├── archive/                     # Completed/dormant projects
│   └── (move old projects here)
│
├── data/                        # All data consolidated
│   ├── sharepoint/              # SharePoint sync data
│   └── logs/                    # Centralized logs
│
├── config/                      # Shared configuration
│   └── shared.env -> active/secondbrain/.env
│
├── Personal/                    # Keep as-is
└── wsl_organizer.py             # This tool
```

---

## Rollback Procedure

At any phase, to rollback:

**Phase 1:** Cannot rollback (but nothing breaks - just less disk space)

**Phase 2-4:** Remove symlinks:
```bash
rm -rf ~/active ~/tools ~/data ~/config
```

**Phase 5:** Reverse the moves:
```bash
# Example
rm ~/copilot-buddy-bytes                           # Remove backward symlink
mv ~/active/oberaconnect ~/copilot-buddy-bytes     # Move back
```

**Phase 6:** Re-delete venv if needed, restore from backup
