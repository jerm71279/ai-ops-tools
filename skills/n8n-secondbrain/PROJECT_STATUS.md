# n8n Secondbrain Project Status

## Project Overview
Self-hosted knowledge base replacing NotebookLM with SharePoint ingestion and RAG-powered queries.

**Repository**: `jerm71279/oberaconnect-ai-ops`
**Location**: `skills/n8n-secondbrain/`
**AI Counsel Review**: December 18, 2025

---

## Status Dashboard

| Phase | Status | Progress | Target Date |
|-------|--------|----------|-------------|
| Phase 0: Security Hardening | IN PROGRESS | 80% | Dec 20, 2025 |
| Phase 1: MVP Deployment | NOT STARTED | 0% | Jan 3, 2026 |
| Phase 2: Reliability | NOT STARTED | 0% | Jan 17, 2026 |
| Phase 3: Multi-Tenant | NOT STARTED | 0% | Feb 2026 |

---

## Phase 0: Security Hardening (CURRENT)

### Completed
- [x] Added webhook authentication (headerAuth) to all workflows
- [x] Enabled Qdrant API key authentication in docker-compose.yml
- [x] Secured ports - n8n/Qdrant only on 127.0.0.1
- [x] Created .gitignore to prevent credential commits
- [x] Updated .env.example with secure defaults
- [x] Updated deploy.sh with auto-generated secrets
- [x] Added firewall rules (deny 5678, 6333 external)

### Remaining
- [ ] Set up nginx reverse proxy with SSL/TLS
- [ ] Test authentication end-to-end
- [ ] Create n8n credential for "Secondbrain API Key" (httpHeaderAuth)

### Security Checklist
```
[x] Webhooks require API key
[x] Qdrant requires API key
[x] Services bound to localhost only
[x] .env not in git
[ ] SSL/TLS configured
[ ] Tested external access blocked
```

---

## Phase 1: MVP Deployment (Next)

### Tasks
- [ ] Deploy to production Azure VM
- [ ] Configure SharePoint OAuth2 credentials in n8n
- [ ] Configure Anthropic API credentials in n8n
- [ ] Import workflows via n8n UI
- [ ] Index top 100 SharePoint documents
- [ ] Test query workflow end-to-end
- [ ] Deploy web search UI
- [ ] Train team (lunch & learn)

### Success Criteria
- [ ] Semantic search returns relevant results
- [ ] Query response time < 5 seconds
- [ ] 2+ team members using daily

---

## Phase 2: Reliability (Backlog)

### Tasks
- [ ] Add error handling to all workflow nodes
- [ ] Implement retry logic with exponential backoff
- [ ] Switch embedding model (cost optimization)
- [ ] Add centralized logging
- [ ] Set up monitoring dashboard
- [ ] Implement delta sync (only process changed files)

---

## Phase 3: Multi-Tenant (Backlog)

### Tasks
- [ ] Per-customer Qdrant collections
- [ ] API tenant scoping
- [ ] Customer permission model
- [ ] Audit logging

---

## Metrics

### Target Metrics
| Metric | Target | Current |
|--------|--------|---------|
| Monthly cost | < $200 | TBD |
| Query latency | < 5 sec | TBD |
| Documents indexed | 500+ | 0 |
| Active users | 80% team | 0% |
| Time saved/month | 20+ hrs | TBD |

### Cost Tracking
| Component | Estimated | Actual |
|-----------|-----------|--------|
| Anthropic API | $155/mo | - |
| Azure VM | $0 (existing) | - |
| **Total** | **$155/mo** | - |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Dec 18, 2025 | CONDITIONAL GO | AI Counsel: ROI justified if adopted |
| Dec 18, 2025 | Security first | Critical vulnerabilities must be fixed before any use |
| Dec 18, 2025 | Priority 2/5 | High ROI project, not blocking |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| Security breach | HIGH if unsecured | CRITICAL | Phase 0 hardening | IN PROGRESS |
| Team doesn't adopt | MEDIUM | HIGH | Mandatory training | NOT STARTED |
| API costs escalate | LOW | MEDIUM | Switch embedding model | PLANNED |
| System complexity | LOW | LOW | Clear runbooks | NOT STARTED |

---

## Files in This Skill

| File | Purpose | Status |
|------|---------|--------|
| `docker-compose.yml` | Container stack (secured) | UPDATED |
| `deploy.sh` | Deployment automation | UPDATED |
| `.env.example` | Environment template | UPDATED |
| `.gitignore` | Prevent credential commits | CREATED |
| `workflow-query.json` | RAG query (secured) | UPDATED |
| `workflow-ingestion.json` | SharePoint sync (secured) | UPDATED |
| `workflow-obsidian-sync.json` | Obsidian bidirectional | NEEDS UPDATE |
| `sb-query.sh` | CLI query tool | TO COPY |
| `SKILL.md` | Full documentation | TO COPY |
| `README.md` | Quick start | TO UPDATE |
| `PROJECT_STATUS.md` | This file | CURRENT |

---

## Next Actions

1. **Today**: Complete remaining security items
2. **This Week**: Test security end-to-end
3. **Next Week**: Begin Phase 1 deployment
4. **2 Weeks**: Team training session

---

*Last Updated: December 18, 2025*
