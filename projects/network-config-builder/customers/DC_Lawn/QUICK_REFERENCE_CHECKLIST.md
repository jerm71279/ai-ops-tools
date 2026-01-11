# DC Lawn - Quick Reference Checklist

**Customer:** DC Lawn | **Circuit:** 205922 | **Date:** ___________

Print this page and check off each step during bench testing and deployment.

---

## Pre-Deployment Bench Testing

### Initial Setup (15 min)
- [ ] 1. Connect computer to ether2, power on MikroTik
- [ ] 2. WinBox → Connect to 192.168.88.1 (admin/blank password)
- [ ] 3. Record: Model _______ Serial _______ RouterOS _______
- [ ] 4. Backup factory config (Files → Backup)
- [ ] 5. Download factory backup to computer

### Configuration Upload (10 min)
- [ ] 6. Upload `router.rsc` to MikroTik (Files → Upload)
- [ ] 7. Terminal: `/import file-name=router.rsc`
- [ ] 8. Reconnect WinBox to 10.54.0.1 (admin/ChangeMe@205922!)

### Verification (10 min)
- [ ] 9. Check IPs: `/ip address print`
  - Expected: 142.190.216.66/30 on ether1 ✓
  - Expected: 10.54.0.1/24 on bridge-lan ✓
- [ ] 10. Check route: `/ip route print`
  - Expected: gateway 142.190.216.65 ✓
- [ ] 11. Check DHCP: `/ip dhcp-server print`
  - Expected: lan-dhcp enabled ✓
- [ ] 12. Check NAT: `/ip firewall nat print`
  - Expected: masquerade rule present ✓
- [ ] 13. Check security: `/ip service print`
  - Expected: Only WinBox & SSH enabled ✓

### LAN Testing (10 min)
- [ ] 14. Connect test device to ether2-5
- [ ] 15. Test device gets IP 10.54.0.100-200 ✓
- [ ] 16. Ping 10.54.0.1 from test device ✓
- [ ] 17. WinBox works from test device ✓

### Final Preparation (5 min)
- [ ] 18. Change password: `/user set admin password=___________`
- [ ] 19. Document new password in password manager
- [ ] 20. Create backup: `/system backup save name=DC_Lawn_PreDeploy`
- [ ] 21. Download backup files
- [ ] 22. Label router: "DC Lawn | 142.190.216.66 | LAN: 10.54.0.1"
- [ ] 23. Power off and pack for transport

---

## On-Site Deployment

### Physical Installation
- [ ] 24. Unpack router and verify labels
- [ ] 25. Connect ether1 to Calix port (Circuit 205922)
  - Port speed: Auto | Duplex: Auto
- [ ] 26. Connect ether2-5 to customer LAN/switch
- [ ] 27. Power on router, wait 60 seconds

### WAN Verification
- [ ] 28. WinBox → Connect 10.54.0.1 (from LAN device)
- [ ] 29. Check WAN link: `/interface print`
  - Expected: ether1 shows "running" ✓
- [ ] 30. Ping gateway: `/ping 142.190.216.65 count=5`
  - Expected: 0% packet loss ✓
- [ ] 31. Ping internet: `/ping 8.8.8.8 count=5`
  - Expected: 0% packet loss ✓
- [ ] 32. Test DNS: `/ping google.com count=5`
  - Expected: Resolves and pings ✓

### LAN Verification
- [ ] 33. Connect customer device to LAN
- [ ] 34. Device gets DHCP IP: 10.54.0._____ ✓
- [ ] 35. Device can browse internet ✓
- [ ] 36. Test website: google.com ✓
- [ ] 37. Test email/apps (if applicable) ✓

### Final Documentation
- [ ] 38. Record install date/time: _____________
- [ ] 39. Technician name: _____________
- [ ] 40. Customer signature: _____________
- [ ] 41. Take photos of installation
- [ ] 42. Create post-install backup
- [ ] 43. Update customer documentation

---

## Quick Reference Information

### Network Configuration
| Item | Value |
|------|-------|
| **WAN Interface** | ether1 |
| **WAN IP** | 142.190.216.66/30 |
| **Gateway** | 142.190.216.65 |
| **Subnet Mask** | 255.255.255.252 |
| **DNS Primary** | 142.190.111.111 |
| **DNS Secondary** | 142.190.222.222 |
| **LAN Interface** | bridge-lan |
| **LAN IP** | 10.54.0.1/24 |
| **LAN Subnet Block** | 10.54.0.0/24 - 10.54.3.0/24 |
| **DHCP Range** | 10.54.0.100-200 |
| **Admin User** | admin |
| **Admin Password** | (See password manager) |

### Emergency Commands
```bash
# Check connectivity
/ping 8.8.8.8

# View IP addresses
/ip address print

# View routes
/ip route print

# Check DHCP leases
/ip dhcp-server lease print

# View NAT rules
/ip firewall nat print

# Create backup
/system backup save name=emergency_backup
```

### Troubleshooting Quick Fixes

**Can't ping gateway?**
1. Check cable: `/interface print` (ether1 should be "running")
2. Verify WAN IP: `/ip address print`
3. Contact ISP/Unifi to verify circuit active

**LAN devices no DHCP?**
1. Check server: `/ip dhcp-server print` (should be enabled)
2. Check pool: `/ip pool print` (verify range)
3. Clear leases: `/ip dhcp-server lease remove [find dynamic]`

**No internet from LAN?**
1. Test from router: `/ping 8.8.8.8`
2. Check NAT: `/ip firewall nat print` (masquerade rule present?)
3. Check DNS: `/ping google.com`

**Factory Reset (EMERGENCY ONLY)**
- Hold reset button 10 seconds while powered
- Then restore from backup file

---

## Support Contacts

**Obera Connect:**
- Support: ________________
- After Hours: ________________

**ISP/Unifi Circuit 205922:**
- Support: ________________
- Circuit Contact: ________________

**MikroTik:**
- Wiki: wiki.mikrotik.com
- Forum: forum.mikrotik.com

---

## Installation Notes

```
Site Contact: _______________________________
Phone: _____________________________________
Special Instructions:
_____________________________________________
_____________________________________________
_____________________________________________

Issues/Resolutions:
_____________________________________________
_____________________________________________
_____________________________________________

Additional Equipment Installed:
_____________________________________________
_____________________________________________
```

---

**Installation Status:** [ ] Bench Tested [ ] Deployed [ ] Verified [ ] Complete

**Completed By:** _______________ **Date:** _______________ **Time:** _______________

---

*Generated by Multi-Vendor Network Config Builder*
*Customer: DC Lawn | Circuit ID: 205922 | Location: Fairhope, AL*
