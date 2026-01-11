# Secure Device Deployment Architecture

**Status:** Planned for Phase 3 (Q3 2025)
**Current:** Manual deployment only

## Overview

This document describes how the Multi-Vendor Network Configuration Builder will securely interface with network devices to deploy configurations.

## Current State (Phase 1 & 2)

### Manual Deployment Process

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Generate  │────────▶│    Files     │────────▶│   Manual     │
│   Configs   │         │  (.rsc/.cli/ │         │   Import     │
│             │         │    .json)    │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
```

**Current Workflow:**
1. User generates configuration files locally
2. User manually transfers files to device (SCP, web upload, etc.)
3. User manually imports/applies configuration
4. No direct API communication with devices

**Security:** 
- ✅ No credentials stored in application
- ✅ No direct network access required
- ✅ User controls all deployment steps
- ⚠️ Requires manual intervention
- ⚠️ Prone to human error

## Planned Secure Deployment (Phase 3)

### Architecture Overview

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Config     │────────▶│  Validation  │────────▶│  Deployment  │
│  Generator   │         │   & Review   │         │   Engine     │
└──────────────┘         └──────────────┘         └──────────────┘
                                                          │
                         ┌────────────────────────────────┤
                         │                                │
                         ▼                                ▼
                  ┌──────────────┐              ┌──────────────┐
                  │   Encrypted  │              │   Secure     │
                  │     API      │              │   Channel    │
                  │  Connection  │              │   (SSH/TLS)  │
                  └──────────────┘              └──────────────┘
                         │                                │
                         ▼                                ▼
                  ┌──────────────┐              ┌──────────────┐
                  │   Network    │              │   Network    │
                  │   Device     │              │   Device     │
                  └──────────────┘              └──────────────┘
```

### Secure Communication Methods

#### 1. MikroTik RouterOS API

**Protocol:** RouterOS API over TLS
**Port:** 8729 (API-SSL)
**Library:** `librouteros` or custom implementation

**Security Features:**
```python
from librouteros import connect
from librouteros.login import login_tls

class MikroTikDeployer:
    def deploy_secure(self, device_ip: str, username: str, password: str, 
                      config: NetworkConfig):
        """Deploy via encrypted API"""
        
        # 1. Establish TLS connection
        api = connect(
            host=device_ip,
            username=username,
            password=password,
            ssl_wrapper=ssl.wrap_socket,  # TLS encryption
            port=8729,
            timeout=10
        )
        
        # 2. Verify device identity (optional certificate pinning)
        cert = api.get_certificate()
        if not self._verify_device_cert(cert):
            raise SecurityError("Device certificate mismatch")
        
        # 3. Create backup before deployment
        backup_id = api('/system/backup/save', name='pre-deployment')
        
        # 4. Deploy configuration commands
        try:
            for command in self._parse_rsc_to_api_commands(config):
                response = api(command)
                self._log_deployment(command, response)
        except Exception as e:
            # 5. Rollback on failure
            api('/system/backup/load', numbers=backup_id)
            raise DeploymentError(f"Deployment failed: {e}")
        
        # 6. Verify configuration
        self._verify_deployment(api, config)
        
        api.close()
```

**Security Measures:**
- ✅ TLS encryption (API-SSL)
- ✅ Username/password authentication
- ✅ Optional certificate pinning
- ✅ Automatic backup before deployment
- ✅ Rollback on failure
- ✅ Command-level audit logging
- ✅ No plaintext credential storage

#### 2. SonicWall Management API

**Protocol:** HTTPS REST API
**Port:** 443
**Authentication:** Token-based

**Security Features:**
```python
import requests
from requests.auth import HTTPBasicAuth

class SonicWallDeployer:
    def deploy_secure(self, device_ip: str, username: str, password: str,
                      config: NetworkConfig):
        """Deploy via SonicWall API"""
        
        # 1. Authenticate and get token
        session = requests.Session()
        auth_url = f"https://{device_ip}/api/sonicos/auth"
        
        # Verify SSL certificate
        session.verify = True  # or path to CA bundle
        
        response = session.post(
            auth_url,
            auth=HTTPBasicAuth(username, password),
            timeout=10
        )
        
        if response.status_code != 200:
            raise AuthenticationError("Failed to authenticate")
        
        token = response.headers.get('X-NSAPI-Session')
        session.headers.update({'X-NSAPI-Session': token})
        
        # 2. Create configuration backup
        backup_response = session.post(
            f"https://{device_ip}/api/sonicos/config/backup"
        )
        
        # 3. Deploy configuration
        try:
            # Convert CLI to API calls
            api_config = self._cli_to_api_format(config)
            
            for endpoint, data in api_config.items():
                response = session.post(
                    f"https://{device_ip}/api/sonicos/{endpoint}",
                    json=data,
                    timeout=30
                )
                
                if response.status_code not in [200, 201]:
                    raise DeploymentError(f"API call failed: {response.text}")
        
        except Exception as e:
            # 4. Rollback on failure
            session.post(f"https://{device_ip}/api/sonicos/config/restore")
            raise
        
        finally:
            # 5. Logout and invalidate token
            session.delete(f"https://{device_ip}/api/sonicos/auth")
```

**Security Measures:**
- ✅ HTTPS/TLS encryption
- ✅ Token-based authentication (no password in each request)
- ✅ SSL certificate verification
- ✅ Session timeout
- ✅ Automatic token invalidation
- ✅ Configuration backup/restore
- ✅ API rate limiting awareness

#### 3. Ubiquiti UniFi Controller API

**Protocol:** HTTPS REST API
**Port:** 8443
**Authentication:** Cookie-based session

**Security Features:**
```python
import requests
import json

class UniFiDeployer:
    def deploy_secure(self, controller_ip: str, username: str, password: str,
                      config: NetworkConfig, site: str = "default"):
        """Deploy via UniFi Controller API"""
        
        session = requests.Session()
        session.verify = True  # SSL verification
        
        # 1. Login to controller
        login_url = f"https://{controller_ip}:8443/api/login"
        login_data = {
            "username": username,
            "password": password,
            "remember": False  # Don't create persistent session
        }
        
        response = session.post(login_url, json=login_data, timeout=10)
        
        if response.status_code != 200:
            raise AuthenticationError("Controller login failed")
        
        # 2. Get current configuration (for backup)
        current_config = session.get(
            f"https://{controller_ip}:8443/api/s/{site}/rest/networkconf"
        ).json()
        
        # 3. Deploy new configuration
        try:
            # Networks
            for network in config.networks:
                response = session.post(
                    f"https://{controller_ip}:8443/api/s/{site}/rest/networkconf",
                    json=network,
                    timeout=30
                )
                
                if response.status_code not in [200, 201]:
                    raise DeploymentError(f"Network creation failed: {network['name']}")
            
            # Wireless networks
            for wlan in config.wlans:
                response = session.post(
                    f"https://{controller_ip}:8443/api/s/{site}/rest/wlanconf",
                    json=wlan,
                    timeout=30
                )
        
        except Exception as e:
            # 4. Rollback - restore previous config
            self._restore_config(session, controller_ip, site, current_config)
            raise
        
        finally:
            # 5. Logout
            session.post(f"https://{controller_ip}:8443/api/logout")
```

**Security Measures:**
- ✅ HTTPS/TLS encryption
- ✅ Cookie-based session authentication
- ✅ Session cleanup on completion
- ✅ SSL certificate verification
- ✅ Configuration backup before deployment
- ✅ Automatic rollback on failure

### Credential Management

#### Secure Credential Storage Options

**1. Environment Variables (Simple)**
```bash
export DEVICE_IP="192.168.1.1"
export DEVICE_USER="admin"
export DEVICE_PASSWORD="$(cat /secure/path/password.txt)"

./network-config deploy -i config.yaml
```

**2. Encrypted Credential Store (Recommended)**
```python
from cryptography.fernet import Fernet
import keyring

class SecureCredentialStore:
    def __init__(self):
        self.cipher = Fernet(self._get_encryption_key())
    
    def store_credential(self, device_id: str, username: str, password: str):
        """Store encrypted credentials in system keyring"""
        encrypted_password = self.cipher.encrypt(password.encode())
        keyring.set_password("network-config-builder", 
                            f"{device_id}:{username}", 
                            encrypted_password.decode())
    
    def get_credential(self, device_id: str, username: str):
        """Retrieve and decrypt credentials"""
        encrypted = keyring.get_password("network-config-builder",
                                        f"{device_id}:{username}")
        return self.cipher.decrypt(encrypted.encode()).decode()
    
    def _get_encryption_key(self):
        """Get or create encryption key"""
        key = keyring.get_password("network-config-builder", "master-key")
        if not key:
            key = Fernet.generate_key()
            keyring.set_password("network-config-builder", "master-key", key.decode())
        return key.encode()
```

**3. SSH Agent Integration (MikroTik)**
```python
import paramiko

def deploy_via_ssh(device_ip: str, config_file: str):
    """Deploy using SSH keys (no password)"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Use SSH agent for authentication
    ssh.connect(
        device_ip,
        username='admin',
        look_for_keys=True,  # Use SSH agent
        allow_agent=True
    )
    
    # Upload and import config
    sftp = ssh.open_sftp()
    sftp.put(config_file, '/flash/config.rsc')
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command('/import config.rsc')
    
    ssh.close()
```

**4. Vault Integration (Enterprise)**
```python
import hvac

class VaultCredentialProvider:
    def __init__(self, vault_addr: str, vault_token: str):
        self.client = hvac.Client(url=vault_addr, token=vault_token)
    
    def get_device_credentials(self, device_id: str):
        """Fetch credentials from HashiCorp Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=f"network-devices/{device_id}"
        )
        return secret['data']['data']
```

### Deployment Workflow

#### Interactive Deployment

```bash
./network-config deploy -i config.yaml -d 192.168.1.1 -u admin
Password: ********

🔐 Authenticating to 192.168.1.1...
✅ Authentication successful

📋 Configuration Summary:
   - 2 VLANs
   - 3 Firewall rules
   - 1 Wireless network

⚠️  This will modify the device configuration!

Create backup before deployment? [Y/n]: y
✅ Backup created: backup-20250115-143022.backup

Proceed with deployment? [y/N]: y

🚀 Deploying configuration...
   ✅ VLAN 10 configured
   ✅ VLAN 20 configured
   ✅ Firewall rules applied
   ✅ Wireless network created

🔍 Verifying deployment...
   ✅ Configuration verified

✅ Deployment completed successfully!

Backup location: /backups/backup-20250115-143022.backup
Rollback command: ./network-config rollback -d 192.168.1.1 -b backup-20250115-143022.backup
```

#### Automated Deployment (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy Network Configuration

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate Configuration
        run: |
          ./network-config validate -i production-config.yaml
      
      - name: Deploy to Production
        env:
          DEVICE_IP: ${{ secrets.DEVICE_IP }}
          DEVICE_USER: ${{ secrets.DEVICE_USER }}
          DEVICE_PASSWORD: ${{ secrets.DEVICE_PASSWORD }}
        run: |
          ./network-config deploy \
            -i production-config.yaml \
            -d $DEVICE_IP \
            -u $DEVICE_USER \
            --backup \
            --verify \
            --log-level debug
```

### Security Best Practices

#### 1. Network Security
- ✅ Deploy only from trusted networks (management VLAN)
- ✅ Use VPN for remote deployments
- ✅ Firewall rules to restrict API access
- ✅ Network segmentation (management network)

#### 2. Authentication
- ✅ Strong passwords (min 16 chars, complexity requirements)
- ✅ Multi-factor authentication (where supported)
- ✅ SSH keys instead of passwords (where possible)
- ✅ Regular credential rotation
- ✅ Principle of least privilege

#### 3. Audit and Logging
- ✅ Log all deployment attempts
- ✅ Track configuration changes
- ✅ Store logs securely (syslog, SIEM integration)
- ✅ Alert on deployment failures

```python
import logging
import syslog

class DeploymentLogger:
    def __init__(self):
        self.logger = logging.getLogger('network-config-deploy')
        
        # File logging
        fh = logging.FileHandler('/var/log/network-config/deploy.log')
        fh.setLevel(logging.INFO)
        
        # Syslog for SIEM integration
        sh = logging.handlers.SysLogHandler(address='/dev/log')
        sh.setLevel(logging.WARNING)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)
    
    def log_deployment(self, device_ip: str, user: str, 
                       config_hash: str, status: str):
        self.logger.info(
            f"DEPLOYMENT: device={device_ip} user={user} "
            f"config_hash={config_hash} status={status}"
        )
```

#### 4. Configuration Validation
- ✅ Dry-run mode (preview changes)
- ✅ Pre-deployment validation
- ✅ Post-deployment verification
- ✅ Automated rollback on failure

#### 5. Backup and Recovery
- ✅ Automatic backup before deployment
- ✅ Backup retention policy
- ✅ Quick rollback capability
- ✅ Disaster recovery procedures

### CLI Usage Examples

```bash
# Deploy with interactive prompts
./network-config deploy -i config.yaml -d 192.168.1.1 -u admin

# Deploy with environment variables (CI/CD)
export DEVICE_PASSWORD="$(vault read -field=password secret/device1)"
./network-config deploy -i config.yaml -d 192.168.1.1 -u admin

# Deploy with SSH keys (no password)
./network-config deploy -i config.yaml -d 192.168.1.1 --ssh-key ~/.ssh/id_rsa

# Deploy with backup and verification
./network-config deploy -i config.yaml -d 192.168.1.1 \
  --backup \
  --verify \
  --rollback-on-failure

# Dry-run (preview only)
./network-config deploy -i config.yaml -d 192.168.1.1 --dry-run

# Deploy with custom timeout
./network-config deploy -i config.yaml -d 192.168.1.1 --timeout 300

# Deploy to multiple devices
./network-config deploy -i config.yaml --devices devices.csv
```

### Compliance and Standards

- **PCI DSS**: Encrypted transmission, access logging
- **HIPAA**: Audit trails, access controls
- **SOC 2**: Security monitoring, change management
- **NIST**: Secure configuration management

## Migration Path

### Phase 3 Implementation Plan

1. **Milestone 1: MikroTik API Deployment**
   - Implement RouterOS API client
   - Add credential management
   - Create backup/restore functionality

2. **Milestone 2: SonicWall API Deployment**
   - Implement SonicWall REST API client
   - Add token-based authentication
   - Create rollback mechanism

3. **Milestone 3: UniFi API Deployment**
   - Implement UniFi Controller API client
   - Add site management
   - Create configuration verification

4. **Milestone 4: Security Hardening**
   - Add credential encryption
   - Implement audit logging
   - Add multi-factor authentication support

5. **Milestone 5: Enterprise Features**
   - Vault integration
   - SAML/OAuth support
   - Role-based access control

## Summary

**Current (Phase 1 & 2):** 
- ✅ Secure by design (no direct device access)
- ✅ Manual deployment with full user control
- ✅ No credential storage

**Future (Phase 3):**
- ✅ Optional automated deployment
- ✅ Multi-layer security (TLS, authentication, authorization)
- ✅ Comprehensive audit logging
- ✅ Automatic backup and rollback
- ✅ Enterprise credential management

**Security Philosophy:**
- Defense in depth
- Principle of least privilege
- Fail-safe defaults
- Complete audit trail
- User control and transparency

