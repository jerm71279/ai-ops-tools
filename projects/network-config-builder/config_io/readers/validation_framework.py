#!/usr/bin/env python3
"""
Validation Framework
Reusable validation helpers for automation scripts.
"""

import ipaddress
import re
from typing import Any, Callable, List


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validator:
    """Chainable validator for building validation logic."""
    
    def __init__(self, value: Any, field_name: str = "field"):
        self.value = value
        self.field_name = field_name
        self.errors: List[str] = []
    
    def required(self, message: str = None) -> 'Validator':
        """Validate field is not empty."""
        if not self.value or (isinstance(self.value, str) and not self.value.strip()):
            msg = message or f"{self.field_name} is required"
            self.errors.append(msg)
        return self
    
    def is_ipv4(self, message: str = None) -> 'Validator':
        """Validate value is a valid IPv4 address."""
        try:
            ipaddress.IPv4Address(str(self.value))
        except Exception:
            msg = message or f"{self.field_name} must be a valid IPv4 address"
            self.errors.append(msg)
        return self
    
    def is_cidr(self, message: str = None) -> 'Validator':
        """Validate value is a valid CIDR notation."""
        try:
            ipaddress.IPv4Network(str(self.value), strict=False)
        except Exception:
            msg = message or f"{self.field_name} must be valid CIDR notation"
            self.errors.append(msg)
        return self
    
    def is_email(self, message: str = None) -> 'Validator':
        """Validate value is a valid email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, str(self.value)):
            msg = message or f"{self.field_name} must be a valid email address"
            self.errors.append(msg)
        return self
    
    def min_length(self, min_len: int, message: str = None) -> 'Validator':
        """Validate minimum string length."""
        if len(str(self.value)) < min_len:
            msg = message or f"{self.field_name} must be at least {min_len} characters"
            self.errors.append(msg)
        return self
    
    def max_length(self, max_len: int, message: str = None) -> 'Validator':
        """Validate maximum string length."""
        if len(str(self.value)) > max_len:
            msg = message or f"{self.field_name} must be at most {max_len} characters"
            self.errors.append(msg)
        return self
    
    def matches_regex(self, pattern: str, message: str = None) -> 'Validator':
        """Validate value matches regex pattern."""
        if not re.match(pattern, str(self.value)):
            msg = message or f"{self.field_name} must match pattern {pattern}"
            self.errors.append(msg)
        return self
    
    def one_of(self, allowed_values: List[Any], message: str = None) -> 'Validator':
        """Validate value is in allowed list."""
        if self.value not in allowed_values:
            msg = message or f"{self.field_name} must be one of: {', '.join(map(str, allowed_values))}"
            self.errors.append(msg)
        return self
    
    def custom(self, validator_func: Callable[[Any], bool], message: str) -> 'Validator':
        """Apply custom validation function."""
        try:
            if not validator_func(self.value):
                self.errors.append(message)
        except Exception as e:
            self.errors.append(f"{self.field_name} validation error: {str(e)}")
        return self
    
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self.errors


def validate_field(value: Any, field_name: str) -> Validator:
    """
    Create a new validator for a field.
    
    Example:
        errors = validate_field(email, "Email").required().is_email().get_errors()
    """
    return Validator(value, field_name)


def collect_errors(*validators: Validator) -> List[str]:
    """
    Collect errors from multiple validators.
    
    Example:
        errors = collect_errors(
            validate_field(name, "Name").required(),
            validate_field(email, "Email").required().is_email()
        )
    """
    all_errors = []
    for validator in validators:
        all_errors.extend(validator.get_errors())
    return all_errors
