"""
Interactive Configuration Wizard

Guides users through creating network configurations step-by-step.
"""

import click
from pathlib import Path
import yaml

def run_wizard():
    """Run the interactive configuration wizard"""
    
    click.echo("🧙 " + click.style("Interactive Configuration Wizard", bold=True, fg='cyan'))
    click.echo("=" * 80)
    click.echo()
    click.echo("This wizard will help you create a network configuration.")
    click.echo("You can press Ctrl+C at any time to cancel.")
    click.echo()
    
    config = {}
    
    # Step 1: Vendor Selection
    click.echo(click.style("Step 1: Vendor Selection", bold=True, fg='green'))
    config['vendor'] = click.prompt(
        'Select vendor',
        type=click.Choice(['mikrotik', 'sonicwall', 'unifi'], case_sensitive=False),
        default='mikrotik'
    )
    
    config['device_model'] = click.prompt('Device model (e.g., RB4011iGS+RM, TZ370, UDM Pro)')
    click.echo()
    
    # Step 2: Customer Information
    click.echo(click.style("Step 2: Customer Information", bold=True, fg='green'))
    config['customer'] = {
        'name': click.prompt('Customer/Company name'),
        'site': click.prompt('Site name'),
        'contact': click.prompt('Contact email', default='admin@example.com')
    }
    click.echo()
    
    # Step 3: Deployment Type
    click.echo(click.style("Step 3: Deployment Type", bold=True, fg='green'))
    
    if config['vendor'] == 'sonicwall':
        deployment_choices = ['firewall', 'router_only']
    else:
        deployment_choices = ['router_only', 'ap_only', 'router_and_ap', 'firewall']
    
    config['deployment_type'] = click.prompt(
        'Deployment type',
        type=click.Choice(deployment_choices, case_sensitive=False),
        default=deployment_choices[0]
    )
    click.echo()
    
    # Step 4: WAN Configuration
    if config['deployment_type'] in ['router_only', 'router_and_ap', 'firewall']:
        click.echo(click.style("Step 4: WAN Configuration", bold=True, fg='green'))
        
        wan_interface = 'ether1' if config['vendor'] == 'mikrotik' else 'X0' if config['vendor'] == 'sonicwall' else 'eth0'
        
        config['wan'] = {
            'interface': click.prompt('WAN interface', default=wan_interface),
            'mode': click.prompt(
                'WAN mode',
                type=click.Choice(['static', 'dhcp', 'pppoe'], case_sensitive=False),
                default='static'
            )
        }
        
        if config['wan']['mode'] == 'static':
            config['wan']['ip'] = click.prompt('WAN IP address', type=str)
            config['wan']['netmask'] = click.prompt('WAN netmask (CIDR prefix)', type=int, default=24)
            config['wan']['gateway'] = click.prompt('WAN gateway', type=str)
            
            if click.confirm('Configure DNS servers?', default=True):
                dns_servers = []
                dns_servers.append(click.prompt('Primary DNS', default='8.8.8.8'))
                if click.confirm('Add secondary DNS?', default=True):
                    dns_servers.append(click.prompt('Secondary DNS', default='8.8.4.4'))
                config['wan']['dns'] = dns_servers
        
        elif config['wan']['mode'] == 'pppoe':
            config['wan']['pppoe_username'] = click.prompt('PPPoE username')
            config['wan']['pppoe_password'] = click.prompt('PPPoE password', hide_input=True)
        
        click.echo()
    
    # Step 5: LAN Configuration
    if config['deployment_type'] in ['router_only', 'router_and_ap', 'firewall']:
        click.echo(click.style("Step 5: LAN Configuration", bold=True, fg='green'))
        
        lan_interface = 'bridge-lan' if config['vendor'] == 'mikrotik' else 'X1' if config['vendor'] == 'sonicwall' else 'eth1'
        
        config['lan'] = {
            'interface': click.prompt('LAN interface', default=lan_interface),
            'ip': click.prompt('LAN IP address', default='10.54.0.1'),
            'netmask': click.prompt('LAN netmask (CIDR prefix)', type=int, default=24)
        }
        
        if click.confirm('Enable DHCP server?', default=True):
            config['lan']['dhcp'] = {
                'enabled': True,
                'pool_start': click.prompt('DHCP pool start', default='10.54.0.100'),
                'pool_end': click.prompt('DHCP pool end', default='10.54.0.200'),
                'lease_time': click.prompt('Lease time', default='24h'),
                'dns_servers': [config['wan'].get('dns', ['8.8.8.8'])[0]] if 'wan' in config else ['8.8.8.8']
            }
        
        click.echo()
    
    # Step 6: VLANs
    click.echo(click.style("Step 6: VLAN Configuration", bold=True, fg='green'))
    
    if click.confirm('Add VLANs?', default=False):
        config['vlans'] = []
        
        while True:
            click.echo()
            click.echo(click.style(f"VLAN #{len(config['vlans']) + 1}", fg='yellow'))
            
            vlan = {
                'id': click.prompt('VLAN ID', type=int),
                'name': click.prompt('VLAN name'),
                'subnet': click.prompt('VLAN subnet (CIDR)', default=f'10.54.{10 + len(config["vlans"])}.0/24')
            }
            
            if click.confirm('Enable DHCP for this VLAN?', default=True):
                vlan['dhcp'] = True
                
                # Extract network from subnet for default pool
                network_base = vlan['subnet'].split('/')[0].rsplit('.', 1)[0]
                
                vlan['dhcp_config'] = {
                    'pool_start': click.prompt('DHCP pool start', default=f'{network_base}.100'),
                    'pool_end': click.prompt('DHCP pool end', default=f'{network_base}.200'),
                    'lease_time': click.prompt('Lease time', default='12h')
                }
            
            if click.confirm('Enable guest isolation for this VLAN?', default=False):
                vlan['isolation'] = True
            
            config['vlans'].append(vlan)
            
            if not click.confirm('Add another VLAN?', default=False):
                break
    
    click.echo()
    
    # Step 7: Wireless Networks
    if config['deployment_type'] in ['ap_only', 'router_and_ap']:
        click.echo(click.style("Step 7: Wireless Configuration", bold=True, fg='green'))
        
        if click.confirm('Add wireless networks?', default=True):
            config['wireless'] = []
            
            while True:
                click.echo()
                click.echo(click.style(f"Wireless Network #{len(config['wireless']) + 1}", fg='yellow'))
                
                wireless = {
                    'ssid': click.prompt('SSID name'),
                    'password': click.prompt('WiFi password (min 8 chars)', hide_input=True),
                    'mode': click.prompt(
                        'WiFi mode',
                        type=click.Choice(['wifi6', 'wifi5', 'legacy'], case_sensitive=False),
                        default='wifi6'
                    ),
                    'band': click.prompt(
                        'Frequency band',
                        type=click.Choice(['2ghz-b/g/n', '5ghz', 'both'], case_sensitive=False),
                        default='both'
                    ),
                    'channel_width': click.prompt(
                        'Channel width',
                        type=click.Choice(['20mhz', '40mhz', '80mhz'], case_sensitive=False),
                        default='40mhz'
                    ),
                    'country': click.prompt('Country code', default='us')
                }
                
                if config.get('vlans'):
                    if click.confirm('Assign to VLAN?', default=False):
                        vlan_ids = [v['id'] for v in config['vlans']]
                        click.echo(f"Available VLANs: {', '.join(map(str, vlan_ids))}")
                        wireless['vlan'] = click.prompt('VLAN ID', type=int)
                
                wireless['guest_mode'] = click.confirm('Enable guest mode (isolation)?', default=False)
                
                config['wireless'].append(wireless)
                
                if not click.confirm('Add another wireless network?', default=False):
                    break
        
        click.echo()
    
    # Step 8: Security Configuration
    click.echo(click.style("Step 8: Security Configuration", bold=True, fg='green'))
    
    config['security'] = {
        'admin_username': click.prompt('Admin username', default='admin'),
        'admin_password': click.prompt('Admin password (min 8 chars)', hide_input=True, confirmation_prompt=True),
        'disable_unused_services': click.confirm('Disable unused services?', default=True)
    }
    
    if click.confirm('Restrict management access by IP?', default=True):
        config['security']['allowed_management_ips'] = []
        config['security']['allowed_management_ips'].append(
            click.prompt('Management IP/network (CIDR)', default='10.54.0.0/24')
        )
        
        while click.confirm('Add another management network?', default=False):
            config['security']['allowed_management_ips'].append(
                click.prompt('Management IP/network (CIDR)')
            )
    
    click.echo()
    
    # Step 9: Vendor-Specific Options
    if config['vendor'] == 'mikrotik':
        click.echo(click.style("Step 9: MikroTik-Specific Options", bold=True, fg='green'))
        
        config['mikrotik'] = {
            'enable_winbox': click.confirm('Enable WinBox access?', default=True),
            'enable_ssh': click.confirm('Enable SSH access?', default=True),
            'bandwidth_test': click.confirm('Enable bandwidth test server?', default=False),
            'stun_port': click.confirm('Enable STUN port forwarding?', default=False)
        }
        click.echo()
    
    # Step 10: Review and Save
    click.echo()
    click.echo(click.style("Configuration Summary", bold=True, fg='cyan'))
    click.echo("=" * 80)
    click.echo(f"Vendor: {config['vendor']}")
    click.echo(f"Device: {config['device_model']}")
    click.echo(f"Customer: {config['customer']['name']} - {config['customer']['site']}")
    click.echo(f"Deployment: {config['deployment_type']}")
    
    if 'wan' in config:
        click.echo(f"WAN: {config['wan']['mode'].upper()}", nl=False)
        if config['wan']['mode'] == 'static':
            click.echo(f" - {config['wan']['ip']}/{config['wan']['netmask']}")
        else:
            click.echo()
    
    if 'lan' in config:
        click.echo(f"LAN: {config['lan']['ip']}/{config['lan']['netmask']}")
    
    if config.get('vlans'):
        click.echo(f"VLANs: {len(config['vlans'])} configured")
    
    if config.get('wireless'):
        click.echo(f"Wireless: {len(config['wireless'])} network(s)")
    
    click.echo("=" * 80)
    click.echo()
    
    if click.confirm('Save this configuration?', default=True):
        # Generate filename
        safe_name = config['customer']['name'].lower().replace(' ', '-')
        safe_site = config['customer']['site'].lower().replace(' ', '-')
        default_filename = f"{safe_name}-{safe_site}.yaml"
        
        filename = click.prompt('Configuration filename', default=default_filename)
        
        # Ensure .yaml extension
        if not filename.endswith('.yaml'):
            filename += '.yaml'
        
        # Save to file
        filepath = Path(filename)
        
        # Create directory if needed
        if filepath.parent != Path('.'):
            filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        click.echo()
        click.echo(click.style(f"✅ Configuration saved to: {filepath}", fg='green', bold=True))
        click.echo()
        
        # Offer to generate configs
        if click.confirm('Generate device configuration now?', default=True):
            return str(filepath)
        else:
            click.echo()
            click.echo("To generate device configuration later, run:")
            click.echo(f"  ./network-config generate -i {filepath} -o outputs -v")
            return None
    else:
        click.echo()
        click.echo(click.style("Configuration not saved.", fg='yellow'))
        return None


if __name__ == '__main__':
    run_wizard()
