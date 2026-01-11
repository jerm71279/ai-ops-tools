# 5-Phase High-Level Action Items
## From Network Installation Interactive Checklist

**Source:** network_install_workflow_interactive.html
**Date:** 2025-11-17
**Purpose:** Quick reference extracted directly from the interactive checklist

---

## PHASE 1: NETWORK DISCOVERY & ASSESSMENT
### → Onsite Pre-sales

### Initial Site Survey
1. Schedule on-site or virtual discovery session with customer
2. Document current network topology
   - Identify existing network devices (routers, switches, APs)
   - Map IP addressing scheme and VLAN structure
   - Document internet connection type and bandwidth
   - Identify critical systems and devices
3. Assess physical infrastructure
   - Evaluate existing cabling (Cat5e/6, fiber)
   - Check rack space availability
   - Identify mounting locations for access points
   - Verify power availability (PoE requirements, UPS)
4. Gather business requirements
   - Number of users and devices
   - Bandwidth requirements per department/function
   - Guest network requirements
   - Security and compliance requirements

### Network Analysis
5. Conduct wireless site survey (if applicable)
   - Identify RF interference sources
   - Determine AP placement and quantity
   - Plan channel allocation
6. Analyze traffic patterns and bottlenecks
7. Document security gaps and vulnerabilities
8. Identify single points of failure
9. Review backup and redundancy needs

### Documentation Deliverables
10. Create network diagram (current state)
11. Document findings report

---

## PHASE 2: RECOMMENDATION & DESIGN
### → After Phase 1, before SOW Quote

### Device Recommendations
1. Select router/firewall platform
   - Model and specifications
   - Throughput requirements
2. Create proposed network topology diagram

### Design Documentation
3. Define IP addressing and VLAN scheme
   - Management VLAN
   - User/data VLANs
   - Voice VLAN
   - Guest VLAN
   - IoT/security VLAN
4. Plan wireless network architecture
   - SSID naming and security
   - AP coverage map
5. Design security policies
   - Firewall rules
   - Access control lists
   - Guest portal requirements
6. Plan redundancy and failover
7. Develop naming conventions for devices

---

## PHASE 3: PRE-CONFIGURATION & PREPARATION
### → After Quote is Signed

### Pre-Configuration
1. Create configuration templates
   - Router/firewall base config
   - Switch base config
   - AP base config
2. Configure devices in lab/staging environment
   - Set management IPs
   - Configure VLANs and trunking (if needed)
   - Apply security policies
   - Set up wireless controller and SSIDs
   - Configure monitoring/management access
3. Test configurations
   - Verify connectivity
   - Test VLAN routing
   - Validate security rules
   - Check wireless functionality
4. Document all configurations
5. Create device labels with IP addresses

### Installation Planning
6. Schedule installation date/time with customer
7. Coordinate downtime window (if required)
8. Assign installation team roles
9. Brief team on installation plan

---

## PHASE 4: INSTALLATION DAY
### → On-site Install

### Configuration & Cutover
1. Connect to each device and verify config
2. Upload final configurations
3. Establish internet connectivity
4. Configure and test inter-VLAN routing
5. Verify wireless network operation
6. Test connectivity from each VLAN
7. Migrate devices to new network (if applicable)
8. Update DHCP scopes and DNS settings

### Testing & Validation
9. Test internet connectivity from all VLANs
10. Verify wireless coverage and performance
11. Test guest network isolation
12. Validate firewall rules
13. Check VPN connectivity (if applicable)
14. Test failover/redundancy mechanisms
15. Verify critical applications are accessible
16. Run speed tests from multiple locations
17. Test roaming between APs

---

## PHASE 5: POST-INSTALLATION & HANDOFF

### Monitoring & Optimization
1. Configure network monitoring
   - Set up SNMP monitoring
   - Configure alerts and notifications
   - Enable logging
2. Add devices to management platform
   - NinjaOne/RMM integration
   - Network management controller
3. Monitor for first 24-48 hours
   - Check for errors or warnings
   - Optimize wireless channels if needed
   - Adjust QoS policies

### Project Closeout
4. Conduct final walkthrough with customer
5. Obtain customer sign-off
6. Document lessons learned
7. Schedule 30-day follow-up review
8. Package all documentation for handoff
9. Update customer records in PSA/CRM

---

## ONGOING MAINTENANCE (Post-Install)

### Regular Tasks
1. Weekly monitoring review
2. Monthly bandwidth utilization analysis
3. Quarterly firmware updates
4. Quarterly security policy review

### Support & Optimization
1. Monitor alert notifications
2. Review and address issues proactively
3. Track network growth and capacity needs
4. Plan for future expansion
5. Maintain current documentation
6. Schedule annual customer review

---

## 📊 PHASE SUMMARY

| Phase | Task Count | Key Focus |
|-------|------------|-----------|
| **Phase 1** | 11 items | Discovery & Assessment |
| **Phase 2** | 7 items | Design & Recommendation |
| **Phase 3** | 9 items | Pre-Config & Planning |
| **Phase 4** | 17 items | Installation & Testing |
| **Phase 5** | 9 items | Handoff & Monitoring |
| **Ongoing** | 10 items | Maintenance & Support |

**Total:** 63 actionable items across complete lifecycle

---

## ✅ CRITICAL SUCCESS FACTORS

### Must Complete (No Skip):
- ✓ Wireless site survey (if WiFi deployment)
- ✓ Lab/staging testing before install
- ✓ Test all VLANs and security rules
- ✓ Verify wireless coverage (minimum -67dBm)
- ✓ Test guest network isolation
- ✓ Configure monitoring before handoff
- ✓ Obtain customer sign-off
- ✓ Complete documentation package

### Quality Standards:
- **Wireless:** Minimum -67dBm signal strength
- **Testing:** 100% of VLANs and security rules validated
- **Documentation:** Network diagram + configs + credentials
- **Monitoring:** All devices in NinjaOne before closeout

---

**Document Version:** 1.0 (Direct from Interactive Checklist)
**Last Updated:** 2025-11-17
**Source:** network_install_workflow_interactive.html
