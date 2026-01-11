OBERA NETWORK SCANNER - PORTABLE EDITION
=========================================

This portable version can run directly from USB drive or any folder
without requiring installation.


QUICK START
-----------

1. First Time Setup:
   - Double-click "Setup-Portable.bat"
   - Wait for Python and Nmap to download
   - This only needs to be done once

2. Start Scanner:
   - Double-click "Start-Scanner.bat"
   - Open browser to http://localhost:8080

3. Access from other devices:
   - Find your IP address in the console output
   - Browse to http://YOUR-IP:8080


FOLDER STRUCTURE
----------------

OberaScanner/
  |-- Start-Scanner.bat    - Launch the scanner
  |-- Setup-Portable.bat   - First-time setup
  |-- README.txt           - This file
  |-- python/              - Python embedded (created by setup)
  |-- nmap/                - Nmap portable (created by setup)
  |-- service/             - Scanner backend
  |-- web-ui/              - Web interface


REQUIREMENTS
------------

- Windows 10/11 or Windows Server 2016+
- Internet connection (for initial setup only)
- Administrator privileges (recommended for full scan capabilities)
- Minimum 500MB free space


OFFLINE SETUP
-------------

If you need to run in an environment without internet:

1. Run Setup-Portable.bat on a machine with internet
2. This will download python/ and nmap/ folders
3. Copy the entire OberaScanner folder to offline machine
4. Run Start-Scanner.bat


FIREWALL NOTES
--------------

If other devices cannot access the scanner:

1. Allow Python through Windows Firewall
2. Or run: netsh advfirewall firewall add rule name="Obera Scanner" dir=in action=allow protocol=TCP localport=8080

To remove the firewall rule:
netsh advfirewall firewall delete rule name="Obera Scanner"


TROUBLESHOOTING
---------------

"Python not found" error:
  - Run Setup-Portable.bat first
  - Ensure no antivirus is blocking downloads

"Port 8080 already in use":
  - Another application is using port 8080
  - Close it or edit scanner_service.py to use different port

"Access denied" errors during scans:
  - Run Start-Scanner.bat as Administrator
  - Right-click > Run as administrator

Scanner not accessible from other devices:
  - Check Windows Firewall settings
  - Verify you're using correct IP address


SUPPORT
-------

For issues and feature requests:
https://github.com/obera/network-scanner/issues

Documentation:
https://docs.obera.com/network-scanner


VERSION
-------

Version: 1.0.0
Build Date: 2024
