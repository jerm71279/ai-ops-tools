# Network Installation Checklist
## Customer: City of Spanish Fort

**Date Created:** 2025-11-19
**Project Manager:** Jeremy Smith
**Site Address:** 30686 Driftwood Lane, Spanish Fort, AL 36527
**Contact:**  |  | 

---

## Project Overview

### Current Network
- **ISP:** 
- **Internet Speed:** 
- **Number of Users:** 54-56
- **Estimated Devices:** 

### Existing Equipment
- **Router/Firewall:** ISP
- **Switches:** 
- **Access Points:** 

### Requirements
- **VLANs Needed:** Data, Voice, Guest, IoT, Security
- **Guest Network:** Yes
- **VoIP:** Yes
- **VPN:** No

### Recommended Equipment
- **Router/Firewall:** SonicWall TZ
- **Switches:** Ubiquity 24 port POE
- **Access Points:** Ubiquiti UniFi

### Notes
IT Contractor: Computer Backup, Inc. Site survey completed Oct 10, 2024.

---

## Phase 1: Network Discovery & Assessment

### Initial Site Survey
- [x] Schedule on-site or virtual discovery session with customer
  - **Scheduled: 11/30/2025**
- [ ] Document current network topology
  - [ ] Identify existing network devices (routers, switches, APs)
  - [ ] Map IP addressing scheme and VLAN structure
  - [ ] Document internet connection type and bandwidth
  - [ ] Identify critical systems and devices
- [ ] Assess physical infrastructure
  - [ ] Evaluate existing cabling (Cat5e/6, fiber)
  - [ ] Check rack space availability
  - [ ] Identify mounting locations for access points
  - [ ] Verify power availability (PoE requirements, UPS)
- [ ] Gather business requirements
  - [ ] Number of users and devices
  - [ ] Bandwidth requirements per department/function
  - [ ] Guest network requirements
  - [ ] Security and compliance requirements

### Network Analysis
- [ ] Conduct wireless site survey (if applicable)
  - [ ] Identify RF interference sources
  - [ ] Determine AP placement and quantity
  - [ ] Plan channel allocation
- [ ] Analyze traffic patterns and bottlenecks
- [ ] Document security gaps and vulnerabilities
- [ ] Identify single points of failure
- [ ] Review backup and redundancy needs

### Documentation Deliverables
- [ ] Create network diagram (current state)
- [ ] Document findings report

---

## Phase 2: Recommendation & Design

### Device Recommendations
- [ ] **Core Router/Firewall**
  - [ ] Model and specifications
  - [ ] Throughput requirements

### Design Documentation
- [ ] Create proposed network topology diagram
- [x] Define IP addressing scheme
  - [x] Native VLAN: **10.55.0.0/24** (Gateway: 10.55.0.1)
  - [ ] Reserved for expansion: 10.55.1.0/24, 10.55.2.0/24, 10.55.3.0/24
- [ ] Plan VLAN structure (if needed - determine during discovery)
- [ ] Plan wireless network architecture
  - [ ] SSID naming and security
  - [ ] AP coverage map
- [ ] Design security policies
  - [ ] Firewall rules
  - [ ] Access control lists
  - [ ] Guest portal requirements
- [ ] Plan redundancy and failover
- [ ] Develop naming conventions for devices

---

## Phase 3: Pre-Configuration & Preparation

### Pre-Configuration
- [ ] Create configuration templates
  - [ ] Router/firewall base config
  - [ ] Switch base config
  - [ ] AP base config
- [ ] Configure devices in lab/staging environment
  - [ ] Set management IPs
  - [ ] Configure VLANs and (trunking if needed)
  - [ ] Apply security policies
  - [ ] Set up wireless controller and SSIDs
  - [ ] Configure monitoring/management access
- [ ] Test configurations
  - [ ] Verify connectivity
  - [ ] Test VLAN routing
  - [ ] Validate security rules
  - [ ] Check wireless functionality
- [ ] Document all configurations
- [ ] Create device labels with IP addresses

### Installation Planning
- [ ] Schedule installation date/time with customer
- [ ] Coordinate downtime window (if required)
- [ ] Assign installation team roles
- [ ] Brief team on installation plan

---

## Phase 4: Installation Day

### Configuration & Cutover
- [ ] Connect to each device and verify config
- [ ] Upload final configurations
- [ ] Establish internet connectivity
- [ ] Configure and test inter-VLAN routing
- [ ] Verify wireless network operation
- [ ] Test connectivity from each VLAN
- [ ] Migrate devices to new network (if applicable)
- [ ] Update DHCP scopes and DNS settings

### Testing & Validation
- [ ] Test internet connectivity from all VLANs
- [ ] Verify wireless coverage and performance
- [ ] Test guest network isolation
- [ ] Validate firewall rules
- [ ] Check VPN connectivity (if applicable)
- [ ] Test failover/redundancy mechanisms
- [ ] Verify critical applications are accessible
- [ ] Run speed tests from multiple locations
- [ ] Test roaming between APs

---

## Phase 5: Post-Installation & Handoff (Hand off to IT Services?)

### Monitoring & Optimization
- [ ] Configure network monitoring
  - [ ] Set up SNMP monitoring
  - [ ] Configure alerts and notifications
  - [ ] Enable logging
- [ ] Add devices to management platform
  - [ ] NinjaOne/RMM integration
  - [ ] Network management controller
- [ ] Monitor for first 24-48 hours
  - [ ] Check for errors or warnings
  - [ ] Optimize wireless channels if needed
  - [ ] Adjust QoS policies

### Project Closeout
- [ ] Conduct final walkthrough with customer
- [ ] Obtain customer sign-off
- [ ] Document lessons learned
- [ ] Schedule 30-day follow-up review
- [ ] Package all documentation for handoff
- [ ] Update customer records in PSA/CRM
- [ ] Close project in project management system

---

## Ongoing Maintenance (Post-Install)

### Regular Tasks
- [ ] Schedule firmware updates
- [ ] Review monitoring alerts weekly
- [ ] Conduct quarterly network health checks
- [ ] Update documentation as changes occur
- [ ] Review security policies quarterly

### Support & Optimization
- [ ] Monitor network growth and capacity
- [ ] Adjust configurations as needed
- [ ] Plan for future expansion
- [ ] Schedule annual network review with customer
