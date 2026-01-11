# Customer Lifecycle Process - Enhanced Version 2.0
## With High-Level Quality Assurance & Documentation Standards

**Version:** 2.0 (Enhanced)
**Date:** 2025-11-17
**Changes:** Added QA checkpoints, documentation deliverables, customer touchpoints, and quality gates

---

## 🎨 Color Legend for Visio/Draw.io Implementation

- **Blue (Sales):** #DBE8F3
- **Yellow (Marketing):** #FFF2CC
- **Pink (Engineering):** #F4CCCC
- **Green (Plant):** #D9EAD3
- **Purple (IT):** #E4D7F5
- **Lime (Billing):** #D9EAD3 (darker)
- **Gray (Operations):** #CCCCCC
- **🔴 Red Border:** Quality Gate / Critical Checkpoint
- **⭐ Star Icon:** Customer Touchpoint
- **📋 Clipboard Icon:** Documentation Deliverable

---

## PHASE 1: PROSPECTING & LEAD QUALIFICATION

### 1. Marketing Generated Lead
**Owner:** Marketing
**Type:** Start Event (oval)
**HubSpot Stage:** Marketing Generated Lead

↓

### 2. Move to Marketing Qualified Lead Bucket
**Owner:** Marketing
**Type:** Process (parallelogram)
**HubSpot Stage:** Marketing Qualified Lead

↓

### 3. HubSpot Auto-Assigns to Sales Exec by Territory
**Owner:** Marketing (automated)
**Type:** Process (parallelogram)

↓

### OR: Prospecting (Research, Lead Gathering)
**Owner:** Sales
**Type:** Process (rounded rectangle)

→ **Sales Exec inputs lead contact into HubSpot and moves to "unqualified" bucket**

↓

### 4. Sales Exec Makes Initial Contact
**Owner:** Sales
**Type:** Process (rounded rectangle)
**Actions:** Call, email, walk-in to schedule meeting

↓

### 5. Decision: Prospect Proceeds?
**Owner:** Sales
**Type:** Decision (diamond)

**If NO:**
→ Move lead into 'lost bucket' and add notes
→ Sales Exec informs prospect they will follow up on [specific date]
→ END

**If YES:** ↓

---

## PHASE 2: INITIAL MEETING & NEEDS ASSESSMENT

### 6. Move Lead to 'Meeting Scheduled' Bucket
**Owner:** Sales
**Type:** Process (parallelogram)
**HubSpot Stage:** Meeting Scheduled

↓

### 7. Initial Meeting (Info Gathering)
**Owner:** Sales
**Type:** Process (rounded rectangle)

**📋 NEW: Enhanced Data Collection**
```
Concurrent with meeting:
├─ Sales Intake Form / Tech Needs Assessment
└─ 📋 Technical Requirements Documentation Checklist
   ├─ Network topology requirements
   ├─ Current equipment inventory
   ├─ IP addressing scheme needs
   ├─ VLAN requirements
   ├─ Bandwidth requirements
   ├─ Security/compliance requirements
   ├─ 📌 Compliance Requirements Checklist
   │  ├─ Industry compliance (HIPAA, PCI-DSS, ISO27001)
   │  ├─ Security policies required
   │  ├─ Data retention requirements
   │  └─ Access control standards
   └─ Single points of failure identification
```

↓

### 8. Move into Sales Qualified Lead Bucket
**Owner:** Sales
**Type:** Process (parallelogram)
**HubSpot Stage:** Sales Qualified Lead

↓

### 9. Subscriber Created in OneBill (Automatic Workflow)
**Owner:** System (automated)
**Type:** Process (parallelogram)

↓

---

## PHASE 3: SITE SURVEY & SOW DEVELOPMENT

### 10. Sales Exec Creates Ticket in OneBill for Site Survey
**Owner:** Sales
**Type:** Process (rectangle)
**Action:** Assigns to Plant

↓

### 11. Plant Reviews Notes and Schedules Site Survey
**Owner:** Plant
**Type:** Process (rectangle)

**📋 NEW: Site Survey Standards**
```
If Wireless Installation:
└─ 📋 Wireless Site Survey Standards Checklist
   ├─ Use UniFi WiFiman app for RF survey
   ├─ Minimum signal strength: -67dBm target
   ├─ AP placement map created
   ├─ Channel plan documented (2.4GHz: 1,6,11 / 5GHz width)
   ├─ Interference sources identified
   └─ Coverage overlap for roaming confirmed
```

↓

### 12. Move to 'Site Survey Scheduled' Bucket
**Owner:** Plant
**Type:** Process (parallelogram)
**HubSpot Stage:** Site Survey Scheduled

↓

### 13. Plant Team Conducts Site Survey (Short-form or On-site)
**Owner:** Plant
**Type:** Process (rectangle)

↓

### 14. Plant Team Creates SOW
**Owner:** Plant
**Type:** Process (rectangle)
**Action:** Attaches to OneBill ticket with Engineering as watcher

**📋 NEW: Enhanced SOW Development**
```
└─ Add to SOW:
   ├─ 📋 Technology Selection Matrix
   │  ├─ Firewall/Router recommendation with justification
   │  │  • SonicWall (TZ/NSa/NSsp series)
   │  │  • MikroTik (hEX S/CCR series)
   │  │  • UniFi Gateway (UDM/UDM-Pro/UXG)
   │  ├─ Switch selection and port count
   │  ├─ Access point models and quantity
   │  ├─ Throughput requirements validated
   │  ├─ Licensing requirements identified
   │  └─ Future scalability considered
   │
   └─ Deliverable: Technology Selection Summary (1-page document)
```

↓

### 🔴 QUALITY GATE: Design Review Loop

**15. Engineering Reviews SOW and Determines Components**
**Owner:** Engineering
**Type:** Process (rectangle)

**📋 NEW: Engineering Design Standards**
```
└─ Engineering validates:
   ├─ 📋 Standard VLAN Design Template
   │  ├─ Management VLAN: VLAN 10 (10.x.10.0/24)
   │  ├─ User/Data VLANs: VLAN 20+ (department-based)
   │  ├─ Voice VLAN: VLAN 30 (10.x.30.0/24) - if VoIP
   │  ├─ Guest VLAN: VLAN 40 (10.x.40.0/24) - isolated
   │  ├─ IoT/Security VLAN: VLAN 50 (10.x.50.0/24)
   │  └─ Inter-VLAN firewall rules defined
   │
   ├─ 📋 Security Policy Design Checklist
   │  ├─ Firewall zone-based rules documented
   │  ├─ Guest network isolation configured
   │  ├─ Content filtering requirements specified
   │  ├─ VPN access requirements defined
   │  └─ Application control rules documented
   │
   └─ Deliverable: IP Addressing & VLAN Scheme Spreadsheet
```

↓

### 16. Engineering Updates SOW with Requirements & Project Plan
**Owner:** Engineering
**Type:** Process (rectangle)
**HubSpot Stage:** Design In Progress (NEW)

↓

### 17. IT Reviews SOW and Updates with IT Requirements
**Owner:** IT Services
**Type:** Process (rectangle)

↓

### 18. IT Develops Project Plan to Accompany Quote
**Owner:** IT Services
**Type:** Process (rectangle)

↓

### **📋 NEW: 19. Move to Design Review Scheduled**
**Owner:** Sales
**Type:** Process (parallelogram)
**HubSpot Stage:** Design Review Scheduled (NEW)

↓

### ⭐ **NEW: 20. Customer Design Review Meeting**
**Owner:** Sales + Engineering Lead
**Type:** Customer Touchpoint (star shape)

```
Review with Customer:
├─ Present proposed topology diagram
├─ Review VLAN design and IP scheme
├─ Explain security policies
├─ Walk through wireless coverage map (if applicable)
├─ Review project timeline and milestones
└─ Answer questions and gather feedback
```

↓

### 🔴 **NEW: QUALITY GATE 1: Design Approval**
**Approval Required:** Sales Manager + Customer
**Criteria:** Customer understands and approves design

↓

### ⭐ **NEW: 21. Customer Design Sign-Off Obtained**
**Owner:** Sales
**Type:** Documentation (document icon)
**📋 Deliverable:** Design Approval Document (signed by customer)

↓

---

## PHASE 4: PROPOSAL & CONTRACT

### 22. Sales Exec Creates Quote in OneBill
**Owner:** Sales
**Type:** Process (rectangle)

↓

### 23. Move Lead into 'Present Proposal' Bucket
**Owner:** Sales
**Type:** Process (parallelogram)
**HubSpot Stage:** Present Proposal

↓

### 24. Present Proposal to Customer
**Owner:** Sales
**Type:** Process (rounded rectangle)

↓

### 25. Decision: Customer Elects to Move Forward with Contract?
**Owner:** Customer
**Type:** Decision (diamond)

**If NO:**
→ Move to 'lost bucket' and add notes
→ END

**If YES:** ↓

↓

### 26. Move into 'Won' Bucket
**Owner:** Sales
**Type:** Process (parallelogram)
**HubSpot Stage:** Won

↓

### 27. Sales Exec Prepares Final Quote for Signature
**Owner:** Sales
**Type:** Process (rectangle)

↓

### 28. Sales Exec Preps Contract and Sends to Customer via DocuSign
**Owner:** Sales
**Type:** Process (rectangle)

↓

### 29. Client Signs via DocuSign
**Owner:** Customer
**Type:** Process (rounded rectangle)

↓

### 30. Signed Contract Received
**Owner:** Sales
**Type:** Event (document icon)

↓

### 31. Initial Sales Process Complete
**Owner:** Sales
**Type:** Milestone (rounded rectangle)

↓

---

## PHASE 5: EQUIPMENT PROCUREMENT & BILLING

### 32. Sales Exec Reassigns Ticket to Billing Manager (NRC)
**Owner:** Sales
**Type:** Process (rectangle)

↓

### 33. Billing Manager Reviews Ticket and Issues Invoice for NRC
**Owner:** Billing
**Type:** Process (rectangle)
**HubSpot Stage:** Equipment Ordered (NEW)

↓

### 34. Billing Manager Reassigns Ticket to VP, Plant for Purchasing
**Owner:** Billing
**Type:** Process (rectangle)

↓

### 35. VP, Plant Purchases Equipment
**Owner:** VP Plant
**Type:** Process (rectangle)

↓

### 36. Equipment is Delivered
**Owner:** VP Plant / OPM
**Type:** Event (rectangle)

↓

### 37. OPM Adds Inventory in SmartSheets
**Owner:** OPM (Plant Operations)
**Type:** Process (rectangle)
**Status:** 'Assigned/Pending Customer Install'

↓

### 38. Billing Manager Validates Receipts Included for Purchases
**Owner:** Billing
**Type:** Process (rectangle)

↓

### 39. Billing Manager Categorizes Transaction in QBO
**Owner:** Billing
**Type:** Process (rectangle)

↓

---

## PHASE 6: PRE-CONFIGURATION & PREPARATION

### 40. Communicate with Carrier (ECD, FOC, IP Information)
**Owner:** OPM
**Type:** Process (rectangle)
**Actions:**
- Obtain Estimated Completion Date (ECD)
- Obtain Firm Order Commitment (FOC)
- Receive IP Information

↓

### 41. Update 'Circuit Inventory' SmartSheet
**Owner:** OPM
**Type:** Process (rectangle)

↓

### 42. OPM Assigns Ticket to Engineering for Provisioning/Configuration
**Owner:** OPM
**Type:** Process (rectangle)
**HubSpot Stage:** Pre-Configuration In Progress (NEW)

↓

### 43. Engineering Completes Configuration
**Owner:** Engineering
**Type:** Process (rectangle)

**📋 NEW: Lab Testing & Pre-Configuration Validation**
```
└─ 📋 Lab Testing Completed Checklist
   ├─ Configuration uploaded to all devices
   ├─ Internet connectivity tested
   ├─ VLAN routing verified
   ├─ Wireless SSIDs tested
   ├─ Security rules validated
   ├─ VPN connectivity tested (if applicable)
   ├─ Performance baseline documented
   │
   ├─ 📋 Configuration Backup Created
   │  ├─ Firewall/router config backed up
   │  ├─ Switch configs backed up
   │  ├─ Wireless controller config backed up
   │  └─ All configs stored in password vault/SharePoint
   │
   └─ Deliverable: Pre-Config Test Report (passed/failed checklist)
```

↓

### 🔴 **NEW: QUALITY GATE 2: Pre-Configuration Validation**
**Approval Required:** Engineering Lead
**Criteria:** Lab testing passed, equipment ready

↓

### 44. Engineering Reassigns Ticket to OPM
**Owner:** Engineering
**Type:** Process (rectangle)

↓

### 45. VP, Plant Reassigns Ticket to OPM to Schedule Install
**Owner:** VP Plant
**Type:** Process (rectangle)

↓

### 46. OPM Schedules Date/Time for Install with Customer
**Owner:** OPM
**Type:** Process (rectangle)

**📋 NEW: Installation Readiness Checklist**
```
└─ 📋 Installation Readiness Confirmed
   ├─ All equipment delivered and inventoried
   ├─ Equipment pre-configured and tested
   ├─ Tools and materials checklist completed
   ├─ Team members confirmed and available
   ├─ Customer contact reconfirmed
   ├─ Site access/parking arrangements confirmed
   └─ Backup/rollback plan documented
```

↓

### 47. Update Outlook with Calendar Block on Support Calendar
**Owner:** OPM
**Type:** Process (rectangle)
**Action:** Add resources as attendees

↓

### 48. Update OneBill Ticket with Install Date
**Owner:** OPM
**Type:** Process (rectangle)
**HubSpot Stage:** Installation Scheduled (NEW)

↓

### ⭐ **NEW: 49. Customer Pre-Install Briefing**
**Owner:** OPM
**Type:** Customer Touchpoint (star shape)

```
Communicate with Customer:
├─ Installation timeline confirmed
├─ Downtime window confirmed (if any)
├─ User notification sent
├─ On-site contact designated
└─ Post-install expectations set
```

↓

### 50. Day Before Install: Review Project Checklist
**Owner:** OPM
**Type:** Process (rectangle)
**Action:** Confirm all equipment and materials are loaded and ready

↓

### 51. OPM Reassigns Ticket to Director of Operations to Communicate with Watchers
**Owner:** OPM
**Type:** Process (rectangle)
**Note:** *Add hours/notes to ticket*

↓

---

## PHASE 7: INSTALLATION DAY

### 52. On-Site Installation
**Owner:** Plant Team
**Type:** Process (rectangle)
**HubSpot Stage:** Installation In Progress (NEW)

↓

### 53. Move Inventory to 'Installed' in SmartSheets
**Owner:** Plant Tech
**Type:** Process (rectangle)

↓

### 54. Upload Close-Out Pictures and Cable Certifications to SharePoint
**Owner:** Plant Tech
**Type:** Process (rectangle)
**Location:** Customer folder in SharePoint

↓

### 🔴 **NEW: 55. Installation QA Checklist Completed**
**Owner:** Plant Tech / Lead Technician
**Type:** Quality Gate (red border rectangle)

**📋 Installation Quality Assurance Checklist**
```
Network Connectivity:
├─ ✓ Internet connectivity verified from all VLANs
├─ ✓ DNS resolution tested
└─ ✓ DHCP functioning on all VLANs

Wireless Validation (if applicable):
├─ ✓ All APs online and broadcasting
├─ ✓ Signal strength ≥ -67dBm in all coverage areas
├─ ✓ Roaming between APs tested
└─ ✓ Guest portal functionality verified

Security Validation:
├─ ✓ Firewall rules tested (allow/deny)
├─ ✓ Guest network isolation confirmed
└─ ✓ VPN connectivity tested (if configured)

Performance Testing:
├─ ✓ Speed tests from multiple locations
├─ ✓ Baseline performance documented
└─ ✓ Critical applications tested

Documentation:
├─ ✓ As-built diagram updated (if changes)
├─ ✓ Photos uploaded to SharePoint
├─ ✓ Cable certifications uploaded
└─ ✓ Device labels applied with IPs

Deliverable: Installation QA Report (signed by lead technician)
```

↓

### 🔴 **QUALITY GATE 3: Installation Validation**
**Approval Required:** Lead Technician + OPM
**Criteria:** QA checklist 100% passed

↓

### 56. Validate All Work is Complete Against Contract and Project Plan
**Owner:** Plant Tech
**Type:** Process (rectangle)
**HubSpot Stage:** Installation Complete - Pending QA (NEW)

↓

### ⭐ **NEW: 57. Customer Installation Walkthrough**
**Owner:** Plant Tech / OPM
**Type:** Customer Touchpoint (star shape)

```
Walkthrough with Customer:
├─ Demonstrate network functionality
├─ Show WiFi coverage and speeds
├─ Review security features
├─ Explain user access methods
├─ Provide admin credentials (via secure method)
└─ Answer customer questions
```

↓

### 🔴 **NEW: QUALITY GATE 4: Customer Handoff**
**Approval Required:** Customer
**Criteria:** Customer satisfied, sign-off obtained

↓

### ⭐ **NEW: 58. Customer Installation Sign-Off Obtained**
**Owner:** OPM / Plant Tech
**Type:** Documentation (document icon)

```
Customer acknowledges:
├─ Installation complete
├─ Any punch-list items documented
└─ Signature captured (DocuSign or paper)

📋 Deliverable: Installation Completion Certificate (signed by customer)
```

↓

### 59. Plant Tech Reassigns Ticket to OPM for Closeout
**Owner:** Plant Tech
**Type:** Process (rectangle)

↓

---

## PHASE 8: POST-INSTALLATION & HANDOFF

### **NEW: 60. Customer Documentation Package Delivered**
**Owner:** OPM / Engineering
**Type:** Documentation (document icon)

**📋 Customer Documentation Package**
```
Technical Documentation:
├─ As-built network diagram
├─ IP address spreadsheet
├─ VLAN documentation
├─ WiFi network details (SSIDs, passwords)
├─ Equipment list with serial numbers
└─ Warranty/license expiration dates

Configuration Backups:
├─ Firewall/router configuration export
├─ Switch configuration backups
└─ Wireless controller backup

Support Information:
├─ Admin credentials (in password vault)
├─ Support contact information
├─ Escalation procedures
└─ Monitoring/alerting setup confirmation

✓ All documentation uploaded to customer SharePoint folder
✓ Customer notified of documentation availability
```

↓

### **NEW: 61. Monitoring & Alerting Configured**
**Owner:** Engineering / IT Services
**Type:** Process (rectangle)

**📋 Monitoring & Alerting Setup**
```
├─ All devices added to NinjaOne RMM
├─ SNMP monitoring enabled
├─ Email alerts configured
├─ Syslog forwarding setup (if applicable)
├─ Device health checks scheduled
├─ Alert recipients confirmed
└─ Test alerts sent and received
```

↓

### 62. Client Moved into Marketing Pipeline in HubSpot
**Owner:** Marketing
**Type:** Process (parallelogram)
**HubSpot Stage:** Customer Handoff Complete (NEW)

↓

### 63. Onboarding + CSAT Survey Sent
**Owner:** Marketing
**Type:** Process (rectangle)

↓

### 64. CSAT Data Logged to Customer Profile in HubSpot
**Owner:** Marketing
**Type:** Process (rectangle)

↓

### 65. OPM Assigns Ticket to Billing Manager for MRC
**Owner:** OPM
**Type:** Process (rectangle)

↓

### 66. Billing Manager Reviews Ticket and Establishes Invoice for MRC
**Owner:** Billing
**Type:** Process (rectangle)

↓

### 67. Project Complete - Customer Onboarded
**Owner:** Operations
**Type:** End Event (rounded rectangle)

↓

---

## PHASE 9: ONGOING SUPPORT & MAINTENANCE

### ⭐ **NEW: 68. 30-Day Follow-Up Review**
**Owner:** OPM / Sales
**Type:** Customer Touchpoint (star shape)
**Schedule:** 30 days after installation complete

```
30-Day Review:
├─ Review any outstanding issues
├─ Check network performance
├─ Gather additional feedback
├─ Make any necessary adjustments
└─ Document lessons learned
```

↓

### **NEW: 69. Quarterly Network Health Check**
**Owner:** Engineering / Operations
**Type:** Recurring Process (rectangle with cycle icon)
**Schedule:** Every 90 days

```
Quarterly Health Check:
├─ Review monitoring alerts and logs
├─ Check firmware versions
├─ Verify backup configurations exist
├─ Review bandwidth utilization trends
├─ Test failover mechanisms
└─ Update documentation as needed
```

↓

### ⭐ **NEW: 70. Annual Customer Review**
**Owner:** Sales / Operations
**Type:** Customer Touchpoint (star shape)
**Schedule:** Annually

```
Annual Review:
├─ Present performance report
├─ Review incidents and resolutions
├─ Discuss improvement opportunities
├─ Plan for capacity/growth
└─ Recommend upgrades if needed
```

---

## 📊 NEW: HubSpot Stage Additions

### Current Stages (Keep These):
1. Marketing Generated Lead
2. Marketing Qualified Lead
3. Sales Qualified Lead
4. Meeting Scheduled
5. Site Survey Scheduled
6. Present Proposal
7. Won
8. Lost

### **NEW Stages to Add:**
9. **Design In Progress** (added after Site Survey)
10. **Design Review Scheduled** (added before Present Proposal)
11. **Equipment Ordered** (added after Won)
12. **Pre-Configuration In Progress** (during config)
13. **Installation Scheduled** (before install)
14. **Installation In Progress** (during install)
15. **Installation Complete - Pending QA** (after install, before handoff)
16. **Customer Handoff Complete** (after QA passed)
17. **Marketing Pipeline** (existing - for ongoing customers)

---

## 🚦 Quality Gates Summary

| Gate # | Name | Approval Required | Location | Criteria |
|--------|------|-------------------|----------|----------|
| **Gate 1** | Design Approval | Sales Manager + Customer | After Design Review | Customer approves design, SOW technically sound |
| **Gate 2** | Pre-Config Validation | Engineering Lead | After Lab Testing | All equipment tested, configs validated |
| **Gate 3** | Installation Validation | Lead Tech + OPM | After Install QA | 100% QA checklist passed |
| **Gate 4** | Customer Handoff | Customer | After Walkthrough | Customer satisfied, sign-off obtained |

---

## ⭐ Customer Touchpoints Summary

| # | Touchpoint | Owner | When | Purpose |
|---|------------|-------|------|---------|
| 1 | Customer Design Review Meeting | Sales + Engineering | Phase 3 (SOW) | Present design, obtain approval |
| 2 | Customer Pre-Install Briefing | OPM | Phase 6 (Pre-Config) | Set expectations, confirm timeline |
| 3 | Customer Installation Walkthrough | Plant Tech / OPM | Phase 7 (Install Day) | Demonstrate system, train |
| 4 | Customer Installation Sign-Off | OPM / Plant Tech | Phase 7 (Install Day) | Formal handoff, obtain signature |
| 5 | 30-Day Follow-Up Review | OPM / Sales | 30 days post-install | Address issues, gather feedback |
| 6 | Annual Customer Review | Sales / Operations | Annually | Performance review, upsell opportunities |

---

## 📋 Documentation Deliverables Summary

| Phase | Document | Owner | Format | Storage Location |
|-------|----------|-------|--------|------------------|
| 2 | Technical Requirements Checklist | Sales | Form/Checklist | OneBill Ticket |
| 2 | Compliance Requirements Checklist | Sales | Form/Checklist | OneBill Ticket |
| 3 | Wireless Site Survey Report | Plant | PDF/Photos | SharePoint Customer Folder |
| 3 | Technology Selection Summary | Plant/Engineering | 1-page Doc | Attached to SOW |
| 3 | IP Addressing & VLAN Scheme | Engineering | Excel Spreadsheet | SharePoint Customer Folder |
| 3 | Design Approval Document | Sales | PDF (signed) | SharePoint + OneBill |
| 6 | Pre-Config Test Report | Engineering | Checklist/Form | OneBill Ticket |
| 7 | Installation QA Report | Plant Tech | Checklist/Form | OneBill Ticket |
| 7 | Close-out Photos | Plant Tech | Photos | SharePoint Customer Folder |
| 7 | Cable Certifications | Plant Tech | PDF Reports | SharePoint Customer Folder |
| 7 | Installation Completion Certificate | OPM | PDF (signed) | SharePoint + OneBill |
| 8 | As-Built Network Diagram | Engineering | Visio/Draw.io | SharePoint Customer Folder |
| 8 | Configuration Backups | Engineering | Config Files | Password Vault + SharePoint |
| 8 | Customer Documentation Package | OPM/Engineering | Folder with all docs | SharePoint Customer Folder |

---

## 🔄 Master Install Ticket Structure (OneBill)

```
📋 Master Ticket: [Customer Name] - Network Installation
   │
   ├── 🏗️ Child Ticket 1: Plant - Site Survey & Physical Install
   │   ├─ Status: In Progress
   │   ├─ Dependencies: None
   │   ├─ Deliverables: Site survey report, equipment installed
   │   └─ Duration: 1-2 weeks
   │
   ├── ⚙️ Child Ticket 2: Engineering - Configuration & Provisioning
   │   ├─ Status: Waiting
   │   ├─ Dependencies: Equipment delivery
   │   ├─ Deliverables: Configs completed, lab tested, backups stored
   │   └─ Duration: 2-3 weeks
   │
   ├── 💻 Child Ticket 3: IT Services - Server/Application Integration
   │   ├─ Status: Waiting
   │   ├─ Dependencies: Engineering config complete
   │   ├─ Deliverables: Server configs, integrations tested
   │   └─ Duration: 1 week
   │
   ├── 💰 Child Ticket 4: Billing - NRC Invoice
   │   ├─ Status: In Progress
   │   ├─ Dependencies: Contract signed
   │   ├─ Deliverables: NRC invoiced, payment received
   │   └─ Duration: 1 week
   │
   ├── 📦 Child Ticket 5: Billing - Equipment Procurement
   │   ├─ Status: Waiting
   │   ├─ Dependencies: NRC payment
   │   ├─ Deliverables: Equipment ordered, received, inventoried
   │   └─ Duration: 2-4 weeks (vendor dependent)
   │
   └── 📊 Child Ticket 6: Billing - MRC Setup
       ├─ Status: Waiting
       ├─ Dependencies: Installation complete
       ├─ Deliverables: MRC billing established
       └─ Duration: 1 day
```

---

## ⏱️ Phase Duration Estimates

| Phase | Duration | Effort (Hours) | Bottlenecks |
|-------|----------|----------------|-------------|
| Phase 1: Prospecting | Variable | 2-4 | Lead response time |
| Phase 2: Initial Meeting | 1-2 weeks | 8-16 | Meeting scheduling |
| Phase 3: Site Survey & SOW | 1-2 weeks | 12-24 | Multi-team coordination |
| Phase 4: Proposal & Contract | 1-3 weeks | 8-16 | Customer decision time |
| Phase 5: Equipment Procurement | 2-4 weeks | 4-8 | Vendor lead times |
| Phase 6: Pre-Configuration | 1-2 weeks | 16-32 | Lab testing thoroughness |
| Phase 7: Installation | 1-3 days | 16-40 | On-site complexity |
| Phase 8: Post-Install & Handoff | 1 week | 4-8 | Documentation completion |

**Total Project Timeline:** 8-16 weeks (from initial meeting to go-live)

---

## 📈 Key Performance Indicators (KPIs)

### Quality Metrics:
- **Installation QA Pass Rate:** Target 100% first-time pass
- **Customer Sign-Off Rate:** Target 100% without disputes
- **Rework Rate:** Target <5% of installations require rework

### Customer Satisfaction:
- **CSAT Score:** Target ≥4.5/5.0
- **30-Day Follow-Up Issues:** Target <2 issues per installation
- **Annual Review Attendance:** Target 80% customer participation

### Operational Efficiency:
- **Lab Testing Pass Rate:** Target ≥95%
- **Documentation Completion Rate:** Target 100% within 7 days of install
- **Project Timeline Adherence:** Target ±10% of estimated duration

---

## 🎯 Next Steps for Implementation

1. **Update Visio/Draw.io Diagram:**
   - Add new process boxes for QA checkpoints
   - Add star icons for customer touchpoints
   - Add document icons for deliverables
   - Add red borders for quality gates
   - Update with new HubSpot stages

2. **Create OneBill Workflows:**
   - Implement Master Install Ticket structure
   - Set up child ticket dependencies
   - Create automated notifications at quality gates

3. **Develop Templates:**
   - Technical Requirements Checklist template
   - Lab Testing Report template
   - Installation QA Checklist template
   - Customer Documentation Package template

4. **Train Teams:**
   - Sales: Customer touchpoints and design approvals
   - Engineering: Lab testing standards and VLAN templates
   - Plant: Installation QA procedures
   - Billing: Updated ticket workflow

5. **Update HubSpot:**
   - Add new pipeline stages
   - Create automated workflows for stage transitions
   - Set up reporting dashboards

---

**Version:** 2.0 Enhanced
**Last Updated:** 2025-11-17
**Maintained By:** Operations Team
**Next Review:** 2025-12-17 (30 days after implementation)
