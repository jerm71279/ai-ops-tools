#!/usr/bin/env python3
"""
Quick Start - Generate your first configuration

Usage:
    python3 quickstart.py
"""

print("""
🌐 Multi-Vendor Network Config Builder
================================================================================

Welcome! This tool helps you generate configurations for:
  • MikroTik RouterOS (routers, APs, switches)
  • SonicWall SonicOS (firewalls, UTM, VPN)
  • Ubiquiti UniFi/EdgeRouter (SMB networking, WiFi)

📋 Getting Started:
  1. Look at examples in examples/mikrotik/basic_router.yaml
  2. Create your own YAML configuration
  3. Run: ./network-config generate --input yourconfig.yaml

📖 Documentation:
  - README.md - Overview and quick start
  - docs/ARCHITECTURE.md - System design
  - docs/VENDOR_COMPARISON.md - Vendor capabilities
  - examples/ - Sample configurations

🔧 Current Status: Phase 1 (Core Framework)
  [x] Project structure
  [x] Core models
  [ ] Template system (coming soon)
  [ ] CLI (coming soon)

🚧 TO BUILD THE FRAMEWORK, RUN:
    python3 build_framework.py

================================================================================
""")
