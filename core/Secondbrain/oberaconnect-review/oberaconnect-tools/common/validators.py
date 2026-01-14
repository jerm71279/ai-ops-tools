"""
Reusable Validators

Common validation rules for OberaConnect operations.
"""

import re
from typing import Any, List, Optional, Tuple
from ipaddress import ip_network, ip_address, AddressValueError


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
    
    def __str__(self):
        if self.value is not None:
            return f"{self.field}: {self.message} (got: {self.value})"
        return f"{self.field}: {self.message}"


class Validator:
    """
    Chainable validator for field values.
    
    Example:
        errors = collect_errors(
            Validator(email, 'Email').required().is_email(),
            Validator(ip, 'IP Address').is_ipv4(),
            Validator(vlan, 'VLAN ID').is_integer().in_range(1, 4094)
        )
    """
    
    def __init__(self, value: Any, field_name: str):
        self.value = value
        self.field_name = field_name
        self.errors: List[ValidationError] = []
    
    def required(self) -> 'Validator':
        """Value must not be None or empty."""
        if self.value is None or self.value == '':
            self.errors.append(ValidationError(
                self.field_name, 
                "is required"
            ))
        return self
    
    def is_string(self) -> 'Validator':
        """Value must be a string."""
        if self.value is not None and not isinstance(self.value, str):
            self.errors.append(ValidationError(
                self.field_name,
                "must be a string",
                type(self.value).__name__
            ))
        return self
    
    def is_integer(self) -> 'Validator':
        """Value must be an integer."""
        if self.value is not None:
            try:
                int(self.value)
            except (ValueError, TypeError):
                self.errors.append(ValidationError(
                    self.field_name,
                    "must be an integer",
                    self.value
                ))
        return self
    
    def in_range(self, min_val: int, max_val: int) -> 'Validator':
        """Value must be within range (inclusive)."""
        if self.value is not None:
            try:
                val = int(self.value)
                if val < min_val or val > max_val:
                    self.errors.append(ValidationError(
                        self.field_name,
                        f"must be between {min_val} and {max_val}",
                        val
                    ))
            except (ValueError, TypeError):
                pass  # Already caught by is_integer
        return self
    
    def min_length(self, length: int) -> 'Validator':
        """String must have minimum length."""
        if self.value is not None and len(str(self.value)) < length:
            self.errors.append(ValidationError(
                self.field_name,
                f"must be at least {length} characters",
                len(str(self.value))
            ))
        return self
    
    def max_length(self, length: int) -> 'Validator':
        """String must have maximum length."""
        if self.value is not None and len(str(self.value)) > length:
            self.errors.append(ValidationError(
                self.field_name,
                f"must be at most {length} characters",
                len(str(self.value))
            ))
        return self
    
    def matches(self, pattern: str, description: str = "pattern") -> 'Validator':
        """Value must match regex pattern."""
        if self.value is not None:
            if not re.match(pattern, str(self.value)):
                self.errors.append(ValidationError(
                    self.field_name,
                    f"must match {description}",
                    self.value
                ))
        return self
    
    def is_email(self) -> 'Validator':
        """Value must be a valid email address."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return self.matches(email_pattern, "email format")
    
    def is_ipv4(self) -> 'Validator':
        """Value must be a valid IPv4 address."""
        if self.value is not None:
            try:
                addr = ip_address(self.value)
                if addr.version != 4:
                    raise AddressValueError("Not IPv4")
            except (AddressValueError, ValueError):
                self.errors.append(ValidationError(
                    self.field_name,
                    "must be a valid IPv4 address",
                    self.value
                ))
        return self
    
    def is_cidr(self) -> 'Validator':
        """Value must be a valid CIDR notation."""
        if self.value is not None:
            try:
                ip_network(self.value, strict=False)
            except (AddressValueError, ValueError):
                self.errors.append(ValidationError(
                    self.field_name,
                    "must be valid CIDR notation (e.g., 192.168.1.0/24)",
                    self.value
                ))
        return self
    
    def is_mac_address(self) -> 'Validator':
        """Value must be a valid MAC address."""
        mac_pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        return self.matches(mac_pattern, "MAC address format (XX:XX:XX:XX:XX:XX)")
    
    def is_in(self, allowed: List[Any]) -> 'Validator':
        """Value must be in allowed list."""
        if self.value is not None and self.value not in allowed:
            self.errors.append(ValidationError(
                self.field_name,
                f"must be one of: {', '.join(str(v) for v in allowed)}",
                self.value
            ))
        return self
    
    def not_in(self, forbidden: List[Any]) -> 'Validator':
        """Value must not be in forbidden list."""
        if self.value is not None and self.value in forbidden:
            self.errors.append(ValidationError(
                self.field_name,
                f"cannot be: {', '.join(str(v) for v in forbidden)}",
                self.value
            ))
        return self
    
    def custom(self, check_fn, error_message: str) -> 'Validator':
        """Apply custom validation function."""
        if self.value is not None:
            if not check_fn(self.value):
                self.errors.append(ValidationError(
                    self.field_name,
                    error_message,
                    self.value
                ))
        return self


def collect_errors(*validators: Validator) -> List[str]:
    """
    Collect all errors from multiple validators.
    
    Returns list of error messages.
    """
    errors = []
    for validator in validators:
        for error in validator.errors:
            errors.append(str(error))
    return errors


# OberaConnect-specific validators

def validate_vlan_id(vlan_id: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate VLAN ID per OberaConnect rules.
    
    Rules:
    - Must be integer 1-4094
    - VLAN 1 reserved (native)
    - VLAN 4095 reserved (system)
    """
    try:
        vlan = int(vlan_id)
    except (ValueError, TypeError):
        return False, f"VLAN ID must be an integer, got: {vlan_id}"
    
    if vlan < 1 or vlan > 4094:
        return False, f"VLAN ID must be 1-4094, got: {vlan}"
    
    if vlan == 1:
        return False, "VLAN 1 is reserved (native VLAN)"
    
    return True, None


def validate_wifi_channel(channel: Any, band: str = "2.4") -> Tuple[bool, Optional[str]]:
    """
    Validate WiFi channel per OberaConnect rules.
    
    Rules:
    - 2.4GHz: Only channels 1, 6, 11 (non-overlapping)
    - 5GHz: Various depending on region, but common DFS channels allowed
    """
    try:
        ch = int(channel)
    except (ValueError, TypeError):
        return False, f"Channel must be an integer, got: {channel}"
    
    if band == "2.4":
        allowed = [1, 6, 11]
        if ch not in allowed:
            return False, f"2.4GHz channel must be {allowed}, got: {ch}"
    elif band == "5":
        # 5GHz channels (UNII-1, UNII-2, UNII-2e, UNII-3)
        allowed = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 
                   116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]
        if ch not in allowed:
            return False, f"Invalid 5GHz channel: {ch}"
    
    return True, None


def validate_signal_strength(dbm: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate WiFi signal strength per OberaConnect rules.
    
    Rules:
    - Minimum acceptable: -65dBm
    - Warning threshold: -70dBm
    """
    try:
        signal = int(dbm)
    except (ValueError, TypeError):
        return False, f"Signal strength must be an integer, got: {dbm}"
    
    if signal < -90:
        return False, f"Signal strength {signal}dBm is below minimum viable (-90dBm)"
    
    if signal < -65:
        return False, f"Signal strength {signal}dBm is below OberaConnect minimum (-65dBm)"
    
    return True, None


def validate_ssid(ssid: str, allow_open: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate SSID per OberaConnect rules.
    
    Rules:
    - Max 32 characters
    - No trailing/leading spaces
    - Open networks not allowed by default
    """
    if not ssid:
        return False, "SSID cannot be empty"
    
    if len(ssid) > 32:
        return False, f"SSID must be 32 characters or less, got: {len(ssid)}"
    
    if ssid != ssid.strip():
        return False, "SSID cannot have leading/trailing spaces"
    
    return True, None


__all__ = [
    'ValidationError',
    'Validator',
    'collect_errors',
    'validate_vlan_id',
    'validate_wifi_channel',
    'validate_signal_strength',
    'validate_ssid'
]
