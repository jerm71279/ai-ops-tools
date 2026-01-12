# Standard Operating Procedure: VPN Remote Printer Setup

| | |
|---|---|
| **Document ID:** | SOP-NET-010 |
| **Title:** | VPN Remote Printer Setup using Direct TCP/IP Port 9100 |
| **Category:** | Network Infrastructure |
| **Version:** | 1.0 |
| **Status:** | Final |
| **Author:** | Jeremy Smith |
| **Creation Date:** | 2026-01-12 |
| **Approval Date:** | 2026-01-12 |

---

### 1.0 Purpose

This procedure establishes the standard method for configuring remote printers across site-to-site VPN connections. It specifically addresses the limitation that Windows automatic printer discovery (WSD) does not function over VPN tunnels.

### 2.0 Scope

This procedure applies to:
- All OberaConnect managed sites with SonicWall site-to-site VPNs
- Windows 10/11 workstations requiring access to printers at remote sites
- Network printers with TCP/IP printing capability (port 9100)

### 3.0 Definitions

| Term | Definition |
|------|------------|
| **WSD** | Web Services for Devices - Windows auto-discovery protocol using multicast (does NOT work over VPN) |
| **Port 9100** | RAW/JetDirect printing port - direct TCP connection to printer |
| **Port 631** | IPP (Internet Printing Protocol) port |
| **Port 515** | LPR/LPD legacy printing port |
| **S2S VPN** | Site-to-Site VPN tunnel between two firewalls |

### 4.0 Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| Network Engineer | Verify VPN policy allows printer traffic |
| Support Technician | Configure printers on client workstations |
| End User | Report printing issues |

### 5.0 Prerequisites

- [ ] Site-to-site VPN tunnel is established and operational
- [ ] Printer IP address at remote site is known
- [ ] Port 9100 is allowed in VPN policy (both directions)
- [ ] Administrative access to the workstation
- [ ] Printer is powered on and connected to network

---

### 6.0 Procedure

#### 6.1 Verify VPN Connectivity to Printer

Before configuring the printer, verify the VPN path is working.

**Step 1:** Open PowerShell as Administrator

**Step 2:** Test basic connectivity:
```powershell
Test-NetConnection -ComputerName <PRINTER_IP> -Port 9100
```

**Step 3:** Verify the result shows:
```
TcpTestSucceeded : True
```

If `TcpTestSucceeded : False`, check:
- VPN tunnel status on SonicWall
- VPN policy includes port 9100
- Printer is online at remote site

#### 6.2 Identify Printer Model (Optional)

If printer model is unknown, access the printer's web interface:

```powershell
Start-Process "http://<PRINTER_IP>"
```

Note the printer model for driver selection.

#### 6.3 Add Printer Port via PowerShell

**Step 1:** Create the TCP/IP printer port:
```powershell
Add-PrinterPort -Name "<SITENAME>_<PRINTERNAME>" -PrinterHostAddress "<PRINTER_IP>"
```

**Example:**
```powershell
Add-PrinterPort -Name "Fairhope_HP_OfficeJet" -PrinterHostAddress "192.168.0.24"
```

**Step 2:** Verify port was created:
```powershell
Get-PrinterPort -Name "<SITENAME>_<PRINTERNAME>"
```

#### 6.4 Add Printer via PowerShell

**Option A: Using Generic Driver (Recommended for simplicity)**
```powershell
Add-Printer -Name "<PRINTER_DISPLAY_NAME>" -PortName "<SITENAME>_<PRINTERNAME>" -DriverName "Microsoft IPP Class Driver"
```

**Example:**
```powershell
Add-Printer -Name "HP OfficeJet Fairhope (VPN)" -PortName "Fairhope_HP_OfficeJet" -DriverName "Microsoft IPP Class Driver"
```

**Option B: Using Specific HP Driver**

First, check available drivers:
```powershell
Get-PrinterDriver | Where-Object {$_.Name -like "*HP*"} | Select-Object Name
```

Then add with specific driver:
```powershell
Add-Printer -Name "HP OfficeJet Fairhope (VPN)" -PortName "Fairhope_HP_OfficeJet" -DriverName "HP OfficeJet Pro 9120"
```

#### 6.5 Add Printer via GUI (Alternative Method)

1. Open **Settings** → **Printers & Scanners**
2. Click **Add device** → **The printer I want isn't listed**
3. Select **Add a printer using TCP/IP address or hostname**
4. Enter:
   - Device type: **TCP/IP Device**
   - Hostname or IP: `<PRINTER_IP>`
   - Port name: `<SITENAME>_<PRINTERNAME>`
5. Uncheck "Query the printer" for faster setup
6. If prompted for device type, select **Standard** → **Generic Network Card**
7. Select appropriate driver or use **Microsoft IPP Class Driver**
8. Name the printer clearly: `<Model> <Location> (VPN)`

#### 6.6 Test Printing

**Method 1: Send test page via PowerShell**
```powershell
rundll32 printui.dll,PrintUIEntry /k /n "<PRINTER_NAME>"
```

**Method 2: Direct raw test (bypasses Windows spooler)**
```powershell
try {
    $job = [System.Net.Sockets.TcpClient]::new("<PRINTER_IP>", 9100)
    $stream = $job.GetStream()
    $bytes = [System.Text.Encoding]::ASCII.GetBytes("VPN TEST - $(Get-Date)`r`n`r`n")
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Close()
    $job.Close()
    "Success - data sent to printer"
} catch {
    "Failed - $_"
}
```

**Method 3: Print from application**
1. Open Notepad
2. Type test text
3. File → Print → Select the VPN printer
4. Print

---

### 7.0 Verification & Quality Checks

| Check | Command/Action | Expected Result |
|-------|----------------|-----------------|
| Port exists | `Get-PrinterPort -Name "<PORT_NAME>"` | Returns port details |
| Printer exists | `Get-Printer -Name "<PRINTER_NAME>"` | Returns printer details |
| Port 9100 open | `Test-NetConnection <IP> -Port 9100` | TcpTestSucceeded: True |
| Queue empty | `Get-PrintJob -PrinterName "<PRINTER_NAME>"` | Empty (job sent) |

### 8.0 Troubleshooting

| Issue | Resolution |
|-------|------------|
| `TcpTestSucceeded: False` on port 9100 | Check SonicWall VPN policy allows port 9100 both directions |
| Printer shows in queue but doesn't print | Verify bidirectional traffic allowed in VPN policy |
| "Driver not found" error | Use `Microsoft IPP Class Driver` as universal fallback |
| Jobs stuck in queue | Delete printer, recreate with correct port settings |
| Can ping printer but can't print | Confirm using TCP/IP port, not WSD port |
| Slow printing | Normal over VPN - data traverses tunnel |

#### 8.1 Verify Printer is Not Using WSD

Check current printer configuration:
```powershell
Get-Printer | ForEach-Object {
    $port = Get-PrinterPort -Name $_.PortName -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        Name = $_.Name
        Port = $_.PortName
        IP = $port.PrinterHostAddress
    }
} | Where-Object {$_.Port -like "WSD*"}
```

If printer shows WSD port, it will NOT work over VPN. Reconfigure with TCP/IP port.

#### 8.2 SonicWall VPN Policy Check

On both SonicWall firewalls, verify VPN policy:
1. Navigate to **VPN** → **Settings** → **VPN Policies**
2. Edit the site-to-site policy
3. Confirm **Local Networks** and **Remote Networks** include printer subnets
4. Verify no access rules blocking port 9100

### 9.0 Related Documents

| Document | Description |
|----------|-------------|
| SOP-NET-006 | SonicWall Backup Configuration |
| SOP-NET-007 | SonicWall Config Restore |
| SOP-AZ-002 | Azure VPN to SonicWall S2S |

### 10.0 Revision History

| Version | Date | Author | Change Description |
|---------|------|--------|-------------------|
| 1.0 | 2026-01-12 | Jeremy Smith | Initial document creation |

### 11.0 Approval

| Name | Role | Signature | Date |
|------|------|-----------|------|
| Jeremy Smith | Network Engineer | Approved | 2026-01-12 |

---

## Quick Reference Card

### Add VPN Printer (Copy/Paste Ready)

```powershell
# Variables - UPDATE THESE
$PrinterIP = "192.168.X.X"
$PortName = "SiteName_PrinterName"
$PrinterName = "Printer Model Location (VPN)"

# Create port and add printer
Add-PrinterPort -Name $PortName -PrinterHostAddress $PrinterIP
Add-Printer -Name $PrinterName -PortName $PortName -DriverName "Microsoft IPP Class Driver"

# Verify
Get-Printer -Name $PrinterName
Test-NetConnection -ComputerName $PrinterIP -Port 9100
```

### Why WSD Doesn't Work Over VPN

| Protocol | Transport | VPN Compatible |
|----------|-----------|----------------|
| WSD | Multicast UDP | No |
| TCP/IP Port 9100 | Unicast TCP | Yes |
| IPP (Port 631) | Unicast TCP | Yes |
| LPR (Port 515) | Unicast TCP | Yes (if enabled) |

**Always use Direct TCP/IP (port 9100) for VPN printers.**
