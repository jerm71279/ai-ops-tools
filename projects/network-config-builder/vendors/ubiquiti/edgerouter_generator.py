"""
Ubiquiti EdgeRouter Configuration Generator - Placeholder

Full implementation coming soon.
"""

import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.models import NetworkConfig
from vendors.base import VendorGenerator


class EdgeRouterGenerator(VendorGenerator):
    """EdgeRouter generator - placeholder"""
    
    vendor_name = "edgerouter"
    supported_features = []
    
    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        raise NotImplementedError("EdgeRouter generator coming soon")
    
    def deploy_config(self, config: NetworkConfig, device_ip: str, credentials: Dict[str, str]) -> bool:
        raise NotImplementedError("EdgeRouter deployment not yet implemented")
