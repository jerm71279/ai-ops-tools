# MikroTik Configuration Builder - Improvement Roadmap

## Executive Summary

This document outlines the planned improvements to transform the original single-file script into a modular, extensible, production-grade MikroTik configuration generation system.

## Design Principles

1. **Separation of Concerns** - Clear boundaries between validation, generation, I/O
2. **Template-Driven** - Use Jinja2 templates for all RouterOS script generation
3. **Extensibility** - Plugin architecture for new features
4. **Type Safety** - Use Python dataclasses and type hints throughout
5. **Testability** - 80%+ code coverage with unit and integration tests
6. **User-Friendly** - Multiple input formats, clear error messages, interactive modes
7. **Production-Ready** - Logging, dry-run, validation-only, versioning

## Phase 1: Foundation (Priority: HIGH)

### 1.1 Modular Architecture

**Goal:** Break monolithic script into maintainable modules

**Deliverables:**
- `core/models.py` - Dataclass models for all configuration objects
  - `CustomerData` - Customer information
  - `WANConfig` - WAN interface settings
  - `LANConfig` - LAN bridge and addressing
  - `DHCPConfig` - DHCP server settings
  - `WirelessConfig` - Wi-Fi settings
  - `SecurityConfig` - Admin access, hardening
  - `RouterConfig` - Complete router configuration

- `core/validators.py` - Modular validation classes
  - `IPValidator` - IP address and subnet validation
  - `NetworkValidator` - Network topology validation
  - `SecurityValidator` - Security policy validation
  - `ConfigValidator` - Orchestrates all validators

- `core/exceptions.py` - Custom exception types
  - `ValidationError` - Input validation failures
  - `GenerationError` - Script generation failures
  - `ConfigurationError` - Configuration object errors

**Timeline:** 3-4 days

**Dependencies:** None

### 1.2 Template System

**Goal:** Replace string concatenation with Jinja2 templates

**Deliverables:**
- Template directory structure in `templates/`
- Base templates for common patterns
  - `templates/base/header.j2` - Script headers
  - `templates/base/footer.j2` - Script footers
- Router templates
  - `templates/router/wan.j2` - WAN interface configuration
  - `templates/router/lan.j2` - LAN bridge configuration
  - `templates/router/dhcp.j2` - DHCP server setup
  - `templates/router/nat.j2` - NAT rules
  - `templates/router/admin.j2` - Admin user creation
  - `templates/router/hardening.j2` - Security hardening
- Wireless templates
  - `templates/wireless/legacy.j2` - Legacy wireless interface
  - `templates/wireless/wifi6.j2` - Modern wifi package
- Template renderer with proper escaping and validation

**Timeline:** 3-4 days

**Dependencies:** 1.1 (models)

### 1.3 Input Format Expansion

**Goal:** Support YAML and JSON in addition to CSV

**Deliverables:**
- `io/csv_reader.py` - Refactored CSV reader
- `io/yaml_reader.py` - YAML configuration reader
- `io/json_reader.py` - JSON configuration reader
- `io/base_reader.py` - Abstract base class for readers
- Auto-detection of input format based on file extension
- Schema validation for YAML/JSON (using jsonschema)

**Example YAML structure:**
```yaml
customer:
  name: OberaMain
  site: Main Office

deployment:
  type: router_and_ap
  device_model: RB4011

wan:
  ip: 192.0.2.10
  netmask: 24
  gateway: 192.0.2.1

lan:
  bridge_name: bridge-lan
  ip: 192.168.88.1
  netmask: 24
  dhcp:
    pool_start: 192.168.88.100
    pool_end: 192.168.88.200
    lease_time: 12h
  dns_servers:
    - 8.8.8.8
    - 8.8.4.4

wireless:
  ssid: OberaGuest
  password: SecurePass123
  band: 2ghz-b/g/n
  channel_width: 20mhz
  country: us

security:
  admin_username: oberadmin
  admin_password: SuperSecure!
  allowed_ips:
    - 192.168.1.0/24
    - 10.0.0.0/8

features:
  winbox: true
  ssh: true
  stun: true
  throughput_test: true
```

**Timeline:** 2-3 days

**Dependencies:** 1.1 (models)

### 1.4 Testing Infrastructure

**Goal:** Establish comprehensive testing framework

**Deliverables:**
- pytest configuration
- Test fixtures for common scenarios
  - `tests/fixtures/valid_configs.yaml` - Valid test data
  - `tests/fixtures/invalid_configs.yaml` - Invalid test data
- Unit tests
  - `tests/test_validators.py` - All validation logic
  - `tests/test_models.py` - Data class behavior
  - `tests/test_readers.py` - Input parsing
- Integration tests
  - `tests/integration/test_generation.py` - End-to-end generation
  - `tests/integration/test_templates.py` - Template rendering
- Mock RouterOS environment for testing
- Code coverage reporting (target: 80%+)

**Timeline:** 4-5 days

**Dependencies:** 1.1, 1.2, 1.3

### 1.5 CLI Enhancement

**Goal:** Better command-line interface with multiple modes

**Deliverables:**
- `cli/commands.py` - Click-based CLI
  - `generate` - Generate configuration scripts
  - `validate` - Validate input only (no generation)
  - `interactive` - Interactive wizard mode
  - `dry-run` - Preview output without writing files
- `cli/interactive.py` - Interactive questionnaire
- Progress bars for long operations
- Colored output for errors/warnings/success
- Verbose and quiet modes

**Example usage:**
```bash
# Generate from YAML
mikrotik-builder generate --input customer.yaml --output ./configs/

# Validation only
mikrotik-builder validate --input customer.yaml

# Interactive mode
mikrotik-builder interactive

# Dry-run (preview)
mikrotik-builder generate --input customer.yaml --dry-run

# Verbose output
mikrotik-builder generate --input customer.yaml -v
```

**Timeline:** 2-3 days

**Dependencies:** 1.1, 1.2, 1.3

**Phase 1 Total Timeline:** 2-3 weeks

## Phase 2: Feature Expansion (Priority: MEDIUM)

### 2.1 VLAN Support

**Goal:** Configure VLANs on bridge and interfaces

**Deliverables:**
- VLAN configuration model
- VLAN validation (ID range, conflicts)
- Templates for:
  - VLAN creation
  - VLAN interface assignment
  - Bridge VLAN filtering
  - Inter-VLAN routing
  - DHCP per VLAN

**YAML Example:**
```yaml
vlans:
  - id: 10
    name: Management
    subnet: 192.168.10.0/24
    dhcp:
      enabled: true
      pool_start: 192.168.10.100
      pool_end: 192.168.10.200
  - id: 20
    name: Guest
    subnet: 192.168.20.0/24
    dhcp:
      enabled: true
      pool_start: 192.168.20.100
      pool_end: 192.168.20.200
    isolation: true
  - id: 30
    name: IoT
    subnet: 192.168.30.0/24
    dhcp:
      enabled: true
      pool_start: 192.168.30.100
      pool_end: 192.168.30.200
```

**Timeline:** 4-5 days

**Dependencies:** Phase 1 complete

### 2.2 Modern Wireless (Wi-Fi 6)

**Goal:** Support `/interface wifi` for AX/Wave2 devices

**Deliverables:**
- Wireless mode detection (legacy vs modern)
- Wi-Fi 6 configuration model
- Templates for:
  - `/interface wifi` configuration
  - Multiple SSIDs per radio
  - 5GHz band support
  - Guest network isolation
  - WPA3 security profiles

**YAML Example:**
```yaml
wireless:
  mode: wifi6  # or 'legacy'
  radios:
    - name: wifi1
      band: 2ghz
      channel: auto
      channel_width: 20mhz
      country: us
      ssids:
        - name: OberaMain
          password: SecurePass123
          security: wpa2-psk
          vlan: 10
        - name: OberaGuest
          password: GuestPass456
          security: wpa2-psk
          vlan: 20
          isolation: true
    - name: wifi2
      band: 5ghz
      channel: auto
      channel_width: 40mhz
      country: us
      ssids:
        - name: OberaMain-5G
          password: SecurePass123
          security: wpa3-psk
          vlan: 10
```

**Timeline:** 5-6 days

**Dependencies:** Phase 1 complete

### 2.3 Advanced Firewall

**Goal:** Comprehensive firewall rule generation

**Deliverables:**
- Firewall rule model (action, chain, protocol, ports, etc.)
- Rule validation and conflict detection
- Templates for:
  - Port forwarding rules
  - Input chain filtering
  - Forward chain filtering
  - Address lists
  - Custom chains
- Preset rule sets:
  - Basic protection
  - Advanced protection
  - Guest network isolation
  - IoT device restrictions

**YAML Example:**
```yaml
firewall:
  preset: advanced_protection  # basic | advanced | custom

  port_forwarding:
    - name: Web Server
      protocol: tcp
      dst_port: 80
      to_address: 192.168.10.50
      to_port: 80
    - name: SSH Server
      protocol: tcp
      dst_port: 2222
      to_address: 192.168.10.50
      to_port: 22

  custom_rules:
    - chain: input
      protocol: icmp
      action: accept
      comment: Allow ping
    - chain: input
      protocol: tcp
      dst_port: 8291
      src_address: 10.0.0.0/8
      action: accept
      comment: WinBox from VPN only
```

**Timeline:** 5-6 days

**Dependencies:** Phase 1 complete

### 2.4 VPN Support

**Goal:** Generate VPN configurations

**Deliverables:**
- VPN configuration models
- VPN type validation
- Templates for:
  - IPsec site-to-site
  - IPsec road warrior
  - WireGuard server
  - WireGuard client
  - L2TP/IPsec server
  - PPTP server (with warnings)

**YAML Example:**
```yaml
vpn:
  wireguard:
    enabled: true
    interface: wireguard1
    listen_port: 51820
    private_key: "{{ vault.wg_private_key }}"
    address: 10.10.10.1/24
    peers:
      - name: Remote Office
        public_key: "abcd1234..."
        allowed_ips:
          - 10.10.10.2/32
          - 192.168.50.0/24
      - name: Mobile User
        public_key: "efgh5678..."
        allowed_ips:
          - 10.10.10.10/32

  ipsec:
    enabled: true
    mode: site-to-site
    peer: 203.0.113.50
    local_subnet: 192.168.88.0/24
    remote_subnet: 192.168.99.0/24
    preshared_key: "{{ vault.ipsec_key }}"
```

**Timeline:** 6-7 days

**Dependencies:** Phase 1 complete, 2.3 (firewall)

**Phase 2 Total Timeline:** 3-4 weeks

## Phase 3: Operations & Quality (Priority: MEDIUM)

### 3.1 Dry-Run & Preview

**Goal:** Preview configurations without writing files

**Deliverables:**
- Dry-run mode that shows:
  - What files would be created
  - File contents preview
  - Validation results
  - Warnings and suggestions
- Syntax highlighting for RouterOS scripts
- Diff view for updates to existing files

**Timeline:** 2-3 days

**Dependencies:** Phase 1 complete

### 3.2 Enhanced Validation & Warnings

**Goal:** Better error messages and proactive warnings

**Deliverables:**
- Contextual error messages with:
  - Exact location (line number for YAML/JSON)
  - What's wrong
  - Suggested fix
  - Link to documentation
- Warning system for:
  - Weak passwords
  - Insecure configurations
  - Performance concerns
  - Best practice violations
- Network topology validation:
  - IP conflict detection
  - Overlapping subnets
  - Gateway reachability
  - DHCP pool exhaustion warnings

**Example output:**
```
ERROR: Invalid IP address in WAN configuration
  File: customer.yaml
  Line: 12
  Field: wan.ip
  Value: "192.0.2.999"
  Problem: Octet '999' is out of range (0-255)
  Fix: Use a valid IP address like "192.0.2.10"
  Docs: https://docs.example.com/wan-config

WARNING: Weak wireless password
  File: customer.yaml
  Line: 28
  Field: wireless.password
  Value: "password123"
  Problem: Password is common and easily guessable
  Suggestion: Use at least 16 characters with mixed case, numbers, symbols
  Docs: https://docs.example.com/wireless-security
```

**Timeline:** 3-4 days

**Dependencies:** Phase 1 complete

### 3.3 Configuration Versioning

**Goal:** Track configuration versions and changes

**Deliverables:**
- Git integration for automatic commits
- Version metadata in generated files
- Change tracking:
  - Who generated the config
  - When it was generated
  - What input file was used
  - What version of the tool
- Diff between versions
- Rollback capability

**Timeline:** 3-4 days

**Dependencies:** Phase 1 complete

### 3.4 Documentation Generation

**Goal:** Auto-generate documentation for configurations

**Deliverables:**
- Markdown documentation generator
- HTML documentation generator (using Jinja2)
- Documentation includes:
  - Network topology diagram (text-based)
  - IP address plan
  - VLAN summary
  - Firewall rules summary
  - Admin access information
  - Deployment notes
- Export to PDF (using markdown-pdf)

**Timeline:** 4-5 days

**Dependencies:** Phase 1 complete

**Phase 3 Total Timeline:** 2-3 weeks

## Phase 4: Advanced Features (Priority: LOW)

### 4.1 Web Interface

**Goal:** Browser-based configuration builder

**Stack:** Flask or FastAPI + Bootstrap 5

**Deliverables:**
- Form-based data entry
- Real-time validation
- Preview panel
- Download generated configs
- Multi-customer management
- Template library

**Timeline:** 2-3 weeks

**Dependencies:** Phase 1-3 complete

### 4.2 REST API

**Goal:** Programmatic access for integrations

**Deliverables:**
- RESTful API using FastAPI
- Endpoints:
  - POST /validate - Validate configuration
  - POST /generate - Generate scripts
  - GET /templates - List available templates
  - GET /docs - API documentation
- OpenAPI/Swagger documentation
- Authentication (API keys)
- Rate limiting

**Timeline:** 1-2 weeks

**Dependencies:** Phase 1-3 complete

### 4.3 MikroTik API Integration

**Goal:** Direct deployment to devices

**Deliverables:**
- MikroTik API client using librouteros
- Commands:
  - `deploy` - Apply configuration to device
  - `backup` - Backup current config
  - `rollback` - Revert to previous config
- Pre-deployment validation
- Post-deployment verification
- Change tracking

**Timeline:** 2-3 weeks

**Dependencies:** Phase 1-3 complete

## Quick Wins (Can be done anytime)

1. **Better README** - Comprehensive documentation with examples
2. **Field reference guide** - Document all supported fields
3. **Example configurations** - Library of common scenarios
4. **Migration guide** - How to migrate from old script
5. **Troubleshooting guide** - Common issues and solutions
6. **Video tutorials** - Screen recordings for common tasks

## Success Metrics

### Code Quality
- [ ] 80%+ test coverage
- [ ] All public functions documented
- [ ] Type hints on all functions
- [ ] Pass pylint with score > 8.0
- [ ] Pass mypy strict mode
- [ ] Black formatted

### Features
- [ ] Support CSV, YAML, JSON input
- [ ] Generate router-only configs
- [ ] Generate AP-only configs
- [ ] Generate combined configs
- [ ] Support VLANs
- [ ] Support modern wireless
- [ ] Support advanced firewall
- [ ] Support VPN configurations

### User Experience
- [ ] Clear error messages with context
- [ ] Interactive wizard mode
- [ ] Dry-run capability
- [ ] Generated configs work first time
- [ ] Documentation covers all features
- [ ] < 5 minutes from install to first config

### Operations
- [ ] Version tracking
- [ ] Change auditing
- [ ] Rollback capability
- [ ] Automated testing in CI/CD
- [ ] Docker container available

## Implementation Order (Recommended)

### Sprint 1 (Week 1-2): Foundation
1. Modular architecture (1.1)
2. Template system (1.2)
3. CLI enhancement basics (1.5 - partial)

### Sprint 2 (Week 3): Input & Testing
1. YAML/JSON support (1.3)
2. Testing infrastructure (1.4)
3. Complete CLI enhancement (1.5)

### Sprint 3 (Week 4-5): Core Features
1. VLAN support (2.1)
2. Modern wireless (2.2)
3. Dry-run mode (3.1)

### Sprint 4 (Week 6-7): Advanced Features
1. Advanced firewall (2.3)
2. Enhanced validation (3.2)
3. VPN support (2.4)

### Sprint 5 (Week 8): Polish & Documentation
1. Configuration versioning (3.3)
2. Documentation generation (3.4)
3. Examples and guides (Quick Wins)

### Future Sprints: Enterprise
1. Web interface (4.1)
2. REST API (4.2)
3. MikroTik API integration (4.3)

## Risk Management

### Technical Risks
- **Jinja2 learning curve** - Mitigation: Start with simple templates
- **Test complexity** - Mitigation: Build incrementally, one module at a time
- **RouterOS API changes** - Mitigation: Version-specific templates

### Schedule Risks
- **Scope creep** - Mitigation: Stick to roadmap, defer nice-to-haves
- **Testing taking longer** - Mitigation: Parallel development and testing

## Conclusion

This roadmap transforms a 462-line single-file script into a professional-grade tool with:
- **10-15x better maintainability** (modular vs monolithic)
- **5x more features** (VLANs, VPN, modern wireless, etc.)
- **100x better UX** (interactive, YAML, validation, etc.)
- **∞ better quality** (from 0% to 80%+ test coverage)

**Total estimated effort:** 8-10 weeks for phases 1-3, then ongoing for phase 4.
