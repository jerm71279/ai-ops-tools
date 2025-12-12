# Network Installation Workflow Checklist

## Phase 1: Network Discovery & Assessment

### Initial Site Survey
- [ ] Schedule on-site or virtual discovery session with customer
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
- [ ] Define IP addressing and VLAN scheme
  - [ ] Management VLAN
  - [ ] User/data VLANs
  - [ ] Voice VLAN
  - [ ] Guest VLAN
  - [ ] IoT/security VLAN
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

### Equipment Receipt and Registration
- [ ] Verify all equipment received and matches order
- [ ] Check for physical damage during shipping
- [ ] Document serial numbers for all devices
- [ ] Register SonicWall device in MySonicWall portal
- [ ] Register UniFi devices in UniFi account (if applicable)
- [ ] Activate warranty and support contracts
- [ ] Verify firmware versions

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
  - [ ] Enable remote management for security remote access
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
