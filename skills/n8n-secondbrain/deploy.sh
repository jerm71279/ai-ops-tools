#!/bin/bash
# =============================================================================
# OberaConnect Secondbrain - Secure Deployment Script
# =============================================================================
# This script deploys the n8n + Qdrant stack with security hardening
# Run as: sudo ./deploy.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
INSTALL_DIR="/opt/oberaconnect-secondbrain"
DATA_DIR="/var/lib/secondbrain"
BACKUP_DIR="/var/backups/secondbrain"
LOG_DIR="/var/log/secondbrain"

# -----------------------------------------------------------------------------
# Pre-flight Checks
# -----------------------------------------------------------------------------
log_info "Running pre-flight checks..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (sudo ./deploy.sh)"
    exit 1
fi

# Check for required commands
for cmd in docker docker-compose curl openssl; do
    if ! command -v $cmd &> /dev/null; then
        log_warn "$cmd not found. Installing..."
        if [ "$cmd" = "docker" ]; then
            curl -fsSL https://get.docker.com | sh
            systemctl enable docker
            systemctl start docker
        elif [ "$cmd" = "docker-compose" ]; then
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
        fi
    fi
done

log_success "Pre-flight checks passed"

# -----------------------------------------------------------------------------
# Directory Setup
# -----------------------------------------------------------------------------
log_info "Setting up directories..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR/n8n"
mkdir -p "$DATA_DIR/qdrant"
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$INSTALL_DIR/workflows"
mkdir -p "$INSTALL_DIR/nginx/ssl"

# Secure permissions
chmod 700 "$INSTALL_DIR"
chmod 700 "$DATA_DIR"
chmod 700 "$BACKUP_DIR"

log_success "Directories created with secure permissions"

# -----------------------------------------------------------------------------
# Copy Files
# -----------------------------------------------------------------------------
log_info "Copying configuration files..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
    cp "$SCRIPT_DIR/docker-compose.yml" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/.gitignore" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/workflow-"*.json "$INSTALL_DIR/workflows/" 2>/dev/null || true
fi

log_success "Files copied"

# -----------------------------------------------------------------------------
# Generate Secrets (if .env doesn't exist)
# -----------------------------------------------------------------------------
if [ ! -f "$INSTALL_DIR/.env" ]; then
    log_info "Generating secure secrets..."

    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"

    # Generate encryption key
    ENCRYPTION_KEY=$(openssl rand -hex 16)
    sed -i "s/GENERATE_WITH_OPENSSL_RAND_HEX_16/$ENCRYPTION_KEY/" "$INSTALL_DIR/.env"

    # Generate Qdrant API key
    QDRANT_KEY=$(openssl rand -hex 32)
    sed -i "s/GENERATE_WITH_OPENSSL_RAND_HEX_32/$QDRANT_KEY/" "$INSTALL_DIR/.env"

    # Generate Webhook API key
    WEBHOOK_KEY=$(openssl rand -hex 24)
    sed -i "s/GENERATE_WITH_OPENSSL_RAND_HEX_24/$WEBHOOK_KEY/" "$INSTALL_DIR/.env"

    # Generate n8n password
    N8N_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 20)
    sed -i "s/CHANGE_TO_STRONG_PASSWORD_MIN_16_CHARS/$N8N_PASSWORD/" "$INSTALL_DIR/.env"

    # Secure the .env file
    chmod 600 "$INSTALL_DIR/.env"

    log_success "Secrets generated"
    log_warn "IMPORTANT: Edit $INSTALL_DIR/.env to add your API keys:"
    log_warn "  - ANTHROPIC_API_KEY"
    log_warn "  - MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID"
    log_warn "  - SHAREPOINT_SITE_ID, SHAREPOINT_DRIVE_ID"

    echo ""
    echo "=========================================="
    echo "Generated Credentials (SAVE THESE!):"
    echo "=========================================="
    echo "n8n Password: $N8N_PASSWORD"
    echo "Qdrant API Key: $QDRANT_KEY"
    echo "Webhook API Key: $WEBHOOK_KEY"
    echo "=========================================="
    echo ""
else
    log_info ".env file already exists, skipping secret generation"
fi

# -----------------------------------------------------------------------------
# Docker Network
# -----------------------------------------------------------------------------
log_info "Setting up Docker network..."

docker network create secondbrain-network 2>/dev/null || log_info "Network already exists"

# -----------------------------------------------------------------------------
# Pull Images
# -----------------------------------------------------------------------------
log_info "Pulling Docker images..."

cd "$INSTALL_DIR"
docker-compose pull

log_success "Images pulled"

# -----------------------------------------------------------------------------
# Firewall Configuration (SECURE)
# -----------------------------------------------------------------------------
log_info "Configuring firewall (secure mode)..."

if command -v ufw &> /dev/null; then
    # Only allow SSH and HTTPS - n8n/Qdrant stay internal
    ufw allow 22/tcp comment 'SSH'
    ufw allow 443/tcp comment 'HTTPS (nginx proxy)'

    # DO NOT expose 5678 or 6333 directly
    ufw deny 5678/tcp comment 'n8n - use nginx proxy instead'
    ufw deny 6333/tcp comment 'Qdrant - internal only'
    ufw deny 6334/tcp comment 'Qdrant gRPC - internal only'

    log_success "UFW rules configured (secure mode)"
    log_info "n8n accessible via nginx proxy on port 443 only"
else
    log_warn "UFW not found. Please manually configure firewall:"
    log_warn "  - Allow: 22 (SSH), 443 (HTTPS)"
    log_warn "  - DENY: 5678, 6333, 6334 (internal services)"
fi

# -----------------------------------------------------------------------------
# Systemd Service
# -----------------------------------------------------------------------------
log_info "Creating systemd service..."

cat > /etc/systemd/system/secondbrain.service << EOF
[Unit]
Description=OberaConnect Secondbrain (n8n + Qdrant)
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable secondbrain

log_success "Systemd service created"

# -----------------------------------------------------------------------------
# Start Services
# -----------------------------------------------------------------------------
log_info "Starting services..."

cd "$INSTALL_DIR"
docker-compose up -d

log_info "Waiting for services to start..."
sleep 15

# Check health (using API key for Qdrant)
source "$INSTALL_DIR/.env"

if curl -s http://localhost:5678/healthz > /dev/null 2>&1; then
    log_success "n8n is running"
else
    log_warn "n8n may still be starting..."
fi

if curl -s -H "api-key: $QDRANT_API_KEY" http://localhost:6333/health > /dev/null 2>&1; then
    log_success "Qdrant is running (with API key auth)"
else
    log_warn "Qdrant may still be starting..."
fi

# -----------------------------------------------------------------------------
# Create Qdrant Collection (with API key)
# -----------------------------------------------------------------------------
log_info "Creating Qdrant collection..."

sleep 5

curl -s -X PUT "http://localhost:6333/collections/oberaconnect-docs" \
    -H "Content-Type: application/json" \
    -H "api-key: $QDRANT_API_KEY" \
    -d '{
        "vectors": {
            "size": 1024,
            "distance": "Cosine"
        },
        "optimizers_config": {
            "indexing_threshold": 20000
        }
    }' > /dev/null 2>&1 && log_success "Qdrant collection created" || log_warn "Collection may already exist"

# -----------------------------------------------------------------------------
# Backup Cron Job
# -----------------------------------------------------------------------------
log_info "Setting up backup cron job..."

cat > /etc/cron.daily/secondbrain-backup << 'CRONEOF'
#!/bin/bash
set -e
BACKUP_DIR="/var/backups/secondbrain"
INSTALL_DIR="/opt/oberaconnect-secondbrain"
DATE=$(date +%Y%m%d)
LOG_FILE="/var/log/secondbrain/backup-$DATE.log"

source "$INSTALL_DIR/.env"

echo "Starting backup at $(date)" >> "$LOG_FILE"

# Backup Qdrant
docker exec qdrant qdrant-backup /snapshots/backup-$DATE 2>> "$LOG_FILE" || true

# Backup n8n workflows
docker exec n8n n8n export:workflow --all --output=/home/node/backups/workflows-$DATE.json 2>> "$LOG_FILE" || true

# Copy to backup dir
cp -r /var/lib/secondbrain/n8n/backups/* "$BACKUP_DIR/" 2>> "$LOG_FILE" || true

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed at $(date)" >> "$LOG_FILE"
CRONEOF

chmod +x /etc/cron.daily/secondbrain-backup
log_success "Backup cron job created"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "============================================================================="
echo -e "${GREEN}Secure Deployment Complete!${NC}"
echo "============================================================================="
echo ""
echo "SECURITY FEATURES ENABLED:"
echo "  - n8n and Qdrant only accessible via localhost (127.0.0.1)"
echo "  - Qdrant requires API key authentication"
echo "  - Webhooks require API key in X-API-Key header"
echo "  - Firewall blocks direct access to services"
echo ""
echo "ACCESS:"
echo "  n8n UI (local): http://127.0.0.1:5678"
echo "  n8n UI (via nginx): https://your-domain:443"
echo ""
echo "CREDENTIALS (from .env):"
echo "  n8n User: admin"
echo "  n8n Password: (see .env file)"
echo "  Webhook API Key: (see .env file)"
echo ""
echo "NEXT STEPS:"
echo "  1. Edit credentials: nano $INSTALL_DIR/.env"
echo "  2. Add your API keys (Anthropic, Microsoft)"
echo "  3. Restart: systemctl restart secondbrain"
echo "  4. Set up nginx for SSL termination"
echo "  5. Import workflows via n8n UI"
echo ""
echo "============================================================================="
