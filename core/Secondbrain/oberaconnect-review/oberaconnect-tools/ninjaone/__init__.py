"""
OberaConnect Tools - NinjaOne Module

NinjaOne RMM integration with cross-platform correlation.

Features:
- NinjaOne API client
- Alert and device management
- Cross-platform correlation with UniFi
"""

from .client import (
    NinjaOneAPIError,
    NinjaOneConfig,
    NinjaOneAlert,
    NinjaOneDevice,
    NinjaOneOrg,
    NinjaOneClient,
    DemoNinjaOneClient,
    get_client
)

from .correlator import (
    CorrelatedIncident,
    Correlator
)

__all__ = [
    # Client
    'NinjaOneAPIError',
    'NinjaOneConfig',
    'NinjaOneAlert',
    'NinjaOneDevice',
    'NinjaOneOrg',
    'NinjaOneClient',
    'DemoNinjaOneClient',
    'get_client',
    # Correlator
    'CorrelatedIncident',
    'Correlator'
]
