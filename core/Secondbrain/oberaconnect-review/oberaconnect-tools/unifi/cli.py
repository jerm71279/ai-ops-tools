"""
UniFi Fleet Query Engine CLI

Command-line interface for querying UniFi fleet data.

Usage:
    python -m unifi.cli --demo --query "summary"
    python -m unifi.cli --demo --query "sites with offline devices"
    python -m unifi.cli --demo  # Interactive mode
"""

import argparse
import json
import sys
from typing import Optional

from .api_client import get_client
from .analyzer import UniFiAnalyzer, QueryResult


def format_result(result: QueryResult, output_format: str = 'text') -> str:
    """Format query result for display."""
    if output_format == 'json':
        return json.dumps(result.to_dict(), indent=2)
    
    # Text format
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Query Result: {result.intent.name}")
    lines.append(f"{'='*60}")
    
    if not result.success:
        lines.append(f"\n❌ {result.message}")
        return '\n'.join(lines)
    
    lines.append(f"\n✅ {result.message}")
    lines.append(f"   Sites: {result.site_count}")
    
    data = result.data
    
    # Handle different data types
    if isinstance(data, dict):
        # Summary or grouped data
        if 'totalSites' in data:
            # Fleet summary
            lines.append("\n--- Fleet Summary ---")
            lines.append(f"Total Sites:      {data.get('totalSites', 0)}")
            lines.append(f"Healthy Sites:    {data.get('healthySites', 0)}")
            lines.append(f"Warning Sites:    {data.get('warningSites', 0)}")
            lines.append(f"Critical Sites:   {data.get('criticalSites', 0)}")
            lines.append(f"Fleet Health:     {data.get('fleetHealthScore', 0)}%")
            lines.append(f"Total Devices:    {data.get('totalDevices', 0)}")
            lines.append(f"Offline Devices:  {data.get('offlineDevices', 0)}")
            lines.append(f"Total Clients:    {data.get('totalClients', 0)}")
            
            if data.get('sitesByISP'):
                lines.append("\n--- Sites by ISP ---")
                for isp, count in sorted(data['sitesByISP'].items(), key=lambda x: -x[1]):
                    lines.append(f"  {isp}: {count}")
        
        elif 'groupedBy' in data:
            # Grouped data
            lines.append(f"\n--- Grouped by {data['groupedBy']} ---")
            for group, count in sorted(data['groups'].items(), key=lambda x: -x[1]):
                lines.append(f"  {group}: {count} sites")
        
        elif 'count' in data:
            # Count result
            lines.append(f"\nCount: {data['count']}")
    
    elif isinstance(data, list):
        # List of sites
        if data:
            lines.append("\n--- Sites ---")
            for i, site in enumerate(data[:20], 1):  # Limit to 20
                name = site.get('name', 'Unknown')
                devices = site.get('totalDevices', 0)
                offline = site.get('offlineDevices', 0)
                clients = site.get('totalClients', 0)
                health = site.get('healthStatus', 'unknown')
                
                status_icon = '✅' if health == 'healthy' else '⚠️' if health == 'warning' else '❌'
                
                lines.append(f"  {i}. {status_icon} {name}")
                lines.append(f"      Devices: {devices} ({offline} offline) | Clients: {clients}")
            
            if len(data) > 20:
                lines.append(f"\n  ... and {len(data) - 20} more sites")
    
    return '\n'.join(lines)


def interactive_mode(analyzer: UniFiAnalyzer, output_format: str = 'text'):
    """Run in interactive REPL mode."""
    print("\n" + "="*60)
    print("UniFi Fleet Query Engine - Interactive Mode")
    print("="*60)
    print("\nExamples:")
    print("  - summary")
    print("  - sites with offline devices")
    print("  - top 5 by clients")
    print("  - group by isp")
    print("  - find setco")
    print("\nType 'quit' or 'exit' to exit.\n")
    
    while True:
        try:
            query = input("unifi> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not query:
            continue
        
        if query.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        
        if query.lower() == 'help':
            print("\nQuery examples:")
            print("  summary              - Fleet overview")
            print("  show all             - List all sites")
            print("  sites with offline   - Sites with offline devices")
            print("  top 5 by clients     - Top 5 sites by client count")
            print("  bottom 3 by health   - Bottom 3 by health score")
            print("  group by isp         - Group sites by ISP")
            print("  find <name>          - Search for site by name")
            print("  how many healthy     - Count healthy sites")
            print()
            continue
        
        result = analyzer.analyze(query)
        print(format_result(result, output_format))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='UniFi Fleet Query Engine CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo --query "summary"
  %(prog)s --demo --query "sites with offline devices"
  %(prog)s --demo --query "top 5 by clients"
  %(prog)s --demo  # Interactive mode
        """
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Use demo data (no API credentials needed)'
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Query to execute (if not provided, enters interactive mode)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Get client
    try:
        client = get_client(demo=args.demo)
    except Exception as e:
        print(f"Error initializing client: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load sites
    try:
        sites = client.get_sites()
        if args.verbose:
            print(f"Loaded {len(sites)} sites")
    except Exception as e:
        print(f"Error loading sites: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create analyzer
    analyzer = UniFiAnalyzer(sites)
    
    # Execute query or enter interactive mode
    if args.query:
        result = analyzer.analyze(args.query)
        print(format_result(result, args.format))
    else:
        interactive_mode(analyzer, args.format)


if __name__ == '__main__':
    main()
