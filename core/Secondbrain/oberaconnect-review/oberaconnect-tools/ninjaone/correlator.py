"""
Cross-Platform Correlator

Correlates events across UniFi and NinjaOne platforms.

Example use cases:
- AP goes offline → Check for related endpoint alerts
- Multiple devices offline at same customer → Likely network issue
- Endpoint alerts spike → Check network health
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from unifi.models import UniFiSite, FleetSummary
from .client import NinjaOneAlert, NinjaOneDevice


logger = logging.getLogger(__name__)


@dataclass
class CorrelatedIncident:
    """
    Represents a correlated incident across platforms.
    
    Combines UniFi network issues with NinjaOne endpoint alerts.
    """
    customer_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    summary: str
    
    # UniFi data
    unifi_site_id: Optional[str] = None
    unifi_site_name: Optional[str] = None
    offline_network_devices: int = 0
    network_health_score: int = 100
    
    # NinjaOne data
    ninjaone_org_id: Optional[str] = None
    endpoint_alerts: List[NinjaOneAlert] = field(default_factory=list)
    offline_endpoints: int = 0
    
    # Correlation metadata
    correlation_type: str = "unknown"  # network_outage, endpoint_issue, combined
    confidence: float = 0.0  # 0-1 confidence score
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'customerName': self.customer_name,
            'severity': self.severity,
            'summary': self.summary,
            'unifiSiteId': self.unifi_site_id,
            'unifiSiteName': self.unifi_site_name,
            'offlineNetworkDevices': self.offline_network_devices,
            'networkHealthScore': self.network_health_score,
            'ninjaoneOrgId': self.ninjaone_org_id,
            'endpointAlertCount': len(self.endpoint_alerts),
            'offlineEndpoints': self.offline_endpoints,
            'correlationType': self.correlation_type,
            'confidence': round(self.confidence, 2),
            'createdAt': self.created_at.isoformat()
        }


class Correlator:
    """
    Correlates events across UniFi and NinjaOne platforms.
    
    Uses customer name matching to link UniFi sites with NinjaOne orgs.
    """
    
    def __init__(
        self,
        unifi_sites: List[UniFiSite] = None,
        ninjaone_alerts: List[NinjaOneAlert] = None,
        ninjaone_devices: List[NinjaOneDevice] = None
    ):
        self._unifi_sites = unifi_sites or []
        self._ninjaone_alerts = ninjaone_alerts or []
        self._ninjaone_devices = ninjaone_devices or []
        
        # Build lookup indexes
        self._build_indexes()
    
    def _build_indexes(self):
        """Build lookup indexes for efficient correlation."""
        # UniFi sites by normalized name
        self._unifi_by_name: Dict[str, UniFiSite] = {}
        for site in self._unifi_sites:
            key = self._normalize_name(site.name)
            self._unifi_by_name[key] = site
        
        # NinjaOne alerts by org name
        self._alerts_by_org: Dict[str, List[NinjaOneAlert]] = {}
        for alert in self._ninjaone_alerts:
            key = self._normalize_name(alert.org_name)
            if key not in self._alerts_by_org:
                self._alerts_by_org[key] = []
            self._alerts_by_org[key].append(alert)
        
        # NinjaOne devices by org name
        self._devices_by_org: Dict[str, List[NinjaOneDevice]] = {}
        for device in self._ninjaone_devices:
            key = self._normalize_name(device.org_name)
            if key not in self._devices_by_org:
                self._devices_by_org[key] = []
            self._devices_by_org[key].append(device)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize customer name for matching."""
        if not name:
            return ""
        # Lowercase, remove common suffixes, strip whitespace
        name = name.lower().strip()
        for suffix in [' inc', ' llc', ' corp', ' ltd', ' main', ' hq']:
            name = name.replace(suffix, '')
        return name.strip()
    
    def _match_customer(self, unifi_name: str, ninjaone_name: str) -> float:
        """
        Calculate match confidence between customer names.
        
        Returns confidence score 0-1.
        """
        norm_unifi = self._normalize_name(unifi_name)
        norm_ninja = self._normalize_name(ninjaone_name)
        
        # Exact match
        if norm_unifi == norm_ninja:
            return 1.0
        
        # One contains the other
        if norm_unifi in norm_ninja or norm_ninja in norm_unifi:
            return 0.8
        
        # Check first word match (often company name)
        unifi_first = norm_unifi.split()[0] if norm_unifi else ""
        ninja_first = norm_ninja.split()[0] if norm_ninja else ""
        
        if unifi_first and ninja_first and unifi_first == ninja_first:
            return 0.6
        
        return 0.0
    
    def get_incident_context(self, customer_name: str) -> CorrelatedIncident:
        """
        Get full incident context for a customer.
        
        Args:
            customer_name: Customer/site name to look up
            
        Returns:
            CorrelatedIncident with all available data
        """
        norm_name = self._normalize_name(customer_name)
        
        # Find UniFi site
        unifi_site = self._unifi_by_name.get(norm_name)
        
        # Find best matching NinjaOne org
        best_match_key = None
        best_confidence = 0.0
        
        for key in self._alerts_by_org.keys():
            confidence = self._match_customer(norm_name, key)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match_key = key
        
        # Also check devices
        for key in self._devices_by_org.keys():
            if key not in self._alerts_by_org:
                confidence = self._match_customer(norm_name, key)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match_key = key
        
        # Get NinjaOne data
        alerts = self._alerts_by_org.get(best_match_key, []) if best_match_key else []
        devices = self._devices_by_org.get(best_match_key, []) if best_match_key else []
        offline_endpoints = sum(1 for d in devices if not d.is_online)
        
        # Determine severity and correlation type
        severity, correlation_type, summary = self._analyze_incident(
            unifi_site, alerts, offline_endpoints
        )
        
        return CorrelatedIncident(
            customer_name=customer_name,
            severity=severity,
            summary=summary,
            unifi_site_id=unifi_site.id if unifi_site else None,
            unifi_site_name=unifi_site.name if unifi_site else None,
            offline_network_devices=unifi_site.offline_devices if unifi_site else 0,
            network_health_score=unifi_site.health_score if unifi_site else 100,
            ninjaone_org_id=alerts[0].org_id if alerts else None,
            endpoint_alerts=alerts,
            offline_endpoints=offline_endpoints,
            correlation_type=correlation_type,
            confidence=best_confidence if best_match_key else (1.0 if unifi_site else 0.0)
        )
    
    def _analyze_incident(
        self,
        unifi_site: Optional[UniFiSite],
        alerts: List[NinjaOneAlert],
        offline_endpoints: int
    ) -> Tuple[str, str, str]:
        """
        Analyze incident severity and type.
        
        Returns: (severity, correlation_type, summary)
        """
        has_network_issues = unifi_site and unifi_site.offline_devices > 0
        has_endpoint_issues = len(alerts) > 0 or offline_endpoints > 0
        critical_alerts = [a for a in alerts if a.severity == 'CRITICAL']
        
        # Determine type
        if has_network_issues and has_endpoint_issues:
            correlation_type = "combined"
        elif has_network_issues:
            correlation_type = "network_outage"
        elif has_endpoint_issues:
            correlation_type = "endpoint_issue"
        else:
            correlation_type = "healthy"
        
        # Determine severity
        if unifi_site and unifi_site.health_score < 50:
            severity = "CRITICAL"
        elif critical_alerts:
            severity = "CRITICAL"
        elif has_network_issues and has_endpoint_issues:
            severity = "HIGH"
        elif unifi_site and unifi_site.offline_devices >= 3:
            severity = "HIGH"
        elif has_network_issues or has_endpoint_issues:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        # Generate summary
        parts = []
        if unifi_site:
            if unifi_site.offline_devices > 0:
                parts.append(f"{unifi_site.offline_devices} network device(s) offline")
            else:
                parts.append(f"Network healthy ({unifi_site.health_score}% health)")
        
        if alerts:
            parts.append(f"{len(alerts)} endpoint alert(s)")
        
        if offline_endpoints > 0:
            parts.append(f"{offline_endpoints} endpoint(s) offline")
        
        summary = "; ".join(parts) if parts else "No issues detected"
        
        return severity, correlation_type, summary
    
    def find_correlated_issues(self) -> List[CorrelatedIncident]:
        """
        Find all customers with correlated issues.
        
        Returns incidents where both network and endpoint issues exist.
        """
        incidents = []
        
        # Check all UniFi sites with issues
        for site in self._unifi_sites:
            if site.offline_devices > 0 or site.health_score < 70:
                incident = self.get_incident_context(site.name)
                if incident.correlation_type == "combined":
                    incidents.append(incident)
        
        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        incidents.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        return incidents
    
    def get_morning_check_report(self) -> Dict[str, Any]:
        """
        Generate a morning check report combining UniFi and NinjaOne data.
        
        Returns a summary suitable for daily review.
        """
        # UniFi summary
        unifi_summary = FleetSummary.from_sites(self._unifi_sites) if self._unifi_sites else None
        
        # NinjaOne summary
        critical_alerts = [a for a in self._ninjaone_alerts if a.severity == 'CRITICAL']
        major_alerts = [a for a in self._ninjaone_alerts if a.severity == 'MAJOR']
        
        offline_devices = [d for d in self._ninjaone_devices if not d.is_online]
        
        # Find correlated issues
        correlated = self.find_correlated_issues()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'network': {
                'totalSites': unifi_summary.total_sites if unifi_summary else 0,
                'healthySites': unifi_summary.healthy_sites if unifi_summary else 0,
                'criticalSites': unifi_summary.critical_sites if unifi_summary else 0,
                'offlineDevices': unifi_summary.offline_devices if unifi_summary else 0,
                'fleetHealthScore': unifi_summary.fleet_health_score if unifi_summary else 100
            },
            'endpoints': {
                'totalAlerts': len(self._ninjaone_alerts),
                'criticalAlerts': len(critical_alerts),
                'majorAlerts': len(major_alerts),
                'offlineEndpoints': len(offline_devices)
            },
            'correlatedIncidents': [i.to_dict() for i in correlated],
            'summary': self._generate_summary_text(unifi_summary, critical_alerts, correlated)
        }
    
    def _generate_summary_text(
        self,
        unifi_summary: Optional[FleetSummary],
        critical_alerts: List[NinjaOneAlert],
        correlated: List[CorrelatedIncident]
    ) -> str:
        """Generate human-readable summary."""
        lines = ["Morning Check Summary", "=" * 40]
        
        if unifi_summary:
            lines.append(f"\nNetwork: {unifi_summary.fleet_health_score}% healthy")
            if unifi_summary.critical_sites > 0:
                lines.append(f"  ⚠️ {unifi_summary.critical_sites} critical site(s)")
            if unifi_summary.offline_devices > 0:
                lines.append(f"  📡 {unifi_summary.offline_devices} device(s) offline")
        
        lines.append(f"\nEndpoints: {len(critical_alerts)} critical alert(s)")
        
        if correlated:
            lines.append(f"\n🔗 {len(correlated)} correlated incident(s):")
            for inc in correlated[:5]:
                lines.append(f"  - {inc.customer_name}: {inc.summary}")
        
        return "\n".join(lines)


__all__ = [
    'CorrelatedIncident',
    'Correlator'
]
