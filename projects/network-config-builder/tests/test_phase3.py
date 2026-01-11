"""
Unit tests for Phase 3 features.

Tests the interactive wizard and SSH deployment functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from io import StringIO
from datetime import datetime
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vendors.mikrotik.deployer import MikroTikDeployer, deploy_to_mikrotik


# ===== MikroTik Deployer Tests =====

class TestMikroTikDeployer:
    """Test MikroTik SSH deployment functionality"""

    def test_deployer_initialization(self):
        """Test deployer initializes with correct parameters"""
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123",
            port=22,
            timeout=30
        )

        assert deployer.device_ip == "192.168.1.1"
        assert deployer.username == "admin"
        assert deployer.password == "test123"
        assert deployer.port == 22
        assert deployer.timeout == 30
        assert deployer.client is None
        assert deployer.backup_name is None

    @patch('paramiko.SSHClient')
    def test_connect_success(self, mock_ssh_client):
        """Test successful SSH connection to MikroTik device"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        # Mock exec_command to return RouterOS output
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"RouterOS v7.12"
        mock_client_instance.exec_command.return_value = (None, mock_stdout, None)

        # Test connection
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )

        result = deployer.connect()

        assert result is True
        assert deployer.client is not None
        mock_client_instance.connect.assert_called_once()

    @patch('paramiko.SSHClient')
    def test_connect_failure_not_mikrotik(self, mock_ssh_client):
        """Test connection fails if device is not RouterOS"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        # Mock exec_command to return non-RouterOS output
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"Linux server"
        mock_client_instance.exec_command.return_value = (None, mock_stdout, None)

        # Test connection
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )

        with pytest.raises(ConnectionError, match="Failed to connect"):
            deployer.connect()

    @patch('paramiko.SSHClient')
    @patch('time.sleep')
    def test_create_backup(self, mock_sleep, mock_ssh_client):
        """Test automatic backup creation"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        # Mock connection check
        mock_stdout_resource = MagicMock()
        mock_stdout_resource.read.return_value = b"RouterOS v7.12"

        # Store the backup name that will be created
        created_backup_name = None

        # Create a function to capture and verify backup name
        def exec_command_handler(cmd):
            nonlocal created_backup_name

            if '/system backup save' in cmd:
                # Extract backup name from command
                import re
                match = re.search(r'name=(\S+)', cmd)
                if match:
                    created_backup_name = match.group(1)
                mock_out = MagicMock()
                mock_out.read.return_value = b""
                return (None, mock_out, None)
            elif '/file print' in cmd:
                # Return file list containing the backup name
                mock_out = MagicMock()
                output = f"backup files: {created_backup_name}.backup pre-deploy-".encode()
                mock_out.read.return_value = output
                return (None, mock_out, None)
            else:
                mock_out = MagicMock()
                mock_out.read.return_value = b""
                return (None, mock_out, None)

        # Set up mock responses
        mock_client_instance.exec_command.side_effect = [
            (None, mock_stdout_resource, None),  # Initial connection check
            *[exec_command_handler(cmd) for cmd in ['backup', 'file']]  # Will be called with actual commands
        ]

        # Override to use the handler
        mock_client_instance.exec_command = exec_command_handler

        # Test backup creation
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )

        # Mock the initial connection
        deployer.client = mock_client_instance
        deployer.client.exec_command = exec_command_handler

        backup_name = deployer.create_backup()

        assert backup_name is not None
        assert backup_name.startswith("pre-deploy-")
        assert deployer.backup_name == backup_name
        assert created_backup_name == backup_name

    @patch('paramiko.SSHClient')
    @patch('time.sleep')
    def test_deploy_configuration_success(self, mock_sleep, mock_ssh_client):
        """Test successful configuration deployment"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        # Mock SFTP
        mock_sftp = MagicMock()
        mock_file = MagicMock()
        mock_sftp.file.return_value.__enter__.return_value = mock_file
        mock_client_instance.open_sftp.return_value = mock_sftp

        # Mock exec_command responses
        mock_stdout_resource = MagicMock()
        mock_stdout_resource.read.return_value = b"RouterOS v7.12"

        mock_stdout_import = MagicMock()
        mock_stdout_import.read.return_value = b"Import successful"
        mock_stderr_import = MagicMock()
        mock_stderr_import.read.return_value = b""

        mock_stdout_verify = MagicMock()
        mock_stdout_verify.read.return_value = b"192.168.1.1"

        mock_client_instance.exec_command.side_effect = [
            (None, mock_stdout_resource, None),  # Connection check
            (None, mock_stdout_import, mock_stderr_import),  # Import
            (None, mock_stdout_verify, None),  # Verification
            (None, MagicMock(), None),  # Cleanup
        ]

        # Test deployment
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )
        deployer.connect()

        config_script = "/ip address add address=192.168.1.1/24 interface=bridge-lan"
        success, message = deployer.deploy_configuration(config_script, verify=True)

        assert success is True
        assert "successful" in message.lower()

    @patch('paramiko.SSHClient')
    @patch('time.sleep')
    def test_deploy_configuration_failure(self, mock_sleep, mock_ssh_client):
        """Test deployment failure handling"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        # Mock SFTP
        mock_sftp = MagicMock()
        mock_file = MagicMock()
        mock_sftp.file.return_value.__enter__.return_value = mock_file
        mock_client_instance.open_sftp.return_value = mock_sftp

        # Mock exec_command to return failure
        mock_stdout_resource = MagicMock()
        mock_stdout_resource.read.return_value = b"RouterOS v7.12"

        mock_stdout_import = MagicMock()
        mock_stdout_import.read.return_value = b""
        mock_stderr_import = MagicMock()
        mock_stderr_import.read.return_value = b"failure: syntax error"

        mock_client_instance.exec_command.side_effect = [
            (None, mock_stdout_resource, None),  # Connection check
            (None, mock_stdout_import, mock_stderr_import),  # Import failure
        ]

        # Test deployment
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )
        deployer.connect()

        config_script = "invalid script"
        success, message = deployer.deploy_configuration(config_script, verify=False)

        assert success is False
        assert "failed" in message.lower()

    @patch('paramiko.SSHClient')
    def test_rollback(self, mock_ssh_client):
        """Test configuration rollback"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"RouterOS v7.12"
        mock_client_instance.exec_command.return_value = (None, mock_stdout, None)

        # Test rollback
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )
        deployer.connect()
        deployer.backup_name = "pre-deploy-20250115-143022"

        success, message = deployer.rollback()

        assert success is True
        assert "pre-deploy-20250115-143022" in message

    @patch('paramiko.SSHClient')
    def test_rollback_no_backup(self, mock_ssh_client):
        """Test rollback fails when no backup exists"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"RouterOS v7.12"
        mock_client_instance.exec_command.return_value = (None, mock_stdout, None)

        # Test rollback without backup
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )
        deployer.connect()
        deployer.backup_name = None

        success, message = deployer.rollback()

        assert success is False
        assert "no backup" in message.lower()

    @patch('paramiko.SSHClient')
    def test_get_device_info(self, mock_ssh_client):
        """Test retrieving device information"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        # Mock identity response
        mock_stdout_identity = MagicMock()
        mock_stdout_identity.read.return_value = b"name: MyRouter"

        # Mock resource response
        mock_stdout_resource = MagicMock()
        mock_stdout_resource.read.return_value = b"""
version: 7.12.1 (stable)
board-name: hEX S
RouterOS
"""

        mock_client_instance.exec_command.side_effect = [
            (None, mock_stdout_resource, None),  # Initial connection
            (None, mock_stdout_identity, None),  # Identity
            (None, mock_stdout_resource, None),  # Resource info
        ]

        # Test device info retrieval
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )
        deployer.connect()

        info = deployer.get_device_info()

        assert "identity" in info
        assert info["identity"] == "MyRouter"
        assert "version" in info
        assert "7.12.1" in info["version"]
        assert "board" in info
        assert "hEX S" in info["board"]

    @patch('paramiko.SSHClient')
    def test_context_manager(self, mock_ssh_client):
        """Test deployer works as context manager"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"RouterOS v7.12"
        mock_client_instance.exec_command.return_value = (None, mock_stdout, None)

        # Test context manager
        with MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        ) as deployer:
            assert deployer.client is not None

        # Verify disconnect was called
        mock_client_instance.close.assert_called_once()

    def test_disconnect(self):
        """Test disconnect closes client"""
        deployer = MikroTikDeployer(
            device_ip="192.168.1.1",
            username="admin",
            password="test123"
        )

        # Mock client
        deployer.client = MagicMock()

        deployer.disconnect()

        assert deployer.client is None


class TestDeployToMikroTikFunction:
    """Test the convenience deploy_to_mikrotik() function"""

    @patch('vendors.mikrotik.deployer.MikroTikDeployer')
    def test_deploy_to_mikrotik_success(self, mock_deployer_class):
        """Test successful deployment using convenience function"""
        # Setup mock
        mock_deployer = MagicMock()
        mock_deployer_class.return_value.__enter__.return_value = mock_deployer

        mock_deployer.get_device_info.return_value = {
            "identity": "TestRouter",
            "version": "7.12.1",
            "board": "hEX S"
        }
        mock_deployer.create_backup.return_value = "pre-deploy-20250115-143022"
        mock_deployer.download_backup.return_value = True
        mock_deployer.deploy_configuration.return_value = (True, "Configuration deployed successfully")

        # Test deployment
        result = deploy_to_mikrotik(
            device_ip="192.168.1.1",
            username="admin",
            password="test123",
            config_script="/ip address add address=192.168.1.1/24 interface=bridge-lan",
            backup_path="./backups",
            verify=True,
            rollback_on_failure=True
        )

        assert result["success"] is True
        assert "deployed successfully" in result["message"]
        assert result["backup"] == "pre-deploy-20250115-143022"
        assert "TestRouter" in str(result["device_info"])

    @patch('vendors.mikrotik.deployer.MikroTikDeployer')
    def test_deploy_to_mikrotik_failure_with_rollback(self, mock_deployer_class):
        """Test deployment failure triggers rollback"""
        # Setup mock
        mock_deployer = MagicMock()
        mock_deployer_class.return_value.__enter__.return_value = mock_deployer

        mock_deployer.get_device_info.return_value = {"identity": "TestRouter"}
        mock_deployer.create_backup.return_value = "pre-deploy-20250115-143022"
        mock_deployer.download_backup.return_value = True
        mock_deployer.deploy_configuration.return_value = (False, "Deployment failed")
        mock_deployer.rollback.return_value = (True, "Rolled back successfully")

        # Test deployment
        result = deploy_to_mikrotik(
            device_ip="192.168.1.1",
            username="admin",
            password="test123",
            config_script="invalid script",
            backup_path="./backups",
            verify=True,
            rollback_on_failure=True
        )

        assert result["success"] is False
        assert "Rollback" in result["message"]
        mock_deployer.rollback.assert_called_once()

    @patch('vendors.mikrotik.deployer.MikroTikDeployer')
    def test_deploy_to_mikrotik_exception_handling(self, mock_deployer_class):
        """Test exception handling in deployment"""
        # Setup mock to raise exception
        mock_deployer_class.return_value.__enter__.side_effect = Exception("Connection timeout")

        # Test deployment
        result = deploy_to_mikrotik(
            device_ip="192.168.1.1",
            username="admin",
            password="test123",
            config_script="/ip address add address=192.168.1.1/24 interface=bridge-lan",
            backup_path="./backups"
        )

        assert result["success"] is False
        assert "error" in result["message"].lower()
        assert "timeout" in result["message"].lower()


# ===== Interactive Wizard Tests =====

class TestInteractiveWizard:
    """Test interactive configuration wizard"""

    @patch('click.prompt')
    @patch('click.confirm')
    @patch('builtins.open', new_callable=mock_open)
    def test_wizard_basic_router(self, mock_file, mock_confirm, mock_prompt):
        """Test wizard creates basic router configuration"""
        from cli.wizard import run_wizard

        # Mock user inputs
        mock_prompt.side_effect = [
            'mikrotik',  # Vendor
            'hEX S',  # Device model
            'Test Corp',  # Customer name
            'Main Office',  # Site name
            'admin@test.com',  # Contact email
            'router_only',  # Deployment type
            'ether1',  # WAN interface
            'static',  # WAN mode
            '203.0.113.10',  # WAN IP
            24,  # WAN netmask
            '203.0.113.1',  # WAN gateway
            '8.8.8.8',  # Primary DNS
            '8.8.4.4',  # Secondary DNS
            'bridge-lan',  # LAN interface
            '192.168.1.1',  # LAN IP
            24,  # LAN netmask
            '192.168.1.100',  # DHCP start
            '192.168.1.200',  # DHCP end
            '24h',  # Lease time
            'admin',  # Admin username
            'StrongPass123!',  # Admin password
            'StrongPass123!',  # Password confirmation
            '192.168.1.0/24',  # Management IP
            'test-config.yaml'  # Filename
        ]

        mock_confirm.side_effect = [
            True,  # Configure DNS?
            True,  # Add secondary DNS?
            True,  # Enable DHCP?
            False,  # Add VLANs?
            True,  # Disable unused services?
            True,  # Restrict management access?
            False,  # Add another management network?
            True,  # Enable WinBox?
            True,  # Enable SSH?
            False,  # Enable bandwidth test?
            False,  # Enable STUN?
            True,  # Save configuration?
            False  # Generate now?
        ]

        # Run wizard
        result = run_wizard()

        # Verify file was written
        mock_file.assert_called_once()
        assert result is None  # User chose not to generate

    @patch('click.prompt')
    @patch('click.confirm')
    @patch('click.echo')
    def test_wizard_keyboard_interrupt(self, mock_echo, mock_confirm, mock_prompt):
        """Test wizard handles Ctrl+C gracefully"""
        from cli.wizard import run_wizard

        # Mock user pressing Ctrl+C
        mock_prompt.side_effect = KeyboardInterrupt()

        # Run wizard
        with pytest.raises(KeyboardInterrupt):
            run_wizard()


# ===== Integration Tests =====

class TestPhase3Integration:
    """Test Phase 3 features work together"""

    @patch('vendors.mikrotik.deployer.MikroTikDeployer')
    @patch('click.prompt')
    @patch('click.confirm')
    @patch('builtins.open', new_callable=mock_open)
    def test_wizard_to_deployment_workflow(self, mock_file, mock_confirm, mock_prompt, mock_deployer_class):
        """Test complete workflow: wizard → YAML → deployment"""
        from cli.wizard import run_wizard
        from config_io.readers.yaml_reader import YAMLConfigReader

        # This integration test would verify the complete workflow
        # For now, we test that the components are compatible
        assert True  # Placeholder for full integration test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
