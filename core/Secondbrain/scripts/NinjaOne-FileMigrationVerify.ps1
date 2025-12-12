#Requires -Version 5.1
<#
.SYNOPSIS
    Obera Connect - File Migration Verification Script
    Deploy via NinjaOne remote session - prompts for paths at runtime

.DESCRIPTION
    Verifies file migration from on-prem file server to SharePoint/OneDrive
    Prompts for source and destination paths when run

.NOTES
    Company: Obera Connect
    Deploy via: NinjaOne Remote Terminal or Script Library
    Run as: Admin user with access to both file server and SharePoint sync folder
#>

$ErrorActionPreference = "Continue"

# ============================================================
# BANNER
# ============================================================
Clear-Host
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  OBERA CONNECT - FILE MIGRATION VERIFICATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Endpoint:  $env:COMPUTERNAME" -ForegroundColor Gray
Write-Host "  User:      $env:USERNAME" -ForegroundColor Gray
Write-Host "  Time:      $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# INTERACTIVE PROMPTS
# ============================================================
Write-Host "Enter the paths for migration verification:" -ForegroundColor Yellow
Write-Host ""

# Source Path
Write-Host "SOURCE PATH (file server):" -ForegroundColor White
Write-Host "  Examples: \\FILESERVER\SharedData" -ForegroundColor Gray
Write-Host "            D:\CompanyData" -ForegroundColor Gray
Write-Host "            \\192.168.1.10\Files" -ForegroundColor Gray
$SourcePath = Read-Host "  Enter source path"

if ([string]::IsNullOrWhiteSpace($SourcePath)) {
    Write-Host ""
    Write-Host "[ERROR] Source path cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Destination Path
Write-Host "DESTINATION PATH (SharePoint/OneDrive synced folder):" -ForegroundColor White
Write-Host "  Examples: C:\Users\admin\OneDrive - CompanyName\Documents" -ForegroundColor Gray
Write-Host "            C:\Users\admin\SharePoint\Site - Documents" -ForegroundColor Gray
$DestPath = Read-Host "  Enter destination path"

if ([string]::IsNullOrWhiteSpace($DestPath)) {
    Write-Host ""
    Write-Host "[ERROR] Destination path cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Customer Name (for report)
$CustomerName = Read-Host "Customer Name (for report filename)"
if ([string]::IsNullOrWhiteSpace($CustomerName)) {
    $CustomerName = "Customer"
}

Write-Host ""

# Spot check count
Write-Host "Spot check count (default 50):" -ForegroundColor White
$spotInput = Read-Host "  Enter number or press Enter for default"
if ([string]::IsNullOrWhiteSpace($spotInput)) {
    $SpotCheckCount = 50
} else {
    $SpotCheckCount = [int]$spotInput
}

# Setup report path
$reportDir = "C:\OberaConnect\MigrationReports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}
$safeCustomerName = $CustomerName -replace '[^\w\-]', '_'
$ExportReport = "$reportDir\$($safeCustomerName)_MigrationVerify_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# ============================================================
# CONFIRMATION
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "  VERIFICATION SETTINGS" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "  Customer:     $CustomerName" -ForegroundColor White
Write-Host "  Source:       $SourcePath" -ForegroundColor White
Write-Host "  Destination:  $DestPath" -ForegroundColor White
Write-Host "  Spot Checks:  $SpotCheckCount files" -ForegroundColor White
Write-Host "  Report:       $ExportReport" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Proceed with verification? (Y/n)"
if ($confirm -eq 'n' -or $confirm -eq 'N') {
    Write-Host "Verification cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# ============================================================
# INITIALIZE RESULTS
# ============================================================
$results = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    CustomerName = $CustomerName
    Endpoint = $env:COMPUTERNAME
    RunBy = $env:USERNAME
    SourcePath = $SourcePath
    DestPath = $DestPath
    Status = "UNKNOWN"
    Summary = @{}
    Issues = @()
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch($Level) {
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    $prefix = switch($Level) {
        "OK"    { "[OK]   " }
        "WARN"  { "[WARN] " }
        "ERROR" { "[ERR]  " }
        default { "[INFO] " }
    }
    Write-Host "$timestamp $prefix $Message" -ForegroundColor $color
}

# ============================================================
# VALIDATE PATHS
# ============================================================
Write-Host "--- VALIDATING PATHS ---" -ForegroundColor Cyan

if (-not (Test-Path $SourcePath)) {
    Write-Log "Source path not accessible: $SourcePath" "ERROR"
    Write-Log "Check: Is file server online? Do you have permissions?" "ERROR"
    $results.Status = "FAILED"
    $results.Issues += "Source path not accessible"
    $results | ConvertTo-Json -Depth 5 | Out-File $ExportReport -Encoding UTF8
    Write-Host ""
    Write-Host "Report saved: $ExportReport" -ForegroundColor Gray
    exit 1
}
Write-Log "Source path accessible" "OK"

if (-not (Test-Path $DestPath)) {
    Write-Log "Destination path not accessible: $DestPath" "ERROR"
    Write-Log "Check: Is OneDrive/SharePoint synced? Is the sync client running?" "ERROR"
    $results.Status = "FAILED"
    $results.Issues += "Destination path not accessible"
    $results | ConvertTo-Json -Depth 5 | Out-File $ExportReport -Encoding UTF8
    Write-Host ""
    Write-Host "Report saved: $ExportReport" -ForegroundColor Gray
    exit 1
}
Write-Log "Destination path accessible" "OK"

Write-Host ""

# ============================================================
# PHASE 1: COUNT COMPARISON
# ============================================================
Write-Host "--- PHASE 1: COUNT COMPARISON ---" -ForegroundColor Cyan
Write-Log "Scanning source folder (may take several minutes)..."

$srcItems = Get-ChildItem $SourcePath -Recurse -Force -ErrorAction SilentlyContinue
$srcFiles = $srcItems | Where-Object { -not $_.PSIsContainer }
$srcFolders = $srcItems | Where-Object { $_.PSIsContainer }
$srcFileCount = ($srcFiles | Measure-Object).Count
$srcFolderCount = ($srcFolders | Measure-Object).Count
$srcTotalSize = ($srcFiles | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
if ($null -eq $srcTotalSize) { $srcTotalSize = 0 }
$srcSizeGB = [math]::Round($srcTotalSize / 1GB, 2)

Write-Log "Source: $srcFileCount files, $srcFolderCount folders, $srcSizeGB GB"
Write-Log "Scanning destination folder..."

$dstItems = Get-ChildItem $DestPath -Recurse -Force -ErrorAction SilentlyContinue
$dstFiles = $dstItems | Where-Object { -not $_.PSIsContainer }
$dstFolders = $dstItems | Where-Object { $_.PSIsContainer }
$dstFileCount = ($dstFiles | Measure-Object).Count
$dstFolderCount = ($dstFolders | Measure-Object).Count
$dstTotalSize = ($dstFiles | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
if ($null -eq $dstTotalSize) { $dstTotalSize = 0 }
$dstSizeGB = [math]::Round($dstTotalSize / 1GB, 2)

Write-Log "Dest:   $dstFileCount files, $dstFolderCount folders, $dstSizeGB GB"
Write-Host ""

# Display comparison
$fileMatch = if($srcFileCount -eq $dstFileCount){"MATCH"}else{"DIFF"}
$folderMatch = if($srcFolderCount -eq $dstFolderCount){"MATCH"}else{"DIFF"}
$sizeMatch = if([math]::Abs($srcSizeGB - $dstSizeGB) -lt 0.1){"MATCH"}else{"DIFF"}

Write-Host "  +-----------------------------------------------------------+" -ForegroundColor Gray
Write-Host "  |              SOURCE          DEST            STATUS      |" -ForegroundColor Gray
Write-Host "  +-----------------------------------------------------------+" -ForegroundColor Gray
Write-Host "  |  Files:   $($srcFileCount.ToString().PadLeft(10))    $($dstFileCount.ToString().PadLeft(10))        [$fileMatch]     |"
Write-Host "  |  Folders: $($srcFolderCount.ToString().PadLeft(10))    $($dstFolderCount.ToString().PadLeft(10))        [$folderMatch]     |"
Write-Host "  |  Size GB: $($srcSizeGB.ToString().PadLeft(10))    $($dstSizeGB.ToString().PadLeft(10))        [$sizeMatch]     |"
Write-Host "  +-----------------------------------------------------------+" -ForegroundColor Gray
Write-Host ""

$results.Summary = @{
    SourceFiles = $srcFileCount
    SourceFolders = $srcFolderCount
    SourceSizeGB = $srcSizeGB
    DestFiles = $dstFileCount
    DestFolders = $dstFolderCount
    DestSizeGB = $dstSizeGB
    FileDiff = $srcFileCount - $dstFileCount
    SizeDiffGB = [math]::Round($srcSizeGB - $dstSizeGB, 2)
}

if ($srcFileCount -ne $dstFileCount) {
    $diff = $srcFileCount - $dstFileCount
    if ($diff -gt 0) {
        Write-Log "MISSING $diff files in destination" "WARN"
        $results.Issues += "Missing $diff files"
    } else {
        Write-Log "EXTRA $([math]::Abs($diff)) files in destination" "WARN"
        $results.Issues += "Extra $([math]::Abs($diff)) files"
    }
}

# ============================================================
# PHASE 2: MISSING FILE DETECTION
# ============================================================
Write-Host "--- PHASE 2: MISSING FILE DETECTION ---" -ForegroundColor Cyan
Write-Log "Building file index..."

$srcRelPaths = @{}
$srcPathLen = $SourcePath.TrimEnd('\','/').Length
foreach ($file in $srcFiles) {
    $relPath = $file.FullName.Substring($srcPathLen).TrimStart('\','/')
    $srcRelPaths[$relPath.ToLower()] = @{
        Path = $relPath
        Size = $file.Length
    }
}

$dstRelPaths = @{}
$dstPathLen = $DestPath.TrimEnd('\','/').Length
foreach ($file in $dstFiles) {
    $relPath = $file.FullName.Substring($dstPathLen).TrimStart('\','/')
    $dstRelPaths[$relPath.ToLower()] = @{
        Path = $relPath
        Size = $file.Length
    }
}

# Find missing
$missingInDest = @()
foreach ($key in $srcRelPaths.Keys) {
    if (-not $dstRelPaths.ContainsKey($key)) {
        $missingInDest += $srcRelPaths[$key].Path
    }
}

Write-Host ""
if ($missingInDest.Count -gt 0) {
    Write-Log "$($missingInDest.Count) FILES MISSING IN DESTINATION:" "WARN"
    $showCount = [math]::Min(15, $missingInDest.Count)
    for ($i = 0; $i -lt $showCount; $i++) {
        Write-Host "    - $($missingInDest[$i])" -ForegroundColor Yellow
    }
    if ($missingInDest.Count -gt 15) {
        Write-Host "    ... and $($missingInDest.Count - 15) more (see JSON report)" -ForegroundColor Yellow
    }
    $results.Issues += "Missing files: $($missingInDest.Count)"
    $results.MissingFiles = $missingInDest
} else {
    Write-Log "No missing files detected" "OK"
}

Write-Host ""

# ============================================================
# PHASE 3: SPOT CHECK
# ============================================================
Write-Host "--- PHASE 3: SPOT CHECK VERIFICATION ---" -ForegroundColor Cyan

$commonKeys = $srcRelPaths.Keys | Where-Object { $dstRelPaths.ContainsKey($_) }
$sampleSize = [math]::Min($SpotCheckCount, $commonKeys.Count)

if ($sampleSize -gt 0) {
    Write-Log "Checking $sampleSize random files..."

    $spotCheckKeys = $commonKeys | Get-Random -Count $sampleSize
    $sizeMismatches = @()
    $passed = 0

    foreach ($key in $spotCheckKeys) {
        if ($srcRelPaths[$key].Size -eq $dstRelPaths[$key].Size) {
            $passed++
        } else {
            $sizeMismatches += @{
                Path = $srcRelPaths[$key].Path
                SourceSize = $srcRelPaths[$key].Size
                DestSize = $dstRelPaths[$key].Size
            }
        }
    }

    Write-Host ""
    Write-Host "  Spot Check: $passed / $sampleSize passed" -ForegroundColor $(if($passed -eq $sampleSize){"Green"}else{"Yellow"})

    if ($sizeMismatches.Count -gt 0) {
        Write-Log "$($sizeMismatches.Count) SIZE MISMATCHES:" "WARN"
        foreach ($m in $sizeMismatches[0..([math]::Min(4, $sizeMismatches.Count-1))]) {
            Write-Host "    - $($m.Path)" -ForegroundColor Yellow
        }
        $results.Issues += "Size mismatches: $($sizeMismatches.Count)"
        $results.SizeMismatches = $sizeMismatches
    } else {
        Write-Log "All spot checks passed" "OK"
    }

    $results.SpotCheckSummary = @{
        Total = $sampleSize
        Passed = $passed
        Failed = $sizeMismatches.Count
    }
}

Write-Host ""

# ============================================================
# FINAL STATUS
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION RESULT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$hasCritical = ($missingInDest.Count -gt 0) -or ($sizeMismatches.Count -gt 0)

if ($results.Issues.Count -eq 0) {
    $results.Status = "PASSED"
    Write-Host ""
    Write-Host "  STATUS: PASSED" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Migration verification successful!" -ForegroundColor Green
    Write-Host "  All $srcFileCount files accounted for." -ForegroundColor Green
} elseif (-not $hasCritical) {
    $results.Status = "PASSED_WITH_WARNINGS"
    Write-Host ""
    Write-Host "  STATUS: PASSED WITH WARNINGS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Migration appears complete with minor differences." -ForegroundColor Yellow
} else {
    $results.Status = "FAILED"
    Write-Host ""
    Write-Host "  STATUS: FAILED - ACTION REQUIRED" -ForegroundColor Red
    Write-Host ""
    foreach ($issue in $results.Issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  Report: $ExportReport" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Export
$results | ConvertTo-Json -Depth 10 | Out-File $ExportReport -Encoding UTF8
Write-Log "Report saved to $ExportReport"

# Pause for NinjaOne terminal
Write-Host ""
Read-Host "Press Enter to exit"

switch ($results.Status) {
    "PASSED" { exit 0 }
    "PASSED_WITH_WARNINGS" { exit 0 }
    default { exit 1 }
}
