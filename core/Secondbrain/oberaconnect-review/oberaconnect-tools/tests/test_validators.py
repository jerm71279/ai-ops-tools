"""
Tests for Reusable Validators.

Tests:
- Chainable validator patterns
- OberaConnect-specific validations (VLAN, WiFi, signal)
- Error collection
"""

import pytest


class TestValidator:
    """Tests for the chainable Validator class."""

    def test_required_validation(self):
        """Test required field validation."""
        from common.validators import Validator

        # Valid value
        v = Validator("test", "field").required()
        assert len(v.errors) == 0

        # Empty string
        v = Validator("", "field").required()
        assert len(v.errors) == 1

        # None
        v = Validator(None, "field").required()
        assert len(v.errors) == 1

    def test_is_string_validation(self):
        """Test string type validation."""
        from common.validators import Validator

        v = Validator("hello", "field").is_string()
        assert len(v.errors) == 0

        v = Validator(123, "field").is_string()
        assert len(v.errors) == 1

    def test_is_integer_validation(self):
        """Test integer validation."""
        from common.validators import Validator

        v = Validator(42, "field").is_integer()
        assert len(v.errors) == 0

        v = Validator("42", "field").is_integer()
        assert len(v.errors) == 0

        v = Validator("not a number", "field").is_integer()
        assert len(v.errors) == 1

    def test_in_range_validation(self):
        """Test range validation."""
        from common.validators import Validator

        v = Validator(50, "field").in_range(1, 100)
        assert len(v.errors) == 0

        v = Validator(0, "field").in_range(1, 100)
        assert len(v.errors) == 1

        v = Validator(101, "field").in_range(1, 100)
        assert len(v.errors) == 1

    def test_min_length_validation(self):
        """Test minimum length validation."""
        from common.validators import Validator

        v = Validator("hello", "field").min_length(3)
        assert len(v.errors) == 0

        v = Validator("hi", "field").min_length(3)
        assert len(v.errors) == 1

    def test_max_length_validation(self):
        """Test maximum length validation."""
        from common.validators import Validator

        v = Validator("hi", "field").max_length(10)
        assert len(v.errors) == 0

        v = Validator("this is a very long string", "field").max_length(10)
        assert len(v.errors) == 1

    def test_is_email_validation(self):
        """Test email format validation."""
        from common.validators import Validator

        v = Validator("user@example.com", "email").is_email()
        assert len(v.errors) == 0

        v = Validator("not-an-email", "email").is_email()
        assert len(v.errors) == 1

        v = Validator("user@", "email").is_email()
        assert len(v.errors) == 1

    def test_is_ipv4_validation(self):
        """Test IPv4 address validation."""
        from common.validators import Validator

        v = Validator("192.168.1.1", "ip").is_ipv4()
        assert len(v.errors) == 0

        v = Validator("10.0.0.1", "ip").is_ipv4()
        assert len(v.errors) == 0

        v = Validator("256.0.0.1", "ip").is_ipv4()
        assert len(v.errors) == 1

        v = Validator("not.an.ip", "ip").is_ipv4()
        assert len(v.errors) == 1

    def test_is_cidr_validation(self):
        """Test CIDR notation validation."""
        from common.validators import Validator

        v = Validator("192.168.1.0/24", "subnet").is_cidr()
        assert len(v.errors) == 0

        v = Validator("10.0.0.0/8", "subnet").is_cidr()
        assert len(v.errors) == 0

        v = Validator("192.168.1.0", "subnet").is_cidr()
        assert len(v.errors) == 1

    def test_is_mac_address_validation(self):
        """Test MAC address validation."""
        from common.validators import Validator

        v = Validator("00:1A:2B:3C:4D:5E", "mac").is_mac_address()
        assert len(v.errors) == 0

        v = Validator("00-1A-2B-3C-4D-5E", "mac").is_mac_address()
        assert len(v.errors) == 1  # Wrong format

        v = Validator("not-a-mac", "mac").is_mac_address()
        assert len(v.errors) == 1

    def test_is_in_validation(self):
        """Test allowed values validation."""
        from common.validators import Validator

        v = Validator("active", "status").is_in(["active", "inactive", "pending"])
        assert len(v.errors) == 0

        v = Validator("deleted", "status").is_in(["active", "inactive", "pending"])
        assert len(v.errors) == 1

    def test_not_in_validation(self):
        """Test forbidden values validation."""
        from common.validators import Validator

        v = Validator("user", "role").not_in(["admin", "superuser"])
        assert len(v.errors) == 0

        v = Validator("admin", "role").not_in(["admin", "superuser"])
        assert len(v.errors) == 1

    def test_chained_validation(self):
        """Test chaining multiple validations."""
        from common.validators import Validator

        v = Validator("test@example.com", "email").required().is_email()
        assert len(v.errors) == 0

        v = Validator("", "email").required().is_email()
        assert len(v.errors) >= 1

    def test_custom_validation(self):
        """Test custom validation function."""
        from common.validators import Validator

        is_even = lambda x: x % 2 == 0

        v = Validator(4, "number").custom(is_even, "must be even")
        assert len(v.errors) == 0

        v = Validator(3, "number").custom(is_even, "must be even")
        assert len(v.errors) == 1


class TestCollectErrors:
    """Tests for error collection."""

    def test_collect_errors_no_errors(self):
        """Test error collection with no errors."""
        from common.validators import Validator, collect_errors

        errors = collect_errors(
            Validator("test", "field1").required(),
            Validator("user@example.com", "email").is_email()
        )

        assert len(errors) == 0

    def test_collect_errors_multiple(self):
        """Test error collection with multiple errors."""
        from common.validators import Validator, collect_errors

        errors = collect_errors(
            Validator("", "field1").required(),
            Validator("not-email", "email").is_email(),
            Validator(0, "vlan").in_range(1, 4094)
        )

        assert len(errors) == 3


class TestVlanIdValidator:
    """Tests for VLAN ID validation."""

    def test_valid_vlan_ids(self):
        """Test valid VLAN IDs."""
        from common.validators import validate_vlan_id

        valid, error = validate_vlan_id(10)
        assert valid is True
        assert error is None

        valid, error = validate_vlan_id(4094)
        assert valid is True

    def test_invalid_vlan_out_of_range(self):
        """Test VLAN IDs out of valid range."""
        from common.validators import validate_vlan_id

        valid, error = validate_vlan_id(0)
        assert valid is False

        valid, error = validate_vlan_id(4095)
        assert valid is False

    def test_reserved_vlan_1(self):
        """Test that VLAN 1 is rejected (reserved native)."""
        from common.validators import validate_vlan_id

        valid, error = validate_vlan_id(1)
        assert valid is False
        assert "reserved" in error.lower()

    def test_non_integer_vlan(self):
        """Test non-integer VLAN ID."""
        from common.validators import validate_vlan_id

        valid, error = validate_vlan_id("abc")
        assert valid is False


class TestWifiChannelValidator:
    """Tests for WiFi channel validation."""

    def test_valid_24ghz_channels(self):
        """Test valid 2.4GHz channels (1, 6, 11 only per OberaConnect)."""
        from common.validators import validate_wifi_channel

        for ch in [1, 6, 11]:
            valid, error = validate_wifi_channel(ch, "2.4")
            assert valid is True, f"Channel {ch} should be valid"

    def test_invalid_24ghz_channels(self):
        """Test invalid 2.4GHz channels."""
        from common.validators import validate_wifi_channel

        # OberaConnect only allows non-overlapping channels
        for ch in [2, 3, 4, 5, 7, 8, 9, 10]:
            valid, error = validate_wifi_channel(ch, "2.4")
            assert valid is False, f"Channel {ch} should be invalid for 2.4GHz"

    def test_valid_5ghz_channels(self):
        """Test valid 5GHz channels."""
        from common.validators import validate_wifi_channel

        valid_channels = [36, 40, 44, 48, 149, 153, 157, 161, 165]
        for ch in valid_channels:
            valid, error = validate_wifi_channel(ch, "5")
            assert valid is True, f"Channel {ch} should be valid for 5GHz"

    def test_invalid_5ghz_channel(self):
        """Test invalid 5GHz channel."""
        from common.validators import validate_wifi_channel

        valid, error = validate_wifi_channel(1, "5")
        assert valid is False


class TestSignalStrengthValidator:
    """Tests for WiFi signal strength validation."""

    def test_good_signal(self):
        """Test good signal strength passes."""
        from common.validators import validate_signal_strength

        valid, error = validate_signal_strength(-55)
        assert valid is True

        valid, error = validate_signal_strength(-65)
        assert valid is True

    def test_signal_below_minimum(self):
        """Test signal below OberaConnect minimum (-65dBm)."""
        from common.validators import validate_signal_strength

        valid, error = validate_signal_strength(-70)
        assert valid is False
        assert "-65dBm" in error

    def test_signal_below_viable(self):
        """Test signal below viable (-90dBm)."""
        from common.validators import validate_signal_strength

        valid, error = validate_signal_strength(-95)
        assert valid is False
        assert "-90dBm" in error


class TestSsidValidator:
    """Tests for SSID validation."""

    def test_valid_ssid(self):
        """Test valid SSID."""
        from common.validators import validate_ssid

        valid, error = validate_ssid("OberaConnect-Guest")
        assert valid is True

    def test_empty_ssid(self):
        """Test empty SSID rejected."""
        from common.validators import validate_ssid

        valid, error = validate_ssid("")
        assert valid is False

    def test_ssid_too_long(self):
        """Test SSID over 32 characters rejected."""
        from common.validators import validate_ssid

        long_ssid = "A" * 33
        valid, error = validate_ssid(long_ssid)
        assert valid is False
        assert "32 characters" in error

    def test_ssid_with_spaces(self):
        """Test SSID with leading/trailing spaces rejected."""
        from common.validators import validate_ssid

        valid, error = validate_ssid(" Guest Network ")
        assert valid is False
        assert "spaces" in error.lower()
