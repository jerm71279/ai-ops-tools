# Obera Network Scanner Suite

A comprehensive network scanning solution with web interface, designed for IT professionals and MSPs. Deployable via RMM (NinjaOne), Windows installer, or portable USB.

## Features

- **Web-Based Dashboard** - Modern, responsive interface accessible from any browser
- **Real-Time Progress** - WebSocket updates during scans
- **Multiple Scan Types** - Quick discovery, standard, and intensive scanning
- **Result Export** - Download nmap output files in multiple formats
- **Multiple Deployment Options** - Installer, RMM, or portable

## Architecture

```
NetworkScannerSuite/
├── service/           # FastAPI backend
│   ├── scanner_service.py
│   ├── requirements.txt
│   └── scans/         # Scan output storage
├── web-ui/            # Browser interface
│   └── public/
│       └── index.html
├── installer/         # NSIS Windows installer
├── portable/          # USB/portable package
└── deployment/        # RMM scripts
    └── ninjaone/
```

## Quick Start

### Option 1: Run from Source

```bash
# Install dependencies
cd service
pip install -r requirements.txt

# Start service
python scanner_service.py
```

Open http://localhost:8080 in your browser.

### Option 2: Windows Installer

1. Download `OberaNetworkScanner-Setup.exe`
2. Run as Administrator
3. Follow installation wizard
4. Scanner starts automatically

### Option 3: Portable (USB)

1. Copy `OberaScanner-Portable` folder to USB drive
2. Run `Setup-Portable.bat` (first time only)
3. Run `Start-Scanner.bat`
4. Open http://localhost:8080

## Deployment Options

### NinjaOne RMM Deployment

Deploy remotely via NinjaOne:

1. Upload `Deploy-Scanner.ps1` to NinjaOne Scripts
2. Configure custom fields: `scannerStatus`, `scannerUrl`, `scannerHealth`
3. Deploy to target devices
4. Access scanner URL from NinjaOne device dashboard

### Silent Installation

```powershell
OberaNetworkScanner-Setup.exe /S /D=C:\OberaTools\NetworkScanner
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/scans` | List all scans |
| POST | `/api/scans` | Start new scan |
| GET | `/api/scans/{id}` | Get scan details |
| DELETE | `/api/scans/{id}` | Cancel scan |
| GET | `/api/scans/{id}/files` | List output files |
| GET | `/api/scans/{id}/files/{name}` | Download file |
| WS | `/ws` | Real-time updates |

### Start Scan Request

```json
POST /api/scans
{
  "target": "192.168.1.0/24",
  "scan_type": "standard",
  "name": "Office Network",
  "exclusions": ["192.168.1.1"]
}
```

### Scan Types

- **quick** - Host discovery only (`nmap -sn`)
- **standard** - Ports + services (`nmap -F -sV`)
- **intense** - Full ports + OS detection (`nmap -p- -sV -sC -O`)

## Configuration

### Service Configuration

Edit `config.ini`:

```ini
[service]
port=8080
host=0.0.0.0

[paths]
scans_dir=./scans
nmap_path=/usr/bin/nmap
```

### Firewall

The installer automatically creates a firewall rule. Manual creation:

```powershell
New-NetFirewallRule -DisplayName "Obera Scanner" `
    -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

## Building from Source

### Prerequisites

- Python 3.11+
- Node.js (for web UI development)
- NSIS (for Windows installer)
- Nmap

### Build Installer

```powershell
cd installer
.\build-installer.ps1
```

### Build Portable Package

```powershell
cd portable
.\build-portable.ps1 -IncludeDependencies
```

## Security Considerations

- Runs on localhost by default (0.0.0.0 binds all interfaces)
- No built-in authentication (use network segmentation)
- Scan operations require nmap permissions
- Consider running as dedicated service account

### Future Enhancements

- [ ] M365 SSO authentication
- [ ] Role-based access control
- [ ] Scheduled scans
- [ ] Email notifications
- [ ] Integration with vulnerability databases

## Requirements

### Minimum System Requirements

- Windows 10/11 or Windows Server 2016+
- 2GB RAM
- 500MB disk space
- Network access to target hosts

### Software Dependencies

- Python 3.11+ (embedded version included)
- Nmap 7.x (included in installer)
- Modern web browser

## Troubleshooting

### Common Issues

**Service won't start**
- Check port 8080 isn't in use: `netstat -an | findstr 8080`
- Verify Python is installed correctly
- Check logs in `%TEMP%\OberaScanner_Install.log`

**Scans fail with permission error**
- Run as Administrator for full scan capabilities
- Some scans require raw socket access

**Can't access from other devices**
- Verify firewall rule exists
- Check service is bound to 0.0.0.0
- Ensure correct IP address is used

### Logs

- Installation: `%TEMP%\OberaScanner_Install.log`
- Service: Console output or redirect to file

## License

Copyright (c) 2024 Obera Technologies. All rights reserved.

This software includes Nmap which is licensed under https://nmap.org/book/man-legal.html

## Support

- Issues: https://github.com/obera/network-scanner/issues
- Documentation: https://docs.obera.com/network-scanner
