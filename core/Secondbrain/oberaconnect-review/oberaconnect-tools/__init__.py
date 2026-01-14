"""
OberaConnect Tools

Unified tooling for OberaConnect MSP operations.

Modules:
- common: Validation framework and maker/checker patterns
- unifi: UniFi Site Manager integration with NL query engine
- ninjaone: NinjaOne RMM integration with correlation
- n8n: REST API for workflow automation

Quick Start:
    from oberaconnect_tools.unifi import get_client, UniFiAnalyzer
    
    client = get_client(demo=True)
    sites = client.get_sites()
    
    analyzer = UniFiAnalyzer(sites)
    result = analyzer.analyze("show sites with offline devices")
    print(result.message)
"""

__version__ = '1.0.0'
__author__ = 'OberaConnect'

# Convenience imports
from .common import validate_operation, RiskLevel, CheckResult
from .unifi import get_client as get_unifi_client, UniFiAnalyzer
from .ninjaone import get_client as get_ninjaone_client, Correlator

__all__ = [
    '__version__',
    # Common
    'validate_operation',
    'RiskLevel',
    'CheckResult',
    # UniFi
    'get_unifi_client',
    'UniFiAnalyzer',
    # NinjaOne
    'get_ninjaone_client',
    'Correlator'
]
