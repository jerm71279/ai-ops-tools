"""
Ubiquiti configuration generators.
"""

from .unifi_generator import UniFiGenerator
from .edgerouter_generator import EdgeRouterGenerator

__all__ = ['UniFiGenerator', 'EdgeRouterGenerator']
