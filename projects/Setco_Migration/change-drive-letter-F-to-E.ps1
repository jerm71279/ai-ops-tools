# Change Data Drive from F: to E: and Update Shares
# Run on SETCO-DC02 as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Change Drive Letter F: to E:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Backup current share configuration
Write-Host "Step 1: Backing up current share configuration..." -ForegroundColor Yellow
$existingShares = Get-SmbShare | Where-Object {$_.Path -like 'F:*'}
$existingShares | Export-Csv -Path "C:\share-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm').csv" -NoTypeInformation
Write-Host "Backup saved to C:\share-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm').csv" -ForegroundColor Green
Write-Host ""

# Step 2: Remove all F: drive shares
Write-Host "Step 2: Removing all F: drive shares..." -ForegroundColor Yellow
$sharesToRemove = Get-SmbShare | Where-Object {$_.Path -like 'F:*' -and $_.Name -notlike '*$'}
Write-Host "Shares to remove: $($sharesToRemove.Count)" -ForegroundColor Gray

foreach ($share in $sharesToRemove) {
    Write-Host "  Removing share: $($share.Name)" -ForegroundColor Gray
    Remove-SmbShare -Name $share.Name -Force
}
Write-Host "[OK] All F: shares removed" -ForegroundColor Green
Write-Host ""

# Step 3: Verify F: drive is accessible
Write-Host "Step 3: Verifying F: drive status..." -ForegroundColor Yellow
$volumeF = Get-Volume -DriveLetter F -ErrorAction SilentlyContinue
if ($volumeF) {
    Write-Host "F: drive found" -ForegroundColor Green
    Write-Host "  Size: $([math]::Round($volumeF.Size/1GB, 2)) GB" -ForegroundColor Gray
    Write-Host "  Used: $([math]::Round(($volumeF.Size - $volumeF.SizeRemaining)/1GB, 2)) GB" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] F: drive not found!" -ForegroundColor Red
    exit
}
Write-Host ""

# Step 4: Check if E: is already in use
Write-Host "Step 4: Checking if E: is available..." -ForegroundColor Yellow
$volumeE = Get-Volume -DriveLetter E -ErrorAction SilentlyContinue
if ($volumeE) {
    Write-Host "[WARNING] E: drive is already in use!" -ForegroundColor Red
    Write-Host "Current E: drive details:" -ForegroundColor Yellow
    $volumeE | Format-Table DriveLetter, FileSystemLabel, Size, SizeRemaining
    Write-Host ""
    $response = Read-Host "Do you want to continue anyway? This may cause issues. (yes/no)"
    if ($response -ne "yes") {
        Write-Host "Operation cancelled" -ForegroundColor Yellow
        exit
    }
} else {
    Write-Host "[OK] E: drive letter is available" -ForegroundColor Green
}
Write-Host ""

# Step 5: Change drive letter from F: to E:
Write-Host "Step 5: Changing drive letter F: to E:..." -ForegroundColor Yellow
Write-Host "Getting partition information..." -ForegroundColor Gray

# Find the F: partition
$partition = Get-Partition | Where-Object {$_.DriveLetter -eq 'F'}
if (-not $partition) {
    Write-Host "[ERROR] Cannot find F: partition!" -ForegroundColor Red
    exit
}

Write-Host "Found partition on Disk $($partition.DiskNumber), Partition $($partition.PartitionNumber)" -ForegroundColor Gray
Write-Host "Changing drive letter..." -ForegroundColor Gray

Set-Partition -DiskNumber $partition.DiskNumber -PartitionNumber $partition.PartitionNumber -NewDriveLetter E

Write-Host "[OK] Drive letter changed to E:" -ForegroundColor Green
Write-Host ""

# Step 6: Verify E: drive
Write-Host "Step 6: Verifying E: drive..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$volumeE = Get-Volume -DriveLetter E -ErrorAction SilentlyContinue
if ($volumeE) {
    Write-Host "[OK] E: drive is now active" -ForegroundColor Green
    $volumeE | Format-Table DriveLetter, FileSystemLabel, Size, SizeRemaining
} else {
    Write-Host "[ERROR] E: drive not found after change!" -ForegroundColor Red
    exit
}
Write-Host ""

# Step 7: Test E: drive access
Write-Host "Step 7: Testing E: drive access..." -ForegroundColor Yellow
if (Test-Path "E:\") {
    Write-Host "[OK] E:\ is accessible" -ForegroundColor Green
    Write-Host "Top-level folders:" -ForegroundColor Gray
    Get-ChildItem "E:\" -Directory | Select-Object -First 10 | Format-Table Name
} else {
    Write-Host "[ERROR] Cannot access E:\!" -ForegroundColor Red
    exit
}
Write-Host ""

# Step 8: Recreate shares pointing to E:
Write-Host "Step 8: Recreating shares on E: drive..." -ForegroundColor Yellow

$shares = @(
    @{Name="E"; Path="E:\"; FullAccess="Everyone"},
    @{Name="FTP Data"; Path="E:\FTP Data"; FullAccess="Everyone"},
    @{Name="HomeDirs"; Path="E:\HomeDirs"; ReadAccess="Users"; FullAccess="Domain Admins"},
    @{Name="Legal"; Path="E:\HomeDirs\Legal"; FullAccess="Domain Admins"},
    @{Name="PostClosing"; Path="E:\PostClosing"; FullAccess="Domain Admins"},
    @{Name="Qbooks"; Path="E:\Qbooks"; FullAccess="Domain Admins"},
    @{Name="SeaCrestScans"; Path="E:\SeaCrestScans"; FullAccess="Everyone"},
    @{Name="SetcoDocs"; Path="E:\SetcoDocs"; FullAccess="Everyone"},
    @{Name="Versacheck"; Path="E:\Versacheck"; FullAccess="Domain Admins"},
    @{Name="Whole Life Fitness"; Path="E:\Whole Life Fitness"; FullAccess="Domain Admins"},
    @{Name="worddocs"; Path="E:\NTSYS\worddocs"; FullAccess="Everyone"}
)

$created = 0
$failed = 0

foreach ($share in $shares) {
    # Verify path exists first
    if (Test-Path $share.Path) {
        try {
            if ($share.ContainsKey('ReadAccess')) {
                New-SmbShare -Name $share.Name -Path $share.Path -ReadAccess $share.ReadAccess -FullAccess $share.FullAccess -ErrorAction Stop | Out-Null
            } else {
                New-SmbShare -Name $share.Name -Path $share.Path -FullAccess $share.FullAccess -ErrorAction Stop | Out-Null
            }
            Write-Host "  [OK] Created share: $($share.Name) -> $($share.Path)" -ForegroundColor Green
            $created++
        } catch {
            Write-Host "  [FAIL] Could not create share: $($share.Name) - $($_.Exception.Message)" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "  [SKIP] Path does not exist: $($share.Path)" -ForegroundColor Yellow
        $failed++
    }
}

Write-Host ""
Write-Host "Shares created: $created" -ForegroundColor Green
Write-Host "Shares failed: $failed" -ForegroundColor $(if ($failed -gt 0) {"Red"} else {"Green"})
Write-Host ""

# Step 9: Verify shares
Write-Host "Step 9: Verifying all shares..." -ForegroundColor Yellow
$eShares = Get-SmbShare | Where-Object {$_.Path -like 'E:*'}
Write-Host "Total E: drive shares: $($eShares.Count)" -ForegroundColor Green
Write-Host ""
$eShares | Format-Table Name, Path -AutoSize
Write-Host ""

# Step 10: Test share access
Write-Host "Step 10: Testing share access..." -ForegroundColor Yellow
$testResults = @()

foreach ($share in $eShares) {
    $uncPath = "\\localhost\$($share.Name)"
    if (Test-Path $uncPath) {
        Write-Host "  [OK] $uncPath is accessible" -ForegroundColor Green
        $testResults += "PASS"
    } else {
        Write-Host "  [FAIL] $uncPath is NOT accessible" -ForegroundColor Red
        $testResults += "FAIL"
    }
}

Write-Host ""
$passCount = ($testResults | Where-Object {$_ -eq "PASS"}).Count
Write-Host "Share access tests: $passCount/$($testResults.Count) passed" -ForegroundColor $(if ($passCount -eq $testResults.Count) {"Green"} else {"Yellow"})
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[✓] Drive letter changed from F: to E:" -ForegroundColor Green
Write-Host "[✓] Old F: shares removed" -ForegroundColor Green
Write-Host "[✓] New E: shares created: $created" -ForegroundColor Green
Write-Host "[✓] Shares accessible: $passCount/$($testResults.Count)" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test share access from a client workstation" -ForegroundColor Gray
Write-Host "  2. Verify mapped drives reconnect correctly" -ForegroundColor Gray
Write-Host "  3. Check applications that reference drive letters" -ForegroundColor Gray
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
