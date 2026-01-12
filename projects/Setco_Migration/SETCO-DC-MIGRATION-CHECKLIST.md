# Setco Domain Controller Migration Checklist
## Azure Tenant to Tenant Migration - SouthernEscrow.com

---

## Migration Overview
- **Domain:** SouthernEscrow.com
- **NetBIOS Name:** SOUTHERN
- **Original Domain SID:** S-1-5-21-117609710-1303643608-725345543
- **Migration Type:** DC from old Azure tenant to new Azure tenant
- **Data Drive:** F:\ (not E:\)

---

## Phase 1: Pre-Migration Planning & Assessment

### 1.1 Documentation & Discovery
- [ ] Document current DC server name and IP address
- [ ] Document all FSMO roles on current DC
- [ ] List all DNS zones hosted on current DC
- [ ] Document all GPOs and their links
- [ ] List all OU structure
- [ ] Document DFS namespaces and replication topology (if applicable)
- [ ] List all service accounts and their purposes
- [ ] Document DHCP scopes (if DC is also DHCP server)
- [ ] List all SSL certificates installed on DC
- [ ] Document current backup schedule and retention
- [ ] Record all scheduled tasks on current DC
- [ ] List applications that authenticate against this DC

### 1.2 Active Directory Health Check
- [ ] Run `dcdiag /v` on current DC - save output
- [ ] Run `repadmin /showrepl` - verify replication health
- [ ] Check Event Viewer for critical errors (last 7 days)
- [ ] Verify DNS is functioning: `dcdiag /test:dns`
- [ ] Check AD database integrity: `ntdsutil` files integrity check
- [ ] Verify SYSVOL replication is healthy
- [ ] Check for orphaned objects: `repadmin /removelingeringobjects`
- [ ] Verify time synchronization across domain
- [ ] Document current forest/domain functional level
- [ ] Verify no AD replication errors in last 24 hours

### 1.3 User & Group Inventory
- [ ] Export list of all users: `Get-ADUser -Filter * | Export-Csv users.csv`
- [ ] Export list of all groups: `Get-ADGroup -Filter * | Export-Csv groups.csv`
- [ ] Export group memberships for critical groups (Domain Admins, etc.)
- [ ] Document service accounts and their passwords (secure location)
- [ ] List disabled user accounts
- [ ] Document users with "Password Never Expires"
- [ ] Export computer accounts list
- [ ] Verify all user home directories exist and are accessible

### 1.4 Network & Infrastructure Assessment
- [ ] Document current DNS server settings on DC
- [ ] Document DNS forwarders configuration
- [ ] List all DNS A records for servers
- [ ] Document all SRV records for domain services
- [ ] Verify network connectivity to new Azure tenant
- [ ] Document firewall rules for DC traffic (ports 53, 88, 135, 389, 445, 636, 3268, 3269)
- [ ] Plan IP addressing for new DC
- [ ] Document current VPN/ExpressRoute configuration
- [ ] Test network latency between tenants
- [ ] Document current DC's network adapter settings

### 1.5 File Share Documentation
- [ ] List all current SMB shares: `Get-SmbShare`
- [ ] Export share permissions for each share
- [ ] Export NTFS permissions for all shared folders
- [ ] Document share paths and mapped drive letters
- [ ] Calculate total data size on F:\ drive
- [ ] Identify shares with special requirements (DFS, ABE, etc.)
- [ ] Document printer shares
- [ ] List all administrative shares
- [ ] Verify SYSVOL and NETLOGON share health

### 1.6 Dependencies & Integration Points
- [ ] List all applications that use LDAP/AD authentication
- [ ] Document email system integration (Exchange, O365)
- [ ] List all federated applications (ADFS, Azure AD Connect)
- [ ] Document MFA/conditional access policies
- [ ] List all third-party integrations (monitoring, backup, etc.)
- [ ] Document any custom LDAP queries or scripts
- [ ] Check for Azure AD Connect sync status
- [ ] Verify all client computers' DNS settings
- [ ] Document VPN server AD dependencies

---

## Phase 2: New Azure Tenant Preparation

### 2.1 Azure Infrastructure Setup
- [ ] Provision new Azure subscription in target tenant
- [ ] Create Resource Group for DC infrastructure
- [ ] Create Virtual Network with proper subnetting
- [ ] Configure Network Security Groups (NSG) for DC traffic
- [ ] Set up Azure Bastion or VPN for management access
- [ ] Configure Azure DNS or custom DNS as needed
- [ ] Plan and configure ExpressRoute/VPN between tenants (if needed)
- [ ] Set up Azure Backup vault for DC backups
- [ ] Configure Azure Site Recovery (if using for DR)
- [ ] Set up monitoring (Azure Monitor, Log Analytics)

### 2.2 New DC Virtual Machine Provisioning
- [ ] Create new Windows Server VM (2019 or 2022 recommended)
- [ ] Size VM appropriately (min: 2 vCPU, 4GB RAM for small domain)
- [ ] Attach F:\ data disk with adequate size
- [ ] Configure VM for accelerated networking
- [ ] Set static IP address on VM
- [ ] Configure DNS to point to itself (after promotion)
- [ ] Join VM to time service (time.windows.com or domain PDC emulator)
- [ ] Install all Windows Updates
- [ ] Configure Windows Firewall for DC traffic
- [ ] Disable IE Enhanced Security Configuration

### 2.3 Windows Server Configuration
- [ ] Set computer name (document new name)
- [ ] Configure timezone correctly
- [ ] Disable IPv6 (if not used)
- [ ] Configure power settings (High Performance, never sleep)
- [ ] Set page file to system-managed on C:\
- [ ] Install AD DS and DNS server roles
- [ ] Install RSAT tools for management
- [ ] Configure antivirus exclusions for AD
  - C:\Windows\NTDS
  - C:\Windows\SYSVOL
  - NTDS.dit file
  - AD database and log files
- [ ] Verify F:\ drive is online and formatted (NTFS)

---

## Phase 3: Domain Migration Strategy Decision

### 3.1 Choose Migration Approach

**Option A: Same Domain Migration (Recommended if domain SID must be preserved)**
- [ ] Decision: Migrate existing domain to new tenant
- [ ] Method: Backup/Restore or Replication approach
- [ ] Timeline: ___________________
- [ ] Downtime window: ___________________

**Option B: New Domain Creation (If creating fresh domain)**
- [ ] Decision: Create new domain with same name
- [ ] Plan user migration approach (ADMT or manual)
- [ ] Plan computer re-joining to new domain
- [ ] Timeline: ___________________
- [ ] Downtime window: ___________________

**Option C: Hybrid Approach (Temporary cross-tenant trust)**
- [ ] Decision: Set up VPN between tenants
- [ ] Create additional DC in new tenant
- [ ] Replicate AD between tenants
- [ ] Migrate gradually
- [ ] Timeline: ___________________

**Selected Approach:** _______________________

---

## Phase 4: Domain Controller Promotion

### 4.1 Promote New DC (Option A: Adding to Existing Domain)
- [ ] Establish VPN/ExpressRoute connectivity between tenants
- [ ] Configure DNS to resolve existing domain
- [ ] Run `dcpromo` or Install-ADDSDomainController
- [ ] Verify replication with existing DC
- [ ] Check replication status: `repadmin /replsummary`
- [ ] Verify SYSVOL replication
- [ ] Check DNS registration
- [ ] Verify all AD sites and services configuration
- [ ] Test authentication against new DC
- [ ] Monitor Event Viewer for errors

### 4.2 Promote New DC (Option B: New Forest/Domain)
- [ ] Run `Install-ADDSForest` to create new domain
- [ ] Configure domain name: SouthernEscrow.com
- [ ] Set NetBIOS name: SOUTHERN
- [ ] Set Forest/Domain functional level
- [ ] Configure DNS settings
- [ ] Verify SYSVOL creation
- [ ] Create initial OU structure
- [ ] Verify NETLOGON and SYSVOL shares exist
- [ ] Check DNS zones are created
- [ ] Configure DNS forwarders

### 4.3 Post-Promotion Verification
- [ ] Verify DC is advertising correctly: `dcdiag /test:Advertising`
- [ ] Check DNS registrations: `ipconfig /registerdns`
- [ ] Verify LDAP connectivity: `ldp.exe` test
- [ ] Test Kerberos: `klist purge` then authenticate
- [ ] Verify SYSVOL share: `\\servername\SYSVOL`
- [ ] Check NETLOGON share: `\\servername\NETLOGON`
- [ ] Verify Group Policy replication
- [ ] Test user authentication
- [ ] Check Event Viewer: Directory Services log
- [ ] Verify time synchronization

---

## Phase 5: FSMO Role Transfer

### 5.1 Verify Current FSMO Roles
- [ ] Document current FSMO role holders:
  ```powershell
  netdom query fsmo
  ```
  - Schema Master: ___________________
  - Domain Naming Master: ___________________
  - RID Master: ___________________
  - PDC Emulator: ___________________
  - Infrastructure Master: ___________________

### 5.2 Transfer FSMO Roles (if applicable)
- [ ] Transfer Schema Master role
- [ ] Transfer Domain Naming Master role
- [ ] Transfer RID Master role
- [ ] Transfer PDC Emulator role
- [ ] Transfer Infrastructure Master role
- [ ] Verify all roles transferred successfully: `netdom query fsmo`
- [ ] Test time synchronization (PDC emulator should sync with external source)
- [ ] Verify RID pool allocation is working
- [ ] Check for FSMO role seizure in Event Viewer

---

## Phase 6: File Share Migration

### 6.1 Pre-Migration File Share Checks
- [ ] Verify F:\ drive is available and has adequate space
- [ ] Check current share usage and quotas
- [ ] Test file copy/migration tool (Robocopy, Storage Migration Service)
- [ ] Document share dependencies (applications, scripts, mapped drives)
- [ ] Plan migration timing (low-usage window)
- [ ] Notify users of planned migration window

### 6.2 Run File Share Migration Scripts
- [ ] Transfer scripts to C:\ps1 on new DC:
  - 1-Setup-Directories-F-Drive.ps1
  - 2-Set-NTFS-Permissions-F-Drive.ps1
  - 3-Create-SMB-Shares-F-Drive.ps1
  - 4-Validate-Configuration-F-Drive.ps1

- [ ] Open PowerShell as Administrator
- [ ] Navigate to C:\ps1
- [ ] Set execution policy: `Set-ExecutionPolicy RemoteSigned -Scope Process`

- [ ] **Script 1: Create Directories**
  ```powershell
  .\1-Setup-Directories-F-Drive.ps1
  ```
  - [ ] Verify all directories created successfully
  - [ ] Check for any errors in output
  - [ ] Verify F:\ drive has all folders

- [ ] **Script 2: Set NTFS Permissions**
  ```powershell
  .\2-Set-NTFS-Permissions-F-Drive.ps1
  ```
  - [ ] Review confirmation prompt
  - [ ] Press key to continue
  - [ ] Monitor for SID resolution warnings
  - [ ] Verify permissions applied without critical errors
  - [ ] Check for unresolved SIDs

- [ ] **Script 3: Create SMB Shares**
  ```powershell
  .\3-Create-SMB-Shares-F-Drive.ps1
  ```
  - [ ] Verify all 11 data shares created
  - [ ] Check share permissions are set
  - [ ] Note printer shares (configure separately)
  - [ ] Verify NETLOGON and SYSVOL shares exist

- [ ] **Script 4: Validate Configuration**
  ```powershell
  .\4-Validate-Configuration-F-Drive.ps1
  ```
  - [ ] All directories show [OK]
  - [ ] All shares show [OK]
  - [ ] Directories Missing: 0
  - [ ] Shares Missing: 0
  - [ ] Review permissions summary
  - [ ] Check for SID warnings

### 6.3 Data Migration
- [ ] Copy data from old DC to new DC F:\ drive
  ```powershell
  robocopy \\olddc\sharename F:\sharename /E /COPYALL /DCOPY:T /R:3 /W:5 /MT:8 /LOG:migration.log
  ```
- [ ] Verify file counts match source
- [ ] Spot-check file integrity
- [ ] Verify folder permissions preserved
- [ ] Check migration log for errors
- [ ] Test file access from client workstation
- [ ] Verify special permissions (deny entries, inheritance)
- [ ] Check for long path issues (>260 characters)

### 6.4 Share Validation
- [ ] Test access to each share from client PC: `\\newdc\sharename`
- [ ] Verify read permissions work
- [ ] Verify write permissions work
- [ ] Test with different user accounts (different permission levels)
- [ ] Verify home directories are accessible
- [ ] Check QuickBooks share (Qbooks) - critical application share
- [ ] Verify Legal share access (limited users)
- [ ] Test PostClosing share for PostClosers group
- [ ] Verify printer shares functionality (Print Management)
- [ ] Check DFS namespace if applicable

---

## Phase 7: DNS Configuration

### 7.1 DNS Zone Configuration
- [ ] Verify Active Directory integrated zones are created
- [ ] Check forward lookup zone for SouthernEscrow.com
- [ ] Verify reverse lookup zones
- [ ] Check DNS zone replication scope
- [ ] Verify SOA and NS records
- [ ] Configure DNS forwarders (8.8.8.8, 1.1.1.1, or ISP)
- [ ] Set up conditional forwarders (if needed)
- [ ] Verify SRV records for domain services:
  - _ldap._tcp.dc._msdcs.SouthernEscrow.com
  - _kerberos._tcp.dc._msdcs.SouthernEscrow.com
  - _ldap._tcp.SouthernEscrow.com

### 7.2 DNS Client Configuration
- [ ] Update DHCP scope to point to new DC IP for DNS
- [ ] Or manually update client DNS settings (if static)
- [ ] Verify DNS resolution from clients: `nslookup SouthernEscrow.com`
- [ ] Test reverse DNS lookups
- [ ] Flush DNS cache on clients: `ipconfig /flushdns`
- [ ] Verify clients can resolve internal resources
- [ ] Check DNS scavenging settings
- [ ] Configure DNS aging if needed

---

## Phase 8: Group Policy Migration

### 8.1 Group Policy Verification
- [ ] Open Group Policy Management Console (GPMC)
- [ ] Verify all GPOs replicated to new DC
- [ ] Check SYSVOL replication status
- [ ] Run GP Modeling on test computer
- [ ] Verify GP links are preserved
- [ ] Check GP permissions (delegation)
- [ ] Test GPO application on test computer: `gpupdate /force`
- [ ] Review GPO settings for hard-coded paths (update if needed)
- [ ] Verify WMI filters
- [ ] Check for broken GPO links

### 8.2 Group Policy Testing
- [ ] Create test OU and apply test GPO
- [ ] Verify GPO applies to test computer
- [ ] Check `gpresult /r` output on test machine
- [ ] Verify logon scripts execute
- [ ] Test drive mappings from GPO
- [ ] Verify printer deployments via GPO
- [ ] Check software deployment policies
- [ ] Test password policies
- [ ] Verify security filtering works

---

## Phase 9: User Migration & Validation (If New Domain)

### 9.1 User Account Migration (If Creating New Domain)
- [ ] Decide migration method: ADMT or manual recreation
- [ ] Create all OUs in new domain matching old structure
- [ ] Recreate groups with same names
- [ ] Create user accounts with same usernames:
  - [ ] Administrator
  - [ ] PJarvis
  - [ ] gbrannon
  - [ ] GBrannonjr
  - [ ] kcouvillion
  - [ ] datatrustinc
  - [ ] oberaconnect
  - [ ] JMFSolutions
  - [ ] lsavio
  - [ ] setcoadmin
  - [ ] wgibson
  - [ ] oc-michael.mccool
  - [ ] kyork
  - [ ] mhelms
  - [ ] Tmarsh
  - [ ] Bdeweese
  - [ ] bbuege
  - [ ] cgeiselman
  - [ ] cbrooks
  - [ ] kmcdonald
  - [ ] oc-theresa.gilbert
  - [ ] ktoolan
  - [ ] mbrannon
  - [ ] mhudson-2
  - [ ] brookebrannon

- [ ] Create PostClosers security group
- [ ] Assign users to appropriate groups
- [ ] Set password policies
- [ ] Configure user account properties (email, phone, etc.)
- [ ] Set home directory paths
- [ ] Configure profile paths (if using roaming profiles)

### 9.2 SID Validation (If Same Domain)
- [ ] Verify domain SID matches original: `Get-ADDomain | Select-Object DomainSID`
- [ ] Expected: S-1-5-21-117609710-1303643608-725345543
- [ ] If SID differs, run SID translation helper script
- [ ] Check for unresolved SIDs in file permissions
- [ ] Verify user RIDs match original (if possible)
- [ ] Test user authentication with new SID
- [ ] Check service accounts can authenticate

---

## Phase 10: Client Computer Migration

### 10.1 DNS Update for Clients
- [ ] Update DHCP to provide new DC IP as DNS server
- [ ] Or update static DNS on each client manually
- [ ] Verify clients register with new DNS
- [ ] Test domain connectivity: `nltest /dsgetdc:SouthernEscrow.com`
- [ ] Verify Kerberos tickets: `klist tickets`

### 10.2 Client Computer Testing
- [ ] Test user login on pilot workstation
- [ ] Verify group policy applies: `gpresult /r`
- [ ] Test mapped drives
- [ ] Verify access to file shares
- [ ] Test printer connections
- [ ] Check application authentication (Outlook, LOB apps)
- [ ] Verify roaming profile loads (if applicable)
- [ ] Test VPN connectivity
- [ ] Verify time synchronization with DC

### 10.3 Computer Re-joining (If New Domain)
- [ ] Create computer objects in new domain
- [ ] Remove computers from old domain
- [ ] Join computers to new domain
- [ ] Move computers to correct OUs
- [ ] Verify computer group policy applies
- [ ] Migrate user profiles (if needed)
- [ ] Reconfigure local admin accounts

---

## Phase 11: Application & Service Integration

### 11.1 Email Integration
- [ ] Update Exchange (if on-prem) to use new DC for GC
- [ ] Update Office 365 Azure AD Connect settings (if used)
- [ ] Verify Autodiscover is working
- [ ] Test Outlook connectivity
- [ ] Verify GAL lookups work
- [ ] Check calendar sharing
- [ ] Test mail flow

### 11.2 Line of Business Applications
- [ ] Update QuickBooks server/client configuration
- [ ] Verify database connections use DNS names (not IPs)
- [ ] Test application authentication
- [ ] Update application service accounts (if needed)
- [ ] Verify SQL Server authentication (if Windows auth used)
- [ ] Test web applications using AD auth
- [ ] Check SharePoint integration (if applicable)

### 11.3 Third-Party Integrations
- [ ] Update monitoring tools (PRTG, Nagios, etc.)
- [ ] Reconfigure backup software for new DC
- [ ] Update antivirus management console
- [ ] Verify patch management system connectivity
- [ ] Update help desk software AD integration
- [ ] Check MFA provider integration
- [ ] Verify SSO/SAML applications

---

## Phase 12: Security & Compliance

### 12.1 Security Validation
- [ ] Run security compliance scan: `gpresult /h security.html`
- [ ] Verify audit policies are applied
- [ ] Check security event logging is working
- [ ] Verify account lockout policy
- [ ] Test password complexity requirements
- [ ] Check privileged account usage
- [ ] Verify LAPS is working (if deployed)
- [ ] Review firewall rules on DC
- [ ] Check antivirus exclusions are configured
- [ ] Verify BitLocker status (if used)

### 12.2 Backup Configuration
- [ ] Configure Windows Server Backup for system state
- [ ] Set up Azure Backup for DC VM
- [ ] Configure backup for F:\ drive data
- [ ] Test system state backup
- [ ] Test file-level restore
- [ ] Document backup schedule and retention
- [ ] Test AD authoritative restore procedure (in lab if possible)
- [ ] Verify backup logs and alerts
- [ ] Store backup credentials securely

### 12.3 Monitoring & Alerts
- [ ] Configure performance monitoring (CPU, RAM, Disk)
- [ ] Set up NTDS database size alerts
- [ ] Configure replication failure alerts
- [ ] Set up Event Log monitoring for critical events
- [ ] Configure disk space alerts for C:\ and F:\
- [ ] Set up service monitoring (DNS, NTDS, NETLOGON, etc.)
- [ ] Configure network connectivity monitoring
- [ ] Set up backup job failure alerts

---

## Phase 13: Cutover & Decommissioning

### 13.1 Final Pre-Cutover Checks
- [ ] Verify all testing completed successfully
- [ ] Confirm user acceptance testing (UAT) passed
- [ ] Schedule cutover window with stakeholders
- [ ] Send notification to all users about cutover
- [ ] Prepare rollback plan
- [ ] Document all configuration changes
- [ ] Take final backup of old DC
- [ ] Take snapshot of new DC VM

### 13.2 Cutover Execution
- [ ] Update DNS records to point to new DC
- [ ] Update DHCP to provide new DC as DNS server
- [ ] Update VPN server to authenticate against new DC
- [ ] Update firewall rules to allow traffic to new DC
- [ ] Disable replication from old DC (if multi-DC scenario)
- [ ] Monitor user logins to new DC
- [ ] Monitor Event Viewer for errors
- [ ] Verify all services are operational

### 13.3 Old DC Decommissioning (After Successful Cutover)
- [ ] Verify no clients are connecting to old DC
- [ ] Wait minimum 2 weeks for monitoring period
- [ ] Transfer any remaining FSMO roles
- [ ] Demote old DC: `Uninstall-ADDSDomainController`
- [ ] Verify metadata cleanup: `ntdsutil`
- [ ] Remove old DC from DNS
- [ ] Remove old DC computer object from AD
- [ ] Update documentation with new DC information
- [ ] Archive old DC VM (don't delete immediately)
- [ ] Update disaster recovery procedures
- [ ] Cancel old Azure subscription (after 30-day grace period)

---

## Phase 14: Post-Migration Validation

### 14.1 30-Day Post-Migration Checklist
- [ ] Review Event Viewer logs for recurring errors
- [ ] Verify replication health (if multi-DC)
- [ ] Check AD database size and growth
- [ ] Review backup success rate
- [ ] Verify all users can authenticate
- [ ] Check file share access logs
- [ ] Review Group Policy application
- [ ] Verify DNS resolution is working correctly
- [ ] Check for orphaned SIDs in file permissions
- [ ] Test disaster recovery procedures

### 14.2 User Satisfaction Survey
- [ ] Survey users about login experience
- [ ] Check for file access issues
- [ ] Verify mapped drives are working
- [ ] Confirm printer access
- [ ] Check application performance
- [ ] Gather feedback on any issues

### 14.3 Performance Baseline
- [ ] Document CPU utilization average
- [ ] Record memory usage baseline
- [ ] Document disk I/O performance
- [ ] Record network throughput
- [ ] Baseline AD replication time
- [ ] Document user login time average

---

## Phase 15: Documentation & Knowledge Transfer

### 15.1 Updated Documentation
- [ ] Server build document with new DC specs
- [ ] Network diagram with new DC IP and location
- [ ] AD topology diagram
- [ ] DNS zone configuration document
- [ ] Group Policy documentation
- [ ] File share permissions matrix
- [ ] Backup and recovery procedures
- [ ] Disaster recovery runbook
- [ ] Service account inventory with purposes
- [ ] Firewall rules documentation

### 15.2 Knowledge Transfer
- [ ] Train IT staff on new environment
- [ ] Document common troubleshooting procedures
- [ ] Create runbook for routine maintenance
- [ ] Document escalation procedures
- [ ] Update help desk knowledge base
- [ ] Create admin password vault entries

---

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| Primary IT Contact | _____________ | _____________ | _____________ |
| Azure Administrator | _____________ | _____________ | _____________ |
| Network Administrator | _____________ | _____________ | _____________ |
| Security Team | _____________ | _____________ | _____________ |
| Microsoft Support | _____________ | _____________ | _____________ |

---

## Rollback Plan

### If Migration Fails:
1. [ ] Revert DNS settings to old DC
2. [ ] Revert DHCP settings
3. [ ] Re-enable old DC services
4. [ ] Verify users can authenticate to old DC
5. [ ] Document failure cause
6. [ ] Schedule post-mortem meeting

---

## Sign-Off

| Phase | Completed By | Date | Signature |
|-------|--------------|------|-----------|
| Pre-Migration | _____________ | ______ | _____________ |
| DC Promotion | _____________ | ______ | _____________ |
| File Share Migration | _____________ | ______ | _____________ |
| Client Migration | _____________ | ______ | _____________ |
| Final Cutover | _____________ | ______ | _____________ |
| Post-Migration | _____________ | ______ | _____________ |

---

## Notes & Issues Log

| Date | Issue | Resolution | By |
|------|-------|------------|-----|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Maintained By:** IT Department
**Next Review Date:** After Migration Completion
