#!/usr/bin/env python3
"""
Azure VM Backup Daily Report Generator
Generates executive summary reports for management
"""

import subprocess
import json
from datetime import datetime
import sys

def run_az_command(cmd):
    """Execute Azure CLI command and return JSON result"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout

def get_backup_items(vault_name, resource_group):
    """Get all backup items from vault"""
    cmd = f'''az backup item list \
        --vault-name "{vault_name}" \
        --resource-group "{resource_group}" \
        --backup-management-type "AzureIaasVM" \
        --output json 2>/dev/null'''
    return run_az_command(cmd)

def generate_report(vault_name="MyRecoveryServicesVault", resource_group="DataCenter"):
    """Generate the backup status report"""

    items = get_backup_items(vault_name, resource_group)
    if not items:
        return "Error: Could not retrieve backup items"

    # Parse backup items
    protected = []
    issues = []

    # Skip decommissioned/replaced VMs (old naming without -VM suffix that have been replaced)
    skip_vms = ['SETCO-DC02']  # Old DC02 replaced by SETCO-DC02-VM

    for item in items:
        props = item.get('properties', {})
        vm_name = props.get('friendlyName', 'Unknown')
        status = props.get('protectionState', 'Unknown')
        last_backup = props.get('lastBackupTime', 'Never')
        policy = props.get('policyName', 'None')

        # Skip decommissioned VMs
        if vm_name in skip_vms:
            continue

        entry = {
            'name': vm_name,
            'status': status,
            'last_backup': last_backup,
            'policy': policy or 'None'
        }

        if status == 'Protected':
            protected.append(entry)
        else:
            issues.append(entry)

    # Format the report
    report_date = datetime.now().strftime("%B %d, %Y")

    report = f"""### **Azure VM Backup Status Report**

**Date:** {report_date}
**Vault:** {vault_name}
**Resource Group:** {resource_group}

---

### **Executive Summary**

All critical production VMs in the `{vault_name}` vault have been reviewed.

- **Total VMs Reviewed:** {len(protected) + len(issues)}
- **Successfully Protected:** {len(protected)}
- **Protection Issues:** {len(issues)}

---

### **Detailed Backup Status**

| VM Name | Status | Last Successful Backup | Backup Policy |
| ------- | ------ | ---------------------- | ------------- |
"""

    # Add protected VMs
    for vm in sorted(protected, key=lambda x: x['name']):
        last = vm['last_backup']
        if last and last != 'Never':
            try:
                dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
                last = dt.strftime("%Y-%m-%d %H:%M UTC")
            except:
                pass
        report += f"| {vm['name']} | ✅ Protected | {last} | `{vm['policy']}` |\n"

    # Add VMs with issues
    for vm in sorted(issues, key=lambda x: x['name']):
        last = vm['last_backup']
        if last and last != 'Never':
            try:
                dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
                last = dt.strftime("%Y-%m-%d")
            except:
                pass
        status_emoji = "⚠️" if vm['status'] == 'ProtectionStopped' else "❌"
        report += f"| {vm['name']} | {status_emoji} {vm['status']} | {last} | *{vm['policy']}* |\n"

    # Add recommendations
    report += """
---

### **Recommendations**

"""
    if issues:
        for vm in issues:
            if vm['status'] == 'ProtectionStopped':
                report += f"1. **{vm['name']}:** Protection stopped. Verify if VM is decommissioned and clean up resources to avoid costs.\n"
            else:
                report += f"1. **{vm['name']}:** Status is `{vm['status']}`. Investigate and resolve immediately.\n"
    else:
        report += "- All VMs are protected and backing up successfully. No action required.\n"

    report += "\n2. **Policy Review:** Quarterly review recommended to ensure backup policies meet RPO/RTO objectives.\n"

    return report

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Generate Azure VM Backup Report')
    parser.add_argument('--vault', default='MyRecoveryServicesVault', help='Recovery Services Vault name')
    parser.add_argument('--resource-group', default='DataCenter', help='Resource group name')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='Output format')

    args = parser.parse_args()

    report = generate_report(args.vault, args.resource_group)

    if args.format == 'html':
        # Convert markdown to basic HTML
        report = f"""<!DOCTYPE html>
<html>
<head>
    <title>Azure VM Backup Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4472C4; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        h3 {{ color: #2F5496; }}
        code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
<pre>{report}</pre>
</body>
</html>"""

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)

if __name__ == '__main__':
    main()
