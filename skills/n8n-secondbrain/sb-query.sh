#!/bin/bash
# =============================================================================
# Secondbrain CLI Query Tool
# =============================================================================
# Query the OberaConnect knowledge base from the command line
# Integrates with your multi-AI orchestration workflow
#
# Usage:
#   ./sb-query.sh "What are the UniFi WiFi best practices?"
#   ./sb-query.sh "How do I configure VLANs?" --customer "AcmeCorp"
#   ./sb-query.sh --interactive
# =============================================================================

# Configuration
SECONDBRAIN_URL="${SECONDBRAIN_URL:-http://localhost:5678}"
WEBHOOK_PATH="/webhook/query"
SESSION_FILE="$HOME/.secondbrain_session"
API_KEY="${SECONDBRAIN_API_KEY:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Generate or load session ID
get_session_id() {
    if [ -f "$SESSION_FILE" ]; then
        cat "$SESSION_FILE"
    else
        SESSION_ID="cli-$(date +%s)-$$"
        echo "$SESSION_ID" > "$SESSION_FILE"
        echo "$SESSION_ID"
    fi
}

# Display help
show_help() {
    cat << EOF
${CYAN}Secondbrain CLI Query Tool${NC}

${YELLOW}Usage:${NC}
  sb-query.sh "your question here"
  sb-query.sh "question" --customer "CustomerName"
  sb-query.sh --interactive

${YELLOW}Options:${NC}
  --customer, -c    Filter results by customer name
  --session, -s     Specify session ID for conversation memory
  --new-session     Start a new conversation session
  --interactive, -i Start interactive mode
  --json            Output raw JSON response
  --help, -h        Show this help message

${YELLOW}Examples:${NC}
  sb-query.sh "What are the UniFi WiFi best practices?"
  sb-query.sh "How do I configure VLANs for guest network?" -c "AcmeCorp"
  sb-query.sh -i

${YELLOW}Environment Variables:${NC}
  SECONDBRAIN_URL   Base URL for n8n (default: http://localhost:5678)

EOF
}

# Make query request
query() {
    local question="$1"
    local customer="$2"
    local session="$3"
    local raw_json="$4"
    
    # Build JSON payload
    local payload=$(cat << EOF
{
    "query": "$question",
    "customer": "$customer",
    "session_id": "$session"
}
EOF
)
    
    # Check API key
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}Error: SECONDBRAIN_API_KEY environment variable not set${NC}"
        echo "Set it with: export SECONDBRAIN_API_KEY=your-api-key"
        return 1
    fi

    # Make request (with API key auth)
    local response=$(curl -s -X POST "${SECONDBRAIN_URL}${WEBHOOK_PATH}" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "$payload")
    
    # Check for errors
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to connect to Secondbrain${NC}"
        echo "Make sure n8n is running at: $SECONDBRAIN_URL"
        return 1
    fi
    
    # Output response
    if [ "$raw_json" = "true" ]; then
        echo "$response" | jq '.'
    else
        # Parse and format response
        local answer=$(echo "$response" | jq -r '.answer // .response.answer // "No response received"')
        local sources=$(echo "$response" | jq -r '.sources // .response.sources // [] | .[]?' 2>/dev/null)
        
        echo ""
        echo -e "${GREEN}Answer:${NC}"
        echo "$answer"
        
        if [ -n "$sources" ]; then
            echo ""
            echo -e "${BLUE}Sources:${NC}"
            echo "$sources" | while read -r source; do
                echo "  • $source"
            done
        fi
        echo ""
    fi
}

# Interactive mode
interactive_mode() {
    local customer="$1"
    local session=$(get_session_id)
    
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}        ${GREEN}Secondbrain Interactive Query Mode${NC}                   ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Session: ${YELLOW}$session${NC}"
    [ -n "$customer" ] && echo -e "Customer Filter: ${YELLOW}$customer${NC}"
    echo ""
    echo -e "Type your questions. Commands: ${BLUE}/quit${NC}, ${BLUE}/clear${NC}, ${BLUE}/customer <name>${NC}"
    echo ""
    
    while true; do
        echo -ne "${GREEN}You:${NC} "
        read -r input
        
        # Handle commands
        case "$input" in
            /quit|/exit|/q)
                echo -e "${CYAN}Goodbye!${NC}"
                break
                ;;
            /clear)
                rm -f "$SESSION_FILE"
                session=$(get_session_id)
                echo -e "${YELLOW}Session cleared. New session: $session${NC}"
                continue
                ;;
            /customer\ *)
                customer="${input#/customer }"
                echo -e "${YELLOW}Customer filter set to: $customer${NC}"
                continue
                ;;
            /customer)
                customer=""
                echo -e "${YELLOW}Customer filter cleared${NC}"
                continue
                ;;
            /help|/?)
                echo ""
                echo -e "${BLUE}Commands:${NC}"
                echo "  /quit, /exit, /q  - Exit interactive mode"
                echo "  /clear            - Start new session"
                echo "  /customer <name>  - Set customer filter"
                echo "  /customer         - Clear customer filter"
                echo "  /help, /?         - Show this help"
                echo ""
                continue
                ;;
            "")
                continue
                ;;
        esac
        
        # Make query
        echo -e "${BLUE}Secondbrain:${NC}"
        query "$input" "$customer" "$session" "false"
    done
}

# Parse arguments
QUERY=""
CUSTOMER=""
SESSION=""
RAW_JSON="false"
INTERACTIVE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--customer)
            CUSTOMER="$2"
            shift 2
            ;;
        -s|--session)
            SESSION="$2"
            shift 2
            ;;
        --new-session)
            rm -f "$SESSION_FILE"
            shift
            ;;
        -i|--interactive)
            INTERACTIVE="true"
            shift
            ;;
        --json)
            RAW_JSON="true"
            shift
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

# Get session ID if not specified
if [ -z "$SESSION" ]; then
    SESSION=$(get_session_id)
fi

# Run in appropriate mode
if [ "$INTERACTIVE" = "true" ]; then
    interactive_mode "$CUSTOMER"
elif [ -n "$QUERY" ]; then
    query "$QUERY" "$CUSTOMER" "$SESSION" "$RAW_JSON"
else
    show_help
fi
