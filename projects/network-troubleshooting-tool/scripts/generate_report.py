#!/usr/bin/env python3
"""
Network Assessment Report Generator
Combines all scan results into comprehensive HTML and Markdown reports
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import argparse

class ReportGenerator:
    def __init__(self, scan_dir: str):
        self.scan_dir = scan_dir
        self.data = {}
        
    def load_results(self):
        """Load all JSON result files"""
        print("[*] Loading scan results...")
        
        result_files = {
            "discovery": "discovery_results.json",
            "connectivity": "connectivity_results.json",
            "dhcp_dns": "dhcp_dns_results.json"
        }
        
        for key, filename in result_files.items():
            filepath = os.path.join(self.scan_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.data[key] = json.load(f)
            else:
                print(f"[!] Warning: {filename} not found")
                self.data[key] = None
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        print("[*] Generating HTML report...")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Network Assessment Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .section h3 {{
            color: #764ba2;
            margin-top: 20px;
        }}
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .status.pass {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status.fail {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .status.warning {{
            background-color: #fff3cd;
            color: #856404;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
        }}
        .alert {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .alert.error {{
            background-color: #f8d7da;
            border-left: 4px solid #721c24;
            color: #721c24;
        }}
        .alert.warning {{
            background-color: #fff3cd;
            border-left: 4px solid #856404;
            color: #856404;
        }}
        .alert.info {{
            background-color: #d1ecf1;
            border-left: 4px solid #0c5460;
            color: #0c5460;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Network Assessment Report</h1>
        <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
"""
        
        # Executive Summary
        html += self._generate_executive_summary()
        
        # Network Discovery Section
        if self.data.get("discovery"):
            html += self._generate_discovery_section()
        
        # Connectivity Tests Section
        if self.data.get("connectivity"):
            html += self._generate_connectivity_section()
        
        # DHCP/DNS Section
        if self.data.get("dhcp_dns"):
            html += self._generate_dhcp_dns_section()
        
        # Recommendations
        html += self._generate_recommendations()
        
        html += """
    <div class="footer">
        Network Assessment Report | Generated by Network Troubleshooter Skill
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary section"""
        total_devices = 0
        critical_issues = []
        warnings = []
        
        if self.data.get("discovery"):
            total_devices = self.data["discovery"].get("summary", {}).get("total_devices", 0)
        
        if self.data.get("dhcp_dns"):
            if self.data["dhcp_dns"].get("dhcp", {}).get("status") == "WARNING":
                critical_issues.append("Multiple DHCP servers detected (rogue DHCP risk)")
        
        if self.data.get("connectivity"):
            if self.data["connectivity"].get("overall_status") == "ISSUES_FOUND":
                warnings.append("Connectivity issues detected")
        
        html = f"""
    <div class="section">
        <h2>📊 Executive Summary</h2>
        <div class="metric">
            <div class="metric-value">{total_devices}</div>
            <div class="metric-label">Devices Discovered</div>
        </div>
        <div class="metric">
            <div class="metric-value">{len(critical_issues)}</div>
            <div class="metric-label">Critical Issues</div>
        </div>
        <div class="metric">
            <div class="metric-value">{len(warnings)}</div>
            <div class="metric-label">Warnings</div>
        </div>
"""
        
        if critical_issues:
            html += '<div class="alert error"><strong>Critical Issues:</strong><ul>'
            for issue in critical_issues:
                html += f'<li>{issue}</li>'
            html += '</ul></div>'
        
        if warnings:
            html += '<div class="alert warning"><strong>Warnings:</strong><ul>'
            for warning in warnings:
                html += f'<li>{warning}</li>'
            html += '</ul></div>'
        
        if not critical_issues and not warnings:
            html += '<div class="alert info">✅ No critical issues detected. Network appears healthy.</div>'
        
        html += "</div>"
        return html
    
    def _generate_discovery_section(self) -> str:
        """Generate network discovery section"""
        discovery = self.data["discovery"]
        
        html = """
    <div class="section">
        <h2>🌐 Network Discovery</h2>
"""
        
        if discovery.get("arp_scan"):
            html += """
        <h3>Discovered Devices</h3>
        <table>
            <tr>
                <th>IP Address</th>
                <th>MAC Address</th>
                <th>Vendor</th>
            </tr>
"""
            for device in discovery["arp_scan"]:
                html += f"""
            <tr>
                <td><code>{device['ip']}</code></td>
                <td><code>{device['mac']}</code></td>
                <td>{device.get('vendor', 'Unknown')}</td>
            </tr>
"""
            html += "</table>"
        
        html += "</div>"
        return html
    
    def _generate_connectivity_section(self) -> str:
        """Generate connectivity tests section"""
        connectivity = self.data["connectivity"]
        
        status_class = "pass" if connectivity.get("overall_status") == "PASS" else "fail"
        status_text = connectivity.get("overall_status", "UNKNOWN")
        
        html = f"""
    <div class="section">
        <h2>🔌 Connectivity Tests</h2>
        <p>Overall Status: <span class="status {status_class}">{status_text}</span></p>
"""
        
        tests = connectivity.get("tests", {})
        
        # Gateway Test
        if tests.get("gateway"):
            gateway = tests["gateway"]
            html += f"""
        <h3>Gateway Reachability</h3>
        <p>Gateway: <code>{gateway.get('gateway', 'N/A')}</code></p>
        <p>Status: <span class="status {status_class}">{gateway.get('status', 'UNKNOWN')}</span></p>
"""
        
        # Internet Connectivity
        if tests.get("internet"):
            internet = tests["internet"]
            html += f"""
        <h3>Internet Connectivity</h3>
        <p>Tests Passed: {internet.get('success_rate', 'N/A')}</p>
"""
        
        # DNS Tests
        if tests.get("dns"):
            dns = tests["dns"]
            html += f"""
        <h3>DNS Resolution</h3>
        <p>DNS Servers: {', '.join([f"<code>{s}</code>" for s in dns.get('dns_servers', [])])}</p>
        <p>Status: <span class="status {status_class}">{dns.get('status', 'UNKNOWN')}</span></p>
"""
        
        html += "</div>"
        return html
    
    def _generate_dhcp_dns_section(self) -> str:
        """Generate DHCP/DNS troubleshooting section"""
        dhcp_dns = self.data["dhcp_dns"]
        
        html = """
    <div class="section">
        <h2>⚙️ DHCP & DNS Analysis</h2>
"""
        
        # DHCP Section
        if dhcp_dns.get("dhcp"):
            dhcp = dhcp_dns["dhcp"]
            status = dhcp.get("status", "UNKNOWN")
            status_class = "pass" if status == "PASS" else "warning" if status == "WARNING" else "fail"
            
            html += f"""
        <h3>DHCP Servers</h3>
        <p>Status: <span class="status {status_class}">{status}</span></p>
        <p>Servers Found: {dhcp.get('server_count', 0)}</p>
"""
            
            if dhcp.get("warning"):
                html += f'<div class="alert error">⚠️ {dhcp["warning"]}</div>'
            
            if dhcp.get("servers"):
                html += "<h4>Detected DHCP Servers:</h4><ul>"
                for server in dhcp["servers"]:
                    html += f"<li><code>{server['ip']}</code></li>"
                html += "</ul>"
        
        # DNS Section
        if dhcp_dns.get("dns"):
            dns = dhcp_dns["dns"]
            if dns.get("servers"):
                servers = dns["servers"]
                html += f"""
        <h3>DNS Configuration</h3>
        <p>Working Servers: {servers.get('working_servers', 0)}/{len(servers.get('configured_servers', []))}</p>
"""
        
        html += "</div>"
        return html
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations section"""
        recommendations = []
        
        # Analyze data and generate recommendations
        if self.data.get("dhcp_dns", {}).get("dhcp", {}).get("status") == "WARNING":
            recommendations.append({
                "priority": "HIGH",
                "title": "Multiple DHCP Servers Detected",
                "description": "Multiple DHCP servers can cause IP conflicts and network instability. Identify and disable unauthorized DHCP servers.",
                "action": "Run 'dhcp_dns_troubleshoot.py' to identify all DHCP servers, then disable rogue servers."
            })
        
        if self.data.get("connectivity", {}).get("overall_status") == "ISSUES_FOUND":
            recommendations.append({
                "priority": "MEDIUM",
                "title": "Connectivity Issues",
                "description": "Some connectivity tests failed. Review gateway and DNS configuration.",
                "action": "Check gateway reachability and DNS server settings in /etc/resolv.conf"
            })
        
        # Add general recommendations
        recommendations.append({
            "priority": "LOW",
            "title": "VLAN Segmentation",
            "description": "Consider implementing VLAN segmentation to separate internal and guest networks.",
            "action": "Plan VLAN architecture: VLAN 1 (native/internal) and VLAN 10 (guest network)"
        })
        
        html = """
    <div class="section">
        <h2>💡 Recommendations</h2>
"""
        
        for rec in recommendations:
            priority_class = "error" if rec["priority"] == "HIGH" else "warning" if rec["priority"] == "MEDIUM" else "info"
            html += f"""
        <div class="alert {priority_class}">
            <strong>[{rec['priority']}] {rec['title']}</strong>
            <p>{rec['description']}</p>
            <p><em>Action: {rec['action']}</em></p>
        </div>
"""
        
        html += "</div>"
        return html
    
    def generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        print("[*] Generating Markdown report...")
        
        md = f"""# Network Assessment Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

"""
        
        # Add summary stats
        if self.data.get("discovery"):
            total_devices = self.data["discovery"].get("summary", {}).get("total_devices", 0)
            md += f"- **Devices Discovered:** {total_devices}\n"
        
        if self.data.get("connectivity"):
            status = self.data["connectivity"].get("overall_status", "UNKNOWN")
            md += f"- **Connectivity Status:** {status}\n"
        
        if self.data.get("dhcp_dns"):
            dhcp_status = self.data["dhcp_dns"].get("dhcp", {}).get("status", "UNKNOWN")
            md += f"- **DHCP Status:** {dhcp_status}\n"
        
        md += "\n---\n\n"
        
        # Network Discovery
        if self.data.get("discovery"):
            md += "## Network Discovery\n\n"
            md += "### Discovered Devices\n\n"
            md += "| IP Address | MAC Address | Vendor |\n"
            md += "|------------|-------------|--------|\n"
            
            for device in self.data["discovery"].get("arp_scan", []):
                md += f"| `{device['ip']}` | `{device['mac']}` | {device.get('vendor', 'Unknown')} |\n"
            
            md += "\n"
        
        # Connectivity Tests
        if self.data.get("connectivity"):
            md += "## Connectivity Tests\n\n"
            tests = self.data["connectivity"].get("tests", {})
            
            if tests.get("gateway"):
                gateway = tests["gateway"]
                md += f"### Gateway Reachability\n\n"
                md += f"- Gateway: `{gateway.get('gateway', 'N/A')}`\n"
                md += f"- Status: **{gateway.get('status', 'UNKNOWN')}**\n\n"
            
            if tests.get("dns"):
                dns = tests["dns"]
                md += f"### DNS Resolution\n\n"
                md += f"- Status: **{dns.get('status', 'UNKNOWN')}**\n"
                md += f"- DNS Servers: {', '.join([f'`{s}`' for s in dns.get('dns_servers', [])])}\n\n"
        
        # DHCP/DNS Analysis
        if self.data.get("dhcp_dns"):
            md += "## DHCP & DNS Analysis\n\n"
            
            if self.data["dhcp_dns"].get("dhcp"):
                dhcp = self.data["dhcp_dns"]["dhcp"]
                md += f"### DHCP Servers\n\n"
                md += f"- Status: **{dhcp.get('status', 'UNKNOWN')}**\n"
                md += f"- Servers Found: {dhcp.get('server_count', 0)}\n\n"
                
                if dhcp.get("warning"):
                    md += f"⚠️ **WARNING:** {dhcp['warning']}\n\n"
        
        md += "---\n\n"
        md += "*Report generated by Network Troubleshooter Skill*\n"
        
        return md
    
    def generate_reports(self):
        """Generate both HTML and Markdown reports"""
        self.load_results()
        
        # Generate HTML
        html_content = self.generate_html_report()
        html_file = os.path.join(self.scan_dir, "network_report.html")
        with open(html_file, 'w') as f:
            f.write(html_content)
        print(f"[+] HTML report saved to: {html_file}")
        
        # Generate Markdown
        md_content = self.generate_markdown_report()
        md_file = os.path.join(self.scan_dir, "network_report.md")
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"[+] Markdown report saved to: {md_file}")
        
        return html_file, md_file

def main():
    parser = argparse.ArgumentParser(description='Generate Network Assessment Report')
    parser.add_argument('scan_dir', help='Directory containing scan results')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.scan_dir)
    html_file, md_file = generator.generate_reports()
    
    print(f"\n[+] Reports generated successfully!")
    print(f"    HTML: {html_file}")
    print(f"    Markdown: {md_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())
