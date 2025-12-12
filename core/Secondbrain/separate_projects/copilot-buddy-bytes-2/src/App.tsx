import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardPortalLanes from "./components/DashboardPortalLanes";
import Index from "./pages/Index";
import IntegrationsPage from "./pages/IntegrationsPage";
import Auth from "./pages/Auth";
import DemoSelector from "./pages/DemoSelector";
import Portal from "./pages/Portal";
import AnalyticsPortal from "./pages/AnalyticsPortal";
import WorkflowDetail from "./pages/WorkflowDetail";
import KnowledgeBase from "./pages/KnowledgeBase";
import KnowledgeArticle from "./pages/KnowledgeArticle";
import KnowledgeUpload from "./pages/KnowledgeUpload";
import AdminDashboard from "./pages/AdminDashboard";
import ComplianceDashboard from "./pages/ComplianceDashboard";
import ITDashboard from "./pages/ITDashboard";
import OperationsDashboard from "./pages/OperationsDashboard";
import HRDashboard from "./pages/HRDashboard";
import FinanceDashboard from "./pages/FinanceDashboard";
import SalesDashboard from "./pages/SalesDashboard";
import ExecutiveDashboard from "./pages/ExecutiveDashboard";
import SOCDashboard from "./pages/SOCDashboard";
import SharePointSync from "./pages/SharePointSync";
import IntelligentAssistant from "./pages/IntelligentAssistant";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";
import ApplicationsAdmin from "./pages/ApplicationsAdmin";
import OnboardingDashboard from "./pages/OnboardingDashboard";
import OnboardingTemplates from "./pages/OnboardingTemplates";
import OnboardingNew from "./pages/OnboardingNew";
import CompliancePortal from "./pages/CompliancePortal";
import ComplianceFrameworkDetail from "./pages/ComplianceFrameworkDetail";
import ComplianceFrameworkRecords from "./pages/ComplianceFrameworkRecords";
import ComplianceControlDetail from "./pages/ComplianceControlDetail";
import ComplianceAuditReports from "./pages/ComplianceAuditReports";
import ComplianceEvidenceUpload from "./pages/ComplianceEvidenceUpload";
import ComplianceReportDetail from "./pages/ComplianceReportDetail";
import WorkflowAutomation from "./pages/WorkflowAutomation";
import WorkflowExecutionDetail from "./pages/WorkflowExecutionDetail";
import NinjaOneIntegration from "./pages/NinjaOneIntegration";
import PrivilegedAccessAudit from "./pages/PrivilegedAccessAudit";
import CMDBDashboard from "./pages/CMDBDashboard";
import CMDBItemDetail from "./pages/CMDBItemDetail";
import CMDBAddItem from "./pages/CMDBAddItem";
import CMDBEditItem from "./pages/CMDBEditItem";
import CMDBReconciliation from "./pages/CMDBReconciliation";
import ChangeManagement from "./pages/ChangeManagement";
import ChangeManagementNew from "./pages/ChangeManagementNew";
import ChangeManagementDetail from "./pages/ChangeManagementDetail";
import TestWorkflowEvidence from "./pages/TestWorkflowEvidence";
import ComprehensiveTestDashboard from "./pages/ComprehensiveTestDashboard";

import SystemValidationDashboard from "./pages/SystemValidationDashboard";

import WorkflowBuilder from "./pages/WorkflowBuilder";
import MCPServerDashboard from "./pages/MCPServerDashboard";
import SalesPortal from "./pages/SalesPortal";
import CIPPDashboard from "./pages/CIPPDashboard";
import DataFlowPortal from "./pages/DataFlowPortal";
import RBACPortal from "./pages/RBACPortal";
import PredictiveInsights from "./pages/PredictiveInsights";
import WorkflowOrchestration from "./pages/WorkflowOrchestration";
import VisualWorkflowBuilder from "./pages/VisualWorkflowBuilder";
import CustomerAdmin from "./pages/CustomerAdmin";
import IncidentsDashboard from "./pages/IncidentsDashboard";
import RemediationRules from "./pages/RemediationRules";
import ClientPortal from "./pages/ClientPortal";
import CustomReportBuilder from "./pages/CustomReportBuilder";
import NetworkMonitoring from "./pages/NetworkMonitoring";
import NetworkDeviceNew from "./pages/NetworkDeviceNew";
import ProductsAdmin from "./pages/ProductsAdmin";
import Developers from "./pages/Developers";
import ArchitectureDiagram from "./pages/ArchitectureDiagram";
import ArchitectureCanvas from "./pages/ArchitectureCanvas";
import WorkflowIntelligence from "./pages/WorkflowIntelligence";
import SLAManagement from "./pages/SLAManagement";
import TimeTracking from "./pages/TimeTracking";
import ProjectManagement from "./pages/ProjectManagement";
import ContractManagement from "./pages/ContractManagement";
import PurchaseOrders from "./pages/PurchaseOrders";
import ExpenseManagement from "./pages/ExpenseManagement";
import BudgetTracking from "./pages/BudgetTracking";
import InvoiceManagement from "./pages/InvoiceManagement";
import AssetFinancials from "./pages/AssetFinancials";
import FinancialReporting from "./pages/FinancialReporting";
import VendorManagement from "./pages/VendorManagement";
import VendorDetail from "./pages/VendorDetail";
import InventoryManagement from "./pages/InventoryManagement";
import WarehouseManagement from "./pages/WarehouseManagement";
import LeadManagement from "./pages/LeadManagement";
import SalesOpportunities from "./pages/SalesOpportunities";
import SalesQuotes from "./pages/SalesQuotes";
import CustomerAccounts from "./pages/CustomerAccounts";
import CustomerAccountDetail from "./pages/CustomerAccountDetail";
import EmployeeDirectory from "./pages/EmployeeDirectory";
import DepartmentManagement from "./pages/DepartmentManagement";
import LeaveManagement from "./pages/LeaveManagement";
import EmployeeOnboardingDashboard from "./pages/hr/EmployeeOnboardingDashboard";
import EmployeeOnboardingTemplates from "./pages/hr/EmployeeOnboardingTemplates";
import EmployeeOnboardingNew from "./pages/hr/EmployeeOnboardingNew";
import EmployeeOnboardingDetail from "./pages/hr/EmployeeOnboardingDetail";
import EmployeeOnboardingEdit from "./pages/hr/EmployeeOnboardingEdit";
import ModuleManagement from "./pages/ModuleManagement";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <DashboardPortalLanes />
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/integrations" element={<IntegrationsPage />} />
          <Route path="/developers" element={<Developers />} />
          <Route path="/architecture-diagram" element={<ArchitectureDiagram />} />
          <Route path="/architecture/canvas" element={<ArchitectureCanvas />} />
          <Route path="/workflow-intelligence" element={<WorkflowIntelligence />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/demo" element={<DemoSelector />} />
          
          {/* Portal - Protected but no admin required */}
          <Route path="/portal" element={
            <ProtectedRoute>
              <Portal />
            </ProtectedRoute>
          } />
          
          {/* Analytics Portal - Protected but no admin required */}
          <Route path="/analytics" element={
            <ProtectedRoute>
              <AnalyticsPortal />
            </ProtectedRoute>
          } />
          
          {/* Sales Portal - Protected but no admin required */}
          <Route path="/sales-portal" element={
            <ProtectedRoute>
              <SalesPortal />
            </ProtectedRoute>
          } />
          
          {/* Workflow Detail Pages */}
          <Route path="/workflow/:workflowType" element={<WorkflowDetail />} />
          
          {/* Knowledge Base - Protected */}
          <Route path="/knowledge" element={
            <ProtectedRoute>
              <KnowledgeBase />
            </ProtectedRoute>
          } />
          <Route path="/knowledge/upload" element={
            <ProtectedRoute>
              <KnowledgeUpload />
            </ProtectedRoute>
          } />
          <Route path="/knowledge/:id" element={
            <ProtectedRoute>
              <KnowledgeArticle />
            </ProtectedRoute>
          } />
          
          {/* Internal OberaConnect Dashboards - Admin Only */}
          <Route path="/admin" element={
            <ProtectedRoute requireAdmin>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/compliance" element={
            <ProtectedRoute requireAdmin>
              <ComplianceDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/it" element={
            <ProtectedRoute requireAdmin>
              <ITDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/operations" element={
            <ProtectedRoute requireAdmin>
              <OperationsDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/hr" element={
            <ProtectedRoute requireAdmin>
              <HRDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/finance" element={
            <ProtectedRoute requireAdmin>
              <FinanceDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/sales" element={
            <ProtectedRoute requireAdmin>
              <SalesDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/executive" element={
            <ProtectedRoute requireAdmin>
              <ExecutiveDashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/soc" element={
            <ProtectedRoute requireAdmin>
              <SOCDashboard />
            </ProtectedRoute>
          } />
          
          {/* SharePoint Sync - Protected */}
          <Route path="/sharepoint-sync" element={
            <ProtectedRoute>
              <SharePointSync />
            </ProtectedRoute>
          } />
          
          {/* Intelligent Assistant - Protected */}
          <Route path="/intelligent-assistant" element={
            <ProtectedRoute>
              <IntelligentAssistant />
            </ProtectedRoute>
          } />
          
          {/* Application Management - Admin Only */}
          <Route path="/admin/applications" element={
            <ProtectedRoute requireAdmin>
              <ApplicationsAdmin />
            </ProtectedRoute>
          } />
          
          {/* Onboarding - Protected */}
          <Route path="/onboarding" element={
            <ProtectedRoute>
              <OnboardingDashboard />
            </ProtectedRoute>
          } />
          <Route path="/onboarding/new" element={
            <ProtectedRoute>
              <OnboardingNew />
            </ProtectedRoute>
          } />
          <Route path="/onboarding/templates" element={
            <ProtectedRoute>
              <OnboardingTemplates />
            </ProtectedRoute>
          } />
          
          {/* Compliance - Protected */}
          <Route path="/compliance" element={
            <ProtectedRoute>
              <CompliancePortal />
            </ProtectedRoute>
          } />
          
          {/* Workflow Automation - Protected */}
          <Route path="/workflows" element={
            <ProtectedRoute>
              <WorkflowAutomation />
            </ProtectedRoute>
          } />
          <Route path="/workflows/builder" element={
            <ProtectedRoute>
              <WorkflowBuilder />
            </ProtectedRoute>
          } />
          <Route path="/workflow/execution/:executionId" element={
            <ProtectedRoute>
              <WorkflowExecutionDetail />
            </ProtectedRoute>
          } />
          
          {/* NinjaOne Integration - Protected */}
          <Route path="/ninjaone" element={
            <ProtectedRoute>
              <NinjaOneIntegration />
            </ProtectedRoute>
          } />
          
          {/* CMDB & Change Management - Protected */}
          <Route path="/cmdb" element={
            <ProtectedRoute>
              <CMDBDashboard />
            </ProtectedRoute>
          } />
          <Route path="/cmdb/add" element={
            <ProtectedRoute>
              <CMDBAddItem />
            </ProtectedRoute>
          } />
          <Route path="/cmdb/reconciliation" element={
            <ProtectedRoute>
              <CMDBReconciliation />
            </ProtectedRoute>
          } />
          <Route path="/cmdb/:id/edit" element={
            <ProtectedRoute>
              <CMDBEditItem />
            </ProtectedRoute>
          } />
          <Route path="/cmdb/:id" element={
            <ProtectedRoute>
              <CMDBItemDetail />
            </ProtectedRoute>
          } />
          <Route path="/change-management" element={
            <ProtectedRoute>
              <ChangeManagement />
            </ProtectedRoute>
          } />
          <Route path="/change-management/new" element={
            <ProtectedRoute>
              <ChangeManagementNew />
            </ProtectedRoute>
          } />
          <Route path="/change-management/:id" element={
            <ProtectedRoute>
              <ChangeManagementDetail />
            </ProtectedRoute>
          } />
          
          {/* Privileged Access Audit - Admin Only */}
          <Route path="/audit/privileged-access" element={
            <ProtectedRoute requireAdmin>
              <PrivilegedAccessAudit />
            </ProtectedRoute>
          } />
          
          {/* RBAC Portal - Admin Only */}
          <Route path="/rbac" element={
            <ProtectedRoute requireAdmin>
              <RBACPortal />
            </ProtectedRoute>
          } />
          
          {/* Predictive Insights - Protected */}
          <Route path="/predictive-insights" element={
            <ProtectedRoute>
              <PredictiveInsights />
            </ProtectedRoute>
          } />
          
          {/* Workflow Orchestration - Protected */}
          <Route path="/workflow-orchestration" element={
            <ProtectedRoute>
              <WorkflowOrchestration />
            </ProtectedRoute>
          } />
          <Route path="/workflows/visual-builder" element={
            <ProtectedRoute>
              <VisualWorkflowBuilder />
            </ProtectedRoute>
          } />
          
          {/* Compliance Audit Reports - Protected */}
          <Route path="/compliance/audit-reports" element={
            <ProtectedRoute>
              <ComplianceAuditReports />
            </ProtectedRoute>
          } />
          
          {/* Compliance Framework Records - Protected */}
          <Route path="/compliance/framework/:framework/records" element={
            <ProtectedRoute>
              <ComplianceFrameworkRecords />
            </ProtectedRoute>
          } />
          
          {/* Compliance Framework Detail - Protected */}
          <Route path="/compliance/frameworks/:id" element={
            <ProtectedRoute>
              <ComplianceFrameworkDetail />
            </ProtectedRoute>
          } />
          
          {/* Compliance Control Detail - Protected */}
          <Route path="/compliance/frameworks/:frameworkId/controls/:controlId" element={
            <ProtectedRoute>
              <ComplianceControlDetail />
            </ProtectedRoute>
          } />
          <Route path="/compliance/evidence/upload" element={
            <ProtectedRoute>
              <ComplianceEvidenceUpload />
            </ProtectedRoute>
          } />
          
          {/* Test Workflow Evidence - Admin Only */}
          <Route path="/test/workflow-evidence" element={
            <ProtectedRoute requireAdmin>
              <TestWorkflowEvidence />
            </ProtectedRoute>
          } />
          
          {/* Comprehensive Test Dashboard - Admin Only */}
          <Route path="/test/comprehensive" element={
            <ProtectedRoute requireAdmin>
              <ComprehensiveTestDashboard />
            </ProtectedRoute>
          } />
          
          {/* System Validation Dashboard - Admin Only */}
          <Route path="/test/validation" element={
            <ProtectedRoute requireAdmin>
              <SystemValidationDashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/compliance/reports/:id" element={
            <ProtectedRoute>
              <ComplianceReportDetail />
            </ProtectedRoute>
          } />
          
          {/* MCP Server Dashboard - Protected */}
          <Route path="/mcp-servers" element={
            <ProtectedRoute>
              <MCPServerDashboard />
            </ProtectedRoute>
          } />
          
          {/* CIPP Dashboard - Protected */}
          <Route path="/cipp" element={
            <ProtectedRoute>
              <CIPPDashboard />
            </ProtectedRoute>
          } />
          
          {/* Data Flow Portal - Protected */}
          <Route path="/data-flows" element={
            <ProtectedRoute>
              <DataFlowPortal />
            </ProtectedRoute>
          } />
          
          {/* Analytics Portal - Protected */}
          <Route path="/analytics-portal" element={
            <ProtectedRoute>
              <AnalyticsPortal />
            </ProtectedRoute>
          } />
          
          {/* Customer Administration - Protected */}
          <Route path="/customer-admin" element={
            <ProtectedRoute>
              <CustomerAdmin />
            </ProtectedRoute>
          } />
          
          {/* Incidents & Auto-Remediation - Protected */}
          <Route path="/incidents" element={
            <ProtectedRoute>
              <IncidentsDashboard />
            </ProtectedRoute>
          } />
          <Route path="/remediation-rules" element={
            <ProtectedRoute>
              <RemediationRules />
            </ProtectedRoute>
          } />
          
          {/* Client Portal - Protected */}
          <Route path="/client-portal" element={
            <ProtectedRoute>
              <ClientPortal />
            </ProtectedRoute>
          } />
          
          {/* Custom Reports - Protected */}
          <Route path="/reports/builder" element={
            <ProtectedRoute>
              <CustomReportBuilder />
            </ProtectedRoute>
          } />
          
          {/* Network Monitoring - Protected */}
          <Route path="/network-monitoring" element={
            <ProtectedRoute>
              <NetworkMonitoring />
            </ProtectedRoute>
          } />
          <Route path="/network-monitoring/devices/new" element={
            <ProtectedRoute>
              <NetworkDeviceNew />
            </ProtectedRoute>
          } />
          
          {/* Products Admin - Admin Only */}
          <Route path="/admin/products" element={
            <ProtectedRoute requireAdmin>
              <ProductsAdmin />
            </ProtectedRoute>
          } />
          
          {/* MSP ERP Features - Protected */}
          <Route path="/sla-management" element={
            <ProtectedRoute>
              <SLAManagement />
            </ProtectedRoute>
          } />
          <Route path="/time-tracking" element={
            <ProtectedRoute>
              <TimeTracking />
            </ProtectedRoute>
          } />
          <Route path="/projects" element={
            <ProtectedRoute>
              <ProjectManagement />
            </ProtectedRoute>
          } />
          <Route path="/contracts" element={
            <ProtectedRoute>
              <ContractManagement />
            </ProtectedRoute>
          } />
          <Route path="/purchase-orders" element={
            <ProtectedRoute>
              <PurchaseOrders />
            </ProtectedRoute>
          } />
          <Route path="/expenses" element={
            <ProtectedRoute>
              <ExpenseManagement />
            </ProtectedRoute>
          } />
          <Route path="/budgets" element={
            <ProtectedRoute>
              <BudgetTracking />
            </ProtectedRoute>
          } />
          <Route path="/invoices" element={
            <ProtectedRoute>
              <InvoiceManagement />
            </ProtectedRoute>
          } />
          <Route path="/asset-financials" element={
            <ProtectedRoute>
              <AssetFinancials />
            </ProtectedRoute>
          } />
          <Route path="/financial-reports" element={
            <ProtectedRoute>
              <FinancialReporting />
            </ProtectedRoute>
          } />
          <Route path="/vendors" element={
            <ProtectedRoute>
              <VendorManagement />
            </ProtectedRoute>
          } />
          <Route path="/vendors/:id" element={
            <ProtectedRoute>
              <VendorDetail />
            </ProtectedRoute>
          } />
          <Route path="/inventory" element={
            <ProtectedRoute>
              <InventoryManagement />
            </ProtectedRoute>
          } />
          <Route path="/warehouses" element={
            <ProtectedRoute>
              <WarehouseManagement />
            </ProtectedRoute>
          } />
          <Route path="/leads" element={
            <ProtectedRoute>
              <LeadManagement />
            </ProtectedRoute>
          } />
          <Route path="/opportunities" element={
            <ProtectedRoute>
              <SalesOpportunities />
            </ProtectedRoute>
          } />
          <Route path="/quotes" element={
            <ProtectedRoute>
              <SalesQuotes />
            </ProtectedRoute>
          } />
          <Route path="/customers" element={
            <ProtectedRoute>
              <CustomerAccounts />
            </ProtectedRoute>
          } />
          <Route path="/customers/:id" element={
            <ProtectedRoute>
              <CustomerAccountDetail />
            </ProtectedRoute>
          } />
          <Route path="/employees" element={
            <ProtectedRoute>
              <EmployeeDirectory />
            </ProtectedRoute>
          } />
          <Route path="/departments" element={
            <ProtectedRoute>
              <DepartmentManagement />
            </ProtectedRoute>
          } />
          <Route path="/leave-management" element={
            <ProtectedRoute>
              <LeaveManagement />
            </ProtectedRoute>
          } />
          
          {/* HR Employee Onboarding - Protected */}
          <Route path="/hr/employee-onboarding" element={
            <ProtectedRoute>
              <EmployeeOnboardingDashboard />
            </ProtectedRoute>
          } />
          <Route path="/hr/employee-onboarding/new" element={
            <ProtectedRoute>
              <EmployeeOnboardingNew />
            </ProtectedRoute>
          } />
          <Route path="/hr/employee-onboarding/templates" element={
            <ProtectedRoute>
              <EmployeeOnboardingTemplates />
            </ProtectedRoute>
          } />
          <Route path="/hr/employee-onboarding/:id/edit" element={
            <ProtectedRoute>
              <EmployeeOnboardingEdit />
            </ProtectedRoute>
          } />
          <Route path="/hr/employee-onboarding/:id" element={
            <ProtectedRoute>
              <EmployeeOnboardingDetail />
            </ProtectedRoute>
          } />
          
          {/* Module Management - Protected Admin */}
          <Route path="/admin/modules" element={
            <ProtectedRoute requireAdmin>
              <ModuleManagement />
            </ProtectedRoute>
          } />
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
