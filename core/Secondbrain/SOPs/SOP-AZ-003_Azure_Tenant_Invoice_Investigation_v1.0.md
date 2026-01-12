# Standard Operating Procedure: Azure Tenant Invoice Investigation

| | |
|---|---|
| **Document ID:** | SOP-AZ-003 |
| **Title:** | Azure Tenant Invoice Investigation |
| **Category:** | Azure/Cloud |
| **Version:** | 1.0 |
| **Status:** | Draft |
| **Author:** | Jeremy Smith |
| **Creation Date:** | 2026-01-12 |
| **Approval Date:** | Pending |

---

### 1.0 Purpose
Provide a standardized procedure for investigating Azure invoice charges, identifying the associated tenant, and determining which resources are generating costs.

### 2.0 Scope
This procedure applies to OberaConnect technicians investigating Azure billing charges for managed tenants. It covers invoice analysis, tenant identification, resource enumeration, and cost attribution.

### 3.0 Definitions

| Term | Definition |
|------|------------|
| **Tenant ID** | Unique GUID identifying an Azure AD tenant |
| **Subscription ID** | Unique GUID identifying an Azure subscription within a tenant |
| **Billing Profile** | The account holder name associated with billing |
| **Resource Group** | Logical container for Azure resources |
| **Service Category** | Azure billing category (Compute, Storage, Networking, etc.) |

### 4.0 Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **Technician** | Perform invoice investigation and document findings |
| **Account Manager** | Review cost optimization recommendations |
| **Client Contact** | Approve any resource changes |

### 5.0 Prerequisites
- Azure CLI installed locally or access to Azure Cloud Shell
- Administrative access to the Azure tenant
- Copy of the Azure invoice (PDF or portal access)
- Access to Azure portal: https://portal.azure.com

---

### 6.0 Procedure

#### 6.1 Extract Invoice Information

1. Obtain the Azure invoice (PDF or from billing portal)
2. Locate the following key information:

| Field | Location on Invoice |
|-------|---------------------|
| Invoice Number | Invoice Summary section |
| Billing Period | Below Invoice Summary |
| Total Amount | Invoice Summary |
| Billing Profile | Account Information section |
| **Primary Tenant ID** | Account Information section (Page 2+) |
| Subscription ID | Details by Product section |

3. Record the **Primary Tenant ID** - this identifies which Azure tenant to investigate

**Example Invoice Fields:**
```
Invoice Number: G133682474
Billing Period: 12/01/2025 - 12/31/2025
Total Amount: USD 177.68
Primary Tenant ID: ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd
```

#### 6.2 Identify Tenant and Subscription

1. Match the Tenant ID to known tenants:

| Tenant Name | Tenant ID |
|-------------|-----------|
| OberaConnect | ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd |
| SetcoServices | 7cf9e47b-84ff-4248-914f-8d8c70947e3b |

2. If tenant is unknown, check the billing portal link in the invoice:
   - `portal.azure.com` = Standard Azure subscription
   - `admin.microsoft.com` = Azure tied to M365 billing

#### 6.3 Authenticate to Azure CLI

1. Open terminal and authenticate to the specific tenant:
```bash
az login --tenant <TENANT_ID>
```

2. If browser doesn't open (WSL/headless), use device code:
```bash
az login --tenant <TENANT_ID> --use-device-code
```

3. Verify authentication and subscription:
```bash
az account show
```

**Expected Output:**
```json
{
  "name": "Azure subscription 1",
  "id": "f64eae77-b917-4083-ae4e-f25dce921fdf",
  "tenantId": "ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd",
  "state": "Enabled"
}
```

#### 6.4 Enumerate All Resources

1. List all resources in the subscription:
```bash
az resource list --output table
```

2. Group resources by type for analysis:
```bash
az resource list --query "[].{Name:name, Type:type, RG:resourceGroup, Location:location}" --output table
```

#### 6.5 Check Virtual Machine Status

VMs are typically the largest cost driver. Check their status:

1. List all VMs with power state:
```bash
az vm list -d --output table
```

2. Get details on a specific VM:
```bash
az vm show -g <RESOURCE_GROUP> -n <VM_NAME> \
  --query "{Size:hardwareProfile.vmSize, OS:storageProfile.osDisk.osType, DiskSizeGB:storageProfile.osDisk.diskSizeGb}" \
  --output table
```

**Key Fields:**
- **PowerState**: `VM running` = incurring charges, `VM deallocated` = no compute charges
- **Size**: VM SKU determines hourly cost (e.g., Standard_E2ads_v6)
- **PublicIps**: Static IPs incur networking charges

#### 6.6 Map Resources to Invoice Categories

Cross-reference discovered resources with invoice line items:

| Invoice Category | Azure Resource Types |
|------------------|---------------------|
| **Compute** | Virtual Machines, App Services, Functions, Container Instances |
| **Storage** | Storage Accounts, Managed Disks, Backup Vaults |
| **Networking** | Public IPs, VPN Gateways, Load Balancers, Bandwidth/Egress, Application Gateways |
| **Data Services** | SQL Databases, Cosmos DB, Redis Cache |
| **Management** | Log Analytics, Network Watcher, Recovery Services |

#### 6.7 Detailed Cost Analysis (Portal)

For granular cost breakdown:

1. Navigate to **Azure Portal** > **Cost Management + Billing**
2. Select the subscription
3. Click **Cost analysis**
4. Set date range to match invoice billing period
5. Group by:
   - **Resource** - See cost per individual resource
   - **Service name** - See cost by service category
   - **Resource group** - See cost by logical grouping

#### 6.8 Common Cost Drivers

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| High Compute costs | VMs running 24/7 | Implement auto-shutdown schedules |
| High Networking costs | VPN Gateway, Public IPs, egress | Review bandwidth usage, consolidate IPs |
| Unexpected Storage costs | Backup retention, orphaned disks | Clean up unattached disks, adjust retention |
| Growing costs month-over-month | Resource sprawl | Implement tagging and resource governance |

---

### 7.0 Verification & Quality Checks

- [ ] Tenant ID from invoice matches authenticated tenant
- [ ] All resources are accounted for
- [ ] VM power states are documented
- [ ] Cost categories map to discovered resources
- [ ] Findings documented for client communication

### 8.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| `az login` fails with "Application not found" | Azure CLI service principal not in tenant. Run in Cloud Shell: `az rest --method POST --url "https://graph.microsoft.com/v1.0/servicePrincipals" --body '{"appId": "04b07795-8ddb-461a-bbee-02f9e1bf7b46"}'` |
| Cannot determine Tenant ID from invoice | Check Account Information on page 2-3 of invoice PDF, or log into billing portal |
| VM shows "deallocated" but charges persist | Check for Premium disks (charged even when VM stopped) and static Public IPs |
| Networking charges unexpectedly high | Check for VPN Gateway ($100+/month), Application Gateway, or high egress bandwidth |
| `az resource list` returns empty | Verify correct subscription is selected: `az account set --subscription <SUBSCRIPTION_ID>` |

### 9.0 Related Documents

| Document | Description |
|----------|-------------|
| SOP-AZ-001 | Azure VM Administration |
| SOP-AZ-002 | Azure VPN SonicWall Site-to-Site |
| [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) | Estimate resource costs |
| [Azure Cost Management](https://docs.microsoft.com/azure/cost-management-billing/) | Microsoft documentation |

### 10.0 Revision History

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-01-12 | Jeremy Smith | Initial document creation |

### 11.0 Approval

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | Technical Lead | | |
| | Operations Manager | | |
