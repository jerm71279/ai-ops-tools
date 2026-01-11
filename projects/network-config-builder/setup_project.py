#!/usr/bin/env python3
"""
Network Config Builder - Complete Setup Script
Using patterns from automation-script-builder skill
"""

from pathlib import Path
import shutil

print("🚀 Setting up Multi-Vendor Network Config Builder")
print("=" * 80)
print()

base = Path("/home/mavrick/Projects/network-config-builder")

# Step 1: Create core Python modules using automation patterns
print("📝 Creating core framework modules...")

# core/__init__.py
(base / "core/__init__.py").write_text('''"""
Network Config Builder - Core Framework
Multi-vendor network device configuration generation platform.
"""

__version__ = "0.1.0"
__author__ = "Obera Connect"

from .models import NetworkConfig, VendorType
from .validators import ConfigValidator
from .exceptions import ValidationError

__all__ = ['NetworkConfig', 'VendorType', 'ConfigValidator', 'ValidationError']
''')
print("   ✅ core/__init__.py")

# Mark IO as package
(base / "io/__init__.py").write_text('')
(base / "io/readers/__init__.py").write_text('''"""CSV and configuration readers"""
from .csv_template_reader import read_field_value_csv
__all__ = ['read_field_value_csv']
''')
(base / "io/writers/__init__.py").write_text('')
print("   ✅ io packages")

# CLI __init__
(base / "cli/__init__.py").write_text('')
print("   ✅ cli package")

# Vendors __init__
(base / "vendors/__init__.py").write_text('''"""Vendor-specific configuration generators"""''')
(base / "vendors/mikrotik/__init__.py").write_text('')
(base / "vendors/sonicwall/__init__.py").write_text('')
(base / "vendors/ubiquiti/__init__.py").write_text('')
(base / "vendors/ubiquiti/unifi/__init__.py").write_text('')
(base / "vendors/ubiquiti/edgerouter/__init__.py").write_text('')
print("   ✅ vendor packages")

# Step 2: Create quick start script
quickstart = base / "quickstart.py"
quickstart.write_text('''#!/usr/bin/env python3
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
''')
quickstart.chmod(0o755)
print("   ✅ quickstart.py")

# Step 3: Create build script
build_script = base / "build_framework.py"
build_script.write_text('''#!/usr/bin/env python3
"""
Build the core framework Python modules
"""
print("🏗️  Building network-config-builder framework...")
print("This will create all core Python modules with working code.")
print()
print("⚠️  This is a placeholder - actual framework build coming next!")
''')
build_script.chmod(0o755)
print("   ✅ build_framework.py")

# Step 4: Update requirements
requirements = base / "requirements.txt"
requirements.write_text('''# Core dependencies
pyyaml>=6.0
jinja2>=3.1.0
click>=8.1.0
python-dotenv>=1.0.0

# Vendor API clients (optional)
# librouteros>=3.2.0  # MikroTik API
# pyunifi>=2.26       # UniFi Controller API

# Development
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
pylint>=3.0.0
mypy>=1.5.0
''')
print("   ✅ requirements.txt")

print()
print("✅ Project setup complete!")
print()
print(f"📂 Location: {base}")
print()
print("📋 Next steps:")
print("  1. python3 quickstart.py - See getting started guide")
print("  2. python3 build_framework.py - Build framework modules")
print("  3. cd examples/ - Explore sample configurations")
print()

