# Network Engineer & AI Operations Portfolio

**Jeremy Smith | Seeking Engineering Leadership Opportunities**

*Building systems that streamline business processes and solve operational problems at scale.*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/jszerotrustops)
[![CISSP](https://img.shields.io/badge/CISSP-Certified-darkgreen)]()
[![Security+](https://img.shields.io/badge/Security%2B-Certified-green)]()
[![Azure](https://img.shields.io/badge/AZ--900-Certified-blue)]()

---

## Who I Am

Network Engineer with **10+ years of IT experience** and **5 years in prior leadership roles**, most recently serving as the sole infrastructure engineer for a 40-employee MSP. I managed **98 customer sites across 14 states** (492 network devices) with full sign-off authority across all departments.

**This repository contains the production tools I built** to transform that operation from reactive ticket-chasing into proactive, AI-augmented infrastructure management.

When the company restructured and eliminated all engineering positions, I kept building. The work here represents how I think about problems: **automate the repeatable, validate everything, document obsessively.**

---

## What This Repository Proves

### I Build Solutions, Not Just Configurations

| Challenge I Faced | Solution I Built | Result |
|-------------------|------------------|--------|
| 98 dashboards to check fleet health | Natural language query engine | 4 hrs → 15 min weekly |
| Manual site migrations | Automated MikroTik → UniFi translator | 3 hrs → 45 min per site |
| Tribal knowledge operations | Template-driven configs with validation | Zero config drift |
| "Trust me" security posture | Automated compliance mapping | Audit-ready documentation |
| Inconsistent AI outputs | 5-Layer AI Operating System | Reproducible workflows |

---

## Technical Showcase

### 1. Fleet Management at Scale

Managing 492 devices across 98 sites without clicking through individual dashboards:

```bash
# Natural language queries against the entire fleet
python unifi_fleet.py --query "which sites have APs below -65dBm signal?"
python unifi_fleet.py --query "show devices with firmware older than 7.1.0"
python unifi_fleet.py --query "list offline devices by customer"
```

**Built with:** Python, SQLite, UniFi Site Manager API, Claude API for NL parsing

---

### 2. Infrastructure Migration Automation

Migrating 98 sites from mixed MikroTik/SonicWall to standardized Ubiquiti:

```
MikroTik RSC Export → Parser → Security Validation → UniFi JSON → Deployment
```

**What it handles automatically:**
- VLANs, IP addressing, DHCP pools
- Firewall rules and port forwards  
- Wireless networks with security profiles
- Static routes and NAT rules

**What it flags for human review:**
- QoS policies (model differences)
- Complex queue trees
- Custom scripts

---

### 3. Security-First Automation

Every automated operation validates against security standards before execution:

```python
# Maker/Checker validation framework enforces:
✗ No open SSIDs (password required)
✗ VLANs 1 and 4095 reserved (security best practice)
✗ No permit-any firewall rules (zero trust)
✗ Bulk operations (>10 sites) require confirmation
✗ HIGH/CRITICAL changes require rollback plans
```

**Result:** Zero security incidents from automated deployments.

---

### 4. AI Operations Framework

Built a structured approach to AI-assisted operations:

| Layer | What It Does |
|-------|--------------|
| **Identity** | Consistent context across all AI interactions |
| **Execution** | 15 standardized patterns for common tasks |
| **Validation** | Output verification before any action |
| **Orchestration** | Route to optimal model (Claude for code, Grok for research) |
| **Memory** | Persistent context across sessions |

**Why it matters:** Junior techs execute with senior-level consistency. AI augments expertise rather than replacing judgment.

---

### 5. Compliance & Risk Assessment

Automated security assessment mapped to industry frameworks:

```
Infrastructure Audit → ISO 27001 / NIST Mapping → Gap Analysis → Action Plan
```

**Coverage:** UniFi, NinjaOne, Microsoft 365, SonicWall, MikroTik, Axcient

**Output:** Cyber insurance questionnaires completed in hours instead of days, with supporting evidence.

---

## Repository Structure

```
oberaconnect-ai-ops/
├── core/
│   ├── validation_framework/     # Maker/Checker security patterns
│   ├── Secondbrain/              # AI Operating System
│   └── multi-ai-orchestrator/    # Multi-model routing
├── skills/
│   ├── unifi-fleet/              # Fleet management + NL queries
│   ├── ninjaone/                 # RMM integration
│   └── network-troubleshooter/   # Diagnostic automation
├── tools/
│   ├── mikrotik-to-unifi/        # Migration tooling
│   └── content-automator/        # AI content pipeline
└── templates/
    ├── mikrotik/                 # RouterOS configurations
    ├── unifi/                    # UniFi JSON templates
    └── sonicwall/                # Firewall templates
```

---

## Potential Impact

| Metric | Tool Capability |
|--------|-----------------|
| **Fleet Health Checks** | Reduce from hours to minutes with NL queries |
| **Site Migrations** | Automate config translation, cut manual work by 75%+ |
| **Config Drift** | Eliminate with template-driven validation |
| **Compliance Documentation** | Generate audit-ready reports in hours, not days |
| **Tribal Knowledge** | Capture in searchable, executable documentation |

*These tools were built to solve real operational challenges at scale (98 sites, 492 devices). Results will vary based on environment and implementation.*

---

## Technical Stack

**Infrastructure:** Ubiquiti UniFi, MikroTik RouterOS, SonicWall, Azure  
**Languages:** Python, Bash, PowerShell  
**Integrations:** NinjaOne, UniFi Site Manager, Microsoft 365/Entra ID, CIPP  
**AI/Automation:** Claude API, OpenAI API, multi-model orchestration  
**Security:** SIEM patterns (Graylog/Wazuh), ISO 27001, NIST 800-53  

---

## Certifications

| Certification | Status |
|---------------|--------|
| **CISSP** | ✅ Active |
| **CompTIA Security+** | ✅ Active |
| **CompTIA Network+** | ✅ Active |
| **CompTIA A+** | ✅ Active |
| **Azure Fundamentals (AZ-900)** | ✅ Active |
| **CCNA** | 📅 Q2 2026 |

---

## What I'm Looking For

**Roles:** Team Lead, L3 Support Lead, Engineering Team Lead, Security Operations Lead, IT Manager

**What I bring:**
- Proven ability to manage infrastructure at scale (98 sites, 492 devices)
- Security-first mindset backed by CISSP and hands-on implementation
- Track record of building systems that streamline business processes
- AI integration experience that solves business problems, not just technical ones
- 10 years in IT with 5 years in prior leadership roles

**What I do:**
- Identify operational inefficiencies and build systems to eliminate them
- Translate business problems into automated, repeatable solutions
- Create documentation and processes that enable teams to scale
- Lead technical escalations and complex problem resolution

**Environment I thrive in:**
- Organizations ready to transform operations, not just maintain them
- Leadership that sees technology as a business enabler
- Teams solving meaningful problems with measurable impact

**Compensation:** $130k+ | **Location:** Remote, or within 50miles local onsite.

---

## Let's Connect

This repository isn't a demo project—it's production code that solved real business problems. I'm looking for a leadership role where I can bring this same approach: identify inefficiencies, build systems that scale, and align technology strategy with business outcomes.

📧 **Email:** Jerm712@icloud.com  
💼 **LinkedIn:** [linkedin.com/in/jszerotrustops](https://linkedin.com/in/jszerotrustops)  
📍 **Location:** Spanish Fort, AL

---

*I believe technology strategy should solve business problems—not create new ones. Let me show you what that looks like in practice.*
