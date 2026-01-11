# Kali Linux Docker Container with Nmap and MCP Server
FROM kalilinux/kali-rolling:latest

# Update and install essential tools
RUN apt-get update && apt-get upgrade -y

# Install nmap and other useful network discovery tools
RUN apt-get install -y \
    nmap \
    netdiscover \
    masscan \
    arp-scan \
    tcpdump \
    net-tools \
    iproute2 \
    iputils-ping \
    dnsutils \
    curl \
    wget \
    vim \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install MCP SDK and dependencies
RUN pip3 install --no-cache-dir mcp --break-system-packages

# Create directories for scan results and configs
RUN mkdir -p /scans /scans/configs

# Copy MCP server script
COPY mcp_nmap_server.py /usr/local/bin/mcp-nmap-server
RUN chmod +x /usr/local/bin/mcp-nmap-server

# Copy network configuration tool
COPY network-config.py /usr/local/bin/network-config.py
RUN chmod +x /usr/local/bin/network-config.py

# Copy scan scripts
COPY network-discovery.sh /usr/local/bin/network-discovery.sh
COPY intense-scan.sh /usr/local/bin/intense-scan.sh
COPY auto-discover-network.sh /usr/local/bin/auto-discover-network.sh
RUN chmod +x /usr/local/bin/network-discovery.sh /usr/local/bin/intense-scan.sh /usr/local/bin/auto-discover-network.sh

# Set working directory
WORKDIR /scans

# Expose port for MCP server (if using stdio, no port needed)
# EXPOSE 3000

# Default command - can run MCP server or bash
CMD ["/bin/bash"]
