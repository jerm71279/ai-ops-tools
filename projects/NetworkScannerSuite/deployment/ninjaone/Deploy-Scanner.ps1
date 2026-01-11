<#
.SYNOPSIS
    Deploys Obera Network Scanner to a Windows endpoint via NinjaOne RMM.

.DESCRIPTION
    This script downloads and installs the Obera Network Scanner service,
    configures it to start automatically, and reports the access URL back
    to NinjaOne custom fields.

.NOTES
    Deploy via NinjaOne: Automation > Scripts > Add New Script
    Run as: System
    Architecture: All
#>

param(
    [string]$InstallerUrl = "https://your-server.com/OberaNetworkScanner-Setup.exe",
    [string]$InstallPath = "C:\OberaTools\NetworkScanner",
    [int]$WebPort = 8080,
    [switch]$Uninstall
)

# Configuration
$ServiceName = "OberaNetworkScanner"
$LogFile = "$env:TEMP\OberaScanner_Install.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogFile -Append
    Write-Host $Message
}

function Get-LocalIP {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 |
           Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.PrefixOrigin -ne "WellKnown" } |
           Select-Object -First 1).IPAddress
    return $ip
}

function Set-NinjaCustomField {
    param(
        [string]$FieldName,
        [string]$Value
    )
    try {
        # NinjaOne custom field update via ninja-property-set
        if (Get-Command "Ninja-Property-Set" -ErrorAction SilentlyContinue) {
            Ninja-Property-Set $FieldName $Value
            Write-Log "Set NinjaOne field '$FieldName' to '$Value'"
        }
    }
    catch {
        Write-Log "Warning: Could not set NinjaOne custom field: $_"
    }
}

# Uninstall if requested
if ($Uninstall) {
    Write-Log "Uninstalling Obera Network Scanner..."

    # Stop and remove service
    if (Get-Service $ServiceName -ErrorAction SilentlyContinue) {
        Stop-Service $ServiceName -Force
        sc.exe delete $ServiceName
    }

    # Remove files
    if (Test-Path $InstallPath) {
        Remove-Item -Path $InstallPath -Recurse -Force
    }

    # Remove firewall rule
    Remove-NetFirewallRule -DisplayName "Obera Network Scanner" -ErrorAction SilentlyContinue

    # Update NinjaOne
    Set-NinjaCustomField -FieldName "scannerStatus" -Value "Not Installed"
    Set-NinjaCustomField -FieldName "scannerUrl" -Value ""

    Write-Log "Uninstall complete"
    exit 0
}

# Main installation
Write-Log "Starting Obera Network Scanner installation..."
Write-Log "Install path: $InstallPath"

try {
    # Create installation directory
    if (!(Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Log "Created installation directory"
    }

    # Download installer (or copy embedded files)
    $installerPath = "$env:TEMP\OberaScanner-Setup.exe"

    Write-Log "Downloading installer from $InstallerUrl..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    try {
        Invoke-WebRequest -Uri $InstallerUrl -OutFile $installerPath -UseBasicParsing
        Write-Log "Download complete"
    }
    catch {
        Write-Log "Download failed. Using embedded installation method..."

        # Alternative: Install Python and dependencies directly
        # This is a fallback if no installer is available

        # Check for Python
        $pythonPath = Get-Command python -ErrorAction SilentlyContinue
        if (!$pythonPath) {
            Write-Log "Python not found. Installing Python..."

            # Download Python embedded
            $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip"
            $pythonZip = "$env:TEMP\python-embed.zip"
            Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip -UseBasicParsing
            Expand-Archive -Path $pythonZip -DestinationPath "$InstallPath\python" -Force

            # Enable pip
            $pthFile = "$InstallPath\python\python311._pth"
            (Get-Content $pthFile) -replace '#import site', 'import site' | Set-Content $pthFile

            # Download get-pip
            Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$InstallPath\python\get-pip.py"
            & "$InstallPath\python\python.exe" "$InstallPath\python\get-pip.py"
        }
    }

    # Run installer silently (if downloaded)
    if (Test-Path $installerPath) {
        Write-Log "Running installer..."
        Start-Process -FilePath $installerPath -ArgumentList "/S /D=$InstallPath" -Wait -NoNewWindow
        Write-Log "Installation complete"
    }

    # Download Nmap portable (if not included in installer)
    $nmapPath = "$InstallPath\nmap"
    if (!(Test-Path "$nmapPath\nmap.exe")) {
        Write-Log "Downloading Nmap portable..."
        $nmapUrl = "https://nmap.org/dist/nmap-7.94-win32.zip"
        $nmapZip = "$env:TEMP\nmap.zip"
        Invoke-WebRequest -Uri $nmapUrl -OutFile $nmapZip -UseBasicParsing
        Expand-Archive -Path $nmapZip -DestinationPath $InstallPath -Force

        # Rename to simple path
        $extractedDir = Get-ChildItem $InstallPath -Directory | Where-Object { $_.Name -like "nmap-*" } | Select-Object -First 1
        if ($extractedDir) {
            Rename-Item -Path $extractedDir.FullName -NewName "nmap"
        }
        Write-Log "Nmap installed"
    }

    # Add Nmap to PATH for this session
    $env:Path += ";$nmapPath"

    # Create Windows service
    Write-Log "Creating Windows service..."

    $serviceBinary = "$InstallPath\scanner_service.exe"
    if (!(Test-Path $serviceBinary)) {
        # Use Python to run the service
        $serviceBinary = "$InstallPath\python\python.exe"
        $serviceArgs = "`"$InstallPath\service\scanner_service.py`""
    }

    # Create service using sc.exe
    $serviceExists = Get-Service $ServiceName -ErrorAction SilentlyContinue
    if ($serviceExists) {
        Write-Log "Service already exists, stopping..."
        Stop-Service $ServiceName -Force
        sc.exe delete $ServiceName
        Start-Sleep -Seconds 2
    }

    # For Python-based service, we'll create a wrapper batch file
    $wrapperScript = @"
@echo off
cd /d "$InstallPath\service"
"$InstallPath\python\python.exe" scanner_service.py
"@
    $wrapperScript | Out-File -FilePath "$InstallPath\start_service.bat" -Encoding ASCII

    # Create service (using NSSM for better Python service support)
    # Or use Task Scheduler as alternative

    Write-Log "Configuring auto-start via Task Scheduler..."
    $action = New-ScheduledTaskAction -Execute "$InstallPath\start_service.bat" -WorkingDirectory "$InstallPath\service"
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    Unregister-ScheduledTask -TaskName $ServiceName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $ServiceName -Action $action -Trigger $trigger -Principal $principal -Settings $settings

    Write-Log "Scheduled task created"

    # Start the service
    Write-Log "Starting scanner service..."
    Start-ScheduledTask -TaskName $ServiceName
    Start-Sleep -Seconds 5

    # Configure firewall
    Write-Log "Configuring firewall..."
    New-NetFirewallRule -DisplayName "Obera Network Scanner" `
                        -Direction Inbound `
                        -Protocol TCP `
                        -LocalPort $WebPort `
                        -Action Allow `
                        -Profile Any `
                        -ErrorAction SilentlyContinue

    # Get access URL
    $localIP = Get-LocalIP
    $scannerUrl = "http://${localIP}:${WebPort}"

    Write-Log "Scanner URL: $scannerUrl"

    # Test connectivity
    Start-Sleep -Seconds 3
    try {
        $response = Invoke-WebRequest -Uri "$scannerUrl/api/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Log "Service is running and healthy"
            $healthStatus = "Healthy"
        }
    }
    catch {
        Write-Log "Warning: Health check failed. Service may still be starting."
        $healthStatus = "Starting"
    }

    # Update NinjaOne custom fields
    Set-NinjaCustomField -FieldName "scannerStatus" -Value "Installed"
    Set-NinjaCustomField -FieldName "scannerUrl" -Value $scannerUrl
    Set-NinjaCustomField -FieldName "scannerHealth" -Value $healthStatus
    Set-NinjaCustomField -FieldName "scannerInstallDate" -Value (Get-Date -Format "yyyy-MM-dd")

    # Output summary
    Write-Log "============================================"
    Write-Log "INSTALLATION COMPLETE"
    Write-Log "============================================"
    Write-Log "Scanner URL: $scannerUrl"
    Write-Log "Install Path: $InstallPath"
    Write-Log "Log File: $LogFile"
    Write-Log "============================================"

    # Return URL for NinjaOne script output
    Write-Output "SUCCESS: Scanner available at $scannerUrl"
    exit 0
}
catch {
    Write-Log "ERROR: Installation failed - $_"
    Set-NinjaCustomField -FieldName "scannerStatus" -Value "Install Failed"
    Write-Output "FAILED: $($_.Exception.Message)"
    exit 1
}
