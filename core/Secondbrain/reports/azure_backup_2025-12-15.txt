### **Azure VM Backup Status Report**

**Date:** December 15, 2025
**Vault:** MyRecoveryServicesVault
**Resource Group:** DataCenter

---

### **Executive Summary**

All critical production VMs in the `MyRecoveryServicesVault` vault have been reviewed.

- **Total VMs Reviewed:** 6
- **Successfully Protected:** 6
- **Protection Issues:** 0

---

### **Detailed Backup Status**

| VM Name | Status | Last Successful Backup | Backup Policy |
| ------- | ------ | ---------------------- | ------------- |
| ADFS | ✅ Protected | 2025-12-15 03:56 UTC | `DefaultPolicy` |
| ADFSproxy | ✅ Protected | 2025-12-15 03:53 UTC | `DefaultPolicy` |
| SETCO-DC01-VM | ✅ Protected | 2025-12-15 03:54 UTC | `DefaultPolicy` |
| SETCO-DC02-VM | ✅ Protected | 2025-12-15 03:55 UTC | `DefaultPolicy` |
| SETCO-FS01-VM | ✅ Protected | 2025-12-15 03:54 UTC | `DefaultPolicy` |
| SETCO-RDS001 | ✅ Protected | 2025-12-15 03:52 UTC | `DefaultPolicy` |

---

### **Recommendations**

- All VMs are protected and backing up successfully. No action required.

2. **Policy Review:** Quarterly review recommended to ensure backup policies meet RPO/RTO objectives.
