"""
Custom exceptions for network config builder.
"""


class NetworkConfigError(Exception):
    """Base exception for all config errors"""
    pass


class ValidationError(NetworkConfigError):
    """Configuration validation failed"""

    def __init__(self, message, field=None, value=None, suggestion=None):
        self.field = field
        self.value = value
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.field:
            msg += f"\n  Field: {self.field}"
        if self.value:
            msg += f"\n  Value: {self.value}"
        if self.suggestion:
            msg += f"\n  Suggestion: {self.suggestion}"
        return msg


class GenerationError(NetworkConfigError):
    """Configuration generation failed"""
    pass


class DeploymentError(NetworkConfigError):
    """Configuration deployment failed"""
    pass


class UnsupportedVendorError(NetworkConfigError):
    """Vendor not supported"""
    pass


class UnsupportedFeatureError(NetworkConfigError):
    """Feature not supported by this vendor/device"""
    pass
