# Verify Migration Sync - Find files modified on migration day
# Run this on SETCO-DC02 to confirm delta sync worked

param(
    [string]$MigrationDate = "11/21/2025",
    [string]$SearchPath = "F:\"
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Migration Sync Verification" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Migration Date: $MigrationDate" -ForegroundColor White
Write-Host "Search Path: $SearchPath" -ForegroundColor White
Write-Host ""

# Convert migration date to DateTime
$targetDate = [DateTime]::Parse($MigrationDate)
$startDate = $targetDate.Date
$endDate = $targetDate.Date.AddDays(1).AddSeconds(-1)

Write-Host "Searching for files modified between:" -ForegroundColor Yellow
Write-Host "  Start: $startDate" -ForegroundColor Gray
Write-Host "  End:   $endDate" -ForegroundColor Gray
Write-Host ""

# Get all folders to search
Write-Host "Scanning folders on $SearchPath..." -ForegroundColor Yellow
$folders = Get-ChildItem $SearchPath -Directory -ErrorAction SilentlyContinue

Write-Host "Found $($folders.Count) top-level folders" -ForegroundColor Gray
Write-Host ""

# Results collection
$allModifiedFiles = @()
$folderStats = @()

# Search each folder
foreach ($folder in $folders) {
    Write-Host "Searching: $($folder.Name)..." -ForegroundColor Cyan

    try {
        # Find files modified on migration date
        $modifiedFiles = Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $startDate -and $_.LastWriteTime -le $endDate }

        $count = ($modifiedFiles | Measure-Object).Count
        $totalSize = ($modifiedFiles | Measure-Object -Property Length -Sum).Sum
        $sizeGB = if ($totalSize) { [math]::Round($totalSize / 1GB, 2) } else { 0 }

        if ($count -gt 0) {
            Write-Host "  Found: $count files ($sizeGB GB)" -ForegroundColor Green

            # Add to results
            $allModifiedFiles += $modifiedFiles

            # Track folder stats
            $folderStats += [PSCustomObject]@{
                Folder = $folder.Name
                FileCount = $count
                'Size(GB)' = $sizeGB
            }
        } else {
            Write-Host "  Found: 0 files" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Overall stats
$totalFiles = ($allModifiedFiles | Measure-Object).Count
$totalSizeBytes = ($allModifiedFiles | Measure-Object -Property Length -Sum).Sum
$totalSizeGB = if ($totalSizeBytes) { [math]::Round($totalSizeBytes / 1GB, 2) } else { 0 }

Write-Host ""
Write-Host "Total files modified on $MigrationDate : $totalFiles" -ForegroundColor Green
Write-Host "Total size: $totalSizeGB GB" -ForegroundColor Green
Write-Host ""

if ($folderStats.Count -gt 0) {
    Write-Host "Files by folder:" -ForegroundColor Yellow
    $folderStats | Sort-Object FileCount -Descending | Format-Table -AutoSize
}

# Show recent files (top 20 most recently modified)
if ($totalFiles -gt 0) {
    Write-Host ""
    Write-Host "Top 20 most recently modified files:" -ForegroundColor Yellow
    $allModifiedFiles |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 20 |
        Select-Object @{N='Modified';E={$_.LastWriteTime.ToString("MM/dd/yyyy HH:mm:ss")}},
                      @{N='Size(KB)';E={[math]::Round($_.Length/1KB,2)}},
                      @{N='Folder';E={Split-Path $_.DirectoryName -Leaf}},
                      Name |
        Format-Table -AutoSize

    # Export full list to CSV
    $exportPath = "C:\migration-files-$($targetDate.ToString('yyyy-MM-dd')).csv"
    Write-Host ""
    Write-Host "Exporting full list to: $exportPath" -ForegroundColor Cyan

    $allModifiedFiles |
        Select-Object FullName,
                      DirectoryName,
                      Name,
                      @{N='Size(KB)';E={[math]::Round($_.Length/1KB,2)}},
                      @{N='Size(MB)';E={[math]::Round($_.Length/1MB,2)}},
                      LastWriteTime,
                      CreationTime |
        Sort-Object LastWriteTime -Descending |
        Export-Csv -Path $exportPath -NoTypeInformation

    Write-Host "Export complete!" -ForegroundColor Green
}

# Also check for files modified in the 3 days before migration
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "EXTENDED SEARCH (3 days before migration)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$extendedStart = $targetDate.AddDays(-3)
$extendedEnd = $targetDate.Date.AddDays(1).AddSeconds(-1)

Write-Host "Searching for files modified between $($extendedStart.ToString('MM/dd/yyyy')) and $($targetDate.ToString('MM/dd/yyyy'))..." -ForegroundColor Yellow
Write-Host ""

$recentFiles = Get-ChildItem $SearchPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $extendedStart -and $_.LastWriteTime -le $extendedEnd }

$recentCount = ($recentFiles | Measure-Object).Count
$recentSize = ($recentFiles | Measure-Object -Property Length -Sum).Sum
$recentSizeGB = if ($recentSize) { [math]::Round($recentSize / 1GB, 2) } else { 0 }

Write-Host "Files modified in last 3 days before migration: $recentCount files ($recentSizeGB GB)" -ForegroundColor Green

if ($recentCount -gt 0) {
    Write-Host ""
    Write-Host "Files by date:" -ForegroundColor Yellow
    $recentFiles |
        Group-Object {$_.LastWriteTime.Date} |
        Sort-Object Name -Descending |
        Select-Object @{N='Date';E={([DateTime]$_.Name).ToString('MM/dd/yyyy')}}, Count, @{N='Size(GB)';E={[math]::Round(($_.Group | Measure-Object -Property Length -Sum).Sum / 1GB, 2)}} |
        Format-Table -AutoSize
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if ($totalFiles -gt 0) {
    Write-Host "[SUCCESS] Migration sync verified - $totalFiles files from $MigrationDate found on F: drive" -ForegroundColor Green
} else {
    Write-Host "[WARNING] No files from $MigrationDate found - verify migration date is correct" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review the CSV export: $exportPath" -ForegroundColor Gray
Write-Host "  2. Compare with original source to verify specific files" -ForegroundColor Gray
Write-Host "  3. Test opening some of the modified files to ensure they're accessible" -ForegroundColor Gray
