"""
Abstract base class for vendor-specific generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import NetworkConfig


class VendorGenerator(ABC):
    """
    Base class for all vendor-specific configuration generators.

    Each vendor plugin must implement:
    - validate_config(): Vendor-specific validation
    - generate_config(): Generate vendor configuration files
    - deploy_config(): (Optional) Deploy to device via API
    """

    vendor_name: str = "unknown"
    supported_features: List[str] = []

    @abstractmethod
    def validate_config(self, config: NetworkConfig) -> List[str]:
        """
        Validate configuration for this vendor.

        Returns:
            List of error messages (empty if valid)
        """
        pass

    @abstractmethod
    def generate_config(self, config: NetworkConfig) -> Dict[str, str]:
        """
        Generate vendor-specific configuration files.

        Returns:
            Dict mapping filename to file content
        """
        pass

    def deploy_config(self, config: NetworkConfig, device_ip: str,
                     credentials: Dict[str, str]) -> bool:
        """
        Deploy configuration to device via API (optional).

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError(f"{self.vendor_name} API deployment not implemented")

    def get_capabilities(self, model: str) -> Dict[str, Any]:
        """
        Get device capabilities for specific model.

        Returns:
            Dict of capabilities
        """
        # TODO: Load from device_capabilities.yaml
        return {}

    def supports_feature(self, feature: str) -> bool:
        """Check if this vendor supports a feature"""
        return feature in self.supported_features
