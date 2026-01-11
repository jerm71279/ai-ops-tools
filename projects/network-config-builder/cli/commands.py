"""
CLI commands for network config builder.

Uses Click framework for beautiful command-line interface.
"""

import click
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_io.readers.yaml_reader import YAMLConfigReader
from core.validators import ConfigValidator
from core.exceptions import ValidationError
from vendors.mikrotik.generator import MikroTikGenerator
from vendors.sonicwall.generator import SonicWallGenerator
from vendors.ubiquiti.unifi_generator import UniFiGenerator


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    Multi-Vendor Network Configuration Builder

    Supports: MikroTik, SonicWall, Ubiquiti (UniFi/EdgeRouter)
    """
    pass


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='Input configuration file (YAML)')
@click.option('--output', '-o', type=click.Path(),
              default='./outputs',
              help='Output directory for generated configs')
@click.option('--dry-run', is_flag=True,
              help='Preview output without writing files')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def generate(input, output, dry_run, verbose):
    """Generate network device configurations"""

    try:
        # Read configuration
        if verbose:
            click.echo(f"📖 Reading configuration from: {input}")

        config = YAMLConfigReader.read(input)

        if verbose:
            click.echo(f"   Vendor: {config.vendor.value}")
            click.echo(f"   Device: {config.device_model}")
            click.echo(f"   Customer: {config.customer.name} - {config.customer.site}")
            click.echo()

        # Validate
        if verbose:
            click.echo("🔍 Validating configuration...")

        validator = ConfigValidator()
        errors = validator.validate(config)

        if errors:
            click.echo("❌ Validation failed:", err=True)
            for error in errors:
                click.echo(f"   • {error}", err=True)
            sys.exit(1)

        if verbose:
            click.echo("   ✅ Configuration is valid")
            click.echo()

        # Generate
        if verbose:
            click.echo(f"🔨 Generating {config.vendor.value} configuration...")

        # Select generator based on vendor
        if config.vendor.value == 'mikrotik':
            generator = MikroTikGenerator()
        elif config.vendor.value == 'sonicwall':
            generator = SonicWallGenerator()
        elif config.vendor.value in ['unifi', 'ubiquiti']:
            generator = UniFiGenerator()
        else:
            click.echo(f"❌ Vendor {config.vendor.value} not yet implemented", err=True)
            click.echo("   Available: mikrotik, sonicwall, unifi", err=True)
            click.echo("   Coming soon: edgerouter", err=True)
            sys.exit(1)

        scripts = generator.generate_config(config)

        if verbose:
            click.echo(f"   Generated {len(scripts)} file(s):")
            for filename in scripts.keys():
                click.echo(f"      • {filename}")
            click.echo()

        if dry_run:
            click.echo("🔍 DRY-RUN MODE - Preview of generated configurations:")
            click.echo("=" * 80)
            for filename, content in scripts.items():
                click.echo(f"\n📄 {filename}:")
                click.echo("-" * 80)
                click.echo(content)
                click.echo("=" * 80)
            click.echo("\n✅ Dry-run complete. Use without --dry-run to save files.")
        else:
            # Save files
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)

            for filename, content in scripts.items():
                file_path = output_dir / filename
                file_path.write_text(content)
                click.echo(f"💾 Saved: {file_path}")

            click.echo(f"\n✅ Generated {len(scripts)} configuration file(s)")
            click.echo(f"📂 Output directory: {output_dir.absolute()}")

    except ValidationError as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='Input configuration file to validate')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def validate(input, verbose):
    """Validate configuration without generating files"""

    try:
        if verbose:
            click.echo(f"📖 Reading configuration from: {input}")

        config = YAMLConfigReader.read(input)

        if verbose:
            click.echo(f"   Vendor: {config.vendor.value}")
            click.echo(f"   Device: {config.device_model}")
            click.echo()

        click.echo("🔍 Validating configuration...")

        validator = ConfigValidator()
        errors = validator.validate(config)

        if errors:
            click.echo("❌ Validation failed:")
            for error in errors:
                click.echo(f"   • {error}")
            sys.exit(1)
        else:
            click.echo("✅ Configuration is valid!")
            if verbose:
                click.echo(f"\n📊 Summary:")
                click.echo(f"   Customer: {config.customer.name}")
                click.echo(f"   Site: {config.customer.site}")
                click.echo(f"   Vendor: {config.vendor.value}")
                click.echo(f"   Device: {config.device_model}")
                if config.vlans:
                    click.echo(f"   VLANs: {len(config.vlans)}")
                if config.wireless:
                    click.echo(f"   Wireless Networks: {len(config.wireless)}")

    except ValidationError as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', type=click.Path(), default='./outputs',
              help='Output directory for generated configs')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def interactive(output, verbose):
    """Interactive configuration wizard"""

    from cli.wizard import run_wizard

    try:
        # Run wizard and get saved config path
        config_path = run_wizard()

        if config_path:
            # User wants to generate now
            click.echo()
            click.echo(click.style("Generating configuration...", fg='cyan'))
            click.echo()

            # Import here to avoid circular import
            from config_io.readers.yaml_reader import YAMLConfigReader
            from core.validators import ConfigValidator

            config = YAMLConfigReader.read(config_path)

            if verbose:
                click.echo("🔍 Validating configuration...")

            validator = ConfigValidator()
            errors = validator.validate(config)

            if errors:
                click.echo("❌ Validation failed:", err=True)
                for error in errors:
                    click.echo(f"   • {error}", err=True)
                sys.exit(1)

            if verbose:
                click.echo("   ✅ Configuration is valid")
                click.echo()

            # Select generator
            if config.vendor.value == 'mikrotik':
                generator = MikroTikGenerator()
            elif config.vendor.value == 'sonicwall':
                generator = SonicWallGenerator()
            elif config.vendor.value in ['unifi', 'ubiquiti']:
                generator = UniFiGenerator()
            else:
                click.echo(f"❌ Vendor {config.vendor.value} not supported", err=True)
                sys.exit(1)

            scripts = generator.generate_config(config)

            # Save files
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)

            for filename, content in scripts.items():
                file_path = output_dir / filename
                file_path.write_text(content)
                click.echo(f"💾 Saved: {file_path}")

            click.echo()
            click.echo(click.style(f"✅ Generated {len(scripts)} configuration file(s)", fg='green', bold=True))
            click.echo(f"📂 Output directory: {output_dir.absolute()}")

    except KeyboardInterrupt:
        click.echo()
        click.echo()
        click.echo(click.style("Wizard cancelled by user.", fg='yellow'))
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True),
              help='Input configuration file')
@click.option('--device', '-d', required=True, help='Device IP address')
@click.option('--username', '-u', help='Admin username')
@click.option('--password', '-p', help='Admin password')
@click.option('--ssh-key', type=click.Path(exists=True),
              help='Path to SSH private key')
@click.option('--backup-path', default='./backups',
              help='Local path to save backups')
@click.option('--no-backup', is_flag=True,
              help='Skip automatic backup')
@click.option('--no-verify', is_flag=True,
              help='Skip deployment verification')
@click.option('--no-rollback', is_flag=True,
              help='Do not rollback on failure')
@click.option('--dry-run', is_flag=True,
              help='Preview deployment without applying')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def deploy(input, device, username, password, ssh_key, backup_path,
           no_backup, no_verify, no_rollback, dry_run, verbose):
    """Deploy configuration to device via SSH"""

    try:
        # Prompt for credentials if not provided
        if not username:
            username = click.prompt('Username', default='admin')

        if not password and not ssh_key:
            password = click.prompt('Password', hide_input=True)

        click.echo()
        click.echo(click.style(f"🚀 Deploying to {device}", bold=True, fg='cyan'))
        click.echo("=" * 80)
        click.echo()

        # Read and validate configuration
        if verbose:
            click.echo("📖 Reading configuration...")

        config = YAMLConfigReader.read(input)

        if verbose:
            click.echo(f"   Vendor: {config.vendor.value}")
            click.echo(f"   Device Model: {config.device_model}")
            click.echo()

        # Validate configuration
        if verbose:
            click.echo("🔍 Validating configuration...")

        validator = ConfigValidator()
        errors = validator.validate(config)

        if errors:
            click.echo("❌ Validation failed:", err=True)
            for error in errors:
                click.echo(f"   • {error}", err=True)
            sys.exit(1)

        if verbose:
            click.echo("   ✅ Configuration is valid")
            click.echo()

        # Generate configuration
        if config.vendor.value == 'mikrotik':
            generator = MikroTikGenerator()
        elif config.vendor.value == 'sonicwall':
            click.echo("❌ SonicWall deployment not yet implemented", err=True)
            click.echo("   Use: network-config generate and import manually", err=True)
            sys.exit(1)
        elif config.vendor.value in ['unifi', 'ubiquiti']:
            click.echo("❌ UniFi deployment not yet implemented", err=True)
            click.echo("   Use: network-config generate and import via Controller", err=True)
            sys.exit(1)
        else:
            click.echo(f"❌ Unsupported vendor: {config.vendor.value}", err=True)
            sys.exit(1)

        scripts = generator.generate_config(config)

        # Get main configuration script
        config_script = scripts.get('router.rsc', '')

        if not config_script:
            click.echo("❌ No configuration script generated", err=True)
            sys.exit(1)

        # Show configuration summary
        click.echo(click.style("📋 Configuration Summary:", bold=True))
        click.echo(f"   Customer: {config.customer.name} - {config.customer.site}")
        click.echo(f"   Script size: {len(config_script)} bytes")

        if config.vlans:
            click.echo(f"   VLANs: {len(config.vlans)}")
        if config.wireless:
            click.echo(f"   Wireless: {len(config.wireless)} network(s)")

        click.echo()

        if dry_run:
            click.echo(click.style("🔍 DRY-RUN MODE - Preview Only", fg='yellow', bold=True))
            click.echo("=" * 80)
            click.echo(config_script[:500])
            if len(config_script) > 500:
                click.echo("...")
                click.echo(f"(showing first 500 of {len(config_script)} bytes)")
            click.echo("=" * 80)
            click.echo()
            click.echo("✅ Dry-run complete. Use without --dry-run to deploy.")
            return

        # Confirm deployment
        click.echo(click.style("⚠️  WARNING:", fg='yellow', bold=True))
        click.echo("   This will modify the device configuration!")
        click.echo()

        if not click.confirm('Proceed with deployment?', default=False):
            click.echo()
            click.echo(click.style("Deployment cancelled.", fg='yellow'))
            sys.exit(0)

        click.echo()

        # Deploy to device
        if verbose:
            click.echo("🔐 Connecting to device...")

        from vendors.mikrotik.deployer import deploy_to_mikrotik

        result = deploy_to_mikrotik(
            device_ip=device,
            username=username,
            password=password,
            config_script=config_script,
            backup_path=backup_path if not no_backup else None,
            verify=not no_verify,
            rollback_on_failure=not no_rollback
        )

        click.echo()

        if result['success']:
            click.echo(click.style("✅ Deployment Successful!", fg='green', bold=True))
            click.echo()
            click.echo(f"   {result['message']}")

            if result.get('device_info'):
                click.echo()
                click.echo("Device Information:")
                for key, value in result['device_info'].items():
                    click.echo(f"   {key}: {value}")

            if result.get('backup') and not no_backup:
                click.echo()
                click.echo(f"📦 Backup: {result['backup']}")
                click.echo(f"   Location: {backup_path}")
                click.echo()
                click.echo(f"   Rollback command:")
                click.echo(f"   ssh {username}@{device} '/system backup load name={result['backup']}'")
        else:
            click.echo(click.style("❌ Deployment Failed!", fg='red', bold=True))
            click.echo()
            click.echo(f"   {result['message']}")
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo()
        click.echo()
        click.echo(click.style("Deployment cancelled by user.", fg='yellow'))
        sys.exit(0)
    except Exception as e:
        click.echo()
        click.echo(click.style(f"❌ Error: {e}", fg='red'), err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli()
