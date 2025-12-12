# OberaConnect Platform Feature Index

**Last Updated:** October 10, 2025  
**Platform Version:** 2.1  
**Total Pages:** 70+  
**Total Edge Functions:** 17

---

## Table of Contents

1. [Public Pages](#public-pages)
2. [Portal & Dashboards](#portal--dashboards)
3. [Admin Pages](#admin-pages)
4. [Compliance & Audit](#compliance--audit)
5. [Workflow & Automation](#workflow--automation)
6. [CMDB & Change Management](#cmdb--change-management)
7. [AI & Knowledge](#ai--knowledge)
8. [Integration Pages](#integration-pages)
9. [Testing & Validation](#testing--validation)
10. [Feature Status Matrix](#feature-status-matrix)

---

## Public Pages

### Landing & Authentication
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/` | Index | Marketing landing page with hero, features, pricing | ✅ Active |
| `/auth` | Auth | Login/Signup with email + OAuth (Google) | ✅ Active |
| `/integrations` | IntegrationsPage | Integration marketplace showcase | ✅ Active |
| `/404` | NotFound | Custom 404 error page | ✅ Active |

---

## Portal & Dashboards

### Main Portal
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/portal` | Portal | Employee portal with app launcher & toolbar | ✅ Active |
| `/demo` | DemoSelector | Demo mode department selector | ✅ Active |

### Department Dashboards
| Route | Page | Department | Key Features | Status |
|-------|------|------------|--------------|--------|
| `/admin` | AdminDashboard | Admin | Customer mgmt, MCP tools, testing access | ✅ Active |
| `/executive` | ExecutiveDashboard | Executive | KPIs, revenue, workflow insights, alerts | ✅ Active |
| `/it` | ITDashboard | IT | Devices, alerts, M365 integration, tickets | ✅ Active |
| `/hr` | HRDashboard | HR | Onboarding, employees, compliance training | ✅ Active |
| `/sales` | SalesDashboard | Sales | Pipeline, revenue, Revio integration | ✅ Active |
| `/finance` | FinanceDashboard | Finance | Revenue, invoices, budget tracking | ✅ Active |
| `/operations` | OperationsDashboard | Operations | Workflows, incidents, service requests | ✅ Active |
| `/soc` | SOCDashboard | Security | Alerts, threats, compliance, anomalies | ✅ Active |

### Specialized Portals
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/sales-portal` | SalesPortal | Enhanced sales portal with leads & opportunities | ✅ Active |
| `/client-portal` | ClientPortal | External client self-service portal | ✅ Active |
| `/compliance-portal` | CompliancePortal | Compliance dashboard overview | ✅ Active |
| `/analytics-portal` | AnalyticsPortal | Cross-platform analytics & insights | ✅ Active |
| `/dataflow-portal` | DataFlowPortal | Visual data flow documentation | ✅ Active |
| `/rbac-portal` | RBACPortal | Role-based access control management | ✅ Active |

---

## Admin Pages

### System Administration
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/admin/applications` | ApplicationsAdmin | Manage employee portal apps | ✅ Active |
| `/admin/customers` | CustomerAdmin | Customer management & settings | ✅ Active |
| `/admin/products` | ProductsAdmin | Product catalog & pricing management | ✅ New (Oct 9) |
| `/mcp-server` | MCPServerDashboard | MCP server management & monitoring | ✅ Active |

---

## Compliance & Audit

### Compliance Management
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/compliance/dashboard` | ComplianceDashboard | Compliance overview & controls | ✅ Active |
| `/compliance/frameworks/:id` | ComplianceFrameworkDetail | Framework detail view | ✅ Active |
| `/compliance/frameworks/:id/records` | ComplianceFrameworkRecords | Framework compliance records | ✅ Active |
| `/compliance/controls/:id` | ComplianceControlDetail | Control implementation details | ✅ Active |
| `/compliance/evidence/upload` | ComplianceEvidenceUpload | Upload compliance evidence | ✅ Active |
| `/compliance/reports` | ComplianceAuditReports | Audit report generation | ✅ Active |
| `/compliance/reports/:id` | ComplianceReportDetail | Detailed audit report view | ✅ Active |

### Audit & Access
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/privileged-access-audit` | PrivilegedAccessAudit | RMM privileged access audit logs | ✅ Active |

---

## Workflow & Automation

### Workflow Management
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/workflows` | WorkflowAutomation | Workflow list & management | ✅ Active |
| `/workflows/builder` | WorkflowBuilder | Legacy workflow builder | ⚠️ Legacy |
| `/workflows/visual-builder` | VisualWorkflowBuilder | Visual drag-drop workflow builder | ✅ Active |
| `/workflows/orchestration` | WorkflowOrchestration | Workflow orchestration control | ✅ Active |
| `/workflows/:id` | WorkflowDetail | Workflow configuration detail | ✅ Active |
| `/workflows/:id/executions/:execId` | WorkflowExecutionDetail | Execution logs & debugging | ✅ Active |

### Testing & Evidence
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/workflows/test-evidence` | TestWorkflowEvidence | Evidence generation testing | ✅ Active |

---

## CMDB & Change Management

### Configuration Management
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/cmdb` | CMDBDashboard | CMDB overview & CI listing | ✅ Active |
| `/cmdb/add` | CMDBAddItem | Add new configuration item | ✅ Active |
| `/cmdb/edit/:id` | CMDBEditItem | Edit configuration item | ✅ Active |
| `/cmdb/item/:id` | CMDBItemDetail | CI detail view with relationships | ✅ Active |
| `/cmdb/reconciliation` | CMDBReconciliation | CI reconciliation & sync | ✅ Active |

### Change Management
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/change-management` | ChangeManagement | Change request dashboard | ✅ Active |
| `/change-management/new` | ChangeManagementNew | Create new change request | ✅ Active |
| `/change-management/:id` | ChangeManagementDetail | Change request detail & approvals | ✅ Active |

---

## AI & Knowledge

### AI Assistants
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/intelligent-assistant` | IntelligentAssistant | Global AI assistant chat | ✅ Active |
| `/predictive-insights` | PredictiveInsights | ML-powered predictive analytics | ✅ Active |

### Knowledge Management
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/knowledge` | KnowledgeBase | Knowledge base article browser | ✅ Active |
| `/knowledge/upload` | KnowledgeUpload | Upload knowledge documents | ✅ Active |
| `/knowledge/:id` | KnowledgeArticle | Knowledge article viewer | ✅ Active |

---

## Integration Pages

### External System Integrations
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/cipp` | CIPPDashboard | CIPP tenant management portal | ✅ Active |
| `/ninjaone` | NinjaOneIntegration | NinjaOne RMM integration | ✅ Active |
| `/sharepoint-sync` | SharePointSync | SharePoint document sync | ✅ Active |

### Network & Monitoring
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/network-monitoring` | NetworkMonitoring | Network device monitoring | ✅ Active |
| `/network-devices/new` | NetworkDeviceNew | Add new network device | ✅ Active |

---

## Testing & Validation

### System Testing
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/test/validation` | SystemValidationDashboard | System validation & health checks | ✅ Active |
| `/test/comprehensive` | ComprehensiveTestDashboard | Comprehensive testing suite | ✅ Active |

---

## Customer & Business Management

### Customer Management (NEW - Oct 10)
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/customers` | CustomerAccounts | Customer account management | ✅ New (Oct 10) |
| `/customers/:id` | CustomerAccountDetail | Customer detail with contacts, sites, assets | ✅ New (Oct 10) |

### HR & Employee Management (NEW - Oct 10)
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/employees` | EmployeeDirectory | Employee directory and management | ✅ New (Oct 10) |
| `/departments` | DepartmentManagement | Department management | ✅ New (Oct 10) |
| `/leave-management` | LeaveManagement | Leave request management | ✅ New (Oct 10) |

### Project Management (ENHANCED - Oct 10)
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/projects` | ProjectManagement | Project tracking with full lifecycle | ✅ Enhanced (Oct 10) |

### Vendor Management (NEW - Oct 10)
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/vendors` | VendorManagement | Vendor management and tracking | ✅ New (Oct 10) |
| `/vendors/:id` | VendorDetail | Vendor detail with contracts & performance | ✅ New (Oct 10) |

### Client Onboarding
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/onboarding` | OnboardingDashboard | Client onboarding tracking | ✅ Active |
| `/onboarding/templates` | OnboardingTemplates | Onboarding templates management | ✅ Active |

### Incident & Service
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/incidents` | IncidentsDashboard | Incident management | ✅ Active |
| `/remediation-rules` | RemediationRules | Auto-remediation rule config | ✅ Active |

### Reporting
| Route | Page | Description | Status |
|-------|------|-------------|--------|
| `/custom-reports` | CustomReportBuilder | Custom report builder | ✅ Active |

---

## Feature Status Matrix

### Core Capabilities

| Feature Category | Components | Database Tables | Edge Functions | Status |
|-----------------|------------|-----------------|----------------|--------|
| **Authentication** | Auth, ProtectedRoute | user_profiles, user_roles, roles | - | ✅ Production |
| **Customer Management** | CustomerAdmin | customers, customer_customizations | customer-management | ✅ Production |
| **Products & Billing** | ProductsAdmin | products, customer_subscriptions | - | ✅ New (Oct 9) |
| **Applications** | ApplicationsAdmin, AppLauncher | applications, application_access | - | ✅ Production |
| **Department Dashboards** | 8 dashboards | user_profiles (department) | department-assistant | ✅ Production |
| **Compliance** | 7 pages | compliance_* (12 tables) | batch-evidence-generator | ✅ Production |
| **CMDB** | 5 pages | configuration_items, ci_relationships | - | ✅ Production |
| **Change Management** | 3 pages | change_requests, change_approvals | change-impact-analyzer | ✅ Production |
| **Workflows** | 6 pages | workflows, workflow_executions | workflow-executor, workflow-orchestrator | ✅ Production |
| **Customer Management** | 2 pages | customer_accounts, customer_contacts, customer_sites | - | ✅ New (Oct 10) |
| **HR Management** | 3 pages | employees, departments, employee_leave | - | ✅ New (Oct 10) |
| **Project Management** | 1 page | projects, project_tasks, project_milestones | - | ✅ Enhanced (Oct 10) |
| **Vendor Management** | 2 pages | vendors, vendor_contracts, vendor_performance | - | ✅ New (Oct 10) |
| **AI Assistants** | 2 pages | ai_interactions, ml_insights | intelligent-assistant, department-assistant | ✅ Production |
| **Knowledge Base** | 3 pages | knowledge_articles, knowledge_files | knowledge-processor | ✅ Production |
| **MCP Integration** | MCPServerDashboard | mcp_servers, mcp_tools | mcp-server, ai-mcp-generator | ✅ Production |
| **Audit Logging** | PrivilegedAccessAudit | audit_logs | - | ✅ Production |
| **CIPP Integration** | CIPPDashboard | cipp_tenants, cipp_policies | cipp-sync | ✅ Production |
| **NinjaOne Integration** | NinjaOneIntegration | - | ninjaone-sync, ninjaone-webhook | ✅ Production |
| **Revio Integration** | SalesDashboard | - | revio-data | ✅ Production |
| **M365 Integration** | ITDashboard | - | graph-api | ✅ Production |
| **SharePoint** | SharePointSync | - | sharepoint-sync | ✅ Production |
| **Network Monitoring** | NetworkMonitoring | network_devices | snmp-collector, syslog-collector | ✅ Production |
| **Client Portal** | ClientPortal | client_tickets, client_portal_users | client-portal | ✅ Production |
| **Testing** | 2 dashboards | - | comprehensive-test-data-generator | ✅ Production |

---

## Recently Added Features

### October 10, 2025
- **Navigation Revamp**: New 6-category navigation system for better organization
- **Customer & Account Management**: Full customer account management with contacts, sites, assets, service history
- **HR & Employee Management**: Employee directory, department management, leave management, performance reviews, certifications
- **Enhanced Project Management**: Project tracking with tasks, milestones, team management, expenses, time entries
- **Vendor Management**: Vendor tracking with contracts, performance history, and automated vendor codes

### October 9, 2025
- **Products Admin**: Full product catalog management with CRUD operations
- **Keeper Security App**: Added to employee portal for password management
- **Documentation**: Created comprehensive platform feature index

### Recent Enhancements (Last 30 Days)
- CIPP tenant management portal
- Privileged access audit logging
- Change impact analysis AI
- Workflow orchestration improvements
- MCP server integration
- Repetitive task detection
- Auto-remediation rules
- Network monitoring (SNMP/Syslog)
- Custom report builder
- Client onboarding templates

---

## Navigation Structure

### New 6-Category Navigation System (October 10, 2025)

The platform features an organized 6-category horizontal scrolling navigation with grid-based overlay menus. Each category expands into a 3-column responsive grid layout for easy access to all features:

#### 1. Operations & IT
- Operations Dashboard, IT Dashboard, CMDB, Change Management
- Incidents, Network Monitoring, SLA Management
- MCP Server, Admin, NinjaOne Integration

#### 2. Compliance & Security  
- Compliance Portal, Compliance Dashboard, SOC Dashboard
- CIPP, RBAC Portal, Audit Reports, Frameworks
- Privileged Access, Remediation Rules

#### 3. Business & Sales
- Sales Dashboard, Sales Portal, Client Portal
- Customers, Leads, Opportunities, Quotes
- Contracts, Projects

#### 4. Finance
- Finance Dashboard, Budgets, Invoices, Expenses
- Purchase Orders, Asset Financials, Financial Reports
- Vendors, Inventory, Warehouses

#### 5. HR & People
- HR Dashboard, Employee Portal, Employees, Departments
- Leave Requests, Onboarding, Onboarding Templates, Time Tracking

#### 6. Analytics & Automation
- Executive Dashboard, Analytics Portal, Data Flow Portal
- Workflow Automation, Workflow Builder, Workflow Orchestration
- Visual Builder, Workflow Intelligence, Intelligent Assistant
- Predictive Insights, Knowledge Base, Custom Reports

---

## Access Control Matrix

| Page Category | Required Role | Department Access |
|---------------|---------------|-------------------|
| Public Pages | None | All |
| Portal | Authenticated | All |
| Department Dashboards | Authenticated | Department-specific |
| Admin Pages | Admin/Super Admin | Admin only |
| Compliance | Authenticated | Compliance, Admin |
| CMDB | Authenticated | IT, Operations, Admin |
| Change Management | Authenticated | IT, Operations, Admin |
| Client Portal | Portal User | External clients |
| Testing Dashboards | Admin | Admin only |

---

## Integration Summary

### External Systems Connected
1. **Microsoft 365** - Calendar, Email, Teams, Azure
2. **CIPP** - M365 tenant management
3. **NinjaOne** - RMM/PSA integration
4. **Revio** - Billing & revenue data
5. **SharePoint** - Document management
6. **Lovable AI** - AI capabilities (Gemini, GPT)

### Edge Functions (17 Total)
1. `department-assistant` - Department-specific AI
2. `intelligent-assistant` - Global AI assistant
3. `workflow-executor` - Execute workflows
4. `workflow-orchestrator` - Workflow coordination
5. `workflow-webhook` - Webhook handlers
6. `workflow-insights` - Workflow analytics
7. `cipp-sync` - CIPP data synchronization
8. `ninjaone-sync` - NinjaOne data sync
9. `ninjaone-webhook` - NinjaOne webhooks
10. `graph-api` - Microsoft Graph API
11. `sharepoint-sync` - SharePoint sync
12. `revio-data` - Revio billing data
13. `mcp-server` - MCP protocol server
14. `ai-mcp-generator` - AI MCP generation
15. `knowledge-processor` - Knowledge processing
16. `batch-evidence-generator` - Compliance evidence
17. `change-impact-analyzer` - Change impact analysis

---

## Database Statistics

- **Total Tables**: 55+
- **Core Tables**: 10 (customers, users, profiles, roles, etc.)
- **Feature Tables**: 45+ (workflows, compliance, CMDB, etc.)
- **All tables protected by RLS**: ✅ Yes
- **Authentication**: Supabase Auth (Email + OAuth)

---

## Performance Metrics

- **Average Page Load**: <2s
- **Database Query Performance**: <100ms (p95)
- **Edge Function Response**: <500ms
- **RLS Policy Overhead**: Minimal (<10ms)

---

## Support & Documentation

- **Architecture Guide**: ARCHITECTURE.md
- **API Reference**: API_REFERENCE.md
- **Testing Guide**: TESTING_GUIDE.md
- **Component Library**: COMPONENT_LIBRARY.md (new)
- **Developer Handoff**: DEVELOPER_HANDOFF.md
- **Onboarding**: ONBOARDING.md

---

**Note**: This index is automatically updated as new features are added. Last comprehensive review: October 9, 2025.
