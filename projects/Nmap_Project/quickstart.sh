#!/bin/bash
# Quick Start Script for Nmap MCP Server

echo "======================================"
echo "Nmap MCP Server - Quick Start"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Build the container
echo "Building Kali Linux container with MCP server..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✓ Container built successfully"
echo ""

# Start the container
echo "Starting container..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container"
    exit 1
fi

echo "✓ Container started successfully"
echo ""

# Test MCP server
echo "Testing MCP server..."
sleep 2
docker exec kali-network-discovery python3 -c "import mcp; print('✓ MCP SDK installed')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ MCP server is ready"
else
    echo "⚠ Warning: MCP server test failed, but container is running"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure Claude Desktop:"
echo "   Add this to your Claude Desktop config file:"
echo ""
echo "   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "   Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "   Linux: ~/.config/Claude/claude_desktop_config.json"
echo ""
echo "   Configuration:"
cat << 'EOF'
   {
     "mcpServers": {
       "nmap-network-discovery": {
         "command": "docker",
         "args": [
           "exec",
           "-i",
           "kali-network-discovery",
           "python3",
           "/usr/local/bin/mcp-nmap-server"
         ]
       }
     }
   }
EOF
echo ""
echo "2. Restart Claude Desktop"
echo ""
echo "3. Start using nmap through Claude with natural language!"
echo "   Example: 'Run a ping sweep on 192.168.1.0/24'"
echo ""
echo "View logs: docker logs kali-network-discovery"
echo "Access shell: docker exec -it kali-network-discovery /bin/bash"
echo "Stop container: docker-compose down"
echo ""
echo "Read MCP_SETUP_GUIDE.md for detailed instructions"
echo "======================================"
