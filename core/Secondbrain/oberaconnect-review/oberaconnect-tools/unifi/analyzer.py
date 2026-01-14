"""
UniFi Fleet Query Engine

Natural language query processing for UniFi site data.

Supports queries like:
- "show sites with offline devices"
- "which sites have more than 100 clients"
- "top 5 sites by device count"
- "group sites by ISP"
- "summary"
"""

import re
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum, auto

from .models import UniFiSite, FleetSummary


logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Detected intent from natural language query."""
    FILTER = auto()      # Filter sites by criteria
    SORT = auto()        # Sort sites by field
    TOP = auto()         # Get top N sites
    BOTTOM = auto()      # Get bottom N sites
    GROUP = auto()       # Group by field
    SUMMARY = auto()     # Fleet summary
    COUNT = auto()       # Count matching sites
    SEARCH = auto()      # Search by name
    FIND = auto()        # Find specific site
    AGGREGATE = auto()   # Sum/Avg calculations
    UNKNOWN = auto()     # Couldn't determine intent


@dataclass
class QueryResult:
    """Result of a query operation."""
    success: bool
    intent: QueryIntent
    data: Any
    message: str
    site_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'intent': self.intent.name,
            'data': self.data,
            'message': self.message,
            'siteCount': self.site_count
        }


class UniFiAnalyzer:
    """
    Natural Language Query Engine for UniFi Fleet Data.
    
    Processes queries and returns filtered/aggregated results.
    """
    
    # Field mappings from natural language to data attributes
    FIELD_MAPPINGS = {
        # Client/user counts
        'clients': 'total_clients',
        'users': 'total_clients',
        'client': 'total_clients',
        'user': 'total_clients',
        'totalclients': 'total_clients',
        
        # Device counts
        'devices': 'total_devices',
        'device': 'total_devices',
        'totaldevices': 'total_devices',
        
        # Offline devices
        'offline': 'offline_devices',
        'offlinedevices': 'offline_devices',
        'down': 'offline_devices',
        
        # Health
        'health': 'health_score',
        'healthscore': 'health_score',
        'score': 'health_score',
        
        # APs
        'aps': 'ap_count',
        'ap': 'ap_count',
        'accesspoints': 'ap_count',
        'accesspoint': 'ap_count',
        
        # Switches
        'switches': 'switch_count',
        'switch': 'switch_count',
        
        # Gateways
        'gateways': 'gateway_count',
        'gateway': 'gateway_count',
        'router': 'gateway_count',
        'routers': 'gateway_count',
        
        # ISP
        'isp': 'isp',
        'provider': 'isp',
        'internet': 'isp',
        
        # Name
        'name': 'name',
        'sitename': 'name',
        'site': 'name'
    }
    
    # Comparison operators
    COMPARISONS = {
        'more than': '>',
        'greater than': '>',
        'over': '>',
        'above': '>',
        '>': '>',
        'less than': '<',
        'fewer than': '<',
        'under': '<',
        'below': '<',
        '<': '<',
        'at least': '>=',
        'minimum': '>=',
        '>=': '>=',
        'at most': '<=',
        'maximum': '<=',
        '<=': '<=',
        'exactly': '==',
        'equal to': '==',
        'equals': '==',
        '==': '==',
        '=': '=='
    }
    
    # Known ISPs for OberaConnect
    KNOWN_ISPS = {
        'verizon': 'Verizon',
        'lumen': 'Lumen',
        'at&t': 'AT&T',
        'att': 'AT&T',
        'spectrum': 'Spectrum',
        'comcast': 'Comcast',
        'xfinity': 'Comcast',
        'cox': 'Cox',
        'frontier': 'Frontier'
    }
    
    # Known customer names (OberaConnect specific)
    KNOWN_CUSTOMERS = [
        'setco', 'hoods', 'kinder', 'celebration', 
        'gulf shores', 'mobile bay', 'fairhope', 'daphne'
    ]
    
    def __init__(self, sites: List[UniFiSite] = None):
        """
        Initialize analyzer with site data.
        
        Args:
            sites: List of UniFiSite objects to analyze
        """
        self._sites = sites or []
    
    @property
    def sites(self) -> List[UniFiSite]:
        return self._sites
    
    @sites.setter
    def sites(self, value: List[UniFiSite]):
        self._sites = value
    
    def analyze(self, query: str) -> QueryResult:
        """
        Process a natural language query.
        
        Args:
            query: Natural language query string
            
        Returns:
            QueryResult with processed data
        """
        if not self._sites:
            return QueryResult(
                success=False,
                intent=QueryIntent.UNKNOWN,
                data=None,
                message="No site data loaded"
            )
        
        query_lower = query.lower().strip()
        
        # Detect intent and process
        # Check DETAIL first (before SUMMARY, since "status of X" contains "status")
        if self._is_detail_query(query_lower):
            return self._handle_detail(query_lower)

        if self._is_aggregate_query(query_lower):
            return self._handle_aggregate(query_lower)

        if self._is_summary_query(query_lower):
            return self._handle_summary()

        if self._is_top_bottom_query(query_lower):
            return self._handle_top_bottom(query_lower)

        if self._is_group_query(query_lower):
            return self._handle_group(query_lower)

        if self._is_count_query(query_lower):
            return self._handle_count(query_lower)

        if self._is_search_query(query_lower):
            return self._handle_search(query_lower)

        # Default: try to interpret as filter
        return self._handle_filter(query_lower)
    
    def _is_detail_query(self, query: str) -> bool:
        """Check if query is asking for specific site details."""
        # "status of X", "details for X", "show X site"
        patterns = [
            r'status\s+of\s+\w+',
            r'details?\s+(for|of)\s+\w+',
            r'show\s+\w+\s+site',
            r'how\s+is\s+\w+',
            r'what.+about\s+\w+'
        ]
        return any(re.search(p, query) for p in patterns)

    def _is_aggregate_query(self, query: str) -> bool:
        """Check if query is asking for aggregation (sum, avg, total)."""
        # Use word boundaries to avoid matching 'sum' inside 'summary'
        patterns = [r'\btotal\b', r'\bsum\b', r'\baverage\b', r'\bavg\b', r'\bmean\b', r'across all', r'all sites']
        return any(re.search(p, query) for p in patterns)

    def _is_summary_query(self, query: str) -> bool:
        """Check if query is asking for summary."""
        keywords = ['summary', 'overview', 'stats', 'statistics', 'fleet']
        # Removed 'status' - now handled by _is_detail_query
        return any(kw in query for kw in keywords)
    
    def _is_top_bottom_query(self, query: str) -> bool:
        """Check if query is asking for top/bottom N."""
        return bool(re.search(r'\b(top|bottom|highest|lowest|best|worst)\s*\d*\b', query))
    
    def _is_group_query(self, query: str) -> bool:
        """Check if query is asking for grouping."""
        return 'group' in query or 'by isp' in query or 'per isp' in query
    
    def _is_count_query(self, query: str) -> bool:
        """Check if query is asking for count."""
        return query.startswith('how many') or query.startswith('count')
    
    def _is_search_query(self, query: str) -> bool:
        """Check if query is searching for specific site."""
        keywords = ['find', 'search', 'where is', 'show me', 'locate']
        return any(kw in query for kw in keywords)
    
    def _handle_detail(self, query: str) -> QueryResult:
        """Handle site detail queries like 'status of Celebration Church'."""
        # Extract site name from query
        patterns = [
            r'status\s+of\s+(.+?)(?:\?|$)',
            r'details?\s+(?:for|of)\s+(.+?)(?:\?|$)',
            r'how\s+is\s+(.+?)(?:\?|$)',
            r'what.+about\s+(.+?)(?:\?|$)'
        ]

        site_name = None
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                site_name = match.group(1).strip()
                break

        if not site_name:
            return self._handle_search(query)

        # Find matching site
        matches = [s for s in self._sites if site_name.lower() in s.name.lower()]

        if not matches:
            return QueryResult(
                success=True,
                intent=QueryIntent.FIND,
                data=[],
                message=f"No site found matching '{site_name}'",
                site_count=0
            )

        site = matches[0]  # Return first match
        return QueryResult(
            success=True,
            intent=QueryIntent.FIND,
            data=site.to_dict(),
            message=f"Site: {site.name} - Health: {site.health_score}%, Devices: {site.total_devices}, Clients: {site.total_clients}",
            site_count=1
        )

    def _handle_aggregate(self, query: str) -> QueryResult:
        """Handle aggregation queries like 'total clients across all sites'."""
        field = self._detect_field(query)

        # Determine aggregation type
        if 'average' in query or 'avg' in query or 'mean' in query:
            values = [getattr(s, field, 0) for s in self._sites]
            result = sum(values) / len(values) if values else 0
            agg_type = 'average'
        else:  # Default to sum/total
            result = sum(getattr(s, field, 0) for s in self._sites)
            agg_type = 'total'

        return QueryResult(
            success=True,
            intent=QueryIntent.AGGREGATE,
            data={'field': field, 'value': result, 'type': agg_type},
            message=f"{agg_type.title()} {field}: {result:,.0f}" if isinstance(result, (int, float)) else f"{agg_type.title()} {field}: {result}",
            site_count=len(self._sites)
        )

    def _handle_summary(self) -> QueryResult:
        """Generate fleet summary."""
        summary = FleetSummary.from_sites(self._sites)

        return QueryResult(
            success=True,
            intent=QueryIntent.SUMMARY,
            data=summary.to_dict(),
            message=f"Fleet summary: {summary.total_sites} sites, {summary.total_devices} devices, {summary.fleet_health_score}% healthy",
            site_count=summary.total_sites
        )
    
    def _handle_top_bottom(self, query: str) -> QueryResult:
        """Handle top/bottom N queries."""
        # Extract N
        match = re.search(r'\b(top|bottom|highest|lowest|best|worst)\s*(\d+)?', query)
        if not match:
            return self._unknown_result(query)
        
        direction = match.group(1)
        n = int(match.group(2)) if match.group(2) else 5
        
        is_top = direction in ('top', 'highest', 'best')
        
        # Detect field to sort by
        field = self._detect_field(query)
        
        # Sort and slice
        sorted_sites = sorted(
            self._sites,
            key=lambda s: getattr(s, field, 0),
            reverse=is_top
        )[:n]
        
        return QueryResult(
            success=True,
            intent=QueryIntent.TOP if is_top else QueryIntent.BOTTOM,
            data=[s.to_dict() for s in sorted_sites],
            message=f"{'Top' if is_top else 'Bottom'} {n} sites by {field}",
            site_count=len(sorted_sites)
        )
    
    def _handle_group(self, query: str) -> QueryResult:
        """Handle grouping queries."""
        # Determine grouping field
        if 'isp' in query or 'provider' in query:
            groups = self._group_by('isp')
            field = 'ISP'
        elif 'status' in query or 'health' in query:
            groups = self._group_by('health_status')
            field = 'Health Status'
        else:
            groups = self._group_by('isp')  # Default
            field = 'ISP'
        
        # Format output
        formatted = {k: len(v) for k, v in groups.items()}
        
        return QueryResult(
            success=True,
            intent=QueryIntent.GROUP,
            data={
                'groupedBy': field,
                'groups': formatted,
                'details': {k: [s.to_dict() for s in v] for k, v in groups.items()}
            },
            message=f"Sites grouped by {field}: {len(groups)} groups",
            site_count=len(self._sites)
        )
    
    def _handle_count(self, query: str) -> QueryResult:
        """Handle count queries."""
        # Apply any filters first
        filtered = self._apply_filters(query, self._sites)
        
        return QueryResult(
            success=True,
            intent=QueryIntent.COUNT,
            data={'count': len(filtered)},
            message=f"Found {len(filtered)} matching sites",
            site_count=len(filtered)
        )
    
    def _handle_search(self, query: str) -> QueryResult:
        """Handle search queries."""
        # Extract search term
        for kw in ['find', 'search', 'where is', 'show me', 'locate']:
            query = query.replace(kw, '')
        
        search_term = query.strip().lower()
        
        # Search by name
        matches = [
            s for s in self._sites
            if search_term in s.name.lower()
        ]
        
        if not matches:
            return QueryResult(
                success=True,
                intent=QueryIntent.SEARCH,
                data=[],
                message=f"No sites found matching '{search_term}'",
                site_count=0
            )
        
        return QueryResult(
            success=True,
            intent=QueryIntent.SEARCH,
            data=[s.to_dict() for s in matches],
            message=f"Found {len(matches)} site(s) matching '{search_term}'",
            site_count=len(matches)
        )
    
    def _handle_filter(self, query: str) -> QueryResult:
        """Handle filter queries."""
        filtered = self._apply_filters(query, self._sites)
        
        return QueryResult(
            success=True,
            intent=QueryIntent.FILTER,
            data=[s.to_dict() for s in filtered],
            message=f"Found {len(filtered)} sites matching criteria",
            site_count=len(filtered)
        )
    
    def _apply_filters(self, query: str, sites: List[UniFiSite]) -> List[UniFiSite]:
        """Apply detected filters to site list."""
        results = sites.copy()
        
        # Check for offline filter
        if 'offline' in query or 'down' in query:
            if 'no offline' in query or 'without offline' in query:
                results = [s for s in results if s.offline_devices == 0]
            else:
                results = [s for s in results if s.offline_devices > 0]
        
        # Check for numeric comparisons
        predicate = self._build_predicate(query)
        if predicate:
            results = [s for s in results if predicate(s)]
        
        # Check for ISP filter
        for isp_key, isp_name in self.KNOWN_ISPS.items():
            if isp_key in query:
                results = [s for s in results if isp_name.lower() in s.isp.lower()]
                break
        
        # Check for health status
        if 'healthy' in query:
            results = [s for s in results if s.health_status == 'healthy']
        elif 'critical' in query:
            results = [s for s in results if s.health_status == 'critical']
        elif 'warning' in query or 'degraded' in query:
            results = [s for s in results if s.health_status in ('warning', 'degraded')]
        
        return results
    
    def _build_predicate(self, query: str) -> Optional[Callable[[UniFiSite], bool]]:
        """
        Build a filter predicate from query.
        
        Handles patterns like "more than 100 clients", "at least 5 devices"
        """
        # Pattern: [comparison] [number] [field]
        for comp_phrase, op in self.COMPARISONS.items():
            pattern = rf'{re.escape(comp_phrase)}\s*(\d+)\s*(\w+)'
            match = re.search(pattern, query)
            if match:
                value = int(match.group(1))
                field_word = match.group(2).lower()
                field = self._map_field(field_word)
                
                if field:
                    return self._make_comparison(field, op, value)
        
        # Alternative pattern: [number] or more [field]
        match = re.search(r'(\d+)\s+or\s+more\s+(\w+)', query)
        if match:
            value = int(match.group(1))
            field_word = match.group(2).lower()
            field = self._map_field(field_word)
            if field:
                return self._make_comparison(field, '>=', value)
        
        return None
    
    def _make_comparison(
        self, 
        field: str, 
        op: str, 
        value: int
    ) -> Callable[[UniFiSite], bool]:
        """Create a comparison function."""
        def compare(site: UniFiSite) -> bool:
            site_value = getattr(site, field, 0)
            if op == '>':
                return site_value > value
            elif op == '<':
                return site_value < value
            elif op == '>=':
                return site_value >= value
            elif op == '<=':
                return site_value <= value
            elif op == '==':
                return site_value == value
            return True
        
        return compare
    
    def _detect_field(self, query: str) -> str:
        """Detect which field the query is referring to."""
        query_lower = query.lower()
        
        # Check each mapping
        for word, field in self.FIELD_MAPPINGS.items():
            if word in query_lower:
                return field
        
        # Defaults
        if 'offline' in query_lower or 'down' in query_lower:
            return 'offline_devices'
        
        return 'total_devices'  # Default
    
    def _map_field(self, word: str) -> Optional[str]:
        """Map a word to a field name."""
        return self.FIELD_MAPPINGS.get(word.lower())
    
    def _group_by(self, field: str) -> Dict[str, List[UniFiSite]]:
        """Group sites by a field."""
        groups: Dict[str, List[UniFiSite]] = {}
        
        for site in self._sites:
            key = str(getattr(site, field, 'Unknown'))
            if key not in groups:
                groups[key] = []
            groups[key].append(site)
        
        return groups
    
    def _unknown_result(self, query: str) -> QueryResult:
        """Return result for unrecognized query."""
        return QueryResult(
            success=False,
            intent=QueryIntent.UNKNOWN,
            data=None,
            message=f"Could not understand query: {query}"
        )
    
    # Convenience methods
    
    def filter(self, predicate: Callable[[UniFiSite], bool]) -> List[UniFiSite]:
        """Filter sites by predicate function."""
        return [s for s in self._sites if predicate(s)]
    
    def sort(self, field: str, reverse: bool = False) -> List[UniFiSite]:
        """Sort sites by field."""
        return sorted(
            self._sites,
            key=lambda s: getattr(s, field, 0),
            reverse=reverse
        )
    
    def top(self, n: int, field: str) -> List[UniFiSite]:
        """Get top N sites by field."""
        return self.sort(field, reverse=True)[:n]
    
    def bottom(self, n: int, field: str) -> List[UniFiSite]:
        """Get bottom N sites by field."""
        return self.sort(field, reverse=False)[:n]
    
    def sum(self, field: str) -> int:
        """Sum a field across all sites."""
        return sum(getattr(s, field, 0) for s in self._sites)
    
    def avg(self, field: str) -> float:
        """Average a field across all sites."""
        if not self._sites:
            return 0.0
        return self.sum(field) / len(self._sites)
    
    def count(self, predicate: Callable[[UniFiSite], bool] = None) -> int:
        """Count sites, optionally with filter."""
        if predicate:
            return len(self.filter(predicate))
        return len(self._sites)
    
    def find_by_name(self, name: str) -> Optional[UniFiSite]:
        """Find site by exact name match."""
        for site in self._sites:
            if site.name.lower() == name.lower():
                return site
        return None
    
    def search(self, term: str) -> List[UniFiSite]:
        """Search sites by partial name match."""
        term_lower = term.lower()
        return [s for s in self._sites if term_lower in s.name.lower()]
    
    def summary(self) -> FleetSummary:
        """Get fleet summary."""
        return FleetSummary.from_sites(self._sites)


__all__ = [
    'QueryIntent',
    'QueryResult',
    'UniFiAnalyzer'
]
