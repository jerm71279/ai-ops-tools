#!/bin/bash
#
# Azure Backup Report Watchdog
# Detects missed reports and generates them when network is available
#
# This script is designed to run hourly during business hours
# to catch any reports that failed due to network issues
#

REPORT_DIR="/home/mavrick/Projects/Secondbrain/reports"
LOG_FILE="/home/mavrick/Projects/Secondbrain/logs/backup_watchdog.log"
AZURE_CONFIG_DIR="$HOME/AZ_Subs/customer/setcoservices"
PYTHON_VENV="/home/mavrick/Projects/Secondbrain/venv/bin/python"
REPORT_SCRIPT="/home/mavrick/Projects/Secondbrain/scripts/azure_backup_report.py"
UPLOAD_SCRIPT="/home/mavrick/Projects/Secondbrain/Tools/SharePoint-Sync/upload_to_sharepoint.py"

TODAY=$(date +%Y-%m-%d)
REPORT_FILE="${REPORT_DIR}/azure_backup_${TODAY}.md"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if report already exists and is valid (more than 100 bytes = not an error stub)
check_report_exists() {
    if [[ -f "$REPORT_FILE" ]]; then
        local size=$(stat -c%s "$REPORT_FILE" 2>/dev/null || echo 0)
        if [[ $size -gt 100 ]]; then
            return 0  # Valid report exists
        fi
    fi
    return 1  # No valid report
}

# Test network connectivity to Azure
check_network() {
    # Try to resolve Azure login endpoint
    if host login.microsoftonline.com >/dev/null 2>&1; then
        return 0
    fi
    # Fallback: try ping to common DNS
    if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
        # DNS might be slow, try curl with timeout
        if curl -s --connect-timeout 5 https://login.microsoftonline.com >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Generate and upload the report
generate_report() {
    log "Generating missed report for ${TODAY}..."

    export AZURE_CONFIG_DIR

    # Generate the report
    if python3 "$REPORT_SCRIPT" -o "$REPORT_FILE" >> "$LOG_FILE" 2>&1; then
        log "Report generated successfully: ${REPORT_FILE}"

        # Upload to SharePoint
        if "$PYTHON_VENV" "$UPLOAD_SCRIPT" "$REPORT_FILE" \
            --site "OberaConnect Technical" \
            --folder "Setco/Setco AZ VM Backups" >> "$LOG_FILE" 2>&1; then
            log "Report uploaded to SharePoint successfully"
            return 0
        else
            log "ERROR: Failed to upload report to SharePoint"
            return 1
        fi
    else
        log "ERROR: Failed to generate report"
        return 1
    fi
}

# Main logic
main() {
    # Check if valid report already exists
    if check_report_exists; then
        # Report exists, nothing to do
        exit 0
    fi

    log "No valid report found for ${TODAY}, checking network..."

    # Check network availability
    if ! check_network; then
        log "Network not available, will retry later"
        exit 0
    fi

    log "Network available, generating missed report..."
    generate_report
}

main "$@"
