#!/bin/bash
# =============================================================================
# log-change.sh - Quick wrapper for logging changes to Notion
# =============================================================================
# 
# Usage from other oberaconnect-tools:
#   source /path/to/log-change.sh
#   log_change "mikrotik-config-builder" "Acme Corp" "deploy" "Updated VPN config"
#
# Or call directly:
#   ./log-change.sh mikrotik-config-builder "Acme Corp" deploy "Updated VPN config"
#
# Environment variables:
#   NOTION_CONFIG - Path to config.json (default: ~/.config/notion-dashboards/config.json)
#   OBERA_ENGINEER - Your name for audit trail (default: $USER)
# =============================================================================

# Default config location
NOTION_CONFIG="${NOTION_CONFIG:-$HOME/.config/notion-dashboards/config.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/config_change_sync.py"

# Function to log changes - can be sourced by other scripts
log_change() {
    local tool="$1"
    local site="$2"
    local action="$3"
    local summary="$4"
    local details="${5:-}"
    local risk="${6:-}"
    local ticket="${7:-}"
    local rollback="${8:-}"
    
    if [[ -z "$tool" || -z "$site" || -z "$action" || -z "$summary" ]]; then
        echo "Usage: log_change TOOL SITE ACTION SUMMARY [DETAILS] [RISK] [TICKET] [ROLLBACK]"
        echo "Tools: mikrotik-config-builder, sonicwall-scripts, unifi-deploy, azure-automation, network-troubleshooter, manual"
        echo "Actions: deploy, update, rollback, backup, restore, delete, create, modify, assessment"
        return 1
    fi
    
    if [[ ! -f "$NOTION_CONFIG" ]]; then
        echo "Warning: Notion config not found at $NOTION_CONFIG"
        echo "Change not logged to Notion (continuing anyway)"
        return 0
    fi
    
    if [[ ! -f "$SYNC_SCRIPT" ]]; then
        echo "Warning: config_change_sync.py not found at $SYNC_SCRIPT"
        return 0
    fi
    
    # Build command
    local cmd="python3 $SYNC_SCRIPT --config $NOTION_CONFIG log"
    cmd="$cmd --tool $tool"
    cmd="$cmd --site \"$site\""
    cmd="$cmd --action $action"
    cmd="$cmd --summary \"$summary\""
    
    [[ -n "$details" ]] && cmd="$cmd --details \"$details\""
    [[ -n "$risk" ]] && cmd="$cmd --risk $risk"
    [[ -n "$ticket" ]] && cmd="$cmd --ticket \"$ticket\""
    [[ -n "$rollback" ]] && cmd="$cmd --rollback \"$rollback\""
    
    # Execute
    eval "$cmd"
}

# Function to show recent changes
show_recent_changes() {
    local days="${1:-7}"
    python3 "$SYNC_SCRIPT" --config "$NOTION_CONFIG" recent --days "$days"
}

# Function to generate report
generate_report() {
    local site="$1"
    local days="${2:-30}"
    
    if [[ -n "$site" ]]; then
        python3 "$SYNC_SCRIPT" --config "$NOTION_CONFIG" report --site "$site" --days "$days"
    else
        python3 "$SYNC_SCRIPT" --config "$NOTION_CONFIG" report --days "$days"
    fi
}

# If called directly (not sourced), run the command
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 4 ]]; then
        echo "OberaConnect Change Logger"
        echo "=========================="
        echo ""
        echo "Usage: $0 TOOL SITE ACTION SUMMARY [DETAILS]"
        echo ""
        echo "Examples:"
        echo "  $0 mikrotik-config-builder \"Acme Corp\" deploy \"Updated VPN tunnel\""
        echo "  $0 sonicwall-scripts \"Beta Inc\" modify \"Added firewall rule for RDP\""
        echo "  $0 network-troubleshooter \"Gamma LLC\" assessment \"Pre-install network scan\""
        echo ""
        echo "Or source this script in your tools:"
        echo "  source $0"
        echo "  log_change mikrotik-config-builder \"Acme Corp\" deploy \"Updated VPN\""
        exit 1
    fi
    
    log_change "$@"
fi
