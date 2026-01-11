# 5-Phase High-Level Action Items
## Network Installation Customer Lifecycle Process

**Date:** 2025-11-17
**Version:** 2.0 Enhanced
**Purpose:** Quick reference guide for high-level actions at each phase

---

## PHASE 1: NETWORK DISCOVERY & ASSESSMENT
### Onsite Pre-Sales

### High-Level Action Items:

1. **Schedule Discovery Session**
   - Contact customer to schedule meeting
   - Prepare site survey checklist and tools

2. **Document Current Network & Requirements**
   - Identify existing network devices (SonicWall, MikroTik, UniFi)
   - Map IP addressing scheme and VLAN structure
   - Document internet connection and bandwidth
   - Identify critical systems and devices
   - 📋 **Complete Technical Requirements Checklist**
   - 📋 **Complete Compliance Requirements Checklist**

3. **Assess Physical Infrastructure**
   - Evaluate existing cabling (Cat5e/6, fiber)
   - Check rack space availability
   - Identify AP mounting locations
   - Verify power availability (PoE requirements, UPS)

4. **Gather Business Requirements**
   - Number of users and devices
   - Bandwidth requirements per department
   - Guest network requirements
   - Security and compliance requirements

5. **Conduct Wireless Site Survey** (if applicable)
   - Use UniFi WiFiman app for RF survey
   - **Target: Minimum -67dBm signal strength**
   - Determine AP placement and quantity
   - Plan channel allocation
   - 📋 **Complete Wireless Site Survey Report**

6. **Analyze Traffic Patterns**
   - Current bandwidth utilization
   - Identify bottlenecks
   - QoS requirements

7. **Document Security Gaps**
   - Audit current firewall rules
   - Review existing security policies
   - Identify vulnerabilities

8. **Identify Single Points of Failure**
   - Document critical dependencies
   - Backup internet connection needs
   - Redundant gateway requirements

9. **Create Network Diagram (Current State)**
   - Document existing topology
   - Show all devices and connections
   - 📋 **Deliverable: Current State Network Diagram**

10. **Document Findings Report**
    - Site survey summary
    - Current state assessment
    - Identified issues and risks
    - 📋 **Deliverable: Discovery Findings Report**

### Key Deliverables:
- ✅ Technical Requirements Checklist
- ✅ Compliance Requirements Checklist
- ✅ Wireless Site Survey Report (if applicable)
- ✅ Current State Network Diagram
- ✅ Discovery Findings Report

### Quality Gate: None (discovery phase)

---

## PHASE 2: RECOMMENDATION & DESIGN
### After Discovery, Before SOW Quote

### High-Level Action Items:

1. **Select Core Router/Firewall**
   - Evaluate SonicWall (TZ/NSa/NSsp series)
   - Evaluate MikroTik (hEX S/CCR series)
   - Evaluate UniFi Gateway (UDM/UDM-Pro/UXG)
   - Consider throughput, features, budget
   - 📋 **Create Technology Selection Summary**

2. **Design VLAN & IP Addressing Scheme**
   - **Management VLAN:** VLAN 10 (10.x.10.0/24)
   - **User/Data VLANs:** VLAN 20+ (department-based)
   - **Voice VLAN:** VLAN 30 (10.x.30.0/24) - if VoIP
   - **Guest VLAN:** VLAN 40 (10.x.40.0/24) - isolated
   - **IoT/Security VLAN:** VLAN 50 (10.x.50.0/24)
   - 📋 **Create IP Addressing & VLAN Scheme Spreadsheet**

3. **Plan Wireless Network Architecture** (if applicable)
   - SSID naming and security (WPA3/WPA2)
   - AP coverage map with floor plan
   - Minimum -67dBm signal strength target
   - Channel plan and overlap for roaming

4. **Design Security Policies**
   - Firewall rules (zone-based)
   - Access control lists
   - Guest portal requirements (UniFi customization)
   - VPN requirements
   - 📋 **Complete Security Policy Design Checklist**

5. **Plan Redundancy and Failover**
   - Dual WAN failover (SonicWall/MikroTik)
   - Switch stacking (UniFi redundancy)
   - Power redundancy (dual PSU, UPS)
   - UniFi controller backup

6. **Develop Naming Conventions**
   - Location-Type-Number format (e.g., HQ-SW-01)
   - Consistent across all platforms

7. **Create Proposed Network Topology Diagram**
   - Include all recommended devices
   - Show VLAN segmentation
   - Indicate redundancy paths
   - Label all connections and ports
   - 📋 **Deliverable: Proposed Network Topology**

8. **⭐ Customer Design Review Meeting**
   - Present proposed topology diagram
   - Review VLAN design and IP scheme
   - Explain security policies
   - Walk through wireless coverage map
   - Review project timeline
   - Answer questions

9. **🚦 QUALITY GATE 1: Customer Design Approval**
   - **Approval Required:** Sales Manager + Customer
   - **Criteria:** Customer understands and approves design
   - 📋 **Deliverable: Design Approval Document (signed)**

10. **Create Quote in OneBill**
    - All equipment and licensing
    - Labor and installation
    - Project timeline
    - Terms and conditions

### Key Deliverables:
- ✅ Technology Selection Summary
- ✅ IP Addressing & VLAN Scheme Spreadsheet
- ✅ Security Policy Design Document
- ✅ Proposed Network Topology Diagram
- ✅ **Design Approval Document (Customer Signed)** ⭐

### Quality Gate:
🚦 **Gate 1 - Customer Design Approval** (Sales + Customer sign-off)

---

## PHASE 3: PRE-CONFIGURATION & PREPARATION
### After Quote Signed, Before Installation

### High-Level Action Items:

1. **Equipment Procurement**
   - Billing issues NRC invoice
   - VP Plant purchases equipment
   - Validate receipts and categorize in QBO
   - Equipment delivered and received

2. **Inventory Management**
   - Add equipment to SmartSheets as "Assigned/Pending Install"
   - Verify all equipment received and correct

3. **Communicate with Carrier**
   - Obtain Estimated Completion Date (ECD)
   - Obtain Firm Order Commitment (FOC)
   - Receive IP information
   - Update Circuit Inventory SmartSheet

4. **Create Configuration Templates**
   - SonicWall base configuration (zones, NAT, VPN, IPS)
   - MikroTik base configuration (firewall, DHCP, DNS)
   - UniFi configuration (VLANs, WiFi, firewall rules)

5. **Configure Devices in Lab Environment**
   - Set management IPs on all devices
   - Configure VLANs and trunking
   - Apply security policies
   - Set up wireless controller and SSIDs
   - Configure monitoring/management access (SNMP, syslog)

6. **Lab Testing & Validation**
   - Test internet connectivity
   - Verify VLAN routing
   - Test wireless SSIDs
   - Validate security rules
   - Test VPN connectivity (if applicable)
   - Document performance baseline
   - 📋 **Complete Pre-Config Test Report**

7. **Create Configuration Backups**
   - Export SonicWall configuration
   - Save MikroTik .rsc backup
   - Backup UniFi site
   - Store all configs in password vault/SharePoint

8. **🚦 QUALITY GATE 2: Pre-Configuration Validation**
   - **Approval Required:** Engineering Lead
   - **Criteria:** Lab testing passed, equipment ready
   - 📋 **Deliverable: Pre-Config Test Report (passed)**

9. **Schedule Installation**
   - Confirm date/time with customer
   - Confirm team availability
   - Update Outlook Support Calendar
   - Update OneBill ticket with install date
   - 📋 **Complete Installation Readiness Checklist**

10. **⭐ Customer Pre-Install Briefing**
    - Confirm installation timeline
    - Confirm downtime window (if any)
    - Send user notification
    - Designate on-site contact
    - Set post-install expectations

11. **Day Before Install: Final Checklist**
    - Review project checklist
    - Confirm all equipment and materials loaded
    - Confirm team ready
    - Verify site access arrangements

### Key Deliverables:
- ✅ Equipment ordered, received, inventoried
- ✅ Configuration templates created
- ✅ All devices pre-configured
- ✅ **Pre-Config Test Report (passed)** 📋
- ✅ Configuration backups stored
- ✅ Installation Readiness Checklist completed

### Quality Gate:
🚦 **Gate 2 - Pre-Configuration Validation** (Engineering Lead approval)

---

## PHASE 4: INSTALLATION DAY
### On-Site Install

### High-Level Action Items:

1. **Physical Installation**
   - Rack mount equipment
   - Run and terminate cabling
   - Mount access points
   - Connect power (PoE, UPS)
   - Apply device labels with IPs

2. **Configure & Cutover**
   - Connect to each device and verify config
   - Upload final configurations
   - Establish internet connectivity
   - Configure inter-VLAN routing
   - Verify wireless network operation

3. **Test Connectivity from Each VLAN**
   - Management VLAN
   - User/Data VLANs
   - Voice VLAN (VoIP phones)
   - Guest VLAN (internet-only)
   - IoT/Security VLAN

4. **Migrate Devices to New Network** (if applicable)
   - Workstations
   - Printers
   - VoIP phones
   - Servers and static IP devices
   - Test application connectivity

5. **Update DHCP and DNS**
   - Configure DHCP scopes on UniFi/MikroTik
   - Set DHCP reservations for servers/printers
   - Configure DNS forwarding
   - Test DHCP assignments

6. **Comprehensive Testing & Validation**
   - **Network Connectivity:**
     - ✓ Internet verified from all VLANs
     - ✓ DNS resolution tested
     - ✓ DHCP functioning on all VLANs

   - **Wireless Validation** (if applicable):
     - ✓ All APs online and broadcasting
     - ✓ **Signal strength ≥ -67dBm in all coverage areas**
     - ✓ Roaming between APs tested
     - ✓ Guest portal functionality verified

   - **Security Validation:**
     - ✓ Firewall rules tested (allow/deny)
     - ✓ Guest network isolation confirmed
     - ✓ VPN connectivity tested (if configured)

   - **Performance Testing:**
     - ✓ Speed tests from multiple locations
     - ✓ Baseline performance documented
     - ✓ Critical applications tested

7. **🚦 QUALITY GATE 3: Installation QA**
   - **Approval Required:** Lead Technician + OPM
   - **Criteria:** 100% QA checklist passed
   - 📋 **Complete Installation QA Report**

8. **Documentation**
   - Upload close-out pictures to SharePoint
   - Upload cable certifications to SharePoint
   - Update inventory to "Installed" in SmartSheets
   - Update network diagram with any changes (as-built)

9. **Validate Against Contract**
   - Confirm all work complete per contract
   - Document any punch-list items
   - Verify all deliverables provided

10. **⭐ Customer Installation Walkthrough**
    - Demonstrate network functionality
    - Show WiFi coverage and speeds
    - Review security features
    - Explain user access methods
    - Provide admin credentials (via secure method)
    - Answer customer questions

11. **🚦 QUALITY GATE 4: Customer Handoff**
    - **Approval Required:** Customer
    - **Criteria:** Customer satisfied, walkthrough complete
    - 📋 **Obtain Customer Installation Sign-Off**

### Key Deliverables:
- ✅ Physical installation complete
- ✅ **Installation QA Report (100% passed)** 📋
- ✅ Close-out pictures uploaded to SharePoint
- ✅ Cable certifications uploaded to SharePoint
- ✅ As-built network diagram updated
- ✅ **Installation Completion Certificate (Customer Signed)** ⭐

### Quality Gates:
🚦 **Gate 3 - Installation QA** (Lead Tech + OPM approval)
🚦 **Gate 4 - Customer Handoff** (Customer sign-off)

---

## PHASE 5: POST-INSTALLATION & HANDOFF
### Final Handoff & Ongoing Support Setup

### High-Level Action Items:

1. **Configure Network Monitoring**
   - Enable SNMP v2c/v3 on all devices
   - Set up monitoring in NinjaOne RMM
   - Configure email alerts (SonicWall, UniFi, MikroTik)
   - Enable syslog forwarding
   - Set log retention periods
   - Test alert delivery

2. **Add Devices to Management Platform**
   - Add all devices to NinjaOne RMM
   - Configure SNMP monitoring
   - Set up device health checks
   - Configure automated alerts
   - Ensure UniFi controller accessible
   - Set up automatic backups

3. **Prepare Customer Documentation Package**
   - **Technical Documentation:**
     - As-built network diagram
     - IP address spreadsheet
     - VLAN documentation
     - WiFi network details (SSIDs, passwords)
     - Equipment list with serial numbers
     - Warranty/license expiration dates

   - **Configuration Backups:**
     - Firewall/router configuration export
     - Switch configuration backups
     - Wireless controller backup

   - **Support Information:**
     - Admin credentials (in password vault)
     - Support contact information
     - Escalation procedures
     - Monitoring/alerting setup confirmation

4. **Deliver Documentation Package**
   - Upload all documentation to customer SharePoint folder
   - Notify customer of documentation availability
   - 📋 **Deliverable: Customer Documentation Package**

5. **Billing & Financial Closeout**
   - OPM assigns ticket to Billing Manager for MRC
   - Billing Manager establishes invoice for MRC
   - Update QBO with recurring billing

6. **Customer Onboarding**
   - Move client into Marketing Pipeline in HubSpot
   - Send Onboarding + CSAT Survey
   - Log CSAT data to customer profile in HubSpot

7. **Monitor for First 24-48 Hours**
   - Check for errors or warnings
   - Review SonicWall, UniFi, MikroTik logs
   - Optimize wireless channels if needed
   - Adjust QoS policies if needed

8. **Project Closeout**
   - Reassign ticket to OPM for closeout
   - Complete all OneBill ticket notes
   - Archive project documentation
   - Update customer records in PSA/CRM

9. **⭐ Schedule 30-Day Follow-Up Review**
   - Schedule review meeting with customer
   - Review any outstanding issues
   - Check network performance
   - Gather additional feedback
   - Make any necessary adjustments
   - Document lessons learned

10. **Ongoing Maintenance Setup**
    - Schedule quarterly network health checks
    - Schedule annual customer review
    - Set up firmware update schedule
    - Plan for capacity monitoring

### Key Deliverables:
- ✅ Monitoring & alerting configured
- ✅ All devices added to NinjaOne RMM
- ✅ **Customer Documentation Package delivered** 📋
- ✅ MRC billing established
- ✅ CSAT survey completed
- ✅ 30-Day Follow-Up scheduled

### Quality Gate: None (ongoing support)

---

## ONGOING: MAINTENANCE & SUPPORT
### Post-Install Continuous Improvement

### High-Level Action Items:

1. **⭐ 30-Day Follow-Up Review**
   - Meet with customer
   - Address any outstanding issues
   - Review network performance
   - Gather feedback
   - Make necessary adjustments

2. **Quarterly Network Health Checks**
   - Review monitoring alerts and logs
   - Check firmware versions (security patches)
   - Verify backup configurations exist
   - Review bandwidth utilization trends
   - Test failover mechanisms
   - Update documentation as needed

3. **Weekly Monitoring Review**
   - Review NinjaOne RMM alerts
   - Check SonicWall security logs
   - Review UniFi insights and anomalies
   - Monitor bandwidth utilization
   - Address warnings proactively

4. **Schedule Firmware Updates**
   - SonicWall firmware updates (test → production)
   - MikroTik RouterOS updates (stable branch)
   - UniFi firmware updates (staged rollout)
   - Test updates in off-hours
   - Maintain firmware version documentation

5. **Review Security Policies Quarterly**
   - Review SonicWall firewall rules
   - Audit MikroTik access control
   - Review UniFi firewall groups
   - Update security policies
   - Check for security vulnerabilities

6. **Monitor Network Growth and Capacity**
   - Track bandwidth trends
   - Track user/device growth
   - Review UniFi insights for capacity
   - Identify bottlenecks
   - Plan for expansion

7. **Update Documentation as Changes Occur**
   - Update network diagrams
   - Document configuration changes
   - Update IP address spreadsheet
   - Maintain device inventory
   - Keep firmware versions current

8. **⭐ Annual Customer Review**
   - Schedule review meeting
   - Present performance report
   - Review incidents and resolutions
   - Discuss improvement opportunities
   - Plan for next year
   - Recommend upgrades/enhancements
   - **Identify upsell opportunities**

### Key Deliverables:
- ✅ 30-Day Follow-Up completed
- ✅ Quarterly health checks completed
- ✅ Security policies reviewed and updated
- ✅ Documentation kept current
- ✅ Annual customer review completed
- ✅ Capacity planning recommendations

### Quality Gate: None (ongoing relationship)

---

## 🎯 SUMMARY: Critical Success Factors

### Quality Gates (Must Pass):
1. 🚦 **Gate 1:** Customer Design Approval (Phase 2)
2. 🚦 **Gate 2:** Pre-Config Validation (Phase 3)
3. 🚦 **Gate 3:** Installation QA - 100% Pass (Phase 4)
4. 🚦 **Gate 4:** Customer Handoff Sign-Off (Phase 4)

### Customer Touchpoints (Must Complete):
1. ⭐ Customer Design Review Meeting (Phase 2)
2. ⭐ Customer Pre-Install Briefing (Phase 3)
3. ⭐ Customer Installation Walkthrough (Phase 4)
4. ⭐ Customer Installation Sign-Off (Phase 4)
5. ⭐ 30-Day Follow-Up Review (Phase 5)
6. ⭐ Annual Customer Review (Ongoing)

### Critical Standards:
- **Wireless Signal Strength:** ≥ -67dBm minimum in all areas
- **VLAN Standard:** VLANs 10, 20, 30, 40, 50 (consistent scheme)
- **Lab Testing:** 100% of equipment tested before on-site
- **Installation QA:** 100% checklist pass rate
- **Documentation:** Complete package delivered within 7 days

### Key Metrics to Track:
- Installation QA Pass Rate (Target: 100%)
- Rework Rate (Target: <5%)
- CSAT Score (Target: ≥4.5/5.0)
- 30-Day Issues (Target: <2 per install)
- Documentation Completion (Target: 100%)

---

## 📊 PHASE TIMELINE ESTIMATES

| Phase | Duration | Effort | Critical Path |
|-------|----------|--------|---------------|
| **Phase 1:** Discovery & Assessment | 1-2 weeks | 8-16 hours | Site survey scheduling |
| **Phase 2:** Recommendation & Design | 1-2 weeks | 12-24 hours | Multi-team SOW development |
| **Phase 3:** Pre-Config & Prep | 2-4 weeks | 16-32 hours | Equipment delivery |
| **Phase 4:** Installation Day | 1-3 days | 16-40 hours | Customer availability |
| **Phase 5:** Post-Install & Handoff | 1 week | 4-8 hours | Documentation completion |
| **Ongoing:** Maintenance | Continuous | Variable | Scheduled touchpoints |

**Total Project Duration:** 8-16 weeks (initial meeting to go-live)

---

**Document Version:** 2.0
**Last Updated:** 2025-11-17
**Next Review:** After first 3 enhanced projects completed
