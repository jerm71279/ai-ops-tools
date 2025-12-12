#!/usr/bin/env python3
"""
Network Config Complexity Analyzer
Analyzes MikroTik (.rsc) and SonicWall (.exp) configs for VLAN complexity

Identifies customers with complex segmentation similar to Saint Annes (89 VLANs)

Usage:
    ./venv/bin/python3 config_complexity_analyzer.py
    ./venv/bin/python3 config_complexity_analyzer.py --dir /path/to/configs
    ./venv/bin/python3 config_complexity_analyzer.py --file config.rsc
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class ConfigAnalysis:
    """Analysis results for a config file"""
    filename: str
    customer: str
    device_type: str  # mikrotik, sonicwall
    model: str
    vlan_count: int
    vlans: List[int]
    subnet_count: int
    subnets: List[str]
    dhcp_pools: int
    nat_rules: int
    firewall_rules: int
    static_routes: int
    vpn_tunnels: int
    complexity_score: int  # 0-100
    complexity_level: str  # low, medium, high, very_high
    notes: List[str]


class ConfigAnalyzer:
    """Analyze network config files"""

    def __init__(self):
        self.results: List[ConfigAnalysis] = []

    def analyze_file(self, filepath: str) -> Optional[ConfigAnalysis]:
        """Analyze a single config file"""
        path = Path(filepath)

        if not path.exists():
            print(f"File not found: {filepath}")
            return None

        content = path.read_text(errors='ignore')
        filename = path.name

        # Determine device type
        if path.suffix.lower() == '.rsc' or 'routeros' in content.lower() or '/interface' in content:
            return self._analyze_mikrotik(content, filename)
        elif path.suffix.lower() == '.exp' or 'sonicwall' in content.lower() or 'SonicOS' in filename:
            return self._analyze_sonicwall(content, filename)
        else:
            print(f"Unknown config type: {filename}")
            return None

    def _analyze_mikrotik(self, content: str, filename: str) -> ConfigAnalysis:
        """Analyze MikroTik RouterOS config"""
        notes = []

        # Extract customer/device name
        customer = "Unknown"
        model = "Unknown"

        # Look for identity
        identity_match = re.search(r'/system identity\s+set name="?([^"\n]+)"?', content)
        if identity_match:
            customer = identity_match.group(1).strip()

        # Look for model in comments or routerboard
        model_match = re.search(r'model:\s*(\S+)', content, re.IGNORECASE)
        if model_match:
            model = model_match.group(1)

        # Count VLANs
        vlan_matches = re.findall(r'vlan-id=(\d+)', content)
        vlans = list(set(int(v) for v in vlan_matches))
        vlan_count = len(vlans)

        # Count subnets/addresses
        subnet_matches = re.findall(r'address=(\d+\.\d+\.\d+\.\d+/\d+)', content)
        subnets = list(set(subnet_matches))
        subnet_count = len(subnets)

        # Count DHCP pools
        dhcp_pools = len(re.findall(r'/ip pool\s+add', content))
        dhcp_servers = len(re.findall(r'/ip dhcp-server\s+add', content))
        dhcp_count = max(dhcp_pools, dhcp_servers)

        # Count NAT rules
        nat_rules = len(re.findall(r'/ip firewall nat\s+add', content))

        # Count firewall rules
        firewall_rules = len(re.findall(r'/ip firewall filter\s+add', content))

        # Count static routes
        static_routes = len(re.findall(r'/ip route\s+add', content))

        # Count VPN tunnels
        vpn_tunnels = len(re.findall(r'(l2tp|pptp|sstp|ipsec|wireguard)', content, re.IGNORECASE))

        # Calculate complexity score
        complexity_score = self._calculate_complexity(
            vlan_count, subnet_count, dhcp_count, nat_rules,
            firewall_rules, static_routes, vpn_tunnels
        )

        # Determine complexity level
        if complexity_score >= 80:
            complexity_level = "VERY HIGH"
            notes.append("Complex multi-VLAN environment - consider enterprise hardware")
        elif complexity_score >= 60:
            complexity_level = "HIGH"
            notes.append("Significant segmentation - monitor resource usage")
        elif complexity_score >= 40:
            complexity_level = "MEDIUM"
        else:
            complexity_level = "LOW"

        # Special notes
        if vlan_count > 50:
            notes.append(f"ALERT: {vlan_count} VLANs - similar to Saint Annes (89)")
        if vlan_count > 100:
            notes.append("CRITICAL: Consider L3 switch for inter-VLAN routing")

        return ConfigAnalysis(
            filename=filename,
            customer=customer,
            device_type="MikroTik",
            model=model,
            vlan_count=vlan_count,
            vlans=sorted(vlans)[:20],  # First 20 for display
            subnet_count=subnet_count,
            subnets=subnets[:10],  # First 10 for display
            dhcp_pools=dhcp_count,
            nat_rules=nat_rules,
            firewall_rules=firewall_rules,
            static_routes=static_routes,
            vpn_tunnels=vpn_tunnels,
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            notes=notes
        )

    def _analyze_sonicwall(self, content: str, filename: str) -> ConfigAnalysis:
        """Analyze SonicWall config export"""
        notes = []

        # Extract customer from filename
        customer = "Unknown"
        if '_' in filename:
            parts = filename.split('_')
            for part in parts:
                if part not in ['sonicwall', 'TZ', 'SonicOS', '270', '370', '470']:
                    customer = part
                    break

        # Model from filename
        model = "Unknown"
        model_match = re.search(r'(TZ\s*\d+|NSA\s*\d+|NSv\s*\d+)', filename, re.IGNORECASE)
        if model_match:
            model = model_match.group(1)

        # SonicWall .exp files are typically encrypted/binary
        # Try to extract what we can from readable portions

        # Count zones (VLANs in SonicWall terms)
        zone_matches = re.findall(r'zone["\s:]+(\w+)', content, re.IGNORECASE)
        vlans = list(set(hash(z) % 1000 for z in zone_matches))  # Pseudo VLAN IDs
        vlan_count = len(set(zone_matches))

        # Count address objects (subnets)
        subnet_matches = re.findall(r'(\d+\.\d+\.\d+\.\d+/\d+)', content)
        subnets = list(set(subnet_matches))
        subnet_count = len(subnets)

        # Count DHCP (look for dhcp patterns)
        dhcp_count = len(re.findall(r'dhcp', content, re.IGNORECASE)) // 5  # Rough estimate

        # Count NAT policies
        nat_rules = len(re.findall(r'nat.policy', content, re.IGNORECASE))

        # Count access rules
        firewall_rules = len(re.findall(r'access.rule', content, re.IGNORECASE))

        # Routes
        static_routes = len(re.findall(r'route', content, re.IGNORECASE)) // 3

        # VPN
        vpn_tunnels = len(re.findall(r'(vpn|ipsec|tunnel)', content, re.IGNORECASE)) // 5

        # Note: SonicWall exports are often encrypted, so counts may be approximate
        notes.append("SonicWall export - some values estimated from partial data")

        complexity_score = self._calculate_complexity(
            vlan_count, subnet_count, dhcp_count, nat_rules,
            firewall_rules, static_routes, vpn_tunnels
        )

        if complexity_score >= 80:
            complexity_level = "VERY HIGH"
        elif complexity_score >= 60:
            complexity_level = "HIGH"
        elif complexity_score >= 40:
            complexity_level = "MEDIUM"
        else:
            complexity_level = "LOW"

        return ConfigAnalysis(
            filename=filename,
            customer=customer,
            device_type="SonicWall",
            model=model,
            vlan_count=vlan_count,
            vlans=sorted(vlans)[:20],
            subnet_count=subnet_count,
            subnets=subnets[:10],
            dhcp_pools=dhcp_count,
            nat_rules=nat_rules,
            firewall_rules=firewall_rules,
            static_routes=static_routes,
            vpn_tunnels=vpn_tunnels,
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            notes=notes
        )

    def _calculate_complexity(self, vlans: int, subnets: int, dhcp: int,
                              nat: int, firewall: int, routes: int, vpn: int) -> int:
        """Calculate overall complexity score (0-100)"""
        score = 0

        # VLAN weight (major factor)
        if vlans > 80:
            score += 40
        elif vlans > 50:
            score += 30
        elif vlans > 20:
            score += 20
        elif vlans > 10:
            score += 10
        elif vlans > 5:
            score += 5

        # Subnet weight
        if subnets > 50:
            score += 15
        elif subnets > 20:
            score += 10
        elif subnets > 10:
            score += 5

        # DHCP weight
        if dhcp > 50:
            score += 10
        elif dhcp > 20:
            score += 7
        elif dhcp > 10:
            score += 5

        # NAT weight
        if nat > 50:
            score += 10
        elif nat > 20:
            score += 7
        elif nat > 10:
            score += 5

        # Firewall weight
        if firewall > 100:
            score += 10
        elif firewall > 50:
            score += 7
        elif firewall > 20:
            score += 5

        # Routes weight
        if routes > 20:
            score += 8
        elif routes > 10:
            score += 5

        # VPN weight
        if vpn > 5:
            score += 7
        elif vpn > 0:
            score += 3

        return min(100, score)

    def analyze_directory(self, dirpath: str) -> List[ConfigAnalysis]:
        """Analyze all config files in a directory"""
        path = Path(dirpath)

        if not path.exists():
            print(f"Directory not found: {dirpath}")
            return []

        configs = list(path.glob("**/*.rsc")) + list(path.glob("**/*.exp"))
        print(f"Found {len(configs)} config files")

        results = []
        for config in configs:
            print(f"Analyzing: {config.name}...")
            result = self.analyze_file(str(config))
            if result:
                # Use parent folder name as customer if more descriptive
                parent_name = config.parent.name.replace('_', ' ')
                if parent_name and parent_name != 'keeper_configs' and result.customer == 'Unknown':
                    result.customer = parent_name
                elif parent_name and parent_name != 'keeper_configs':
                    result.customer = parent_name  # Prefer folder name
                results.append(result)
                self.results.append(result)

        return results

    def generate_report(self) -> str:
        """Generate analysis report"""
        if not self.results:
            return "No configs analyzed"

        report = []
        report.append("=" * 70)
        report.append("NETWORK CONFIG COMPLEXITY ANALYSIS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 70)

        # Sort by complexity
        sorted_results = sorted(self.results, key=lambda x: x.complexity_score, reverse=True)

        # Summary
        report.append("\n## SUMMARY")
        report.append(f"Total configs analyzed: {len(self.results)}")
        report.append(f"MikroTik: {sum(1 for r in self.results if r.device_type == 'MikroTik')}")
        report.append(f"SonicWall: {sum(1 for r in self.results if r.device_type == 'SonicWall')}")

        # Complexity breakdown
        very_high = [r for r in self.results if r.complexity_level == "VERY HIGH"]
        high = [r for r in self.results if r.complexity_level == "HIGH"]
        medium = [r for r in self.results if r.complexity_level == "MEDIUM"]
        low = [r for r in self.results if r.complexity_level == "LOW"]

        report.append(f"\nComplexity Distribution:")
        report.append(f"  VERY HIGH: {len(very_high)} (similar to Saint Annes)")
        report.append(f"  HIGH:      {len(high)}")
        report.append(f"  MEDIUM:    {len(medium)}")
        report.append(f"  LOW:       {len(low)}")

        # Detailed results
        report.append("\n" + "=" * 70)
        report.append("DETAILED ANALYSIS (sorted by complexity)")
        report.append("=" * 70)

        for result in sorted_results:
            report.append(f"\n### {result.customer}")
            report.append(f"File: {result.filename}")
            report.append(f"Device: {result.device_type} {result.model}")
            report.append(f"Complexity: {result.complexity_level} ({result.complexity_score}/100)")
            report.append(f"")
            report.append(f"  VLANs:          {result.vlan_count}")
            report.append(f"  Subnets:        {result.subnet_count}")
            report.append(f"  DHCP Pools:     {result.dhcp_pools}")
            report.append(f"  NAT Rules:      {result.nat_rules}")
            report.append(f"  Firewall Rules: {result.firewall_rules}")
            report.append(f"  Static Routes:  {result.static_routes}")
            report.append(f"  VPN Tunnels:    {result.vpn_tunnels}")

            if result.notes:
                report.append(f"\n  Notes:")
                for note in result.notes:
                    report.append(f"    - {note}")

        # Recommendations
        report.append("\n" + "=" * 70)
        report.append("RECOMMENDATIONS")
        report.append("=" * 70)

        if very_high:
            report.append("\n## VERY HIGH Complexity Customers:")
            for r in very_high:
                report.append(f"\n  {r.customer} ({r.vlan_count} VLANs)")
                report.append(f"    - Consider upgrading to enterprise-grade hardware")
                report.append(f"    - MikroTik: CCR series or cloud router with more RAM")
                report.append(f"    - Alternative: L3 switch for inter-VLAN routing")
                report.append(f"    - Alternative: UniFi Dream Machine Pro / UXG-Pro")

        return "\n".join(report)

    def save_report(self, filepath: str):
        """Save report to file"""
        report = self.generate_report()
        Path(filepath).write_text(report)
        print(f"Report saved to: {filepath}")

    def save_json(self, filepath: str):
        """Save results as JSON"""
        data = [asdict(r) for r in self.results]
        Path(filepath).write_text(json.dumps(data, indent=2))
        print(f"JSON saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Analyze network config complexity")
    parser.add_argument("--dir", type=str, help="Directory with config files")
    parser.add_argument("--file", type=str, help="Single config file")
    parser.add_argument("--output", type=str, default="config_analysis_report.txt", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Also save JSON output")

    args = parser.parse_args()

    analyzer = ConfigAnalyzer()

    # Default directories to check
    default_dirs = [
        "/home/mavrick/Projects/Secondbrain/keeper_configs",
        "/home/mavrick/Projects/Secondbrain/input_documents/OberaConnect",
        "/mnt/c/Users/JeremySmith/Downloads",
    ]

    if args.file:
        result = analyzer.analyze_file(args.file)
        if result:
            print(f"\n{result.customer}: {result.complexity_level} ({result.vlan_count} VLANs)")
    elif args.dir:
        analyzer.analyze_directory(args.dir)
    else:
        # Analyze all default directories
        for dir_path in default_dirs:
            if Path(dir_path).exists():
                print(f"\nScanning: {dir_path}")
                analyzer.analyze_directory(dir_path)

    if analyzer.results:
        print("\n" + analyzer.generate_report())
        analyzer.save_report(args.output)

        if args.json:
            analyzer.save_json(args.output.replace('.txt', '.json'))


if __name__ == "__main__":
    main()
