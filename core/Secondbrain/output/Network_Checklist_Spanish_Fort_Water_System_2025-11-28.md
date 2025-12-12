# Network Installation Checklist
## Customer: Spanish Fort Water System

**Date Created:** 2025-11-19
**Last Updated:** 2025-12-01
**Project Manager:** Jeremy Smith
**Site Address:** 30686 Driftwood Lane, Spanish Fort, AL 36527
**Contact:**  |  |

---

## Project Overview

### Current Network
- **ISP:** (via ASUS Router)
- **Internet Speed:** (To be verified)
- **Number of Users:** 54-56
- **Estimated Devices:** 18 total (14 Location #1 + 4 Location #2)
- **Network Range:** 192.168.1.0/24 (both locations)
- **Locations:** 3 sites total

### Existing Equipment
- **Router/Firewall:** ASUS WRT (192.168.1.1) - Consumer-grade
- **Switches:** Netgear GS748T 48-port Managed (192.168.1.123)
- **Access Points:** (To be identified) 

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

## Network Scan Results (December 1, 2025)

### Location #1 - Main Office (14 devices)

| IP Address | Hostname | Device Type | Manufacturer |
|------------|----------|-------------|--------------|
| 192.168.1.1 | router.asus.com | Router | ASUSTek |
| 192.168.1.23 | SFWS-PC-RVS | Windows PC | Dell |
| 192.168.1.45 | Counter | Windows PC | Dell |
| 192.168.1.46 | JONDA | Printer | Epson ET-5800 |
| 192.168.1.60 | EPSON7C6ACF | Printer | Epson ET-5800 |
| 192.168.1.98 | W60B | VoIP Base | Yealink |
| 192.168.1.112 | - | VoIP Device | Yealink |
| 192.168.1.123 | - | Switch | Netgear GS748T |
| 192.168.1.128 | Spanish-Fort-AL-SCC | Server | Dell |
| 192.168.1.134 | - | Security Panel | DMP |
| 192.168.1.160 | SFWS-PC24-JONDA | Windows PC | Dell |
| 192.168.1.181 | SFWS-PC-Tanya | Windows PC | Dell |
| 192.168.1.240 | - | Unknown | Arcadyan |

### Location #2 - Secondary Site (4 devices)

| IP Address | Hostname | Device Type | Manufacturer |
|------------|----------|-------------|--------------|
| 192.168.1.1 | router.asus.com | Router | ASUSTek |
| 192.168.1.13 | EPSON834441 | Printer | Epson ET-5800 |
| 192.168.1.166 | Jason-s-Z-Fold6 | Mobile | Samsung |
| 192.168.1.253 | NucBox_K8 | Mini PC | Gaoshengda |

### Key Findings
**Location #1:**
- 4 Windows Workstations (Dell) with standard Windows services
- 2 Epson Printers with HTTP/SMB/Print services
- 2 Yealink VoIP Devices (W60B DECT base + handset)
- 1 Netgear GS748T Managed Switch - Good for VLAN support
- 1 DMP Security Panel (port 2001)
- 1 Dell Server (Spanish-Fort-AL-SCC) on ports 8000/8080

**Location #2:**
- 1 ASUS Router with PowerDNS Recursor 5.1.7
- 1 Epson ET-5800 Printer (WiFi connected to SEWSWH5)
- 1 NucBox_K8 Mini PC (all ports filtered - good security)
- Smaller attack surface with only 4 devices

### Security Observations
1. ASUS consumer routers at both locations - replace with SonicWall
2. SMB services active on workstations - verify SMBv1 disabled
3. VoIP SIP on unencrypted port 5060 at Location #1
4. Multiple HTTP admin interfaces exposed at both locations
5. Location #2 Mini PC has proper firewall enabled (ports filtered)

---

## Phase 1: Network Discovery & Assessment

### Initial Site Survey
- [x] Schedule on-site or virtual discovery session with customer
  - **Scheduled: 11/30/2025**
- [x] Document current network topology
  - [x] Identify existing network devices (routers, switches, APs)
    - **Completed 12/1/2025 - See scan results above**
  - [x] Map IP addressing scheme and VLAN structure
    - **Current: 192.168.1.0/24 - No VLANs configured**
  - [ ] Document internet connection type and bandwidth
  - [x] Identify critical systems and devices
    - **Server: 192.168.1.128, Security: 192.168.1.134**
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
- [x] Document security gaps and vulnerabilities
  - **Completed 12/1/2025 - See Security Observations above**
- [x] Identify single points of failure
  - **Single ASUS router is gateway, no redundancy**
- [ ] Review backup and redundancy needs

### Documentation Deliverables
- [x] Create network diagram (current state)
  - **See Network Scan Report 2025-12-01**
- [x] Document findings report
  - **Network_Scan_Report_Spanish_Fort_Waterboard_2025-12-01.md**

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
