# Network Router Migration Best Practices

## MikroTik to SonicWall (or any router swap)

### Golden Rule
**Match the existing config exactly for zero-downtime swap. Migrate IP schemes later.**

### Pre-Migration Checklist

1. **Export Current MikroTik Config**
   ```bash
   /export file=backup_YYYYMMDD
   ```
   Or via WinBox: Files → backup.rsc

2. **Document Current Settings**
   - LAN IP and subnet (e.g., 192.168.0.1/24)
   - DHCP pool range (e.g., .20-.254)
   - DNS servers
   - VLAN configuration (if any)
   - Static routes
   - Firewall rules
   - Port forwards

3. **Configure New Router to Match**
   - Same LAN gateway IP
   - Same DHCP range
   - Same DNS servers
   - Same VLANs (if used)

4. **Swap Hardware**
   - Power down MikroTik
   - Connect SonicWall with same cabling
   - Power up - clients work immediately

5. **Post-Swap Verification**
   - Test internet connectivity
   - Test DHCP (renew a client)
   - Test any VPNs
   - Test port forwards

### IP Scheme Migration (Phase 2 - Optional)

After successful swap, if migrating to new IP scheme (e.g., 10.x.x.x):

1. Schedule maintenance window
2. Update DHCP scope on new router
3. Update any static IPs on devices
4. Renew DHCP on all clients
5. Update VPN tunnel networks on both ends
6. Update firewall rules referencing old subnets

### Example: Jubilee Pool Migration

**Before (MikroTik):**
| Site | LAN | DHCP |
|------|-----|------|
| Fairhope | 192.168.0.1/24 | .20-.254 |
| Daphne | 192.168.1.1/24 | .20-.254 |

**SonicWall Config (Phase 1 - Match existing):**
- Same IPs as above for zero-downtime swap

**Future (Phase 2 - OberaConnect Standard):**
| Site | LAN | DHCP |
|------|-----|------|
| Fairhope | 10.54.8.1/24 | .100-.254 |
| Daphne | 10.54.9.1/24 | .100-.254 |

### Common Gotchas

- **VLAN mismatch**: If MikroTik uses VLANs, new router must match or APs/switches won't work
- **DHCP conflicts**: Ensure old router is OFF before enabling DHCP on new router
- **DNS caching**: Clients may cache old DNS - flush if issues arise
- **Static IPs**: Printers, servers with static IPs need gateway updated if it changes
