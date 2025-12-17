# NinjaOne RMM Skill

Python client for NinjaOne RMM API integration.

## Quick Start

```bash
# Set credentials
export NINJAONE_CLIENT_ID="your_client_id"
export NINJAONE_CLIENT_SECRET="your_client_secret"
export NINJAONE_REGION="us"

# Install dependencies
pip install -r requirements.txt

# Test connection
python ninjaone_client.py --summary
```

## Usage

```python
from skills.ninjaone.ninjaone_client import NinjaOneClient

async def main():
    client = NinjaOneClient()

    # Get fleet overview
    summary = await client.get_fleet_summary()
    print(f"Total devices: {summary['total_devices']}")
    print(f"Online: {summary['online_percent']}%")

    # Get critical alerts
    alerts = await client.get_critical_alerts()
    for alert in alerts:
        print(f"CRITICAL: {alert['message']}")
```

## Features

- OAuth2 client credentials authentication
- Regional endpoint support (US, EU, OC, CA)
- Device, alert, and organization management
- Fleet summary aggregation
- Script execution
- Patch compliance reporting

## Documentation

See [SKILL.md](SKILL.md) for complete API documentation, data schemas, and examples.

## Security

**IMPORTANT:** Credentials are required. The client will raise `NinjaOneConfigError` if credentials are missing. There is no demo mode fallback to prevent accidentally using fake data in production.
