#!/usr/bin/env python3
"""
UniFi Fleet Manager - Python Client
====================================
Python wrapper for UniFi Site Manager API with natural language query support.

Usage:
    # Direct API access
    client = UniFiClient(headers)
    sites = client.fetch_sites()
    
    # Query engine
    analyzer = UniFiAnalyzer(sites)
    result = analyzer.query("sites with more than 5 offline devices")
    
    # CLI mode
    python unifi_client.py --demo
    python unifi_client.py --headers headers.json
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

# Optional: requests for API calls
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ============================================
# Data Models
# ============================================

@dataclass
class Site:
    """Normalized UniFi site data."""
    id: str
    name: str
    internal_name: str
    
    # Device counts
    total_devices: int
    offline_devices: int
    online_devices: int
    wifi_devices: int
    wired_devices: int
    gateway_devices: int
    
    # Offline breakdown
    offline_wifi: int
    offline_wired: int
    offline_gateway: int
    
    # Client counts
    wifi_clients: int
    wired_clients: int
    total_clients: int
    guest_clients: int
    
    # Alerts
    critical_alerts: int
    warning_alerts: int
    
    # Network
    isp: str
    wan_uptime: float
    external_ip: str
    
    # Performance
    tx_retry: float
    health_score: int
    device_online_percent: int
    
    # Status flags
    is_healthy: bool
    has_issues: bool
    
    @classmethod
    def from_raw(cls, raw: dict) -> 'Site':
        """Create Site from raw API response."""
        meta = raw.get('meta', {})
        stats = raw.get('statistics', {})
        counts = stats.get('counts', {})
        percentages = stats.get('percentages', {})
        wans = stats.get('wans', {})
        
        # Extract WAN details
        wan_list = []
        for name, data in wans.items():
            wan_list.append({
                'name': name,
                'uptime': data.get('wanUptime', 0),
                'external_ip': data.get('externalIp', ''),
                'isp': (data.get('ispInfo', {}).get('name') or 
                       data.get('ispInfo', {}).get('organization', ''))
            })
        
        primary_isp = next((w['isp'] for w in wan_list if w['isp']), '')
        primary_uptime = wan_list[0]['uptime'] if wan_list else 0
        
        # Device counts
        total_devices = counts.get('totalDevice', 0)
        offline_devices = counts.get('offlineDevice', 0)
        online_devices = total_devices - offline_devices
        
        # Client counts
        wifi_clients = counts.get('wifiClient', 0)
        wired_clients = counts.get('wiredClient', 0)
        total_clients = wifi_clients + wired_clients
        
        # Alerts
        critical_alerts = counts.get('criticalNotification', 0)
        warning_alerts = counts.get('warningNotification', 0)
        
        # Performance
        tx_retry = percentages.get('txRetry', 0)
        
        # Health score calculation
        device_online_pct = (online_devices / total_devices * 100) if total_devices > 0 else 100
        health_score = round(
            (device_online_pct * 0.4) +
            (primary_uptime * 0.3) +
            ((100 - tx_retry) * 0.15) +
            ((100 if critical_alerts == 0 else 0) * 0.15)
        )
        
        return cls(
            id=raw.get('siteId', ''),
            name=meta.get('desc') or meta.get('name', 'Unknown'),
            internal_name=meta.get('name', ''),
            total_devices=total_devices,
            offline_devices=offline_devices,
            online_devices=online_devices,
            wifi_devices=counts.get('wifiDevice', 0),
            wired_devices=counts.get('wiredDevice', 0),
            gateway_devices=counts.get('gatewayDevice', 0),
            offline_wifi=counts.get('offlineWifiDevice', 0),
            offline_wired=counts.get('offlineWiredDevice', 0),
            offline_gateway=counts.get('offlineGatewayDevice', 0),
            wifi_clients=wifi_clients,
            wired_clients=wired_clients,
            total_clients=total_clients,
            guest_clients=counts.get('guestClient', 0),
            critical_alerts=critical_alerts,
            warning_alerts=warning_alerts,
            isp=primary_isp,
            wan_uptime=primary_uptime,
            external_ip=wan_list[0]['external_ip'] if wan_list else '',
            tx_retry=tx_retry,
            health_score=health_score,
            device_online_percent=round(device_online_pct),
            is_healthy=(offline_devices == 0 and critical_alerts == 0 and primary_uptime >= 99),
            has_issues=(offline_devices > 0 or critical_alerts > 0 or primary_uptime < 95)
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'total_devices': self.total_devices,
            'offline_devices': self.offline_devices,
            'online_devices': self.online_devices,
            'total_clients': self.total_clients,
            'wifi_clients': self.wifi_clients,
            'wired_clients': self.wired_clients,
            'health_score': self.health_score,
            'wan_uptime': self.wan_uptime,
            'isp': self.isp,
            'is_healthy': self.is_healthy,
            'has_issues': self.has_issues
        }


@dataclass
class FleetSummary:
    """Fleet-wide statistics."""
    total_sites: int
    total_devices: int
    total_clients: int
    wifi_clients: int
    wired_clients: int
    online_devices: int
    offline_devices: int
    healthy_sites: int
    warning_sites: int
    critical_sites: int
    avg_health_score: float
    top_issues: list = field(default_factory=list)


# ============================================
# API Client
# ============================================

class UniFiClient:
    """UniFi Site Manager API client."""
    
    API_URL = "https://cloudaccess.svc.ui.com/api/cloud-access/sites"
    
    def __init__(self, headers: dict):
        """
        Initialize client with API headers.
        
        Args:
            headers: Dict containing x-amz-date, x-amz-security-token, authorization
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library required. Install with: pip install requests")
        
        self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(headers)
    
    def fetch_sites(self) -> list[Site]:
        """Fetch and normalize all sites."""
        response = self.session.get(self.API_URL)
        response.raise_for_status()
        
        data = response.json()
        raw_sites = data.get('data', data)
        
        return [Site.from_raw(s) for s in raw_sites]
    
    @classmethod
    def from_file(cls, path: str) -> 'UniFiClient':
        """Create client from JSON headers file."""
        with open(path) as f:
            headers = json.load(f)
        return cls(headers)


# ============================================
# Query Analyzer
# ============================================

class UniFiAnalyzer:
    """Natural language query engine for UniFi fleet data."""
    
    # Field mapping for natural language detection
    FIELD_PATTERNS = [
        (r'offline\s*device|devices?\s*offline', 'offline_devices'),
        (r'total\s*device|device\s*count', 'total_devices'),
        (r'online\s*device', 'online_devices'),
        (r'wifi\s*device|access\s*point|aps?(?:\s|$)', 'wifi_devices'),
        (r'wired\s*device|switch', 'wired_devices'),
        (r'gateway|udm|usg', 'gateway_devices'),
        (r'wifi\s*client|wireless\s*client', 'wifi_clients'),
        (r'wired\s*client', 'wired_clients'),
        (r'client|user|connected', 'total_clients'),
        (r'guest', 'guest_clients'),
        (r'critical|alert', 'critical_alerts'),
        (r'warning', 'warning_alerts'),
        (r'uptime|wan', 'wan_uptime'),
        (r'retry|tx', 'tx_retry'),
        (r'health|score', 'health_score'),
    ]
    
    # Numeric comparison patterns
    COMPARISON_PATTERNS = [
        (r'more than (\d+)', '>'),
        (r'greater than (\d+)', '>'),
        (r'over (\d+)', '>'),
        (r'above (\d+)', '>'),
        (r'at least (\d+)', '>='),
        (r'(\d+)\s*\+', '>='),
        (r'(\d+)\s*or more', '>='),
        (r'less than (\d+)', '<'),
        (r'under (\d+)', '<'),
        (r'below (\d+)', '<'),
        (r'fewer than (\d+)', '<'),
        (r'at most (\d+)', '<='),
        (r'exactly (\d+)', '=='),
    ]
    
    # ISP patterns
    ISP_PATTERNS = [
        (r'verizon', r'verizon'),
        (r'lumen|level\s*3|centurylink', r'lumen|level3|centurylink'),
        (r'at\s*&?\s*t', r'at&?t'),
        (r'spectrum|charter', r'spectrum|charter'),
        (r'comcast|xfinity', r'comcast|xfinity'),
        (r'cox', r'cox'),
        (r'mediacom', r'mediacom'),
        (r'brightspeed', r'brightspeed'),
    ]
    
    # Common customer names
    CUSTOMER_NAMES = [
        'setco', 'hoods', 'kinder', 'anne', 'celebration', 'jubilee',
        'tracery', 'coastal', 'fairhope', 'freeport', 'panama',
        'destin', 'pensacola', 'dirt', 'fulcrum', 'clauger', 'obera'
    ]
    
    def __init__(self, sites: list[Site] = None):
        """Initialize analyzer with optional site list."""
        self.sites: list[Site] = sites or []
        self.last_update: Optional[datetime] = None
    
    def load_sites(self, sites: list[Site]):
        """Load normalized sites."""
        self.sites = sites
        self.last_update = datetime.now()
    
    def load_raw(self, raw_sites: list[dict]):
        """Load and normalize raw API data."""
        self.sites = [Site.from_raw(s) for s in raw_sites]
        self.last_update = datetime.now()
    
    # ==========================================
    # Core Operations
    # ==========================================
    
    def filter(self, predicate: Callable[[Site], bool]) -> list[Site]:
        """Filter sites by predicate function."""
        return [s for s in self.sites if predicate(s)]
    
    def sort(self, field: str, reverse: bool = True) -> list[Site]:
        """Sort sites by field."""
        return sorted(self.sites, key=lambda s: getattr(s, field, 0), reverse=reverse)
    
    def top(self, n: int, field: str) -> list[Site]:
        """Get top N sites by field."""
        return self.sort(field, reverse=True)[:n]
    
    def bottom(self, n: int, field: str) -> list[Site]:
        """Get bottom N sites by field."""
        return self.sort(field, reverse=False)[:n]
    
    def sum(self, field: str) -> int:
        """Sum a field across all sites."""
        return sum(getattr(s, field, 0) for s in self.sites)
    
    def avg(self, field: str) -> float:
        """Average a field across all sites."""
        if not self.sites:
            return 0
        return round(self.sum(field) / len(self.sites), 1)
    
    def count(self, predicate: Callable[[Site], bool] = None) -> int:
        """Count sites, optionally filtered."""
        if predicate:
            return len(self.filter(predicate))
        return len(self.sites)
    
    def find_by_name(self, name: str) -> Optional[Site]:
        """Find site by name (partial match)."""
        name_lower = name.lower()
        for site in self.sites:
            if name_lower in site.name.lower() or name_lower in site.internal_name.lower():
                return site
        return None
    
    def search(self, query: str) -> list[Site]:
        """Search sites by name or ISP."""
        q = query.lower()
        return [s for s in self.sites 
                if q in s.name.lower() or q in s.internal_name.lower() or q in s.isp.lower()]
    
    # ==========================================
    # Summary
    # ==========================================
    
    def summary(self) -> FleetSummary:
        """Generate fleet summary."""
        healthy = self.filter(lambda s: s.is_healthy)
        with_issues = self.filter(lambda s: s.has_issues)
        critical = self.filter(lambda s: s.offline_gateway > 0 or s.critical_alerts > 0)
        
        top_issues = sorted(
            [s for s in self.sites if s.has_issues],
            key=lambda s: s.offline_devices,
            reverse=True
        )[:5]
        
        return FleetSummary(
            total_sites=len(self.sites),
            total_devices=self.sum('total_devices'),
            total_clients=self.sum('total_clients'),
            wifi_clients=self.sum('wifi_clients'),
            wired_clients=self.sum('wired_clients'),
            online_devices=self.sum('online_devices'),
            offline_devices=self.sum('offline_devices'),
            healthy_sites=len(healthy),
            warning_sites=len(with_issues) - len(critical),
            critical_sites=len(critical),
            avg_health_score=self.avg('health_score'),
            top_issues=[{'name': s.name, 'offline': s.offline_devices, 'alerts': s.critical_alerts} 
                       for s in top_issues]
        )
    
    # ==========================================
    # Natural Language Query Engine
    # ==========================================
    
    def query(self, query_str: str) -> dict:
        """
        Process natural language query and return results.
        
        Returns dict with:
            - type: 'summary', 'filter', 'ranking', 'aggregate', 'detail', 'help', 'unknown'
            - data: Query-specific results
        """
        q = query_str.lower().strip()
        
        # Help
        if re.match(r'^(help|\?|commands)', q):
            return {'type': 'help', 'data': self._help_text()}
        
        # Rankings: "top N", "worst N"
        rank_match = re.search(r'(?:top|best|worst|bottom|lowest|highest)\s*(\d+)?', q)
        if rank_match:
            n = int(rank_match.group(1) or 10)
            field = self._detect_field(q)
            is_worst = bool(re.search(r'worst|bottom|lowest', q))
            sites = self.bottom(n, field) if is_worst else self.top(n, field)
            return {
                'type': 'ranking',
                'data': {
                    'sites': [s.to_dict() for s in sites],
                    'field': field,
                    'order': 'asc' if is_worst else 'desc',
                    'count': n
                }
            }
        
        # Aggregations: "total X", "average X"
        if re.match(r'^(?:total|sum|average|avg|mean)\s+', q) or 'how many' in q:
            field = self._detect_field(q)
            if re.search(r'average|avg|mean', q):
                return {'type': 'aggregate', 'data': {'operation': 'avg', 'field': field, 'value': self.avg(field)}}
            if 'how many sites' in q:
                pred = self._build_predicate(q)
                count = self.count(pred) if pred else len(self.sites)
                return {'type': 'aggregate', 'data': {'operation': 'count', 'field': 'sites', 'value': count}}
            return {'type': 'aggregate', 'data': {'operation': 'sum', 'field': field, 'value': self.sum(field)}}
        
        # Site detail: "status of X"
        detail_match = re.search(r'(?:status|detail|show me|how is|check)\s+(?:of\s+|for\s+)?(.+?)(?:\?|$)', q, re.I)
        if detail_match:
            name = self._extract_site_name(q)
            if name:
                site = self.find_by_name(name)
                if site:
                    return {'type': 'detail', 'data': {'site': site.to_dict()}}
                suggestions = self.search(name.split()[0])[:3]
                return {'type': 'notfound', 'data': {'query': name, 'suggestions': [s.name for s in suggestions]}}
        
        # Summary
        if re.search(r'summary|overview|fleet|dashboard|everything', q):
            return {'type': 'summary', 'data': self.summary().__dict__}
        
        # What's offline
        if re.search(r'what.*(offline|down|issue|problem)', q) or q == 'offline':
            sites = self.filter(lambda s: s.has_issues)
            return {'type': 'filter', 'data': {'sites': [s.to_dict() for s in sites], 'query': 'sites with issues'}}
        
        # Build predicate and filter
        pred = self._build_predicate(q)
        if pred:
            sites = self.filter(pred)
            return {'type': 'filter', 'data': {'sites': [s.to_dict() for s in sites], 'query': q}}
        
        # Search by name
        results = self.search(q)
        if results:
            return {'type': 'search', 'data': {'sites': [s.to_dict() for s in results], 'query': q}}
        
        return {'type': 'unknown', 'data': {'query': q}}
    
    def _detect_field(self, q: str) -> str:
        """Detect which field the query is about."""
        for pattern, field in self.FIELD_PATTERNS:
            if re.search(pattern, q, re.I):
                return field
        return 'total_clients'
    
    def _build_predicate(self, q: str) -> Optional[Callable[[Site], bool]]:
        """Build filter predicate from natural language."""
        predicates = []
        
        # Numeric comparisons
        for pattern, op in self.COMPARISON_PATTERNS:
            match = re.search(pattern, q, re.I)
            if match:
                num = int(match.group(1))
                field = self._detect_field(q)
                
                if op == '>':
                    predicates.append(lambda s, f=field, n=num: getattr(s, f, 0) > n)
                elif op == '>=':
                    predicates.append(lambda s, f=field, n=num: getattr(s, f, 0) >= n)
                elif op == '<':
                    predicates.append(lambda s, f=field, n=num: getattr(s, f, 0) < n)
                elif op == '<=':
                    predicates.append(lambda s, f=field, n=num: getattr(s, f, 0) <= n)
                elif op == '==':
                    predicates.append(lambda s, f=field, n=num: getattr(s, f, 0) == n)
                break
        
        # Status filters
        if re.search(r'(?:^|\s)(offline|down|issue|problem|unhealthy)', q) and not re.search(r'not\s+', q):
            predicates.append(lambda s: s.has_issues)
        if re.search(r'(?:^|\s)(healthy|online|good)(?:\s|$)', q):
            predicates.append(lambda s: s.is_healthy)
        
        # ISP filters
        for query_pattern, isp_pattern in self.ISP_PATTERNS:
            if re.search(query_pattern, q, re.I):
                predicates.append(lambda s, p=isp_pattern: bool(s.isp and re.search(p, s.isp, re.I)))
                break
        
        # Customer name patterns
        for name in self.CUSTOMER_NAMES:
            if name in q:
                predicates.append(lambda s, n=name: n in s.name.lower())
                break
        
        if not predicates:
            return None
        
        return lambda s: all(p(s) for p in predicates)
    
    def _extract_site_name(self, q: str) -> Optional[str]:
        """Extract site name from query."""
        # Quoted
        quoted = re.search(r'["\']([^"\']+)["\']', q)
        if quoted:
            return quoted.group(1)
        
        # Pattern match
        patterns = [
            r'status\s+(?:of\s+)?(.+?)(?:\?|$)',
            r'details?\s+(?:for\s+)?(.+?)(?:\?|$)',
            r'show\s+(?:me\s+)?(.+?)(?:\?|$)',
            r'how\s+is\s+(.+?)(?:\?|$)',
            r'check\s+(?:on\s+)?(.+?)(?:\?|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, q, re.I)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'\s+(site|location|office)$', '', name, flags=re.I)
                return name
        
        return None
    
    def _help_text(self) -> str:
        """Return help text."""
        return """
UniFi Fleet Query Engine
========================

Status Queries:
  - "what's offline?" - Sites with issues
  - "show healthy sites" - Sites without issues
  - "summary" - Fleet overview

Filters:
  - "sites with more than 5 offline devices"
  - "under 95% uptime"
  - "Verizon customers"

Rankings:
  - "top 10 by clients"
  - "worst health score"
  - "bottom 5 uptime"

Aggregations:
  - "total clients"
  - "average health score"
  - "how many sites have issues"

Site Details:
  - "status of [site name]"
  - "show Celebration Church"
"""


# ============================================
# Response Formatter
# ============================================

class ResponseFormatter:
    """Format query results for display."""
    
    FIELD_LABELS = {
        'total_clients': 'clients',
        'offline_devices': 'offline devices',
        'health_score': 'health score',
        'wan_uptime': 'uptime',
        'total_devices': 'devices',
        'tx_retry': 'TX retry',
        'critical_alerts': 'critical alerts'
    }
    
    @classmethod
    def format(cls, result: dict) -> str:
        """Format query result for display."""
        rtype = result['type']
        data = result['data']
        
        if rtype == 'summary':
            return cls._format_summary(data)
        elif rtype == 'detail':
            return cls._format_detail(data['site'])
        elif rtype == 'filter' or rtype == 'search':
            return cls._format_list(data['sites'], data.get('query', ''))
        elif rtype == 'ranking':
            return cls._format_ranking(data['sites'], data['field'], data['order'], data['count'])
        elif rtype == 'aggregate':
            return cls._format_aggregate(data['operation'], data['field'], data['value'])
        elif rtype == 'help':
            return data
        elif rtype == 'notfound':
            return cls._format_notfound(data['query'], data.get('suggestions', []))
        else:
            return f"Unknown query: {data.get('query', '')}"
    
    @classmethod
    def _format_summary(cls, data: dict) -> str:
        pct = round(data['healthy_sites'] / data['total_sites'] * 100) if data['total_sites'] else 0
        
        lines = [
            "🌐 Fleet Status",
            "=" * 40,
            f"Sites: {data['total_sites']} | Devices: {data['total_devices']} | Clients: {data['total_clients']:,}",
            "",
            "Health Overview:",
            f"  🟢 Healthy:  {data['healthy_sites']} ({pct}%)",
            f"  🟡 Warning:  {data['warning_sites']}",
            f"  🔴 Critical: {data['critical_sites']}",
            "",
            f"Avg Health Score: {data['avg_health_score']}%"
        ]
        
        if data.get('top_issues'):
            lines.extend(["", "Top Issues:"])
            for i, issue in enumerate(data['top_issues'][:5], 1):
                lines.append(f"  {i}. {issue['name']} - {issue['offline']} offline")
        
        return "\n".join(lines)
    
    @classmethod
    def _format_detail(cls, site: dict) -> str:
        emoji = '🟢' if site['health_score'] >= 90 else '🟡' if site['health_score'] >= 70 else '🔴'
        
        return f"""📍 {site['name']}
{'=' * 40}
Health Score: {site['health_score']}% {emoji}
ISP: {site.get('isp', 'N/A')} | Uptime: {site.get('wan_uptime', 0)}%

Devices: {site['online_devices']}/{site['total_devices']} online
Clients: {site['total_clients']} ({site['wifi_clients']} WiFi, {site['wired_clients']} wired)

Status: {'⚠️ Has Issues' if site['has_issues'] else '✅ Healthy'}"""
    
    @classmethod
    def _format_list(cls, sites: list, query: str) -> str:
        if not sites:
            return f"No sites found for '{query}'"
        
        lines = [f"Found {len(sites)} sites:"]
        for i, site in enumerate(sites[:15], 1):
            icon = '🔴' if site.get('has_issues') else '🟢'
            detail = f"{site['offline_devices']} offline" if site.get('offline_devices', 0) > 0 else f"{site['total_clients']} clients"
            lines.append(f"  {i}. {icon} {site['name']} ({detail})")
        
        if len(sites) > 15:
            lines.append(f"  ... and {len(sites) - 15} more")
        
        return "\n".join(lines)
    
    @classmethod
    def _format_ranking(cls, sites: list, field: str, order: str, count: int) -> str:
        label = cls.FIELD_LABELS.get(field, field)
        title = f"⚠️ Lowest {label}" if order == 'asc' else f"🏆 Top {count} by {label}"
        suffix = '%' if field in ('wan_uptime', 'health_score', 'tx_retry') else ''
        
        lines = [title]
        for i, site in enumerate(sites, 1):
            lines.append(f"  {i}. {site['name']}: {site.get(field, 0)}{suffix}")
        
        return "\n".join(lines)
    
    @classmethod
    def _format_aggregate(cls, operation: str, field: str, value) -> str:
        label = cls.FIELD_LABELS.get(field, field)
        suffix = '%' if field in ('wan_uptime', 'health_score') else ''
        
        if operation == 'avg':
            return f"📊 Average {label}: {value}{suffix}"
        elif operation == 'count':
            return f"📊 {value} {label}"
        else:
            return f"📊 Total {label}: {value:,}"
    
    @classmethod
    def _format_notfound(cls, query: str, suggestions: list) -> str:
        msg = f"❌ Site '{query}' not found"
        if suggestions:
            msg += "\n\nDid you mean:"
            for s in suggestions:
                msg += f"\n  • {s}"
        return msg


# ============================================
# Demo Data Generator
# ============================================

def generate_demo_data() -> list[dict]:
    """Generate demo site data for testing."""
    import random
    
    names = [
        'Setco Corporate', 'Setco Warehouse', 'Celebration Church Main',
        'Celebration Church South', 'Hoods Discount HQ', 'Jubilee Medical Center',
        'Coastal Realty', 'Fairhope Office Park', 'Panama City Branch',
        'Destin Beach Resort', 'Pensacola Industrial', 'Kinder Morgan Terminal',
        'Fulcrum Engineering', 'Clauger HVAC', 'OberaConnect NOC', 'Tracery Interiors'
    ]
    isps = ['Verizon', 'AT&T', 'Spectrum', 'Lumen', 'Comcast', 'Mediacom']
    
    sites = []
    for i, name in enumerate(names):
        offline = random.randint(1, 3) if random.random() > 0.8 else 0
        total = random.randint(5, 20)
        clients = random.randint(20, 200)
        
        sites.append({
            'siteId': f'site-{i}',
            'meta': {'desc': name, 'name': name.lower().replace(' ', '-')},
            'statistics': {
                'counts': {
                    'totalDevice': total,
                    'offlineDevice': offline,
                    'wifiDevice': int(total * 0.6),
                    'wiredDevice': int(total * 0.3),
                    'gatewayDevice': 1,
                    'offlineWifiDevice': int(offline * 0.5),
                    'offlineWiredDevice': int(offline * 0.3),
                    'offlineGatewayDevice': 1 if offline > 2 else 0,
                    'wifiClient': int(clients * 0.7),
                    'wiredClient': int(clients * 0.3),
                    'guestClient': random.randint(0, 10),
                    'criticalNotification': 1 if offline > 1 else 0,
                    'warningNotification': random.randint(0, 3)
                },
                'percentages': {'txRetry': random.random() * 10},
                'wans': {
                    'WAN1': {
                        'wanUptime': 95 + random.random() * 5,
                        'externalIp': f'203.0.113.{i+1}',
                        'ispInfo': {'name': isps[i % len(isps)]}
                    }
                }
            }
        })
    
    return sites


# ============================================
# CLI Interface
# ============================================

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='UniFi Fleet Manager CLI')
    parser.add_argument('--headers', '-H', help='Path to JSON headers file')
    parser.add_argument('--demo', '-d', action='store_true', help='Use demo data')
    parser.add_argument('--query', '-q', help='Run a single query')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = UniFiAnalyzer()
    
    if args.demo:
        print("Loading demo data...")
        analyzer.load_raw(generate_demo_data())
        print(f"Loaded {len(analyzer.sites)} demo sites.\n")
    elif args.headers:
        if not HAS_REQUESTS:
            print("Error: requests library required for API access.")
            print("Install with: pip install requests")
            sys.exit(1)
        
        print("Fetching data from UniFi API...")
        client = UniFiClient.from_file(args.headers)
        sites = client.fetch_sites()
        analyzer.load_sites(sites)
        print(f"Loaded {len(analyzer.sites)} sites.\n")
    else:
        print("Use --demo for demo data or --headers <file> for API access.")
        print("Run with --help for more options.")
        sys.exit(0)
    
    # Single query mode
    if args.query:
        result = analyzer.query(args.query)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(ResponseFormatter.format(result))
        return
    
    # Interactive mode
    print("UniFi Fleet Query Engine")
    print("Type 'help' for commands, 'quit' to exit.\n")
    
    while True:
        try:
            query = input("query> ").strip()
            if not query:
                continue
            if query.lower() in ('quit', 'exit', 'q'):
                break
            
            result = analyzer.query(query)
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(ResponseFormatter.format(result))
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    main()
