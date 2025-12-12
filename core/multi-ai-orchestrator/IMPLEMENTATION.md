# MAI Implementation Guide
## Complete Setup for OberaConnect Platform Integration

---

## Quick Start (TL;DR)

```bash
# 1. Check status
cd /home/mavrick/multi-ai-orchestrator
./mai status

# 2. Test single task
./mai run "Generate a MikroTik firewall rule to block port 23"

# 3. Test with specific provider
./mai run --provider claude "Write a PowerShell script to check disk space"
./mai run --provider gemini --file /var/log/syslog "Summarize errors in this log"

# 4. Run a workflow
./mai workflow customer_onboarding --customer "TestCorp" --portal-url https://example.com
```

---

## Prerequisites Checklist

### 1. AI Provider CLIs

| Provider | Check Command | Install Command |
|----------|--------------|-----------------|
| Claude | `which claude` | `npm install -g @anthropic-ai/claude-cli && claude auth` |
| Gemini | `which gemini` | `npm install -g @google/gemini-cli && gemini auth` |
| Fara-7B | `ls ~/fara/.venv/bin/python` | See Fara setup below |

### 2. API Keys

```bash
# Check current status
echo "ANTHROPIC: $([ -n "$ANTHROPIC_API_KEY" ] && echo 'SET' || echo 'NOT SET')"
echo "GOOGLE: $([ -n "$GOOGLE_API_KEY" ] && echo 'SET' || echo 'NOT SET')"

# Set keys (add to ~/.bashrc)
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."
```

### 3. Fara-7B Setup (if not installed)

```bash
# Clone and setup
git clone https://github.com/microsoft/fara.git ~/fara
cd ~/fara
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install
```

---

## Usage Guide

### Single Task Execution

```bash
# Auto-select best provider based on task
./mai run "Your prompt here"

# Force specific provider
./mai run --provider claude "Generate Python code for..."
./mai run --provider gemini "Analyze this large document..."
./mai run --provider fara "Navigate to portal and extract..."

# With files
./mai run --provider gemini --file log1.txt --file log2.txt "Analyze these logs"

# Save output to file
./mai run "Generate bash script" -o script.sh
```

### Provider Selection Guide

| Task Type | Use Provider | Flag |
|-----------|-------------|------|
| Code generation | Claude | `--provider claude` |
| Config files (MikroTik, UniFi) | Claude | `--provider claude` |
| Documentation/SOPs | Claude | `--provider claude` |
| Large log analysis (>100KB) | Gemini | `--provider gemini` |
| Video/audio analysis | Gemini | `--provider gemini` |
| Web portal automation | Fara | `--provider fara` |
| Form filling/scraping | Fara | `--provider fara` |

### Workflow Execution

```bash
# List available workflows
./mai workflow --list

# Customer onboarding
./mai workflow customer_onboarding \
  --customer "Acme Corp" \
  --portal-url https://vendor.portal.com \
  --deployment-type standard

# Incident analysis
./mai workflow incident_analysis \
  --incident-id INC-2024-0042 \
  --log-files /var/log/syslog /var/log/auth.log \
  --systems firewall webserver database

# SOP capture from portal
./mai workflow sop_from_portal \
  --sop-name "Create Azure VM" \
  --portal-url https://portal.azure.com \
  --task "Create a Windows Server 2022 VM"

# Vendor price comparison
./mai workflow vendor_price_comparison \
  --product "Ubiquiti U6-Pro" \
  --vendor-urls https://store.ui.com https://amazon.com
```

---

## OberaConnect Platform Integration

### Option A: Direct CLI Calls (Simple)

Call MAI from your platform using subprocess:

```typescript
// In your Edge Function or backend
import { exec } from 'child_process';

async function callMAI(taskType: string, prompt: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const cmd = `cd /home/mavrick/multi-ai-orchestrator && ./mai run --provider ${getProvider(taskType)} "${prompt}"`;
    exec(cmd, (error, stdout, stderr) => {
      if (error) reject(stderr);
      else resolve(stdout);
    });
  });
}

function getProvider(taskType: string): string {
  const routing = {
    'code': 'claude',
    'config': 'claude',
    'docs': 'claude',
    'logs': 'gemini',
    'portal': 'fara'
  };
  return routing[taskType] || 'claude';
}
```

### Option B: Python API (Recommended)

```python
# mai_client.py
import sys
sys.path.insert(0, '/home/mavrick/multi-ai-orchestrator')

from lib import AIClientFactory, AIProvider, select_best_client
from lib.orchestrator import Pipeline, PipelineBuilder

# Single task
def run_task(task_type: str, prompt: str) -> str:
    provider = select_best_client(task_type)
    client = AIClientFactory.get_client(provider)
    response = client.execute(prompt=prompt)
    return response.content

# Pipeline
def run_pipeline(workflow_name: str, **kwargs):
    from workflows.oberaconnect_workflows import get_workflow
    pipeline = get_workflow(workflow_name, **kwargs)
    result = pipeline.execute()
    return result.outputs
```

### Option C: HTTP API Gateway (Production)

Create a FastAPI wrapper:

```python
# mai_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, '/home/mavrick/multi-ai-orchestrator')

from lib import AIClientFactory, select_best_client
from workflows.oberaconnect_workflows import get_workflow

app = FastAPI(title="MAI Gateway")

class TaskRequest(BaseModel):
    task_type: str
    prompt: str
    context: dict = {}

class WorkflowRequest(BaseModel):
    workflow_name: str
    inputs: dict

@app.post("/task")
async def execute_task(request: TaskRequest):
    provider = select_best_client(request.task_type)
    client = AIClientFactory.get_client(provider)
    response = client.execute(prompt=request.prompt)
    return {
        "success": response.success,
        "content": response.content,
        "provider": provider.value
    }

@app.post("/workflow")
async def execute_workflow(request: WorkflowRequest):
    pipeline = get_workflow(request.workflow_name, **request.inputs)
    result = pipeline.execute()
    return result.to_dict()

@app.get("/status")
async def status():
    available = AIClientFactory.get_available_clients()
    return {
        "claude": AIProvider.CLAUDE in available,
        "gemini": AIProvider.GEMINI in available,
        "fara": AIProvider.FARA in available
    }

# Run with: uvicorn mai_api:app --host 0.0.0.0 --port 8000
```

---

## Testing Guide

### Test 1: Provider Availability

```bash
./mai status
```

Expected:
```
Claude CLI      ✅ Available
Gemini CLI      ✅ Available
Fara-7B         ✅ Available
```

### Test 2: Single Task (Claude)

```bash
./mai run --provider claude "Generate a simple MikroTik firewall rule to allow SSH from 10.0.0.0/24"
```

### Test 3: Single Task (Gemini with file)

```bash
# Create test log
echo "2024-12-07 10:00:00 ERROR Connection refused
2024-12-07 10:01:00 WARNING High memory usage
2024-12-07 10:02:00 ERROR Timeout waiting for response" > /tmp/test.log

./mai run --provider gemini --file /tmp/test.log "Summarize the errors in this log"
```

### Test 4: Workflow Pipeline

```bash
./mai workflow --list

# Then run one:
./mai workflow customer_onboarding --customer "TestCo" --portal-url https://test.com --deployment-type standard
```

---

## Troubleshooting

### Issue: "Provider not available"

```bash
# Check which provider
./mai status

# Reinstall if needed
npm install -g @anthropic-ai/claude-cli
claude auth

npm install -g @google/gemini-cli
gemini auth
```

### Issue: "API key not set"

```bash
# Add to ~/.bashrc
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
source ~/.bashrc
```

### Issue: "Timeout"

Edit `/home/mavrick/multi-ai-orchestrator/config/settings.json`:

```json
{
  "providers": {
    "claude": { "timeout": 600 },
    "gemini": { "timeout": 900 }
  }
}
```

### Issue: "Fara browser errors"

```bash
cd ~/fara
source .venv/bin/activate
playwright install
playwright install-deps
```

---

## File Locations

```
/home/mavrick/multi-ai-orchestrator/
├── mai                      # Main CLI executable
├── config/
│   └── settings.json        # Configuration
├── lib/
│   ├── ai_clients.py        # Provider wrappers
│   └── orchestrator.py      # Pipeline engine
├── workflows/
│   └── oberaconnect_workflows.py  # Pre-built workflows
├── output/                  # Workflow outputs saved here
└── logs/                    # Execution logs
```

---

## Next Steps

1. **Test the basics**: Run `./mai status` and `./mai run "hello"`
2. **Try a workflow**: Run `./mai workflow --list` and pick one
3. **Integrate with platform**: Choose Option A, B, or C above
4. **Add Identity Layer**: Load your master prompt into calls

---

## Support

- Documentation: `/home/mavrick/5_step_AI/oberaconnect-mai-architecture.md`
- HTML Docs: `/home/mavrick/5_step_AI/oberaconnect-mai-architecture.html`
- Workflow Source: `/home/mavrick/multi-ai-orchestrator/workflows/oberaconnect_workflows.py`
