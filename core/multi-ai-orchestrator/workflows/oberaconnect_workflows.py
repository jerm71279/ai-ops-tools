#!/usr/bin/env python3
"""
OberaConnect Workflow Implementations
Pre-built pipelines for common MSP operations

Author: OberaConnect Engineering
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import (
    Pipeline, PipelineStep, PipelineBuilder, AIProvider,
    create_portal_to_config_pipeline,
    create_log_analysis_pipeline,
    create_sop_capture_pipeline
)


# =============================================================================
# CUSTOMER ONBOARDING WORKFLOWS
# =============================================================================

def customer_onboarding_workflow(
    customer_name: str,
    portal_url: str,
    deployment_type: str = "standard"
) -> Pipeline:
    """
    Complete customer onboarding automation
    
    Flow:
    1. Fara: Extract customer info from vendor portal
    2. Claude: Generate network configs (MikroTik, UniFi)
    3. Claude: Generate Azure resource templates
    4. Claude: Create onboarding documentation
    """
    return (
        PipelineBuilder(f"onboarding_{customer_name.lower().replace(' ', '_')}")
        .description(f"Customer onboarding for {customer_name}")
        .output_dir(Path(f"./output/customers/{customer_name}"))
        
        # Step 1: Extract from portal
        .fara_step(
            name="extract_customer_data",
            task=f"""
            Navigate to {portal_url} and extract:
            - Company name and contact info
            - Network requirements (IP ranges, VLANs)
            - Service tier and features
            - Existing infrastructure details
            Return as structured JSON.
            """,
            description="Extract customer data from portal"
        )
        
        # Step 2: Generate MikroTik config
        .claude_step(
            name="generate_mikrotik_config",
            prompt="""
            Based on this customer data:
            {extract_customer_data}
            
            Generate a complete MikroTik RouterOS configuration including:
            - Interface configuration with proper naming
            - VLAN setup per requirements
            - Firewall rules (input/forward/output chains)
            - NAT rules
            - DHCP server configuration
            - DNS settings
            - Queue trees for bandwidth management
            - System identity and NTP
            
            Use OberaConnect standard naming conventions.
            Output as RouterOS script format.
            """,
            description="Generate MikroTik configuration"
        )
        
        # Step 3: Generate UniFi config
        .claude_step(
            name="generate_unifi_config",
            prompt="""
            Based on this customer data:
            {extract_customer_data}
            
            Generate UniFi Network configuration including:
            - Site settings
            - Network definitions (VLANs, subnets)
            - WiFi networks with proper security
            - Switch port profiles
            - Firewall rules
            
            Output as JSON for UniFi API import.
            """,
            description="Generate UniFi configuration"
        )
        
        # Step 4: Generate Azure resources
        .claude_step(
            name="generate_azure_bicep",
            prompt="""
            Based on this customer data:
            {extract_customer_data}
            
            Deployment type: {deployment_type}
            
            Generate Azure Bicep templates for:
            - Resource group with proper tagging
            - Virtual network with subnets
            - Network security groups
            - Azure AD integration resources
            - Backup vault configuration
            - Monitoring workspace
            
            Follow OberaConnect Azure naming conventions.
            """,
            description="Generate Azure Bicep templates"
        )
        
        # Step 5: Create documentation
        .claude_step(
            name="generate_documentation",
            prompt="""
            Create comprehensive onboarding documentation for customer:
            
            Customer Data:
            {extract_customer_data}
            
            Generated Configs:
            - MikroTik: {generate_mikrotik_config}
            - UniFi: {generate_unifi_config}
            - Azure: {generate_azure_bicep}
            
            Generate a Markdown document including:
            1. Customer overview
            2. Network topology diagram (Mermaid)
            3. Configuration summary
            4. Deployment checklist
            5. Post-deployment validation steps
            6. Support escalation contacts
            """,
            description="Generate onboarding documentation"
        )
        .build()
    )


# =============================================================================
# VENDOR PORTAL AUTOMATION
# =============================================================================

def vendor_data_extraction_workflow(
    vendor_name: str,
    portal_url: str,
    data_type: str = "licensing"
) -> Pipeline:
    """
    Extract and analyze data from vendor portals
    
    Flow:
    1. Fara: Navigate portal, extract data
    2. Gemini: Analyze large datasets (if needed)
    3. Claude: Generate report
    """
    return (
        PipelineBuilder(f"vendor_extract_{vendor_name.lower()}")
        .description(f"Extract {data_type} data from {vendor_name}")
        
        .fara_step(
            name="extract_vendor_data",
            task=f"""
            Log into {portal_url} and extract {data_type} information:
            - Navigate to the {data_type} section
            - Export or scrape all available data
            - Download any available reports
            Return structured data and file paths.
            """,
            description=f"Extract {data_type} from {vendor_name} portal"
        )
        
        .claude_step(
            name="analyze_and_report",
            prompt="""
            Analyze this vendor data:
            {extract_vendor_data}
            
            Generate a report including:
            1. Summary statistics
            2. Expiring licenses/subscriptions (next 90 days)
            3. Cost optimization opportunities
            4. Compliance status
            5. Recommended actions
            
            Format as Markdown with tables.
            """,
            description="Analyze data and generate report"
        )
        .build()
    )


# =============================================================================
# INCIDENT RESPONSE WORKFLOWS
# =============================================================================

def incident_analysis_workflow(
    incident_id: str,
    log_files: List[str],
    affected_systems: List[str]
) -> Pipeline:
    """
    Incident analysis and remediation
    
    Flow:
    1. Gemini: Analyze large log files (1M+ token context)
    2. Claude: Correlate findings across systems
    3. Claude: Generate remediation scripts
    4. Claude: Create incident report
    """
    return (
        PipelineBuilder(f"incident_{incident_id}")
        .description(f"Incident analysis for {incident_id}")
        
        .gemini_step(
            name="analyze_logs",
            prompt="""
            Perform deep analysis on the provided log files.
            
            Identify:
            1. Timeline of events leading to incident
            2. Error patterns and frequencies
            3. Affected services and dependencies
            4. Root cause indicators
            5. Anomalous behavior patterns
            
            Affected systems: {affected_systems}
            
            Return structured JSON with timeline and findings.
            """,
            description="Deep log analysis with Gemini's 1M context",
            provider_options={"files": log_files}
        )
        
        .claude_step(
            name="correlate_findings",
            prompt="""
            Based on log analysis:
            {analyze_logs}
            
            Correlate findings across systems:
            - {affected_systems}
            
            Determine:
            1. Definitive root cause
            2. Impact assessment
            3. Attack vector (if security incident)
            4. Data exposure risk
            """,
            description="Cross-system correlation"
        )
        
        .claude_step(
            name="generate_remediation",
            prompt="""
            Based on incident analysis:
            {correlate_findings}
            
            Generate remediation scripts for:
            1. Immediate containment (if needed)
            2. Service restoration
            3. Vulnerability patching
            4. Configuration hardening
            
            Include rollback procedures for each script.
            Output as separate bash scripts with comments.
            """,
            description="Generate remediation scripts"
        )
        
        .claude_step(
            name="create_incident_report",
            prompt="""
            Create a formal incident report:
            
            Incident ID: {incident_id}
            Log Analysis: {analyze_logs}
            Correlation: {correlate_findings}
            Remediation: {generate_remediation}
            
            Follow OberaConnect incident report template:
            1. Executive Summary
            2. Incident Timeline
            3. Technical Analysis
            4. Impact Assessment
            5. Root Cause Analysis
            6. Remediation Actions
            7. Lessons Learned
            8. Prevention Recommendations
            """,
            description="Generate formal incident report"
        )
        .build()
    )


# =============================================================================
# AZURE SERVICE DEPLOYMENT WORKFLOWS
# =============================================================================

def azure_service_deployment_workflow(
    service_name: str,
    environment: str = "lab",
    portal_automation: bool = False
) -> Pipeline:
    """
    Azure service deployment with optional portal automation
    
    Flow:
    1. Claude: Generate IaC (Bicep/Terraform)
    2. Claude: Generate deployment scripts
    3. Fara: (Optional) Configure via Azure Portal
    4. Claude: Generate documentation
    """
    builder = (
        PipelineBuilder(f"azure_deploy_{service_name}_{environment}")
        .description(f"Deploy {service_name} to {environment}")
        
        .claude_step(
            name="generate_iac",
            prompt=f"""
            Generate Azure Bicep template for deploying {service_name}.
            
            Environment: {environment}
            
            Include:
            - Resource definitions with proper SKUs for {environment}
            - Parameters for environment-specific values
            - Outputs for connection strings/endpoints
            - RBAC role assignments
            - Diagnostic settings
            - Tags following OberaConnect standards
            
            Follow Azure Well-Architected Framework principles.
            """,
            description="Generate Infrastructure as Code"
        )
        
        .claude_step(
            name="generate_deployment_script",
            prompt="""
            Generate deployment script for:
            {generate_iac}
            
            Include:
            - Pre-deployment validation
            - Azure CLI deployment commands
            - Post-deployment smoke tests
            - Rollback procedure
            - Secret rotation (if applicable)
            
            Output as bash script with proper error handling.
            """,
            description="Generate deployment automation"
        )
    )
    
    if portal_automation:
        builder = builder.fara_step(
            name="portal_configuration",
            task=f"""
            Navigate to Azure Portal and configure {service_name}:
            - Verify deployment succeeded
            - Configure any settings not available via IaC
            - Set up monitoring dashboards
            - Configure alerts
            
            Document any manual steps required.
            """,
            description="Configure remaining settings via portal"
        )
    
    return (
        builder
        .claude_step(
            name="generate_runbook",
            prompt="""
            Generate operational runbook for {service_name}:
            
            Deployment Info:
            {generate_iac}
            {generate_deployment_script}
            
            Include:
            1. Service overview and architecture
            2. Deployment procedures
            3. Monitoring and alerting
            4. Common troubleshooting
            5. Scaling procedures
            6. Backup and recovery
            7. Security considerations
            """,
            description="Generate operational runbook"
        )
        .build()
    )


# =============================================================================
# DOCUMENTATION WORKFLOWS
# =============================================================================

def sop_from_portal_workflow(
    sop_name: str,
    portal_url: str,
    task_description: str
) -> Pipeline:
    """
    Capture portal workflow and generate SOP
    
    Flow:
    1. Fara: Execute task, capture screenshots
    2. Claude: Generate SOP with Scribe format
    """
    return (
        PipelineBuilder(f"sop_{sop_name.lower().replace(' ', '_')}")
        .description(f"Generate SOP for: {sop_name}")
        
        .fara_step(
            name="capture_workflow",
            task=f"""
            Perform this task while documenting every step:
            {task_description}
            
            For each step, record:
            - Action taken (click, type, navigate)
            - Element interacted with
            - Expected result
            - Screenshot reference
            
            Return detailed step-by-step JSON.
            """,
            description="Execute and capture workflow",
            provider_options={
                "url": portal_url,
                "screenshot_dir": f"./screenshots/sop_{sop_name}"
            }
        )
        
        .claude_step(
            name="generate_sop",
            prompt="""
            Generate a Standard Operating Procedure from this captured workflow:
            {capture_workflow}
            
            Format using Scribe SOP template:
            
            # {sop_name}
            
            ## Document Control
            - Version: 1.0
            - Effective Date: [TODAY]
            - Owner: OberaConnect Engineering
            - Review Cycle: Quarterly
            
            ## Purpose
            [Why this procedure exists]
            
            ## Scope
            [Who uses this, when]
            
            ## Prerequisites
            [What's needed before starting]
            
            ## Procedure
            [Numbered steps with screenshots]
            
            ## Verification
            [How to confirm success]
            
            ## Troubleshooting
            [Common issues and solutions]
            
            ## Related Documents
            [Links to related SOPs]
            
            ## Revision History
            | Version | Date | Author | Changes |
            |---------|------|--------|---------|
            | 1.0 | [TODAY] | Auto-generated | Initial release |
            """,
            description="Generate SOP documentation"
        )
        .build()
    )


# =============================================================================
# PRICE COMPARISON WORKFLOW
# =============================================================================

def vendor_price_comparison_workflow(
    product_name: str,
    vendor_urls: List[str]
) -> Pipeline:
    """
    Compare prices across vendor portals
    
    Flow:
    1. Fara: Visit each vendor, extract pricing
    2. Claude: Analyze and recommend
    """
    return (
        PipelineBuilder(f"price_compare_{product_name.lower().replace(' ', '_')}")
        .description(f"Compare prices for {product_name}")
        
        .fara_step(
            name="extract_prices",
            task=f"""
            Visit each of these vendor sites and extract pricing for {product_name}:
            
            URLs: {vendor_urls}
            
            For each vendor, capture:
            - Vendor name
            - Product name/SKU
            - Unit price
            - Volume discounts (if any)
            - Shipping costs
            - Availability/lead time
            - Warranty terms
            
            Return as structured JSON array.
            """,
            description="Extract pricing from all vendors"
        )
        
        .claude_step(
            name="analyze_pricing",
            prompt="""
            Analyze this pricing data:
            {extract_prices}
            
            Generate a recommendation report including:
            
            1. **Price Comparison Table**
               - All vendors side-by-side
               - Highlight best price
            
            2. **Total Cost Analysis**
               - Include shipping
               - Volume discount scenarios
            
            3. **Recommendation**
               - Best overall value
               - Best for bulk orders
               - Fastest delivery option
            
            4. **Risk Assessment**
               - Warranty comparison
               - Vendor reliability notes
            """,
            description="Analyze and recommend"
        )
        .build()
    )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def list_available_workflows() -> Dict[str, str]:
    """List all available workflow templates"""
    return {
        "customer_onboarding": "Complete customer onboarding automation",
        "vendor_data_extraction": "Extract data from vendor portals",
        "incident_analysis": "Incident response and remediation",
        "azure_service_deployment": "Azure service deployment with IaC",
        "sop_from_portal": "Capture portal workflow, generate SOP",
        "vendor_price_comparison": "Compare prices across vendors"
    }


def get_workflow(
    workflow_name: str, 
    **kwargs
) -> Pipeline:
    """Factory function to get workflow by name"""
    workflows = {
        "customer_onboarding": customer_onboarding_workflow,
        "vendor_data_extraction": vendor_data_extraction_workflow,
        "incident_analysis": incident_analysis_workflow,
        "azure_service_deployment": azure_service_deployment_workflow,
        "sop_from_portal": sop_from_portal_workflow,
        "vendor_price_comparison": vendor_price_comparison_workflow
    }
    
    if workflow_name not in workflows:
        raise ValueError(f"Unknown workflow: {workflow_name}. Available: {list(workflows.keys())}")
    
    return workflows[workflow_name](**kwargs)
