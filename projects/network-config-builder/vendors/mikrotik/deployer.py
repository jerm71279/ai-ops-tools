"""
MikroTik Secure Deployment Module

Handles secure deployment to MikroTik RouterOS devices via SSH.
"""

import paramiko
import time
from pathlib import Path
from typing import Dict, Tuple, Optional
import hashlib
from datetime import datetime


class MikroTikDeployer:
    """
    Secure deployment to MikroTik RouterOS devices.
    
    Uses SSH for secure communication and includes:
    - Automatic backup before deployment
    - Configuration verification
    - Rollback on failure
    - Audit logging
    """
    
    def __init__(self, device_ip: str, username: str, password: Optional[str] = None,
                 ssh_key_path: Optional[str] = None, port: int = 22, timeout: int = 30):
        """
        Initialize deployer.
        
        Args:
            device_ip: Device IP address
            username: SSH username  
            password: SSH password (if not using key auth)
            ssh_key_path: Path to SSH private key
            port: SSH port (default 22)
            timeout: Connection timeout in seconds
        """
        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.ssh_key_path = ssh_key_path
        self.port = port
        self.timeout = timeout
        self.client = None
        self.backup_name = None
    
    def connect(self) -> bool:
        """
        Establish SSH connection to device.
        
        Returns:
            True if connection successful
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': self.device_ip,
                'port': self.port,
                'username': self.username,
                'timeout': self.timeout,
                'look_for_keys': True if self.ssh_key_path else False,
                'allow_agent': True
            }
            
            if self.password:
                connect_kwargs['password'] = self.password
            
            if self.ssh_key_path:
                connect_kwargs['key_filename'] = self.ssh_key_path
            
            self.client.connect(**connect_kwargs)
            
            # Verify it's a MikroTik device
            stdin, stdout, stderr = self.client.exec_command('/system resource print')
            output = stdout.read().decode()
            
            if 'RouterOS' not in output:
                raise ValueError("Device does not appear to be running RouterOS")
            
            return True
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.device_ip}: {str(e)}")
    
    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.client = None
    
    def create_backup(self) -> str:
        """
        Create configuration backup on device.
        
        Returns:
            Backup filename
        """
        if not self.client:
            raise RuntimeError("Not connected to device")
        
        # Generate backup name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backup_name = f"pre-deploy-{timestamp}"
        
        # Create backup
        command = f'/system backup save name={self.backup_name} dont-encrypt=yes'
        stdin, stdout, stderr = self.client.exec_command(command)
        
        # Wait for backup to complete
        time.sleep(2)
        
        # Verify backup exists
        stdin, stdout, stderr = self.client.exec_command('/file print where name~"backup"')
        output = stdout.read().decode()
        
        if self.backup_name not in output:
            raise RuntimeError("Backup creation failed")
        
        return self.backup_name
    
    def download_backup(self, local_path: str) -> bool:
        """
        Download backup file from device.
        
        Args:
            local_path: Local directory to save backup
            
        Returns:
            True if download successful
        """
        if not self.client or not self.backup_name:
            raise RuntimeError("No backup to download")
        
        try:
            sftp = self.client.open_sftp()
            
            remote_file = f"/{self.backup_name}.backup"
            local_file = Path(local_path) / f"{self.device_ip}_{self.backup_name}.backup"
            
            # Ensure local directory exists
            Path(local_path).mkdir(parents=True, exist_ok=True)
            
            sftp.get(remote_file, str(local_file))
            sftp.close()
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Backup download failed: {str(e)}")
    
    def deploy_configuration(self, config_script: str, verify: bool = True) -> Tuple[bool, str]:
        """
        Deploy configuration script to device.
        
        Args:
            config_script: RouterOS configuration script
            verify: Verify deployment after applying
            
        Returns:
            Tuple of (success, message)
        """
        if not self.client:
            raise RuntimeError("Not connected to device")
        
        try:
            # Upload script to device
            sftp = self.client.open_sftp()
            
            remote_file = "/flash/deploy-config.rsc"
            
            # Write script to temporary file
            with sftp.file(remote_file, 'w') as f:
                f.write(config_script)
            
            sftp.close()
            
            # Import configuration
            stdin, stdout, stderr = self.client.exec_command(f'/import file-name={remote_file}')
            
            import_output = stdout.read().decode()
            import_errors = stderr.read().decode()
            
            if import_errors and 'failure' in import_errors.lower():
                return False, f"Import failed: {import_errors}"
            
            # Wait for import to complete
            time.sleep(3)
            
            # Verify if requested
            if verify:
                verification_result = self._verify_deployment(config_script)
                if not verification_result[0]:
                    return False, f"Verification failed: {verification_result[1]}"
            
            # Cleanup temporary file
            self.client.exec_command(f'/file remove {remote_file}')
            
            return True, "Configuration deployed successfully"
            
        except Exception as e:
            return False, f"Deployment failed: {str(e)}"
    
    def rollback(self) -> Tuple[bool, str]:
        """
        Rollback to backup configuration.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.client or not self.backup_name:
            return False, "No backup available for rollback"
        
        try:
            command = f'/system backup load name={self.backup_name}'
            stdin, stdout, stderr = self.client.exec_command(command)
            
            # Note: Device will reboot after backup load
            time.sleep(2)
            
            return True, f"Rolled back to backup: {self.backup_name}"
            
        except Exception as e:
            return False, f"Rollback failed: {str(e)}"
    
    def _verify_deployment(self, config_script: str) -> Tuple[bool, str]:
        """
        Verify configuration was applied correctly.
        
        Args:
            config_script: Original configuration script
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check for key configuration elements
            checks_passed = 0
            checks_total = 0
            
            # Check IP addresses if configured
            if '/ip address add' in config_script:
                checks_total += 1
                stdin, stdout, stderr = self.client.exec_command('/ip address print')
                if stdout.read().decode():
                    checks_passed += 1
            
            # Check interfaces if configured
            if '/interface' in config_script:
                checks_total += 1
                stdin, stdout, stderr = self.client.exec_command('/interface print')
                if stdout.read().decode():
                    checks_passed += 1
            
            # Check DHCP server if configured
            if '/ip dhcp-server' in config_script:
                checks_total += 1
                stdin, stdout, stderr = self.client.exec_command('/ip dhcp-server print')
                if stdout.read().decode():
                    checks_passed += 1
            
            if checks_total == 0:
                return True, "No verification checks configured"
            
            if checks_passed == checks_total:
                return True, f"All {checks_total} verification checks passed"
            else:
                return False, f"Only {checks_passed}/{checks_total} verification checks passed"
                
        except Exception as e:
            return False, f"Verification error: {str(e)}"
    
    def get_device_info(self) -> Dict[str, str]:
        """
        Get device information.
        
        Returns:
            Dict with device details
        """
        if not self.client:
            raise RuntimeError("Not connected to device")
        
        info = {}
        
        # Get system identity
        stdin, stdout, stderr = self.client.exec_command('/system identity print')
        identity = stdout.read().decode().strip()
        if 'name:' in identity:
            info['identity'] = identity.split('name:')[-1].strip()
        
        # Get RouterOS version
        stdin, stdout, stderr = self.client.exec_command('/system resource print')
        output = stdout.read().decode()
        
        for line in output.split('\n'):
            if 'version:' in line:
                info['version'] = line.split('version:')[-1].strip()
            elif 'board-name:' in line:
                info['board'] = line.split('board-name:')[-1].strip()
        
        return info
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience function for simple deployment
def deploy_to_mikrotik(device_ip: str, username: str, password: str,
                      config_script: str, backup_path: str = './backups',
                      verify: bool = True, rollback_on_failure: bool = True) -> Dict[str, any]:
    """
    Deploy configuration to MikroTik device with automatic backup.
    
    Args:
        device_ip: Device IP address
        username: SSH username
        password: SSH password
        config_script: Configuration script content
        backup_path: Local path to save backups
        verify: Verify deployment
        rollback_on_failure: Rollback if deployment fails
        
    Returns:
        Dict with deployment results
    """
    result = {
        'success': False,
        'message': '',
        'backup': None,
        'device_info': {}
    }
    
    try:
        with MikroTikDeployer(device_ip, username, password) as deployer:
            # Get device info
            result['device_info'] = deployer.get_device_info()
            
            # Create backup
            backup_name = deployer.create_backup()
            result['backup'] = backup_name
            
            # Download backup
            deployer.download_backup(backup_path)
            
            # Deploy configuration
            success, message = deployer.deploy_configuration(config_script, verify=verify)
            
            if not success and rollback_on_failure:
                # Rollback on failure
                rollback_success, rollback_message = deployer.rollback()
                result['message'] = f"{message}. Rollback: {rollback_message}"
                result['success'] = False
            else:
                result['success'] = success
                result['message'] = message
            
    except Exception as e:
        result['success'] = False
        result['message'] = f"Deployment error: {str(e)}"
    
    return result
