# n8n + MAI Orchestrator Integration Plan

## Overview
Integrate n8n as the top-level orchestrator calling the existing Multi-AI Orchestrator (MAI) and Secondbrain infrastructure, enabling external triggers, session persistence, Slack access, and BA Agent integration.

## Architecture

```
                         EXTERNAL TRIGGERS
          +------------------------------------------+
          |   Slack   |  Webhooks  |  Schedules      |
          +------------------------------------------+
                              |
                              v
+=========================================================================+
|                        n8n ORCHESTRATOR (Port 5678)                      |
|  - MAI Pipeline Triggers    - Conversational Claude Sessions            |
|  - Scheduled BA Reports     - Slack Bot Command Router                  |
+=========================================================================+
          |                    |                     |
          | SSH                | HTTP                | HTTP
          v                    v                     v
+------------------+   +------------------+   +------------------+
|  MAI + Claude    |   | Secondbrain API  |   |    BA Agent      |
|  (Dangerous Mode)|   | Gateway :8080    |   |    :8085         |
+------------------+   +------------------+   +------------------+
          |                    |                     |
          +--------------------+---------------------+
                              |
                    SHARED DATA LAYER
          - MAI Output: /home/mavrick/multi-ai-orchestrator/output/
          - Sessions: Redis (session IDs for Claude -r flag)
          - MCP: SharePoint, Keeper
```

## Critical Files

### Existing (to reference/modify)
- `/home/mavrick/Projects/Secondbrain/docker-compose.yml` - Add n8n services
- `/home/mavrick/multi-ai-orchestrator/mai` - CLI entry point for SSH calls
- `/home/mavrick/multi-ai-orchestrator/lib/ai_clients.py` - Claude CLI patterns
- `/home/mavrick/Projects/Secondbrain/agent_ba.py` - BA Agent to expose via HTTP
- `/home/mavrick/Projects/Secondbrain/docker/nginx.conf` - Add n8n routing

### To Create
- `/home/mavrick/Projects/Secondbrain/docker/mai-executor/Dockerfile` - Isolated Claude container
- `/home/mavrick/Projects/Secondbrain/.env.n8n` - n8n secrets/config
- `/home/mavrick/Projects/Secondbrain/n8n_integration/session_manager.py` - Redis session store
- `/home/mavrick/Projects/Secondbrain/n8n_workflows/` - Workflow JSON exports

---

## Implementation Phases

### Phase 1: Foundation (Deploy n8n)
1. Add to `docker-compose.yml`:
   - n8n service (port 5678)
   - Redis service (session store)
   - mai-executor container (isolated Claude Code)

2. Create `.env.n8n` with:
   - N8N_USER, N8N_PASSWORD
   - TEAMS_BOT_ID, TEAMS_BOT_PASSWORD (Azure Bot Service)
   - MAI_SSH_HOST, MAI_SSH_USER

3. Update `nginx.conf`:
   - Add n8n upstream
   - Add webhook routing

4. Test: Basic n8n → SSH → `./mai status`

### Phase 2: MAI Integration
1. Create n8n workflow: `mai_pipeline_executor.json`
   - SSH node executes: `./mai workflow {name} {params}`
   - Parse JSON output
   - Slack notification on completion

2. Create workflows for each MAI pipeline:
   - customer_onboarding
   - incident_analysis
   - vendor_data_extraction
   - azure_service_deployment
   - sop_from_portal
   - vendor_price_comparison

3. Test: Trigger each workflow via n8n webhook

### Phase 3: Session Management
1. Create `session_manager.py`:
   ```python
   class ClaudeSessionManager:
       def get_or_create_session(user_id) -> session_id
       def end_session(user_id)
       # Sessions stored in Redis with 24h TTL
   ```

2. Create n8n workflow: `claude_session.json`
   - Get/create session from Redis
   - New: `claude --dangerously-skip-permissions -p "{prompt}"`
   - Resume: `claude -r {session_id} -p "{prompt}"`
   - Store session ID for future use

3. Test: Multi-turn conversation via n8n

### Phase 4: MS Teams Integration
1. Create Teams Bot via Azure Bot Service:
   - Register bot in Azure AD
   - Configure messaging endpoint
   - Add to OberaConnect Teams tenant

2. Create n8n workflow: `teams_bot_router.json`
   - `@ai run <prompt>` → Claude session workflow
   - `@ai workflow <name>` → MAI pipeline workflow
   - `@ai ba <report>` → BA Agent workflow
   - `@ai status` → System status

3. Test: Interact via Teams mobile/desktop app

### Phase 5: BA Agent Integration
1. Enhance BA Agent API in `docker/agents/`:
   - POST `/agents/ba/run` with task types:
     - project_health
     - resource_utilization
     - executive_summary
     - quote

2. Create n8n workflows:
   - `ba_daily_report.json` (scheduled)
   - `ba_weekly_executive.json` (scheduled Monday)
   - `ba_on_demand.json` (Slack triggered)

3. Test: Scheduled reports to Slack channel

### Phase 6: Webhook Consolidation
1. Create `webhook_master_router.json`:
   - Route by source (GitHub, NinjaOne, Azure DevOps)
   - Signature validation
   - Execute appropriate sub-workflow

2. Migrate existing webhook handlers from `ai_os/layer1_interface/webhooks.py`

3. Test: End-to-end webhook → AI response

---

## Docker Compose Additions

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - WEBHOOK_URL=${N8N_WEBHOOK_URL}
    volumes:
      - n8n_data:/home/node/.n8n
      - ~/.ssh/id_rsa:/home/node/.ssh/id_rsa:ro
    depends_on:
      - session-store
    networks:
      - secondbrain-net

  session-store:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - session_data:/data
    networks:
      - secondbrain-net

  mai-executor:
    build: ./docker/mai-executor
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - /home/mavrick/multi-ai-orchestrator:/app/mai:ro
      - mai_output:/app/output
    networks:
      - secondbrain-net
```

---

## Security Considerations

1. **Dangerous Mode**: Only in isolated mai-executor container
2. **SSH Keys**: Mounted read-only in n8n container
3. **Secrets**: All in `.env.n8n`, not in compose file
4. **Webhooks**: Signature validation (HMAC-SHA256)
5. **n8n Auth**: Basic auth required for web UI

---

## Key Commands for Claude Code via n8n SSH

```bash
# Check status
./mai status

# Run single task (auto-select provider)
./mai run "Generate MikroTik config for 10.54.4.0/24"

# Run workflow
./mai workflow customer_onboarding --customer "SFWB" --portal-url "https://..."

# Claude with session (new)
claude --dangerously-skip-permissions -p "Check UniFi AP status"

# Claude with session (resume)
claude -r abc12345 --dangerously-skip-permissions -p "Why is one down?"
```

---

## Success Criteria

- [ ] n8n accessible at port 5678 with auth
- [ ] SSH from n8n to host executes `./mai status` successfully
- [ ] MAI workflows triggerable via n8n webhook
- [ ] Multi-turn Claude sessions persist across messages
- [ ] MS Teams bot responds to `@ai` mentions
- [ ] BA Agent reports delivered on schedule
- [ ] All webhooks route through n8n master router

---

## Recommended Priority Order

1. **Phase 1: Foundation** - Deploy n8n + Redis (required base)
2. **Phase 2: MAI Integration** - Trigger existing workflows via webhooks
3. **Phase 5: BA Agent** - Scheduled reports (high business value)
4. **Phase 3: Session Management** - Multi-turn conversations
5. **Phase 4: MS Teams** - Chat interface (after core is stable)
6. **Phase 6: Webhooks** - Consolidate all sources
