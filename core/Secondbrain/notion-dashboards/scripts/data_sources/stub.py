"""
Stub implementations for data source interfaces.

Used for:
- Testing without real API access
- Development and prototyping
- Demo environments

Provides realistic sample data matching OberaConnect's 98-site deployment.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
import random

from data_sources.interface import (
    UniFiDataSource,
    NinjaOneDataSource,
    UniFiSite,
    UniFiDevice,
    NinjaOneOrganization,
    NinjaOneAlert,
    BackupStatus,
    DeviceStatus,
    AlertSeverity,
)


# =============================================================================
# Sample Data Generators
# =============================================================================

# US states where OberaConnect operates (14 states from memory)
STATES = [
    "Alabama", "Georgia", "Florida", "Tennessee", "Mississippi",
    "Louisiana", "Arkansas", "Texas", "North Carolina", "South Carolina",
    "Kentucky", "Virginia", "Missouri", "Oklahoma"
]

# Sample customer names
CUSTOMER_NAMES = [
    "Acme Corp", "Tech Solutions", "DataFlow Inc", "CloudFirst",
    "NetWorks Pro", "Digital Edge", "CyberSecure", "InfoTech",
    "Pinnacle Systems", "Summit Networks", "Apex Digital", "CoreTech",
    "Prime Connect", "Elite Networks", "Quantum IT", "Nexus Systems",
]

# Device models
AP_MODELS = ["U6-Pro", "U6-LR", "U6-Lite", "U6-Enterprise", "UAP-AC-Pro"]
SWITCH_MODELS = ["USW-24-POE", "USW-48-POE", "USW-Pro-24-POE", "USW-Lite-16-POE"]
GATEWAY_MODELS = ["UDM-Pro", "UDM-SE", "USG-Pro-4", "UXG-Pro"]


def generate_mac() -> str:
    """Generate a random MAC address."""
    return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))


def generate_ip(base: str = "192.168.1") -> str:
    """Generate a random IP address."""
    return f"{base}.{random.randint(10, 250)}"


# =============================================================================
# Stub Implementations
# =============================================================================

class StubUniFiDataSource(UniFiDataSource):
    """
    Stub UniFi data source with realistic sample data.
    
    Generates data matching OberaConnect's scale:
    - 98 customer sites
    - ~5 devices per site average
    - Mix of healthy and unhealthy sites
    """
    
    def __init__(self, site_count: int = 98, seed: Optional[int] = None):
        """
        Initialize stub with configurable site count.
        
        Args:
            site_count: Number of sites to generate
            seed: Random seed for reproducible data
        """
        self.site_count = site_count
        if seed is not None:
            random.seed(seed)
        
        self._sites = self._generate_sites()
        self._devices = self._generate_devices()
    
    def _generate_sites(self) -> List[UniFiSite]:
        """Generate sample site data."""
        sites = []
        
        for i in range(self.site_count):
            # Pick customer name (cycle through list)
            customer_idx = i % len(CUSTOMER_NAMES)
            customer_name = CUSTOMER_NAMES[customer_idx]
            
            # Add location suffix for uniqueness
            state = STATES[i % len(STATES)]
            suffix = "" if i < len(CUSTOMER_NAMES) else f" - Site {i // len(CUSTOMER_NAMES) + 1}"
            name = f"{customer_name}{suffix} - {state}"
            
            # Generate realistic metrics
            devices_total = random.randint(3, 15)
            
            # 85% of sites are healthy (all devices online)
            # 10% have 1-2 devices offline
            # 5% have significant issues
            health_roll = random.random()
            if health_roll < 0.85:
                devices_offline = 0
            elif health_roll < 0.95:
                devices_offline = random.randint(1, min(2, devices_total - 1))
            else:
                devices_offline = random.randint(2, max(2, devices_total // 2))
            
            devices_online = devices_total - devices_offline
            
            # WiFi clients
            wifi_clients = random.randint(10, 100)
            # 10% have weak signal issues
            if random.random() < 0.1:
                wifi_clients_weak = random.randint(1, wifi_clients // 4)
            else:
                wifi_clients_weak = 0
            
            site = UniFiSite(
                site_id=f"site_{i:03d}",
                name=name,
                state=state,
                devices_online=devices_online,
                devices_offline=devices_offline,
                devices_total=devices_total,
                wifi_clients=wifi_clients,
                wifi_clients_weak_signal=wifi_clients_weak,
                wan_ip=f"203.0.113.{i % 256}",
                uptime_seconds=random.randint(86400, 86400 * 90),
                last_seen=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 30)),
                has_mikrotik=random.random() < 0.15,  # 15% legacy MikroTik
                has_sonicwall=random.random() < 0.20,  # 20% legacy SonicWall
                has_azure=random.random() < 0.40,  # 40% have Azure
                contract_renewal=f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                primary_contact=f"Contact {i}",
            )
            sites.append(site)
        
        return sites
    
    def _generate_devices(self) -> dict[str, List[UniFiDevice]]:
        """Generate devices for each site."""
        devices_by_site = {}
        
        for site in self._sites:
            devices = []
            device_count = site.devices_total
            
            # Always have 1 gateway
            gateway = UniFiDevice(
                device_id=f"{site.site_id}_gw_001",
                name=f"{site.name.split(' - ')[0]} Gateway",
                mac_address=generate_mac(),
                device_type="gateway",
                model=random.choice(GATEWAY_MODELS),
                status=DeviceStatus.ONLINE if site.devices_offline == 0 else DeviceStatus.ONLINE,
                ip_address=generate_ip("192.168.1"),
                firmware_version="7.0.23",
                uptime_seconds=random.randint(86400, 86400 * 30),
                site_id=site.site_id,
                last_seen=site.last_seen,
            )
            devices.append(gateway)
            
            # Add switches (1-2 per site)
            switch_count = min(2, (device_count - 1) // 3)
            for j in range(switch_count):
                switch = UniFiDevice(
                    device_id=f"{site.site_id}_sw_{j:03d}",
                    name=f"Switch {j + 1}",
                    mac_address=generate_mac(),
                    device_type="switch",
                    model=random.choice(SWITCH_MODELS),
                    status=DeviceStatus.ONLINE,
                    ip_address=generate_ip("192.168.1"),
                    firmware_version="6.5.59",
                    uptime_seconds=random.randint(86400, 86400 * 30),
                    port_count=24 if "24" in random.choice(SWITCH_MODELS) else 48,
                    poe_ports=24,
                    site_id=site.site_id,
                    last_seen=site.last_seen,
                )
                devices.append(switch)
            
            # Add APs (remaining devices)
            ap_count = device_count - len(devices)
            offline_remaining = site.devices_offline
            
            for j in range(ap_count):
                # Assign offline status to some APs
                if offline_remaining > 0 and random.random() < 0.5:
                    status = DeviceStatus.OFFLINE
                    offline_remaining -= 1
                else:
                    status = DeviceStatus.ONLINE
                
                ap = UniFiDevice(
                    device_id=f"{site.site_id}_ap_{j:03d}",
                    name=f"AP {j + 1}",
                    mac_address=generate_mac(),
                    device_type="ap",
                    model=random.choice(AP_MODELS),
                    status=status,
                    ip_address=generate_ip("192.168.1") if status == DeviceStatus.ONLINE else "",
                    firmware_version="6.6.55",
                    uptime_seconds=random.randint(86400, 86400 * 30) if status == DeviceStatus.ONLINE else 0,
                    wifi_clients=random.randint(5, 20) if status == DeviceStatus.ONLINE else 0,
                    channel_2g=random.choice([1, 6, 11]),
                    channel_5g=random.choice([36, 40, 44, 48, 149, 153, 157, 161]),
                    site_id=site.site_id,
                    last_seen=site.last_seen if status == DeviceStatus.ONLINE else None,
                )
                devices.append(ap)
            
            devices_by_site[site.site_id] = devices
        
        return devices_by_site
    
    def fetch_sites(self) -> List[UniFiSite]:
        """Return all sites."""
        return self._sites.copy()
    
    def fetch_site(self, site_id: str) -> Optional[UniFiSite]:
        """Return site by ID."""
        for site in self._sites:
            if site.site_id == site_id:
                return site
        return None
    
    def fetch_devices(self, site_id: str) -> List[UniFiDevice]:
        """Return devices for a site."""
        return self._devices.get(site_id, []).copy()
    
    def fetch_device(self, site_id: str, device_id: str) -> Optional[UniFiDevice]:
        """Return specific device."""
        for device in self._devices.get(site_id, []):
            if device.device_id == device_id:
                return device
        return None


class StubNinjaOneDataSource(NinjaOneDataSource):
    """
    Stub NinjaOne data source with realistic sample data.
    
    Generates monitoring data that correlates with UniFi site data.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional random seed."""
        if seed is not None:
            random.seed(seed)
        
        self._organizations: dict[str, NinjaOneOrganization] = {}
        self._alerts: List[NinjaOneAlert] = []
    
    def _get_or_create_org(self, org_name: str) -> NinjaOneOrganization:
        """Get or create organization data."""
        if org_name not in self._organizations:
            # Generate realistic data
            device_count = random.randint(10, 50)
            offline = random.randint(0, 2) if random.random() < 0.15 else 0
            
            # Tickets (80% have 0, 15% have 1-2, 5% have 3+)
            ticket_roll = random.random()
            if ticket_roll < 0.80:
                open_tickets = 0
            elif ticket_roll < 0.95:
                open_tickets = random.randint(1, 2)
            else:
                open_tickets = random.randint(3, 5)
            
            # Alerts
            critical = random.randint(0, 1) if random.random() < 0.05 else 0
            warning = random.randint(0, 3) if random.random() < 0.20 else 0
            
            # Backup status
            backup_roll = random.random()
            if backup_roll < 0.85:
                backup_status = "success"
            elif backup_roll < 0.95:
                backup_status = "partial"
            else:
                backup_status = "failed"
            
            # Alert summary
            alert_summary = []
            if critical > 0:
                alert_summary.append("Critical: Server unreachable")
            if warning > 0:
                alert_summary.extend([
                    "High CPU on workstation",
                    "Disk space warning on file server",
                    "Certificate expiring soon",
                ][:warning])
            
            self._organizations[org_name] = NinjaOneOrganization(
                org_id=f"org_{len(self._organizations):03d}",
                name=org_name,
                device_count=device_count,
                online_devices=device_count - offline,
                offline_devices=offline,
                open_tickets=open_tickets,
                alerts_critical=critical,
                alerts_warning=warning,
                alerts_info=random.randint(0, 5),
                backup_status=backup_status,
                last_backup=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24)),
                alert_summary=alert_summary,
            )
        
        return self._organizations[org_name]
    
    def fetch_organization(self, org_name: str) -> Optional[NinjaOneOrganization]:
        """Return organization by name."""
        return self._get_or_create_org(org_name)
    
    def fetch_organizations(self) -> List[NinjaOneOrganization]:
        """Return all organizations."""
        return list(self._organizations.values())
    
    def fetch_alerts(
        self,
        org_name: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        active_only: bool = True
    ) -> List[NinjaOneAlert]:
        """Return alerts with filtering."""
        # Generate some alerts if none exist
        if not self._alerts:
            self._generate_sample_alerts()
        
        alerts = self._alerts.copy()
        
        if org_name:
            alerts = [a for a in alerts if org_name.lower() in a.device_name.lower()]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if active_only:
            alerts = [a for a in alerts if a.is_active]
        
        return alerts
    
    def _generate_sample_alerts(self) -> None:
        """Generate sample alerts."""
        alert_templates = [
            ("Disk space low on C:", "disk", AlertSeverity.WARNING),
            ("High CPU utilization", "cpu", AlertSeverity.WARNING),
            ("Server unreachable", "connectivity", AlertSeverity.CRITICAL),
            ("Backup job failed", "backup", AlertSeverity.WARNING),
            ("Certificate expiring in 14 days", "certificate", AlertSeverity.INFO),
            ("Memory usage above 90%", "memory", AlertSeverity.WARNING),
        ]
        
        for i, (message, category, severity) in enumerate(alert_templates):
            alert = NinjaOneAlert(
                alert_id=f"alert_{i:03d}",
                device_id=f"device_{i:03d}",
                device_name=f"Server-{i:02d}",
                severity=severity,
                message=message,
                category=category,
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                is_active=True,
            )
            self._alerts.append(alert)
    
    def fetch_backup_status(self, org_name: str) -> BackupStatus:
        """Return backup status for organization."""
        org = self._get_or_create_org(org_name)
        
        return BackupStatus(
            status=org.backup_status,
            last_successful=org.last_backup if org.backup_status == "success" else None,
            last_attempted=org.last_backup,
            protected_devices=org.device_count - random.randint(0, 2),
            total_devices=org.device_count,
            failed_jobs=["File Server Backup"] if org.backup_status == "failed" else [],
        )
