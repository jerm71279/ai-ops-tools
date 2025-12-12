const ArchitectureDiagram = () => {
  const mermaidDiagram = `graph TB
    subgraph "Frontend Layer (React + Vite)"
        Landing[Landing Page]
        Portal[Employee Portal]
        
        subgraph "Department Dashboards"
            ExecDash[Executive Dashboard]
            ITDash[IT Dashboard]
            HRDash[HR Dashboard]
            SalesDash[Sales Dashboard]
            FinDash[Finance Dashboard]
            OpsDash[Operations Dashboard]
            SOCDash[SOC Dashboard]
            CompDash[Compliance Dashboard]
        end
        
        subgraph "Admin & Tools"
            AdminDash[Admin Dashboard]
            AppAdmin[Applications Admin]
            WorkflowUI[Workflow Builder UI]
            WorkflowDetail[Workflow Execution Detail]
            KnowledgeUI[Knowledge Base UI]
            IntegUI[Integrations UI]
            TestValidation[System Validation Dashboard]
            TestComprehensive[Comprehensive Test Dashboard]
        end
        
        subgraph "AI Features"
            AIAssist[Department AI Assistant]
            IntAssist[Intelligent Assistant]
            MCPGen[MCP Generator UI]
        end
    end
    
    subgraph "Edge Functions Layer (Lovable Cloud)"
        DeptAssist[department-assistant]
        MCPServer[mcp-server]
        WorkflowExec[workflow-executor]
        WorkflowHook[workflow-webhook]
        RevioData[revio-data]
        GraphAPI[graph-api]
        SharePointSync[sharepoint-sync]
        KnowProc[knowledge-processor]
        IntellAssist[intelligent-assistant]
        AIMCPGen[ai-mcp-generator]
        WorkflowInsights[workflow-insights]
        CIPPSync[cipp-sync]
    end
    
    subgraph "Lovable Cloud Backend"
        Auth[Supabase Auth<br/>Email + OAuth]
        
        subgraph "Core Tables"
            Users[user_profiles]
            Customers[customers]
            Roles[roles + user_roles]
            Apps[applications]
        end
        
        subgraph "Integration Data"
            Integrations[integrations]
            IntegCreds[integration_credentials]
            OnboardData[client_onboardings]
        end
        
        subgraph "Workflow System"
            Workflows[workflows]
            WorkflowSteps[workflow_steps]
            WorkflowExecs[workflow_executions]
            WorkflowTriggers[workflow_triggers]
        end
        
        subgraph "AI & Knowledge"
            AIInteract[ai_interactions]
            KnowArticles[knowledge_articles]
            KnowFiles[knowledge_files]
            MLInsights[ml_insights]
        end
        
        subgraph "MCP System"
            MCPServers[mcp_servers]
            MCPTools[mcp_tools]
            MCPLogs[mcp_execution_logs]
        end
        
        subgraph "Compliance & Audit"
            CompFrameworks[compliance_frameworks]
            CompControls[compliance_controls]
            CompReports[compliance_reports]
            AuditLogs[audit_logs]
            PrivAccess[Privileged Access Audit]
        end
        
        RLS[Row Level Security<br/>Policies]
    end
    
    subgraph "External Systems"
        M365[Microsoft 365<br/>Calendar/Email/Teams]
        SharePoint[SharePoint<br/>Documents]
        Revio[Revio Billing<br/>Revenue Data]
        OneBill[OneBill<br/>Current System]
        NinjaOne[NinjaOne<br/>RMM/PSA]
        CIPP[CIPP<br/>M365 Tenant Management]
        LovableAI[Lovable AI<br/>Gemini/GPT Models]
    end
    
    %% Frontend to Edge Functions
    Portal --> DeptAssist
    AIAssist --> DeptAssist
    IntAssist --> IntellAssist
    WorkflowUI --> WorkflowExec
    WorkflowUI --> WorkflowHook
    SalesDash --> RevioData
    ITDash --> GraphAPI
    IntegUI --> SharePointSync
    KnowledgeUI --> KnowProc
    MCPGen --> AIMCPGen
    ExecDash --> WorkflowInsights
    
    %% Edge Functions to Database
    DeptAssist --> AIInteract
    DeptAssist --> KnowArticles
    IntellAssist --> AIInteract
    WorkflowExec --> WorkflowExecs
    WorkflowExec --> Workflows
    WorkflowHook --> WorkflowTriggers
    KnowProc --> KnowArticles
    KnowProc --> KnowFiles
    AIMCPGen --> MCPServers
    AIMCPGen --> MCPTools
    MCPServer --> MCPLogs
    WorkflowInsights --> WorkflowExecs
    
    %% Edge Functions to External Systems
    GraphAPI --> M365
    SharePointSync --> SharePoint
    RevioData --> Revio
    CIPPSync --> CIPP
    
    %% AI Integration
    DeptAssist --> LovableAI
    IntellAssist --> LovableAI
    KnowProc --> LovableAI
    AIMCPGen --> LovableAI
    
    %% Authentication Flow
    Landing --> Auth
    Portal --> Auth
    Auth --> Users
    Auth --> Roles
    RLS --> Auth
    
    %% Database Relationships
    Users --> Customers
    Roles --> Users
    Apps --> Roles
    Integrations --> Customers
    IntegCreds --> Integrations
    OnboardData --> Customers
    Workflows --> Customers
    WorkflowSteps --> Workflows
    MCPServers --> Customers
    MCPTools --> MCPServers
    KnowArticles --> Customers
    CompFrameworks --> CompControls
    CompReports --> Customers
    AuditLogs --> Users
    
    %% RLS Protection
    RLS -.->|Protects| Users
    RLS -.->|Protects| Customers
    RLS -.->|Protects| Workflows
    RLS -.->|Protects| KnowArticles
    RLS -.->|Protects| AIInteract
    
    style Landing fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style Portal fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style Auth fill:#10b981,stroke:#059669,color:#fff
    style RLS fill:#ef4444,stroke:#dc2626,color:#fff
    style LovableAI fill:#f59e0b,stroke:#d97706,color:#fff
    style M365 fill:#0078d4,stroke:#106ebe,color:#fff
    style Revio fill:#3b82f6,stroke:#2563eb,color:#fff`;

  return (
    <div className="min-h-screen w-full bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-[95vw] overflow-auto">
        <div dangerouslySetInnerHTML={{ __html: `<lov-mermaid>${mermaidDiagram}</lov-mermaid>` }} />
      </div>
    </div>
  );
};

export default ArchitectureDiagram;
