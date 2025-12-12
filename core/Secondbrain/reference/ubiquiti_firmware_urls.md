# Ubiquiti Firmware Reference

Quick reference for Ubiquiti/UniFi firmware download URLs and upgrade commands.

## Firmware URLs

| Device Type | Model | Version | Firmware URL | Date Added |
|-------------|-------|---------|--------------|------------|
| Switch | USW-16-POE | 7.1.26+15869 | `https://dl.ui.com/unifi/firmware/USMULTUSW16POE/7.1.26.15869/US.MULT.USW_16_POE_7.1.26+15869.240926.2129.bin` | 2025-12-04 |

## SSH Upgrade Command

From SSH/Putty into the device:
```
upgrade <firmware_url>
```

Example:
```
upgrade https://dl.ui.com/unifi/firmware/USMULTUSW16POE/7.1.26.15869/US.MULT.USW_16_POE_7.1.26+15869.240926.2129.bin
```

## URL Pattern

Ubiquiti firmware URLs follow this pattern:
```
https://dl.ui.com/unifi/firmware/<DEVICE_CODE>/<VERSION>/<FILENAME>.bin
```

## Notes

- **SSH upgrade only needed for switches PRIOR to adoption** - after adoption, firmware is managed via UniFi Controller
- APs can be adopted directly without manual firmware upgrade
- Firmware releases: https://community.ui.com/releases
- Always backup config before upgrading
