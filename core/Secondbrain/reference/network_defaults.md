# Network Configuration Defaults

Standard defaults for OberaConnect network deployments.

## DHCP Scope

| Setting | Default Value |
|---------|---------------|
| DHCP Range | .200-.254 |
| Static IPs | .1-.199 (available for static assignment) |
| Gateway | .1 |

## IP Allocation Convention

| Range | Purpose |
|-------|---------|
| .1 | Gateway/Router |
| .2-.99 | Infrastructure (switches, APs, servers) |
| .100-.199 | Static client devices (printers, cameras, etc.) |
| .200-.254 | DHCP pool |

## Subnet Allocation

- Each customer gets a /24 block minimum (or 4x /24 block for larger deployments)
- Multi-site customers use sequential subnets from their allocated block
