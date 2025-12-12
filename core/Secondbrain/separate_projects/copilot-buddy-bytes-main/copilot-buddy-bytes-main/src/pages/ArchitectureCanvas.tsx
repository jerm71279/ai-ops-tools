import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { ZoomIn, ZoomOut, Maximize2 } from "lucide-react";
import mermaid from "mermaid";

const ArchitectureCanvas = () => {
  const [zoom, setZoom] = useState(1);
  const mermaidRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mermaid.initialize({ 
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    });
  }, []);

  useEffect(() => {
    if (mermaidRef.current) {
      mermaid.contentLoaded();
    }
  }, [zoom]);

  const mermaidDiagram = `
graph TB
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
    CompDash --> CIPPSync
    
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
    CIPPSync --> CompFrameworks
    
    %% Edge Functions to External Systems
    GraphAPI --> M365
    SharePointSync --> SharePoint
    RevioData --> Revio
    CIPPSync --> CIPP
    WorkflowExec --> NinjaOne
    
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
    
    %% Compliance Integration Points
    CompControls --> Workflows
    CompReports --> AuditLogs
    CompFrameworks --> Customers
    WorkflowExecs --> CompReports
    AuditLogs --> CompControls
    
    %% RLS Protection
    RLS -.->|Protects| Users
    RLS -.->|Protects| Customers
    RLS -.->|Protects| Workflows
    RLS -.->|Protects| KnowArticles
    RLS -.->|Protects| AIInteract
    RLS -.->|Protects| CompFrameworks
    
    style Landing fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style Portal fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style Auth fill:#10b981,stroke:#059669,color:#fff
    style RLS fill:#ef4444,stroke:#dc2626,color:#fff
    style LovableAI fill:#f59e0b,stroke:#d97706,color:#fff
    style M365 fill:#0078d4,stroke:#106ebe,color:#fff
    style Revio fill:#3b82f6,stroke:#2563eb,color:#fff
    style CompFrameworks fill:#ec4899,stroke:#db2777,color:#fff
    style CompControls fill:#ec4899,stroke:#db2777,color:#fff
    style CompReports fill:#ec4899,stroke:#db2777,color:#fff
`;

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-[98vw] mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">OberaConnect System Architecture</h1>
            <p className="text-muted-foreground mt-1">Interactive canvas showing all platform interconnections</p>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setZoom(Math.min(zoom + 0.1, 2))}
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setZoom(Math.max(zoom - 0.1, 0.5))}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setZoom(1)}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="border border-border rounded-lg bg-card shadow-lg overflow-auto" style={{ height: 'calc(100vh - 180px)' }}>
          <div 
            className="p-8 transition-transform duration-200"
            style={{ 
              transform: `scale(${zoom})`,
              transformOrigin: 'top left',
              minWidth: '2000px'
            }}
          >
            <div ref={mermaidRef} className="mermaid">
              {mermaidDiagram}
            </div>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#8b5cf6' }}></div>
            <span className="text-muted-foreground">Frontend Layer</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#10b981' }}></div>
            <span className="text-muted-foreground">Authentication</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef4444' }}></div>
            <span className="text-muted-foreground">Security (RLS)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ec4899' }}></div>
            <span className="text-muted-foreground">Compliance System</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureCanvas;
