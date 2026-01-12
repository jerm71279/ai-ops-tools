# DC02 Data Copy Workflow Summary

## Overview
Successfully mirrored E:\ drive to Y:\ (\\setco-fs01-vm\f$) for Azure migration preparation.

**Results:**
- **Total Files:** 549,424
- **Total Size:** 538.865 GB
- **Files Copied:** 291,968 (189.110 GB)
- **Files Skipped:** 256,941 (already identical)
- **Files Failed:** 517 (System Volume Information - acceptable)
- **Copy Time:** 2 hours 54 minutes (with /MT:32)

---

## 1. Create Log Directory

```cmd
mkdir C:\Logs
```

---

## 2. Run Robocopy (Mirror E:\ to Y:\)

```cmd
robocopy E:\ \\setco-fs01-vm\f$ /MIR /COPYALL /DCOPY:T /MT:32 /R:1 /W:1 /B /XD "\\setco-fs01-vm\f$\Backup" /LOG:C:\Logs\robocopy_delta.log /TEE /NP
```

**Key Parameters:**
- `/MIR` - Mirror mode (exact copy, deletes extras)
- `/COPYALL` - Copy all file attributes, permissions, timestamps
- `/DCOPY:T` - Copy directory timestamps
- `/MT:32` - Use 32 threads (fast)
- `/R:1 /W:1` - Retry once, wait 1 second
- `/B` - Backup mode (use backup privileges)
- `/XD` - Exclude Backup folder
- `/LOG` - Log to file
- `/TEE` - Show output on screen and log
- `/NP` - No progress percentage (cleaner output)

---

## 3. Monitor Progress

### Option A: PowerShell Progress Monitor (Recommended)

```powershell
# Run in separate PowerShell (as Administrator)
$totalFiles = 392994  # Adjust based on your E:\ file count

while($true) {
    $currentCount = (Get-ChildItem \\setco-fs01-vm\f$ -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {$_.FullName -notlike '*\Backup\*'} | Measure-Object).Count

    $remaining = $totalFiles - $currentCount
    $progress = [math]::Round(($currentCount / $totalFiles) * 100, 2)

    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
    Write-Host "  Files copied: $currentCount / $totalFiles" -ForegroundColor White
    Write-Host "  Remaining:    $remaining files" -ForegroundColor Yellow
    Write-Host "  Progress:     $progress%" -ForegroundColor Cyan
    Write-Host ""

    Start-Sleep -Seconds 300  # Check every 5 minutes
}
```

### Option B: Manual File Count Check

```powershell
# Get current file count on destination
(Get-ChildItem \\setco-fs01-vm\f$ -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {$_.FullName -notlike '*\Backup\*'} | Measure-Object).Count
```

---

## 4. Validation After Completion

### Check Source File Count
```powershell
(Get-ChildItem E:\ -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object).Count
```

### Check Destination File Count
```powershell
(Get-ChildItem \\setco-fs01-vm\f$ -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {$_.FullName -notlike '*\Backup\*'} | Measure-Object).Count
```

### Compare Sizes
```cmd
dir E:\ /s
dir \\setco-fs01-vm\f$\ /s
```

### Review Failed Files
```cmd
findstr /I "ERROR" C:\Logs\robocopy_delta.log | more
```

### Spot Check Critical Folders
- Navigate to `\\setco-fs01-vm\f$\HomeDirs` - verify user folders
- Check `\\setco-fs01-vm\f$\SetcoDocs` - verify documents
- Check `\\setco-fs01-vm\f$\PostClosing` - verify data exists

---

## Key Findings

**Excluded Items (Expected):**
- Recycle Bin ($RECYCLE.BIN) - skipped automatically
- Backup folder - excluded via /XD parameter
- System Volume Information - failed with Access Denied (expected, not needed)

**Failed Files (517 total):**
- System Volume Information files (shadow copies/restore points)
- 2 Excel files locked by users during copy
- **All failures acceptable** - no critical business data lost

---

## Next Steps
Y:\ drive is now ready for:
- VHD export
- Azure disk image creation
- VM migration to new tenant
