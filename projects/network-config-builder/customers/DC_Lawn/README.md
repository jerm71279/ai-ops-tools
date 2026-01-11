# DC Lawn - MikroTik Configuration Package

**Customer Name:** DC Lawn
**Circuit ID:** 205922 (Unifi Circuit Install)
**Circuit Description:** /INT/205922//UIF/
**Location:** 16520 Gaineswood Dr N, Fairhope, AL 36532-5164
**Generated:** 2025-11-24

## Quick Start

### Files in This Package
```
DC_Lawn/
├── README.md                          # This file - Quick start
├── QUICK_REFERENCE_CHECKLIST.md      # Printable field checklist ⭐
├── BENCH_TESTING_GUIDE.md            # Step-by-step bench testing ⭐
├── WORK_LOG.md                        # Detailed work log
├── customer_config.yaml               # Source configuration (YAML)
└── configs/
    └── router.rsc                    # MikroTik script (ready to upload)
```

⭐ **Start here for bench testing and deployment**

### Deploy to MikroTik

**Option 1: Upload via WinBox (Recommended)**
1. Open WinBox and connect to MikroTik
2. Drag `configs/router.rsc` to Files menu
3. Open New Terminal
4. Run: `/import file-name=router.rsc`

**Option 2: Copy-Paste**
1. Open `configs/router.rsc` in text editor
2. Connect via WinBox Terminal or SSH
3. Copy and paste all commands

### Network Details

| Setting | Value |
|---------|-------|
| WAN IP | 142.190.216.66/30 |
| Gateway | 142.190.216.65 |
| LAN IP | 10.54.0.1/24 |
| LAN Subnet Block | 10.54.0.0/24 - 10.54.3.0/24 (4x /24 reserved) |
| DHCP Pool | 10.54.0.100-200 |
| DNS Servers | 142.190.111.111, 142.190.222.222 |

### Critical Security Notice
⚠️ **CHANGE DEFAULT PASSWORD IMMEDIATELY**
Default admin password: `ChangeMe@205922!`

After deployment:
```
/user set admin password=YourSecurePassword123!
```

### Quick Verification
After deployment, verify:
```bash
/ip address print          # Check IP addresses
/ip route print           # Check default route
/ip dhcp-server print     # Check DHCP server
/ip firewall nat print    # Check NAT rules
ping 8.8.8.8              # Test internet connectivity
```

---

## Documentation Guide

### 📋 For Bench Testing (Before Customer Site)
**→ [BENCH_TESTING_GUIDE.md](BENCH_TESTING_GUIDE.md)**
- Complete step-by-step setup from factory default
- Configuration upload and verification
- Testing procedures
- Troubleshooting guide
- **Start here if testing out-of-box**

### ✅ For Field Deployment
**→ [QUICK_REFERENCE_CHECKLIST.md](QUICK_REFERENCE_CHECKLIST.md)**
- Printable one-page checklist
- Quick reference network info
- Emergency commands
- **Print this for on-site work**

### 📖 For Detailed Information
**→ [WORK_LOG.md](WORK_LOG.md)**
- Complete network configuration details
- Security documentation
- Deployment procedures
- Network topology
