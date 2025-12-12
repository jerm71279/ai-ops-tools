# OberaConnect Tools - Deployment Guide

## Web Interface Deployment for Internal Team Access

---

## Quick Start

### Option 1: Simple Start (Development)
```bash
cd /home/mavrick/Projects/Secondbrain
./start_server.sh --dev
```
Open browser: `http://localhost:5000`

### Option 2: Production Start
```bash
cd /home/mavrick/Projects/Secondbrain
./start_server.sh
```
This uses gunicorn with multiple workers for better performance.

---

## Accessing from Other Computers

The server listens on all network interfaces (0.0.0.0), so team members can access it:

1. Find server IP:
   ```bash
   hostname -I
   ```

2. Access from any computer on the network:
   ```
   http://[SERVER-IP]:5000
   ```

Example: `http://192.168.1.100:5000`

---

## Systemd Service (Auto-Start on Boot)

### Install the Service

1. **Copy service file:**
   ```bash
   sudo cp /home/mavrick/Projects/Secondbrain/oberaconnect-tools.service /etc/systemd/system/
   ```

2. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   ```

3. **Enable auto-start:**
   ```bash
   sudo systemctl enable oberaconnect-tools
   ```

4. **Start the service:**
   ```bash
   sudo systemctl start oberaconnect-tools
   ```

### Service Management Commands

```bash
# Check status
sudo systemctl status oberaconnect-tools

# Stop service
sudo systemctl stop oberaconnect-tools

# Restart service
sudo systemctl restart oberaconnect-tools

# View logs
sudo journalctl -u oberaconnect-tools -f

# Disable auto-start
sudo systemctl disable oberaconnect-tools
```

---

## Configuration

### Port Configuration

Default port is 5000. To change:

1. Edit `gunicorn_config.py`:
   ```python
   bind = "0.0.0.0:8080"  # Change to desired port
   ```

2. Restart the service

### Log Files

Logs are stored in `/home/mavrick/Projects/Secondbrain/logs/`:
- `access.log` - HTTP access logs
- `error.log` - Application errors
- `gunicorn.pid` - Process ID

### Worker Configuration

Edit `gunicorn_config.py` to adjust:
```python
workers = 4  # Number of worker processes
timeout = 120  # Request timeout in seconds
```

---

## Firewall Configuration

If using a firewall, allow port 5000:

### UFW (Ubuntu)
```bash
sudo ufw allow 5000/tcp
```

### firewalld (CentOS/RHEL)
```bash
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

### Windows Firewall
Allow inbound connections on port 5000 for WSL

---

## SSL/HTTPS Configuration (Optional)

For HTTPS support:

1. **Generate certificates** (or use Let's Encrypt):
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout server.key -out server.crt
   ```

2. **Edit `gunicorn_config.py`:**
   ```python
   keyfile = "/path/to/server.key"
   certfile = "/path/to/server.crt"
   ```

3. **Update bind address:**
   ```python
   bind = "0.0.0.0:443"
   ```

---

## Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i:5000

# Kill the process
kill -9 <PID>
```

### Permission Denied
```bash
# Check file permissions
ls -la /home/mavrick/Projects/Secondbrain/

# Fix ownership if needed
sudo chown -R mavrick:mavrick /home/mavrick/Projects/Secondbrain/
```

### Service Won't Start
```bash
# Check logs
sudo journalctl -u oberaconnect-tools --no-pager -n 50

# Check gunicorn directly
cd /home/mavrick/Projects/Secondbrain
source venv/bin/activate
gunicorn -c gunicorn_config.py call_flow_web:app
```

### Can't Access from Network
1. Verify server is running: `curl http://localhost:5000`
2. Check firewall rules
3. Verify IP address: `hostname -I`
4. Check if WSL is properly networked

---

## Features Available

### Call Flow Generator
- Create standardized call flow documents
- Web form with all 39 fields
- Download generated DOCX files
- Consistent format for all customers

### Contract Tracker
- View all active contracts
- Renewal alerts (30/60/90 days)
- Export to CSV
- Service catalog by customer

---

## Backup & Maintenance

### Data Files to Backup
```
/home/mavrick/Projects/Secondbrain/
├── contracts_tracking/
│   └── contracts_data.json      # All contract data
├── call_flows_processed/
│   └── *.json                   # Processed call flow data
└── call_flows_generated/
    └── *.docx                   # Generated documents
```

### Backup Command
```bash
tar -czf oberaconnect-tools-backup-$(date +%Y%m%d).tar.gz \
  contracts_tracking/ \
  call_flows_processed/ \
  call_flows_generated/
```

---

## Team Access Instructions

Share these instructions with your team:

### For Team Members

1. Open your browser
2. Go to: `http://[SERVER-IP]:5000`
3. Use the tabs to switch between:
   - **Call Flow Generator** - Create new call flow documents
   - **Contract Tracker** - View contract renewals and alerts

### Creating a Call Flow
1. Fill in customer information (required: Business Name, Contact Name, Main Phone)
2. Select porting or creating numbers
3. Add configuration details
4. Click "Generate Call Flow Document"
5. Download the DOCX file

### Checking Contract Renewals
1. Click "Contract Tracker" tab
2. Review alerts by urgency:
   - 🔴 Critical (30 days)
   - 🟡 Warning (60 days)
   - 🟢 Upcoming (90 days)
3. Export to CSV for spreadsheet analysis

---

## Support

- **Logs:** `/home/mavrick/Projects/Secondbrain/logs/`
- **Config:** `gunicorn_config.py`
- **Service:** `sudo systemctl status oberaconnect-tools`

---

**Deployment Guide Version:** 1.0
**Last Updated:** November 2025
