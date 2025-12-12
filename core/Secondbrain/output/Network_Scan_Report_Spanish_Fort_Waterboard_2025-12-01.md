# Network Scan Report
## Spanish Fort Waterboard
### Date: December 1, 2025

---

## Executive Summary

A comprehensive network assessment was conducted at Spanish Fort Waterboard on December 1, 2025. Two separate locations were scanned:

- **Location #1 (Main Office)**: 14 hosts discovered - workstations, printers, VoIP, network infrastructure, security systems
- **Location #2 (Secondary Site)**: 4 hosts discovered - router, printer, mini PC, mobile device

Both locations use the same 192.168.1.0/24 subnet but are separate networks with different routers.

---

## Network Overview

### Location #1 - Main Office

| Item | Value |
|------|-------|
| **Network Range** | 192.168.1.0/24 |
| **Gateway/Router** | 192.168.1.1 (ASUS Router - MAC: 4C:ED:FB:AD:3D:88) |
| **Total Hosts Discovered** | 14 |
| **Scan Date** | December 1, 2025 |
| **Scan Type** | Full Assessment (Discovery + Standard + Intensive) |

### Location #2 - Secondary Site

| Item | Value |
|------|-------|
| **Network Range** | 192.168.1.0/24 |
| **Gateway/Router** | 192.168.1.1 (ASUS Router - MAC: 18:31:BF:5E:A5:70) |
| **Total Hosts Discovered** | 4 |
| **Scan Date** | December 1, 2025 |
| **Scan Type** | Discovery + Standard |

---

## Discovered Hosts Summary

### Location #1 - Main Office (14 hosts)

| IP Address | Hostname | Device Type | Manufacturer |
|------------|----------|-------------|--------------|
| 192.168.1.1 | router.asus.com | Router/Firewall | ASUSTek Computer |
| 192.168.1.23 | SFWS-PC-RVS | Windows PC | Dell |
| 192.168.1.45 | Counter | Windows PC | Dell |
| 192.168.1.46 | JONDA | Printer | Seiko Epson |
| 192.168.1.60 | EPSON7C6ACF | Printer | Seiko Epson |
| 192.168.1.98 | W60B | VoIP Base Station | Yealink |
| 192.168.1.112 | (unnamed) | VoIP Device | Yealink |
| 192.168.1.123 | (unnamed) | Network Switch | Netgear GS748T |
| 192.168.1.128 | Spanish-Fort-AL-SCC | Server/System | Dell |
| 192.168.1.134 | (unnamed) | Security Panel | Digital Monitoring Products |
| 192.168.1.160 | SFWS-PC24-JONDA | Windows PC | Dell |
| 192.168.1.181 | SFWS-PC-Tanya | Windows PC | Dell |
| 192.168.1.240 | (unnamed) | Unknown Device | Arcadyan |

### Location #2 - Secondary Site (4 hosts)

| IP Address | Hostname | Device Type | Manufacturer |
|------------|----------|-------------|--------------|
| 192.168.1.1 | router.asus.com | Router/Firewall | ASUSTek Computer |
| 192.168.1.13 | EPSON834441 | Printer | Seiko Epson |
| 192.168.1.166 | Jason-s-Z-Fold6 | Mobile Phone | Unknown |
| 192.168.1.253 | NucBox_K8 | Mini PC | Hui Zhou Gaoshengda |

---

## Device Categories - Location #1 (Main Office)

### Network Infrastructure (2 devices)
- **192.168.1.1** - ASUS Router (Gateway)
  - Services: DNS (53), HTTP Admin (80), Printer (515), JetDirect (9100)
  - DNS: Akamai Vantio CacheServe 7.7.3.0.d

- **192.168.1.123** - Netgear GS748T Managed Switch
  - Services: HTTP Config (80)

### Windows Workstations (4 devices)
- **192.168.1.23** - SFWS-PC-RVS (Dell)
  - Services: RPC (135), NetBIOS (139), SMB (445), UPnP (5357)

- **192.168.1.45** - Counter (Dell)
  - Services: RPC (135), NetBIOS (139), SMB (445), UPnP (5357)

- **192.168.1.160** - SFWS-PC24-JONDA (Dell)
  - Services: RPC (135), NetBIOS (139), SMB (445), UPnP (5357)

- **192.168.1.181** - SFWS-PC-Tanya (Dell)
  - Services: UPnP (5357)

### Printers (2 devices)

#### 192.168.1.46 - JONDA (Epson ET-5800)
| Field | Value |
|-------|-------|
| **Model** | Epson ET-5800 Series |
| **Device Name** | JONDA |
| **MAC Address** | DC:CD:2F:85:8B:D4 |
| **Wi-Fi Direct MAC** | DE:CD:2F:85:0B:D4 |
| **Firmware** | 04.18.KD21P5 (E1.1930.0001/001CC816) |
| **IP Address** | 192.168.1.46 (DHCP) |
| **Subnet Mask** | 255.255.255.0 |
| **Gateway** | 192.168.1.1 |
| **DNS** | 192.168.1.1 (Auto) |
| **Connection** | Ethernet - 100BASE-TX Full Duplex |
| **WiFi** | Off |
| **IPv6** | fe80::decd:2fff:fe85:8bd4/64 (Link Local) |
| **Services** | HTTP (80), HTTPS (443), SMB (139/445), LPD (515), IPP (631), JetDirect (9100) |

#### 192.168.1.60 - EPSON7C6ACF (Epson ET-5800)
| Field | Value |
|-------|-------|
| **Model** | Epson ET-5800 Series |
| **Device Name** | EPSON7C6ACF |
| **MAC Address** | DC:CD:2F:7C:6A:CF |
| **Wi-Fi Direct MAC** | DE:CD:2F:7C:EA:CF |
| **Firmware** | 04.18.KD21P5 (E1.1930.0001/001CC816) |
| **IP Address** | 192.168.1.60 (DHCP) |
| **Subnet Mask** | 255.255.255.0 |
| **Gateway** | 192.168.1.1 |
| **DNS** | 192.168.1.1 (Auto) |
| **Connection** | Ethernet - 100BASE-TX Full Duplex |
| **WiFi** | Off |
| **IPv6** | Disabled |
| **Services** | HTTP (80), HTTPS (443), SMB (139/445), LPD (515), IPP (631), JetDirect (9100) |

**Printer Notes:**
- Both printers are identical Epson ET-5800 EcoTank models with same firmware
- Both using DHCP - consider static IP reservations for stability
- IEEE 802.3az (Energy Efficient Ethernet) enabled on both

### VoIP/Phone System (2 devices)
- **192.168.1.98** - W60B (Yealink DECT Base)
  - Services: HTTP (80), HTTPS (443), SIP (5060)
  - Firmware: 77.83.0.25

- **192.168.1.112** - Yealink Device
  - Services: HTTP (80), HTTPS (443)

### Servers/Special Systems (2 devices)
- **192.168.1.128** - Spanish-Fort-AL-SCC (Dell)
  - Services: HTTP (8000, 8080) - Embedthis HTTP lib
  - Likely: Server or control system

- **192.168.1.134** - Digital Monitoring Products
  - Services: Unknown (2001)
  - Type: Security/Alarm Panel

### Other Devices (1 device)
- **192.168.1.240** - Arcadyan Device
  - Services: Unknown (3000)

---

## Device Categories - Location #2 (Secondary Site)

### Network Infrastructure (1 device)
- **192.168.1.1** - ASUS Router (Gateway)
  - MAC: 18:31:BF:5E:A5:70
  - Services: DNS (53), HTTP Admin (80), WAN Monitor (18017)
  - DNS: PowerDNS Recursor 5.1.7

### Printers (1 device)

#### 192.168.1.13 - EPSON834441 (Epson ET-5800)
| Field | Value |
|-------|-------|
| **Model** | Epson ET-5800 Series |
| **Device Name** | EPSON834441 |
| **MAC Address** | DC:CD:2F:83:44:41 |
| **Wi-Fi Direct MAC** | DE:CD:2F:83:C4:41 |
| **Firmware** | 04.18.KD21P5 (E1.1930.0001) |
| **IP Address** | 192.168.1.13 (DHCP) |
| **Subnet Mask** | 255.255.255.0 |
| **Gateway** | 192.168.1.1 |
| **DNS** | 192.168.1.1 (Auto) |
| **Connection** | WiFi - Infrastructure Mode |
| **WiFi SSID** | SEWSWH5 |
| **WiFi Channel** | 153 (IEEE802.11a/n/ac) |
| **WiFi Security** | WPA2-PSK (AES) |
| **WiFi Speed** | Auto (150Mbps) |
| **Signal Strength** | Excellent |
| **Access Point MAC** | 18:31:BF:5E:A5:74 |
| **IPv6** | fe80::decd:2fff:fe83:4441/64 (Link Local) |
| **Wi-Fi Direct IP** | 172.16.10.1/24 |
| **Services** | HTTP (80), HTTPS (443), SMB (139/445), LPD (515), IPP (631), JetDirect (9100) |

**Printer Notes:**
- WiFi connected (not Ethernet like Location #1 printers)
- Same ET-5800 model and firmware as Location #1 printers
- Connected to access point 18:31:BF:5E:A5:74 (different from router MAC)
- Wi-Fi Direct available but no devices connected

### Computers (1 device)
- **192.168.1.253** - NucBox_K8 (Mini PC)
  - MAC: 4C:50:DD:9B:26:82
  - Manufacturer: Hui Zhou Gaoshengda Technology
  - Services: All ports filtered (firewall enabled - good security posture)

### Mobile Devices (1 device)
- **192.168.1.166** - Jason-s-Z-Fold6
  - MAC: FE:8E:B8:AE:35:62
  - Type: Samsung Galaxy Z Fold6 (mobile phone)
  - Services: All ports filtered

---

## Open Ports Summary

### Location #1 - Main Office

| Port | Service | Protocol | Hosts |
|------|---------|----------|-------|
| 53 | DNS | TCP | 192.168.1.1 |
| 80 | HTTP | TCP | 192.168.1.1, .46, .60, .98, .112, .123 |
| 135 | RPC | TCP | 192.168.1.23, .45, .160 |
| 139 | NetBIOS | TCP | 192.168.1.23, .45, .46, .60, .160 |
| 443 | HTTPS | TCP | 192.168.1.46, .60, .98, .112 |
| 445 | SMB | TCP | 192.168.1.23, .45, .46, .60, .160 |
| 515 | LPD | TCP | 192.168.1.1, .46, .60 |
| 631 | IPP | TCP | 192.168.1.46, .60 |
| 2001 | Unknown | TCP | 192.168.1.134 |
| 3000 | Unknown | TCP | 192.168.1.240 |
| 5060 | SIP | TCP | 192.168.1.98 |
| 5357 | UPnP | TCP | 192.168.1.23, .45, .160, .181 |
| 8000 | HTTP | TCP | 192.168.1.128 |
| 8080 | HTTP | TCP | 192.168.1.128 |
| 9100 | JetDirect | TCP | 192.168.1.1, .46, .60 |

### Location #2 - Secondary Site

| Port | Service | Protocol | Hosts |
|------|---------|----------|-------|
| 53 | DNS | TCP | 192.168.1.1 |
| 80 | HTTP | TCP | 192.168.1.1, .13 |
| 139 | NetBIOS | TCP | 192.168.1.13 |
| 443 | HTTPS | TCP | 192.168.1.13 |
| 445 | SMB | TCP | 192.168.1.13 |
| 515 | LPD | TCP | 192.168.1.13 |
| 631 | IPP | TCP | 192.168.1.13 |
| 9100 | JetDirect | TCP | 192.168.1.13 |
| 18017 | WAN Monitor | TCP | 192.168.1.1 |

---

## Security Observations

### Location #1 - Main Office

### Critical Findings
1. **Router Admin Interface Exposed (192.168.1.1:80)**
   - ASUS WRT admin interface accessible on the network
   - Additional ports found: 1990, 3394, 3838, 5473, 7788, 18017 (WAN monitor)
   - Recommendation: Ensure strong admin credentials, consider restricting access

2. **SMB Services on Multiple Hosts**
   - Windows file sharing active on workstations and printers
   - **SMB signing "enabled but not required"** on Windows hosts - security weakness
   - Recommendation: Enforce SMB signing, disable SMBv1 if present

3. **Unencrypted VoIP SIP (192.168.1.98:5060)**
   - SIP traffic on TCP/5060 may be unencrypted
   - **SIP TLS (5061) available** - can enable encrypted communications
   - Recommendation: Configure SIP over TLS

4. **Splashtop Remote Access (192.168.1.23:6783)**
   - Remote desktop software detected on SFWS-PC-RVS
   - Recommendation: Verify this is authorized and properly secured

### Moderate Findings
5. **Multiple HTTP Management Interfaces**
   - Printers, switches, and VoIP devices have web interfaces
   - Recommendation: Ensure all have strong passwords, consider HTTPS-only

6. **Security Panel (192.168.1.134)**
   - Digital Monitoring Products device with unknown service on port 2001
   - Recommendation: Verify this is properly segmented/protected

7. **SCC Server (192.168.1.128)**
   - Dell server running Embedthis HTTP on ports 8000/8080
   - Appears to be a control system - verify access controls

### Low Findings
8. **Network Printer Protocols**
   - JetDirect (9100), LPD (515), and IPP (631) exposed
   - Epson proprietary service on port 1865
   - Standard for printers, ensure printing is restricted to authorized hosts

9. **Windows Delivery Optimization (192.168.1.45:7680)**
   - P2P update service on Counter PC - normal for Windows 10/11

### Location #2 - Secondary Site

### Moderate Findings
1. **Router Admin Interface Exposed (192.168.1.1:80)**
   - ASUS WRT admin interface accessible
   - WAN Monitor on port 18017
   - Recommendation: Ensure strong admin credentials

2. **Printer SMB Services (192.168.1.13)**
   - SMB file sharing enabled on printer
   - Recommendation: Verify SMB is required for print jobs

### Positive Findings
3. **NucBox_K8 Firewall (192.168.1.253)**
   - All ports filtered - good security posture
   - Mini PC is properly firewalled

4. **Smaller Attack Surface**
   - Only 4 devices vs 14 at Location #1
   - Less exposure overall

---

## Network Diagram (Text-Based)

### Location #1 - Main Office

```
                    [Internet]
                        |
                        |
              [192.168.1.1 - ASUS Router]
                        |
        ________________|________________
       |                |                |
   [Switch]         [Switch]         [Wireless]
       |                |                |
   +-------+        +-------+        +-------+
   |  PCs  |        |Printers|       | VoIP  |
   +-------+        +-------+        +-------+
   .23 RVS          .46 JONDA        .98 W60B
   .45 Counter      .60 EPSON        .112 Yealink
   .160 JONDA-PC
   .181 Tanya

   [192.168.1.123 - Netgear GS748T Switch]
   [192.168.1.128 - SCC Server]
   [192.168.1.134 - DMP Security Panel]
   [192.168.1.240 - Arcadyan Device]
```

---

## Recommendations

### Immediate Actions
1. [ ] Verify router admin password is strong and not default
2. [ ] Check all Windows PCs for current security updates
3. [ ] Verify printer admin passwords are set
4. [ ] Review VoIP system security settings

### Short-Term Improvements
5. [ ] Implement network segmentation (VLANs)
   - Data VLAN for workstations
   - Voice VLAN for VoIP
   - IoT/Printer VLAN
   - Guest VLAN (if needed)
6. [ ] Enable SMB signing on Windows hosts
7. [ ] Disable SMBv1 protocol if not required
8. [ ] Configure switch port security on GS748T

### Long-Term Recommendations
9. [ ] Consider upgrading to enterprise-grade firewall (SonicWall recommended)
10. [ ] Implement 802.1X authentication
11. [ ] Deploy network monitoring solution
12. [ ] Regular vulnerability scanning schedule

---

## Scan Details

### Phase 1: Host Discovery
- **Command**: `nmap -sn 192.168.1.0/24`
- **Duration**: 5.70 seconds
- **Hosts Found**: 14

### Phase 2: Standard Scan
- **Command**: `nmap -F -sV [hosts]`
- **Duration**: 46.50 seconds
- **Ports Scanned**: Top 100 common ports

### Phase 3: Intensive Scan
- **Command**: `nmap -p- -sV -sC -T4 [hosts]`
- **Status**: In Progress
- **Ports Scanned**: All 65535 TCP ports

---

## Files Generated

| File | Description |
|------|-------------|
| 01_discovery.nmap | Host discovery results (text) |
| 01_discovery.xml | Host discovery results (XML) |
| 02_standard.nmap | Standard scan results (text) |
| 02_standard.xml | Standard scan results (XML) |
| 03_intensive.nmap | Intensive scan results (text) |
| 03_intensive.xml | Intensive scan results (XML) |

---

**Report Generated By**: OberaConnect Network Assessment Tool
**Scan Performed By**: [Technician Name]
**Location**: Spanish Fort Waterboard, Spanish Fort, AL
**Date**: December 1, 2025
