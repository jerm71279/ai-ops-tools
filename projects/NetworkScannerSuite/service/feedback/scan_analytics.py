"""
OberaConnect Network Scanner Analytics & Feedback Loops
Aligned with OberaAI Strategy - Leverage Charts + Data Moats

Feedback Loops:
1. Scan Performance Loop - Track timing, optimize nmap parameters
2. Error Recovery Loop - Learn from failures, auto-retry with adjustments
3. Resource Monitoring Loop - Track system load, queue management
4. Network Intelligence Loop - Build proprietary network patterns (Data Moat)

Principles:
- Data Moat: Every scan adds to proprietary network intelligence
- Leverage: AI optimizes scans, human handles exceptions
- 98/2: Auto-handle common issues, escalate unusual findings
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict


class ScanOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"  # Some hosts scanned, some failed
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ErrorCategory(Enum):
    NETWORK_UNREACHABLE = "network_unreachable"
    HOST_DOWN = "host_down"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    INVALID_TARGET = "invalid_target"
    UNKNOWN = "unknown"


@dataclass
class ScanMetrics:
    """Metrics for a single scan"""
    scan_id: str
    target: str
    scan_type: str
    started_at: str
    completed_at: Optional[str]
    duration_seconds: float
    hosts_discovered: int
    hosts_scanned: int
    ports_found: int
    services_identified: int
    outcome: ScanOutcome
    errors: List[Dict] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    nmap_flags_used: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['outcome'] = self.outcome.value
        return data


class ScanPerformanceLoop:
    """
    FEEDBACK LOOP 1: Scan Performance Optimization

    Learns from scan history to:
    - Optimize nmap parameters per network type
    - Predict scan duration
    - Identify slow network segments
    - Recommend scan type based on target
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.metrics_file = data_dir / "scan_metrics.json"
        self.benchmarks_file = data_dir / "scan_benchmarks.json"
        self._ensure_files()

    def _ensure_files(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.metrics_file.exists():
            with open(self.metrics_file, 'w') as f:
                json.dump({'scans': [], 'total_count': 0}, f)

        if not self.benchmarks_file.exists():
            with open(self.benchmarks_file, 'w') as f:
                json.dump({
                    'by_scan_type': {
                        'quick': {'avg_duration': 60, 'avg_hosts_per_second': 10, 'samples': 0},
                        'standard': {'avg_duration': 300, 'avg_hosts_per_second': 2, 'samples': 0},
                        'intense': {'avg_duration': 1800, 'avg_hosts_per_second': 0.5, 'samples': 0}
                    },
                    'by_network_size': {},
                    'optimal_flags': {},
                    'last_updated': None
                }, f)

    def record_scan(self, metrics: ScanMetrics) -> Dict[str, Any]:
        """Record scan metrics and update benchmarks"""

        with open(self.metrics_file, 'r') as f:
            data = json.load(f)

        # Add scan record
        data['scans'].append(metrics.to_dict())
        data['total_count'] += 1

        # Keep last 1000 scans for analysis
        if len(data['scans']) > 1000:
            data['scans'] = data['scans'][-1000:]

        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Update benchmarks
        insights = self._update_benchmarks(metrics)

        return {
            'recorded': True,
            'scan_id': metrics.scan_id,
            'insights': insights
        }

    def _update_benchmarks(self, metrics: ScanMetrics) -> List[str]:
        """Update performance benchmarks from new scan"""

        with open(self.benchmarks_file, 'r') as f:
            benchmarks = json.load(f)

        insights = []

        # Update by scan type
        scan_type = metrics.scan_type
        if scan_type in benchmarks['by_scan_type']:
            type_data = benchmarks['by_scan_type'][scan_type]
            samples = type_data['samples']

            # Running average
            type_data['avg_duration'] = (
                (type_data['avg_duration'] * samples + metrics.duration_seconds) /
                (samples + 1)
            )

            if metrics.duration_seconds > 0 and metrics.hosts_scanned > 0:
                hosts_per_sec = metrics.hosts_scanned / metrics.duration_seconds
                type_data['avg_hosts_per_second'] = (
                    (type_data['avg_hosts_per_second'] * samples + hosts_per_sec) /
                    (samples + 1)
                )

            type_data['samples'] += 1

        # Update by network size (CIDR)
        network_size = self._get_network_size(metrics.target)
        size_key = f"/{network_size}"

        if size_key not in benchmarks['by_network_size']:
            benchmarks['by_network_size'][size_key] = {
                'avg_duration': 0,
                'avg_hosts_found': 0,
                'samples': 0
            }

        size_data = benchmarks['by_network_size'][size_key]
        samples = size_data['samples']
        size_data['avg_duration'] = (
            (size_data['avg_duration'] * samples + metrics.duration_seconds) /
            (samples + 1)
        )
        size_data['avg_hosts_found'] = (
            (size_data['avg_hosts_found'] * samples + metrics.hosts_discovered) /
            (samples + 1)
        )
        size_data['samples'] += 1

        # Generate insights
        if metrics.duration_seconds > benchmarks['by_scan_type'].get(scan_type, {}).get('avg_duration', 0) * 1.5:
            insights.append(f"Scan took {metrics.duration_seconds/60:.1f}min, longer than average")

        if metrics.hosts_discovered < size_data['avg_hosts_found'] * 0.5:
            insights.append(f"Found fewer hosts than typical for {size_key} network")

        benchmarks['last_updated'] = datetime.now().isoformat()

        with open(self.benchmarks_file, 'w') as f:
            json.dump(benchmarks, f, indent=2)

        return insights

    def _get_network_size(self, target: str) -> int:
        """Extract CIDR prefix from target"""
        if '/' in target:
            try:
                return int(target.split('/')[-1])
            except ValueError:
                pass
        return 32  # Single host

    def estimate_duration(self, target: str, scan_type: str) -> Dict[str, Any]:
        """
        FEEDBACK LOOP: Predictive Duration Estimation

        Uses historical data to predict scan duration
        """

        with open(self.benchmarks_file, 'r') as f:
            benchmarks = json.load(f)

        estimate = {
            'target': target,
            'scan_type': scan_type,
            'estimated_seconds': 0,
            'confidence': 'low',
            'basis': []
        }

        # Base estimate from scan type
        type_data = benchmarks['by_scan_type'].get(scan_type, {})
        base_duration = type_data.get('avg_duration', 300)
        samples = type_data.get('samples', 0)

        estimate['estimated_seconds'] = base_duration

        if samples > 10:
            estimate['confidence'] = 'high'
            estimate['basis'].append(f"Based on {samples} previous {scan_type} scans")
        elif samples > 3:
            estimate['confidence'] = 'medium'
            estimate['basis'].append(f"Based on {samples} previous {scan_type} scans")
        else:
            estimate['basis'].append("Using default estimates (limited history)")

        # Adjust for network size
        network_size = self._get_network_size(target)
        size_key = f"/{network_size}"

        if size_key in benchmarks['by_network_size']:
            size_data = benchmarks['by_network_size'][size_key]
            if size_data['samples'] > 3:
                # Weight toward network-size-specific data
                estimate['estimated_seconds'] = (
                    estimate['estimated_seconds'] * 0.4 +
                    size_data['avg_duration'] * 0.6
                )
                estimate['basis'].append(f"Adjusted for {size_key} network size")

        # Calculate expected hosts
        hosts_per_sec = type_data.get('avg_hosts_per_second', 1)
        if hosts_per_sec > 0:
            potential_hosts = 2 ** (32 - network_size)
            estimate['expected_hosts'] = min(potential_hosts,
                benchmarks['by_network_size'].get(size_key, {}).get('avg_hosts_found', potential_hosts * 0.3)
            )

        return estimate

    def get_optimization_suggestions(self, target: str, scan_type: str) -> List[Dict]:
        """
        FEEDBACK LOOP: AI-Powered Optimization Suggestions

        Analyzes patterns to suggest optimal scan parameters
        """

        with open(self.metrics_file, 'r') as f:
            data = json.load(f)

        suggestions = []

        # Find similar scans
        network_prefix = target.rsplit('.', 1)[0] if '.' in target else target
        similar_scans = [
            s for s in data['scans']
            if s['target'].startswith(network_prefix) and s['outcome'] == 'success'
        ]

        if similar_scans:
            # Analyze successful scans of this network
            avg_duration = statistics.mean([s['duration_seconds'] for s in similar_scans])
            avg_hosts = statistics.mean([s['hosts_discovered'] for s in similar_scans])

            suggestions.append({
                'type': 'historical_insight',
                'message': f"Previous scans of {network_prefix}.x found ~{int(avg_hosts)} hosts in ~{int(avg_duration/60)} minutes",
                'confidence': 'high' if len(similar_scans) > 3 else 'medium'
            })

        # Scan type recommendations
        if scan_type == 'intense':
            suggestions.append({
                'type': 'recommendation',
                'message': "Consider 'standard' scan first to identify live hosts, then intense scan specific targets",
                'rationale': "Reduces overall scan time while maintaining thoroughness"
            })

        # Time-based suggestions
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            suggestions.append({
                'type': 'timing',
                'message': "Business hours may show more active hosts but could impact network performance",
                'rationale': "Consider off-hours scanning for intensive scans"
            })

        return suggestions


class ErrorRecoveryLoop:
    """
    FEEDBACK LOOP 2: Error Recovery & Learning

    Learns from scan failures to:
    - Categorize error types
    - Suggest recovery actions
    - Auto-retry with adjusted parameters
    - Track error patterns (Data Moat)
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.errors_file = data_dir / "scan_errors.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.errors_file.exists():
            with open(self.errors_file, 'w') as f:
                json.dump({
                    'errors': [],
                    'patterns': {},
                    'recovery_success': {},
                    'auto_recovery_rules': {}
                }, f)

    def record_error(
        self,
        scan_id: str,
        error_message: str,
        target: str,
        scan_type: str,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Record and analyze scan error"""

        with open(self.errors_file, 'r') as f:
            data = json.load(f)

        # Categorize error
        category = self._categorize_error(error_message)

        error_record = {
            'id': f"err_{scan_id}_{datetime.now().strftime('%H%M%S')}",
            'scan_id': scan_id,
            'category': category.value,
            'message': error_message,
            'target': target,
            'scan_type': scan_type,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'recovery_attempted': False,
            'recovery_successful': None
        }

        data['errors'].append(error_record)

        # Update patterns
        if category.value not in data['patterns']:
            data['patterns'][category.value] = {'count': 0, 'targets': [], 'last_seen': None}

        data['patterns'][category.value]['count'] += 1
        data['patterns'][category.value]['last_seen'] = datetime.now().isoformat()

        # Track target patterns
        target_prefix = target.rsplit('.', 1)[0] if '.' in target else target
        if target_prefix not in data['patterns'][category.value]['targets']:
            data['patterns'][category.value]['targets'].append(target_prefix)
            if len(data['patterns'][category.value]['targets']) > 50:
                data['patterns'][category.value]['targets'] = data['patterns'][category.value]['targets'][-50:]

        with open(self.errors_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Generate recovery suggestion
        recovery = self._suggest_recovery(category, error_message, target, scan_type)

        return {
            'error_id': error_record['id'],
            'category': category.value,
            'recovery_suggestion': recovery,
            'auto_recoverable': recovery.get('auto_recoverable', False)
        }

    def _categorize_error(self, error_message: str) -> ErrorCategory:
        """Categorize error based on message content"""

        error_lower = error_message.lower()

        if 'unreachable' in error_lower or 'no route' in error_lower:
            return ErrorCategory.NETWORK_UNREACHABLE
        elif 'host down' in error_lower or 'no response' in error_lower:
            return ErrorCategory.HOST_DOWN
        elif 'permission' in error_lower or 'denied' in error_lower or 'root' in error_lower:
            return ErrorCategory.PERMISSION_DENIED
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            return ErrorCategory.TIMEOUT
        elif 'memory' in error_lower or 'resource' in error_lower:
            return ErrorCategory.RESOURCE_EXHAUSTED
        elif 'invalid' in error_lower or 'malformed' in error_lower:
            return ErrorCategory.INVALID_TARGET
        else:
            return ErrorCategory.UNKNOWN

    def _suggest_recovery(
        self,
        category: ErrorCategory,
        error_message: str,
        target: str,
        scan_type: str
    ) -> Dict[str, Any]:
        """
        FEEDBACK LOOP: AI-Powered Recovery Suggestions

        Uses 98/2 principle - auto-recover common issues, escalate unusual ones
        """

        # Recovery strategies by category
        strategies = {
            ErrorCategory.NETWORK_UNREACHABLE: {
                'auto_recoverable': False,
                'suggestion': 'Verify network connectivity and routing to target',
                'actions': [
                    'Check if target network exists',
                    'Verify VPN/firewall rules allow scanning',
                    'Try ping test to gateway'
                ],
                'requires_human': True
            },
            ErrorCategory.HOST_DOWN: {
                'auto_recoverable': True,
                'suggestion': 'Target appears offline - can retry with longer timeout',
                'retry_params': {
                    'add_flags': ['--host-timeout', '30m'],
                    'scan_type': scan_type
                },
                'requires_human': False
            },
            ErrorCategory.PERMISSION_DENIED: {
                'auto_recoverable': False,
                'suggestion': 'Scan requires elevated privileges',
                'actions': [
                    'Run scanner service as administrator/root',
                    'Use -Pn flag to skip host discovery',
                    'Check firewall permissions'
                ],
                'requires_human': True
            },
            ErrorCategory.TIMEOUT: {
                'auto_recoverable': True,
                'suggestion': 'Scan timed out - can retry with adjusted timing',
                'retry_params': {
                    'add_flags': ['-T3'],  # Slower timing template
                    'scan_type': 'quick' if scan_type == 'intense' else scan_type
                },
                'requires_human': False
            },
            ErrorCategory.RESOURCE_EXHAUSTED: {
                'auto_recoverable': True,
                'suggestion': 'System resources exhausted - retry with reduced parallelism',
                'retry_params': {
                    'add_flags': ['--min-parallelism', '1', '--max-parallelism', '10'],
                    'scan_type': scan_type
                },
                'requires_human': False
            },
            ErrorCategory.INVALID_TARGET: {
                'auto_recoverable': False,
                'suggestion': 'Target specification invalid',
                'actions': [
                    'Verify CIDR notation is correct',
                    'Check for typos in IP address',
                    'Ensure target is in valid range'
                ],
                'requires_human': True
            },
            ErrorCategory.UNKNOWN: {
                'auto_recoverable': False,
                'suggestion': 'Unknown error - requires investigation',
                'actions': [
                    'Check full error log',
                    'Verify nmap installation',
                    'Try manual nmap command'
                ],
                'requires_human': True
            }
        }

        return strategies.get(category, strategies[ErrorCategory.UNKNOWN])

    def record_recovery_result(
        self,
        error_id: str,
        successful: bool,
        notes: str = None
    ) -> None:
        """Record whether recovery attempt was successful"""

        with open(self.errors_file, 'r') as f:
            data = json.load(f)

        # Find and update error
        for error in data['errors']:
            if error['id'] == error_id:
                error['recovery_attempted'] = True
                error['recovery_successful'] = successful
                error['recovery_notes'] = notes

                # Update recovery success tracking
                category = error['category']
                if category not in data['recovery_success']:
                    data['recovery_success'][category] = {'attempted': 0, 'successful': 0}

                data['recovery_success'][category]['attempted'] += 1
                if successful:
                    data['recovery_success'][category]['successful'] += 1

                break

        with open(self.errors_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_error_analytics(self) -> Dict[str, Any]:
        """Get error pattern analytics"""

        with open(self.errors_file, 'r') as f:
            data = json.load(f)

        analytics = {
            'total_errors': len(data['errors']),
            'by_category': {},
            'recovery_rates': {},
            'recent_errors': data['errors'][-10:] if data['errors'] else []
        }

        for category, pattern in data['patterns'].items():
            analytics['by_category'][category] = {
                'count': pattern['count'],
                'affected_networks': len(pattern.get('targets', [])),
                'last_seen': pattern.get('last_seen')
            }

        for category, recovery in data['recovery_success'].items():
            if recovery['attempted'] > 0:
                rate = recovery['successful'] / recovery['attempted']
                analytics['recovery_rates'][category] = f"{rate:.0%}"

        return analytics


class NetworkIntelligenceLoop:
    """
    FEEDBACK LOOP 3: Network Intelligence (DATA MOAT)

    Builds proprietary network intelligence from scans:
    - Device type patterns by manufacturer
    - Common service configurations
    - Network topology patterns
    - Security posture indicators
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.intelligence_file = data_dir / "network_intelligence.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.intelligence_file.exists():
            with open(self.intelligence_file, 'w') as f:
                json.dump({
                    'device_patterns': {},
                    'service_patterns': {},
                    'port_associations': {},
                    'vendor_profiles': {},
                    'security_indicators': {},
                    'network_profiles': {},
                    'total_hosts_analyzed': 0,
                    'last_updated': None
                }, f)

    def learn_from_scan(
        self,
        scan_results: Dict,
        customer_id: str = None
    ) -> Dict[str, Any]:
        """
        DATA MOAT: Learn from scan results

        Every scan makes the intelligence database more valuable
        """

        with open(self.intelligence_file, 'r') as f:
            intel = json.load(f)

        insights_generated = []
        hosts = scan_results.get('hosts', [])

        for host in hosts:
            intel['total_hosts_analyzed'] += 1

            # Learn device patterns from MAC addresses
            mac = host.get('mac', '')
            if mac:
                vendor = self._extract_vendor(mac)
                if vendor:
                    if vendor not in intel['vendor_profiles']:
                        intel['vendor_profiles'][vendor] = {
                            'count': 0,
                            'common_ports': {},
                            'common_services': {}
                        }
                    intel['vendor_profiles'][vendor]['count'] += 1

            # Learn service patterns
            for port_info in host.get('ports', []):
                port = port_info.get('port')
                service = port_info.get('service', 'unknown')
                product = port_info.get('product', '')

                # Port-service association
                port_key = str(port)
                if port_key not in intel['port_associations']:
                    intel['port_associations'][port_key] = {}

                if service not in intel['port_associations'][port_key]:
                    intel['port_associations'][port_key][service] = 0
                intel['port_associations'][port_key][service] += 1

                # Service patterns
                if service not in intel['service_patterns']:
                    intel['service_patterns'][service] = {
                        'count': 0,
                        'common_ports': {},
                        'products': {}
                    }

                intel['service_patterns'][service]['count'] += 1
                if port_key not in intel['service_patterns'][service]['common_ports']:
                    intel['service_patterns'][service]['common_ports'][port_key] = 0
                intel['service_patterns'][service]['common_ports'][port_key] += 1

                if product:
                    if product not in intel['service_patterns'][service]['products']:
                        intel['service_patterns'][service]['products'][product] = 0
                    intel['service_patterns'][service]['products'][product] += 1

            # Security indicators
            self._analyze_security_indicators(host, intel)

        # Update network profile if customer provided
        if customer_id:
            if customer_id not in intel['network_profiles']:
                intel['network_profiles'][customer_id] = {
                    'scans': 0,
                    'total_hosts': 0,
                    'unique_services': set(),
                    'last_scan': None
                }
            profile = intel['network_profiles'][customer_id]
            profile['scans'] += 1
            profile['total_hosts'] += len(hosts)
            profile['last_scan'] = datetime.now().isoformat()
            # Convert set to list for JSON
            intel['network_profiles'][customer_id]['unique_services'] = list(
                set(profile.get('unique_services', [])) |
                {p.get('service') for h in hosts for p in h.get('ports', [])}
            )

        intel['last_updated'] = datetime.now().isoformat()

        with open(self.intelligence_file, 'w') as f:
            json.dump(intel, f, indent=2)

        return {
            'hosts_analyzed': len(hosts),
            'insights': insights_generated
        }

    def _extract_vendor(self, mac: str) -> Optional[str]:
        """Extract vendor from MAC address OUI"""
        # Common OUI prefixes (simplified)
        oui_db = {
            '00:50:56': 'VMware',
            '00:0C:29': 'VMware',
            'B8:27:EB': 'Raspberry Pi',
            'DC:A6:32': 'Raspberry Pi',
            '00:1A:2B': 'Cisco',
            '00:1B:54': 'Cisco',
            '00:17:C5': 'SonicWall',
            '00:06:B1': 'SonicWall',
            'FC:EC:DA': 'Ubiquiti',
            '24:A4:3C': 'Ubiquiti',
            '78:8A:20': 'Ubiquiti',
            '00:15:6D': 'Ubiquiti',
            '44:D9:E7': 'Ubiquiti',
            '00:1E:58': 'Dell',
            '14:FE:B5': 'Dell',
            '00:25:64': 'Dell',
            '00:1D:D8': 'Microsoft',
            '00:03:FF': 'Microsoft',
            '00:50:F2': 'Microsoft',
        }

        mac_upper = mac.upper().replace('-', ':')
        oui = mac_upper[:8]

        return oui_db.get(oui)

    def _analyze_security_indicators(self, host: Dict, intel: Dict) -> None:
        """Analyze host for security indicators"""

        indicators = intel['security_indicators']

        for port_info in host.get('ports', []):
            port = port_info.get('port')
            service = port_info.get('service', '')
            state = port_info.get('state', '')

            # Track risky open ports
            risky_ports = {
                21: 'FTP (unencrypted)',
                23: 'Telnet (unencrypted)',
                445: 'SMB (potential ransomware vector)',
                3389: 'RDP (brute force target)',
                1433: 'MSSQL (database exposure)',
                3306: 'MySQL (database exposure)',
                5432: 'PostgreSQL (database exposure)',
                6379: 'Redis (often unsecured)',
                27017: 'MongoDB (often unsecured)'
            }

            if port in risky_ports and state == 'open':
                indicator_key = f"open_port_{port}"
                if indicator_key not in indicators:
                    indicators[indicator_key] = {
                        'description': risky_ports[port],
                        'count': 0,
                        'risk_level': 'high' if port in [23, 445, 3389] else 'medium'
                    }
                indicators[indicator_key]['count'] += 1

    def get_network_baseline(self, customer_id: str) -> Dict[str, Any]:
        """
        DATA MOAT VALUE: Get network baseline for comparison

        Enables detecting anomalies in future scans
        """

        with open(self.intelligence_file, 'r') as f:
            intel = json.load(f)

        profile = intel['network_profiles'].get(customer_id)

        if not profile:
            return {'error': 'No baseline data for customer'}

        return {
            'customer_id': customer_id,
            'baseline': {
                'typical_host_count': profile.get('total_hosts', 0) / max(profile.get('scans', 1), 1),
                'known_services': profile.get('unique_services', []),
                'scan_count': profile.get('scans', 0),
                'last_scan': profile.get('last_scan')
            }
        }

    def get_predictive_findings(self, scan_config: Dict) -> List[Dict]:
        """
        DATA MOAT VALUE: Predict likely findings before scan

        Uses historical intelligence to set expectations
        """

        with open(self.intelligence_file, 'r') as f:
            intel = json.load(f)

        predictions = []

        # Predict common services
        if intel['service_patterns']:
            top_services = sorted(
                intel['service_patterns'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:5]

            predictions.append({
                'type': 'common_services',
                'prediction': f"Likely to find: {', '.join(s[0] for s in top_services)}",
                'confidence': 'high' if intel['total_hosts_analyzed'] > 100 else 'medium'
            })

        # Predict security findings
        if intel['security_indicators']:
            high_risk = [
                (k, v) for k, v in intel['security_indicators'].items()
                if v.get('risk_level') == 'high'
            ]
            if high_risk:
                predictions.append({
                    'type': 'security_risk',
                    'prediction': f"Watch for: {', '.join(v['description'] for k, v in high_risk[:3])}",
                    'confidence': 'medium'
                })

        return predictions

    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of network intelligence database"""

        with open(self.intelligence_file, 'r') as f:
            intel = json.load(f)

        return {
            'total_hosts_analyzed': intel['total_hosts_analyzed'],
            'unique_services': len(intel['service_patterns']),
            'known_vendors': len(intel['vendor_profiles']),
            'security_indicators_tracked': len(intel['security_indicators']),
            'customer_profiles': len(intel['network_profiles']),
            'last_updated': intel['last_updated'],
            'top_services': sorted(
                [(k, v['count']) for k, v in intel['service_patterns'].items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


class ResourceMonitorLoop:
    """
    FEEDBACK LOOP 4: Resource Monitoring

    Monitors system resources to:
    - Queue scans during high load
    - Alert on resource constraints
    - Optimize concurrent scan limits
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.resource_file = data_dir / "resource_metrics.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.resource_file.exists():
            with open(self.resource_file, 'w') as f:
                json.dump({
                    'samples': [],
                    'thresholds': {
                        'cpu_percent': 80,
                        'memory_percent': 85,
                        'max_concurrent_scans': 3
                    },
                    'queue': [],
                    'active_scans': 0
                }, f)

    def record_metrics(
        self,
        cpu_percent: float,
        memory_percent: float,
        active_scans: int
    ) -> Dict[str, Any]:
        """Record resource metrics"""

        with open(self.resource_file, 'r') as f:
            data = json.load(f)

        sample = {
            'timestamp': datetime.now().isoformat(),
            'cpu': cpu_percent,
            'memory': memory_percent,
            'active_scans': active_scans
        }

        data['samples'].append(sample)
        data['active_scans'] = active_scans

        # Keep last 100 samples
        if len(data['samples']) > 100:
            data['samples'] = data['samples'][-100:]

        # Check thresholds
        alerts = []
        if cpu_percent > data['thresholds']['cpu_percent']:
            alerts.append({
                'type': 'high_cpu',
                'value': cpu_percent,
                'threshold': data['thresholds']['cpu_percent']
            })

        if memory_percent > data['thresholds']['memory_percent']:
            alerts.append({
                'type': 'high_memory',
                'value': memory_percent,
                'threshold': data['thresholds']['memory_percent']
            })

        with open(self.resource_file, 'w') as f:
            json.dump(data, f, indent=2)

        return {
            'recorded': True,
            'alerts': alerts,
            'can_start_new_scan': (
                active_scans < data['thresholds']['max_concurrent_scans'] and
                cpu_percent < data['thresholds']['cpu_percent'] and
                memory_percent < data['thresholds']['memory_percent']
            )
        }

    def can_start_scan(self) -> Tuple[bool, str]:
        """Check if resources allow starting a new scan"""

        with open(self.resource_file, 'r') as f:
            data = json.load(f)

        active = data['active_scans']
        max_concurrent = data['thresholds']['max_concurrent_scans']

        if active >= max_concurrent:
            return False, f"Maximum concurrent scans ({max_concurrent}) reached"

        # Check recent resource samples
        if data['samples']:
            recent = data['samples'][-5:]
            avg_cpu = statistics.mean([s['cpu'] for s in recent])
            avg_mem = statistics.mean([s['memory'] for s in recent])

            if avg_cpu > data['thresholds']['cpu_percent']:
                return False, f"CPU usage too high ({avg_cpu:.0f}%)"

            if avg_mem > data['thresholds']['memory_percent']:
                return False, f"Memory usage too high ({avg_mem:.0f}%)"

        return True, "Resources available"


class ScanAnalyticsOrchestrator:
    """
    Master orchestrator for all scanner feedback loops

    Coordinates analytics and provides unified insights
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "analytics_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.performance_loop = ScanPerformanceLoop(self.data_dir)
        self.error_loop = ErrorRecoveryLoop(self.data_dir)
        self.intelligence_loop = NetworkIntelligenceLoop(self.data_dir)
        self.resource_loop = ResourceMonitorLoop(self.data_dir)

    def process_completed_scan(
        self,
        scan_id: str,
        target: str,
        scan_type: str,
        started_at: str,
        completed_at: str,
        results: Dict,
        customer_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a completed scan through all feedback loops

        This is the main entry point that triggers all learning
        """

        # Calculate metrics
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(completed_at)
        duration = (end - start).total_seconds()

        hosts = results.get('hosts', [])
        total_ports = sum(len(h.get('ports', [])) for h in hosts)

        metrics = ScanMetrics(
            scan_id=scan_id,
            target=target,
            scan_type=scan_type,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            hosts_discovered=len(hosts),
            hosts_scanned=len(hosts),
            ports_found=total_ports,
            services_identified=total_ports,  # Simplified
            outcome=ScanOutcome.SUCCESS if hosts else ScanOutcome.PARTIAL
        )

        feedback = {
            'scan_id': scan_id,
            'loops_processed': []
        }

        # 1. Performance Loop
        perf_result = self.performance_loop.record_scan(metrics)
        feedback['loops_processed'].append('performance')
        feedback['performance_insights'] = perf_result.get('insights', [])

        # 2. Intelligence Loop (Data Moat)
        intel_result = self.intelligence_loop.learn_from_scan(results, customer_id)
        feedback['loops_processed'].append('intelligence')
        feedback['intelligence_insights'] = intel_result.get('insights', [])

        return feedback

    def process_scan_error(
        self,
        scan_id: str,
        error_message: str,
        target: str,
        scan_type: str
    ) -> Dict[str, Any]:
        """Process a scan error through error recovery loop"""

        result = self.error_loop.record_error(
            scan_id=scan_id,
            error_message=error_message,
            target=target,
            scan_type=scan_type
        )

        return {
            'error_recorded': True,
            'category': result['category'],
            'recovery': result['recovery_suggestion'],
            'auto_recoverable': result['auto_recoverable']
        }

    def get_pre_scan_intelligence(
        self,
        target: str,
        scan_type: str,
        customer_id: str = None
    ) -> Dict[str, Any]:
        """
        Get pre-scan intelligence for setting expectations

        This is the DATA MOAT value - predictions before scanning
        """

        intelligence = {
            'target': target,
            'scan_type': scan_type,
            'generated_at': datetime.now().isoformat()
        }

        # Duration estimate
        intelligence['estimate'] = self.performance_loop.estimate_duration(target, scan_type)

        # Optimization suggestions
        intelligence['suggestions'] = self.performance_loop.get_optimization_suggestions(target, scan_type)

        # Predictive findings
        intelligence['predictions'] = self.intelligence_loop.get_predictive_findings({'target': target})

        # Customer baseline if available
        if customer_id:
            baseline = self.intelligence_loop.get_network_baseline(customer_id)
            if 'error' not in baseline:
                intelligence['baseline'] = baseline

        # Resource check
        can_scan, reason = self.resource_loop.can_start_scan()
        intelligence['resources'] = {
            'ready': can_scan,
            'status': reason
        }

        return intelligence

    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get unified analytics dashboard"""

        return {
            'generated_at': datetime.now().isoformat(),
            'intelligence_summary': self.intelligence_loop.get_intelligence_summary(),
            'error_analytics': self.error_loop.get_error_analytics(),
            'performance_summary': self._get_performance_summary()
        }

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from metrics"""

        metrics_file = self.data_dir / "scan_metrics.json"
        if not metrics_file.exists():
            return {'message': 'No performance data yet'}

        with open(metrics_file, 'r') as f:
            data = json.load(f)

        if not data['scans']:
            return {'message': 'No scans recorded'}

        recent = data['scans'][-50:]  # Last 50 scans

        return {
            'total_scans': data['total_count'],
            'recent_scans': len(recent),
            'avg_duration_minutes': statistics.mean([s['duration_seconds']/60 for s in recent]),
            'success_rate': sum(1 for s in recent if s['outcome'] == 'success') / len(recent),
            'avg_hosts_per_scan': statistics.mean([s['hosts_discovered'] for s in recent])
        }
