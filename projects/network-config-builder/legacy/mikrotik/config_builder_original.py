
#!/usr/bin/env python3
"""
MikroTik Config Builder (single-file, with hardening & feature toggles)

- Reads a 2-column CSV (Field,Value) and generates RouterOS .rsc files.
- Supports:
    * Admin allowlist for WinBox/SSH
    * CIDR/dotted netmask normalization
    * DHCP server + correct 'network' line (LAN subnet)
    * NAT masquerade
    * Create admin user
    * STUN forward (UDP 3478; optional TCP 3478)
    * Throughput test server (bandwidth-server) with firewall lockdown
    * Baseline hardening (disable unused services, disable MAC access & neighbor discovery)
- Also saves a copy of the generated files to ./Customers/<Customer Name>/ (configurable)

CSV expected at: ./Inputs/customer_data_column_format.csv
Outputs written to: ./Outputs/
Customers copies:   ./Customers/<Customer Name>/

New toggles supported (true/false):
  - Enable Winbox Access
  - Enable SSH Access
  - Enable Throughput Port     (enables btest and restricts it to admin allowlist)

References:
- RouterOS services restriction via 'address' property: https://help.mikrotik.com/docs/spaces/ROS/pages/103841820/Services
- RouterOS "Securing your router" baseline: https://help.mikrotik.com/docs/spaces/ROS/pages/328353/Securing+your+router
"""

import csv
import ipaddress
import os
import re
import argparse
import shutil
from typing import Dict, List, Tuple

# ----------------- Helpers -----------------

def _to_prefix(mask: str) -> int:
    """Convert netmask to prefix length. Accepts '24', '/24', or dotted mask."""
    m = str(mask).strip()
    if m.startswith('/'):
        m = m[1:]
    if m.isdigit():
        n = int(m)
        if 0 <= n <= 32:
            return n
        raise ValueError("Prefix out of range")
    return ipaddress.IPv4Network(f"0.0.0.0/{m}").prefixlen

def _split_list(value: str) -> List[str]:
    return [x.strip() for x in re.split(r"[,\s]+", str(value).strip()) if x.strip()]

def _normalize_admin_ips(s: str) -> str:
    """IPs/CIDRs -> comma-separated CIDRs; single IPs become /32."""
    cidrs = []
    for part in _split_list(s):
        if "/" in part:
            net = ipaddress.IPv4Network(part, strict=False)
            cidrs.append(str(net))
        else:
            ip = ipaddress.IPv4Address(part)
            cidrs.append(f"{ip}/32")
    return ",".join(cidrs)

def _normalize_dns_servers(s: str) -> str:
    ips = []
    for part in _split_list(s):
        ips.append(str(ipaddress.IPv4Address(part)))
    return ",".join(ips)

def _q(val: str) -> str:
    """Always quote (escape internal double quotes) for RouterOS CLI."""
    s = str(val)
    return '"' + s.replace('"', r'\"') + '"'

def _sanitize_slug(s: str) -> str:
    """Safe slug for list names, filenames, etc."""
    return "".join(c for c in s if c.isalnum() or c in "-_.").strip() or "customer"

def _has_builtin_wifi(model: str) -> bool:
    """Heuristic: RB4011iGS+RM has no Wi‑Fi; hAP/cAP/Audience models usually do."""
    m = str(model).lower()
    if 'rb4011igs+rm' in m or ('rb4011' in m and 'hac' not in m):
        return False
    if any(x in m for x in ['hap', 'cap', 'audience']):
        return True
    return False

# ----------------- Validation -----------------

def validate_customer_template(customer_data: Dict[str, str]) -> List[str]:
    errors = []

    required_fields = [
        'Customer Name', 'Deployment Type', 'Device Model', 'Site Location',
        'WAN IP Address', 'WAN Netmask', 'WAN Gateway',
        'LAN Bridge Name', 'LAN IP Address', 'LAN Netmask',
        'DHCP Pool Start', 'DHCP Pool End', 'DHCP Lease Time',
        'LAN DNS Servers', 'Wireless SSID',
        'Wireless Band/Channel Width', 'Wireless Channel Width',
        'Wireless Country / Coverage Region', 'Wireless Password',
        'Admin Username', 'Admin Password', 'Allowed Remote IPs for Admin',
        'Enable STUN Port'
    ]
    for field in required_fields:
        if not customer_data.get(field):
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    # Deployment type
    dep = customer_data['Deployment Type'].strip().lower()
    if dep not in {'router only', 'router + ap', 'ap only'}:
        errors.append("Deployment Type must be one of: Router only | Router + AP | AP only")

    # IPv4 fields
    ip_fields = ['WAN IP Address', 'WAN Gateway', 'LAN IP Address',
                 'DHCP Pool Start', 'DHCP Pool End']
    for f in ip_fields:
        try:
            ipaddress.IPv4Address(customer_data[f])
        except Exception:
            errors.append(f"Invalid IPv4 in field: {f}")

    # Netmasks
    for nm_field in ['WAN Netmask', 'LAN Netmask']:
        try:
            _to_prefix(customer_data[nm_field])
        except Exception:
            errors.append(f"Invalid netmask/prefix in {nm_field} (accepts 24, /24, dotted)")

    # DHCP pool inside LAN and start <= end
    try:
        lan_prefix = _to_prefix(customer_data['LAN Netmask'])
        lan_ip = ipaddress.IPv4Address(customer_data['LAN IP Address'])
        lan_net = ipaddress.IPv4Network(f"{lan_ip}/{lan_prefix}", strict=False)
        start = ipaddress.IPv4Address(customer_data['DHCP Pool Start'])
        end = ipaddress.IPv4Address(customer_data['DHCP Pool End'])
        if int(start) > int(end):
            errors.append("DHCP Pool Start must be <= DHCP Pool End")
        if start not in lan_net or end not in lan_net:
            errors.append(f"DHCP pool must be inside LAN subnet {lan_net}")
    except Exception:
        pass

    # DNS servers list
    try:
        dns_parts = _split_list(customer_data['LAN DNS Servers'])
        if not dns_parts:
            errors.append("At least one LAN DNS Server is required")
        else:
            for d in dns_parts:
                ipaddress.IPv4Address(d)
    except Exception:
        errors.append("LAN DNS Servers must be IPv4s separated by commas/spaces")

    # Admin IPs list
    try:
        allow_parts = _split_list(customer_data['Allowed Remote IPs for Admin'])
        if not allow_parts:
            errors.append("Allowed Remote IPs for Admin is required")
        else:
            for a in allow_parts:
                if '/' in a:
                    ipaddress.IPv4Network(a, strict=False)
                else:
                    ipaddress.IPv4Address(a)
    except Exception:
        errors.append("Allowed Remote IPs for Admin must be IPs/CIDRs separated by commas/spaces")

    # Wi‑Fi password minimum
    if len(customer_data.get('Wireless Password', '')) < 8:
        errors.append("Wireless Password must be at least 8 characters")

    # Booleans
    for bool_field in ['Enable STUN Port', 'Enable Winbox Access', 'Enable SSH Access', 'Enable Throughput Port']:
        if bool_field in customer_data:
            val = str(customer_data[bool_field]).strip().lower()
            if val not in {'true', 'false'}:
                errors.append(f"{bool_field} must be true or false")

    # STUN server IP (optional)
    if str(customer_data.get('Enable STUN Port', '')).strip().lower() == 'true' and customer_data.get('STUN Server IP'):
        try:
            ipaddress.IPv4Address(customer_data['STUN Server IP'])
        except Exception:
            errors.append("STUN Server IP must be a valid IPv4 address if provided")

    return errors

# ----------------- Generators -----------------

def generate_router_script(d: Dict[str, str]) -> str:
    # Basic addressing
    wan_ip = d['WAN IP Address'].strip()
    wan_pref = _to_prefix(d['WAN Netmask'])
    wan_gw = d['WAN Gateway'].strip()

    bridge = d['LAN Bridge Name'].strip()
    lan_ip = d['LAN IP Address'].strip()
    lan_pref = _to_prefix(d['LAN Netmask'])
    lan_if = ipaddress.IPv4Interface(f"{lan_ip}/{lan_pref}")
    lan_net = str(lan_if.network)

    # DHCP
    dhcp_start = d['DHCP Pool Start'].strip()
    dhcp_end = d['DHCP Pool End'].strip()
    dhcp_lease = d['DHCP Lease Time'].strip()
    dns_servers = _normalize_dns_servers(d['LAN DNS Servers'])

    # Admin + user
    admin_allowed = _normalize_admin_ips(d['Allowed Remote IPs for Admin'])
    admin_user = _q(d['Admin Username'])
    admin_pass = _q(d['Admin Password'])

    # Toggles (defaults: WinBox/SSH enabled; throughput disabled)
    enable_winbox = str(d.get('Enable Winbox Access', 'true')).strip().lower() == 'true'
    enable_ssh    = str(d.get('Enable SSH Access', 'true')).strip().lower() == 'true'
    enable_btest  = str(d.get('Enable Throughput Port', 'false')).strip().lower() == 'true'

    # STUN
    enable_stun   = str(d.get('Enable STUN Port', '')).strip().lower() == 'true'
    stun_ip       = d.get('STUN Server IP', '').strip()
    stun_tcp_also = str(d.get('STUN TCP Also', 'false')).strip().lower() == 'true'

    cust = d['Customer Name'].strip()
    site = d['Site Location'].strip()
    model = d['Device Model'].strip()
    slug  = _sanitize_slug(cust)
    admin_list = f"admin-allow-{slug}"

    lines: List[str] = []
    lines.append(f"# ===== {cust} | {site} | {model} =====")
    lines.append("")

    # 1) WAN + default route
    lines += [
        f"/ip address add address={wan_ip}/{wan_pref} interface=ether1",
        f"/ip route add gateway={wan_gw}",
        ""
    ]

    # 2) Bridge + LAN addressing
    lines += [
        f"/interface bridge add name={bridge}",
        f"/ip address add address={lan_ip}/{lan_pref} interface={bridge}",
        ""
    ]

    # 3) DHCP server (pool, server, network)
    lines += [
        f"/ip pool add name=lan-pool ranges={dhcp_start}-{dhcp_end}",
        f"/ip dhcp-server add name=lan-dhcp interface={bridge} address-pool=lan-pool lease-time={dhcp_lease} disabled=no",
        f"/ip dhcp-server network add address={lan_net} gateway={lan_ip} dns-server={dns_servers}",
        ""
    ]

    # 4) NAT (simple)
    # baseline NAT for single-WAN
    lines += [
        f"/ip firewall nat add chain=srcnat out-interface=ether1 action=masquerade comment=\"baseline: NAT LAN->WAN\"",
        ""
    ]

    # 5) Baseline hardening — services & MAC/Neighbor
    # 5a) Admin services (WinBox/SSH) — apply address restriction and enable/disable
    if enable_winbox:
        lines.append(f"/ip service set [ find name=winbox ] address={admin_allowed} disabled=no")
    else:
        lines.append(f"/ip service set [ find name=winbox ] disabled=yes")

    if enable_ssh:
        lines.append(f"/ip service set [ find name=ssh ] address={admin_allowed} disabled=no")
    else:
        lines.append(f"/ip service set [ find name=ssh ] disabled=yes")

    # 5b) Disable unused services (telnet/ftp/www/api/api-ssl)
    for svc in ['telnet', 'ftp', 'www', 'api', 'api-ssl']:
        lines.append(f"/ip service set [ find name={svc} ] disabled=yes")
    lines.append("")

    # 5c) Disable MAC-based access & neighbor discovery
    lines += [
        "/tool mac-server set allowed-interface-list=none",
        "/tool mac-server mac-winbox set allowed-interface-list=none",
        "/tool mac-server ping set enabled=no",
        "/ip neighbor discovery-settings set discover-interface-list=none",
        ""
    ]

    # 6) Create admin user (new account)
    lines += [
        f"/user add name={admin_user} password={admin_pass} group=full disabled=no",
        ""
    ]

    # 7) STUN forwarding (UDP 3478; optional TCP)
    if enable_stun and stun_ip:
        lines += [
            f"# STUN forwarding to {stun_ip}",
            f"/ip firewall nat add chain=dstnat in-interface=ether1 protocol=udp dst-port=3478 action=dst-nat to-addresses={stun_ip} to-ports=3478 comment=\"STUN UDP 3478 to server\"",
            f"/ip firewall filter add chain=forward in-interface=ether1 protocol=udp dst-address={stun_ip} dst-port=3478 connection-nat-state=dstnat action=accept comment=\"Allow forwarded STUN UDP\"",
        ]
        if stun_tcp_also:
            lines += [
                f"/ip firewall nat add chain=dstnat in-interface=ether1 protocol=tcp dst-port=3478 action=dst-nat to-addresses={stun_ip} to-ports=3478 comment=\"STUN TCP 3478 to server\"",
                f"/ip firewall filter add chain=forward in-interface=ether1 protocol=tcp dst-address={stun_ip} dst-port=3478 connection-nat-state=dstnat action=accept comment=\"Allow forwarded STUN TCP\"",
            ]
        lines.append("")
    elif enable_stun and not stun_ip:
        lines += [
            "# STUN enabled in CSV but no STUN Server IP provided. Example (disabled):",
            "# :local stunSrv \"X.X.X.X\"",
            "# /ip firewall nat add chain=dstnat in-interface=ether1 protocol=udp dst-port=3478 action=dst-nat to-addresses=$stunSrv to-ports=3478 comment=\"STUN UDP 3478 to server\"",
            "# /ip firewall filter add chain=forward in-interface=ether1 protocol=udp dst-address=$stunSrv dst-port=3478 connection-nat-state=dstnat action=accept comment=\"Allow forwarded STUN\"",
            ""
        ]

    # 8) Throughput test (bandwidth-server, port 2000) — disabled unless explicitly enabled
    if enable_btest:
        lines += [
            "/tool bandwidth-server set enabled=yes",
        ]
        # Build dedicated address-list from admin allowlist
        for net in admin_allowed.split(','):
            lines.append(f"/ip firewall address-list add list={admin_list} address={net} comment=\"admin sources for btest\"")
        # Allow only from admin_list; drop others
        lines += [
            f"/ip firewall filter add chain=input src-address-list={admin_list} protocol=tcp dst-port=2000 action=accept comment=\"btest TCP from admin\"",
            f"/ip firewall filter add chain=input src-address-list={admin_list} protocol=udp dst-port=2000 action=accept comment=\"btest UDP from admin\"",
            f"/ip firewall filter add chain=input protocol=tcp dst-port=2000 action=drop comment=\"btest TCP drop others\"",
            f"/ip firewall filter add chain=input protocol=udp dst-port=2000 action=drop comment=\"btest UDP drop others\"",
            ""
        ]
    else:
        lines += [
            "/tool bandwidth-server set enabled=no",
            ""
        ]

    return "\n".join(lines) + "\n"

def generate_ap_script_legacy_wireless(d: Dict[str, str]) -> str:
    """
    Legacy '/interface wireless' config for APs that use the classic 'wireless' package.
    If your APs are AX/Wave2 (wifi/wifiwave2), ask for a /interface/wifi variant.
    """
    ssid = _q(d['Wireless SSID'])
    wifi_pass = _q(d['Wireless Password'])
    band = d['Wireless Band/Channel Width'].strip()
    width = d['Wireless Channel Width'].strip()
    country = d['Wireless Country / Coverage Region'].strip()

    lines = [
        f"# ===== AP Config (legacy wireless) for {d['Customer Name']} ({d['Site Location']}) =====",
        "/interface wireless security-profiles add name=sec1 authentication-types=wpa2-psk wpa2-pre-shared-key=" + wifi_pass,
        "/interface wireless set [ find default-name=wlan1 ] disabled=no mode=ap-bridge band="
        + band + " channel-width=" + width + " ssid=" + ssid
        + " country=" + country + " security-profile=sec1",
        ""
    ]
    return "\n".join(lines)

def generate_scripts(customer_data: Dict[str, str]) -> Dict[str, str]:
    """
    Returns dict of filename -> script text based on deployment type and model.
    """
    out = {}
    dep = customer_data['Deployment Type'].strip().lower()
    name = _sanitize_slug(customer_data.get("Customer Name", "customer"))
    model = customer_data.get('Device Model', '')

    # Router?
    if dep in {'router only', 'router + ap'}:
        out[f"{name}-router.rsc"] = generate_router_script(customer_data)

    # AP?
    if dep in {'ap only', 'router + ap'}:
        # Generate AP script if explicitly requested or router has no built-in Wi‑Fi
        if dep == 'ap only' or not _has_builtin_wifi(model) or dep == 'router + ap':
            out[f"{name}-ap-legacy-wireless.rsc"] = generate_ap_script_legacy_wireless(customer_data)

    return out

# ----------------- Orchestration / I/O -----------------

def read_field_value_csv(path: str) -> Dict[str, str]:
    """
    Read a 2-column CSV: Field,Value (with a header row).
    Trims whitespace around fields and values.
    """
    data = {}
    with open(path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip header
        for row in reader:
            if not row or len(row) < 2:
                continue
            field, value = row[0].strip(), row[1].strip()
            if field:
                data[field] = value
    return data

def process_customer_data(customer_data: Dict[str, str]) -> Tuple[List[str], Dict[str, str]]:
    """
    Validate and generate scripts for a single customer.
    Returns (errors, scripts_dict).
    """
    errors = validate_customer_template(customer_data)
    if errors:
        return errors, {}
    scripts = generate_scripts(customer_data)
    return [], scripts

def main():
    parser = argparse.ArgumentParser(description="MikroTik config builder (single-file)")
    parser.add_argument("--input", default="./Inputs/customer_data_column_format.csv",
                        help="Path to 2-column customer CSV (Field,Value)")
    parser.add_argument("--output", default="./Outputs",
                        help="Output directory for .rsc files")
    parser.add_argument("--customers-root", default="./Customers",
                        help="Root folder where a per-customer copy will be saved")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    customer_data = read_field_value_csv(args.input)
    errors, scripts = process_customer_data(customer_data)
    if errors:
        print("[ERROR] Validation failed:")
        for e in errors:
            print(f"  - {e}")
        return

    # Base write to Outputs/
    written_paths = []
    for fname, text in scripts.items():
        path = os.path.join(args.output, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        written_paths.append(path)
        print(f"[SUCCESS] Wrote {path}")

    # Also write copies to ./Customers/<Customer Name>/
    cust_name = _sanitize_slug(customer_data.get("Customer Name", "customer"))
    cust_dir = os.path.join(args.customers_root, cust_name)
    os.makedirs(cust_dir, exist_ok=True)

    for fname, text in scripts.items():
        cpath = os.path.join(cust_dir, fname)
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[SUCCESS] Copied to {cpath}")

if __name__ == "__main__":
    main()
