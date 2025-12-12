#!/bin/bash
#
# OberaConnect Tools - Server Startup Script
# Starts the web interface for internal team access
#

# Configuration
APP_DIR="/home/mavrick/Projects/Secondbrain"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
PORT=5000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  OberaConnect Tools - Web Interface"
echo "=========================================="
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Change to app directory
cd "$APP_DIR" || exit 1

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Check if port is already in use
if lsof -i:$PORT > /dev/null 2>&1; then
    echo -e "${RED}Error: Port $PORT is already in use${NC}"
    echo "Kill the existing process or use a different port"
    exit 1
fi

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}Starting server...${NC}"
echo ""
echo "Access URLs:"
echo "  Local:   http://localhost:$PORT"
echo "  Network: http://$LOCAL_IP:$PORT"
echo "  HTTPS:   https://localhost:5443 (with auth)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start with gunicorn (production mode)
if [ "$1" == "--dev" ]; then
    echo -e "${YELLOW}Running in DEVELOPMENT mode (no auth)${NC}"
    python3 call_flow_web.py
elif [ "$1" == "--no-auth" ]; then
    echo -e "${YELLOW}Running in PRODUCTION mode (no auth)${NC}"
    gunicorn -c gunicorn_config.py call_flow_web:app
else
    echo -e "${GREEN}Running in PRODUCTION mode with HTTPS & Authentication${NC}"
    echo ""
    echo "Default credentials:"
    echo "  Admin: admin / oberaconnect2025"
    echo "  User:  user / oberatools"
    echo ""
    gunicorn -c gunicorn_config_ssl.py call_flow_web_auth:app
fi
