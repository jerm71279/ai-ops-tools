#Requires -Version 5.1
<#
.SYNOPSIS
    File Migration Verification Script - Standard Level (Counts + Spot Checks)
    Designed to run via NinjaOne remote session

.DESCRIPTION
    Compares source and destination folders with:
    - File/folder counts
    - Size comparison
    - Random spot checks (configurable sample size)
    - Missing file detection
    - Size mismatch detection

.PARAMETER SourcePath
    Source folder path (e.g., \\fileserver\share)

.PARAMETER DestPath
    Destination folder path (e.g., C:\Users\X\OneDrive\SharePoint\Site)

.PARAMETER SpotCheckCount
    Number of random files to verify (default: 50)

.PARAMETER ExportReport
    Path to export JSON report (optional)

.PARAMETER Verbose
    Show detailed progress

.EXAMPLE
    .\Verify-FileMigration.ps1 -SourcePath "\\fileserver\data" -DestPath "C:\Users\jsmith\SharePoint\Data"

.EXAMPLE
    .\Verify-FileMigration.ps1 -SourcePath "D:\Backup" -DestPath "E:\Mirror" -SpotCheckCount 100 -ExportReport "C:\Reports\verify.json"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,

    [Parameter(Mandatory=$true)]
    [string]$DestPath,

    [int]$SpotCheckCount = 50,

    [string]$ExportReport = "",

    [switch]$IncludeHashCheck
)

# Initialize results
$results = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    SourcePath = $SourcePath
    DestPath = $DestPath
    Status = "UNKNOWN"
    Summary = @{}
    Issues = @()
    SpotChecks = @()
}

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $prefix = switch($Type) {
        "OK"    { "[OK]   " }
        "WARN"  { "[WARN] " }
        "ERROR" { "[ERR]  " }
        "INFO"  { "[INFO] " }
        default { "       " }
    }
    Write-Host "$prefix $Message" -ForegroundColor $(switch($Type) {
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    })
}

# Banner
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  FILE MIGRATION VERIFICATION - STANDARD LEVEL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Status "Source:      $SourcePath"
Write-Status "Destination: $DestPath"
Write-Status "Spot Checks: $SpotCheckCount files"
Write-Host ""

# Validate paths
if (-not (Test-Path $SourcePath)) {
    Write-Status "Source path not accessible: $SourcePath" "ERROR"
    $results.Status = "FAILED"
    $results.Issues += "Source path not accessible"
    exit 1
}

if (-not (Test-Path $DestPath)) {
    Write-Status "Destination path not accessible: $DestPath" "ERROR"
    $results.Status = "FAILED"
    $results.Issues += "Destination path not accessible"
    exit 1
}

# PHASE 1: Count Comparison
Write-Host "--- PHASE 1: COUNT COMPARISON ---" -ForegroundColor Yellow
Write-Status "Scanning source folder..."

$srcItems = Get-ChildItem $SourcePath -Recurse -Force -ErrorAction SilentlyContinue
$srcFiles = $srcItems | Where-Object { -not $_.PSIsContainer }
$srcFolders = $srcItems | Where-Object { $_.PSIsContainer }
$srcFileCount = ($srcFiles | Measure-Object).Count
$srcFolderCount = ($srcFolders | Measure-Object).Count
$srcTotalSize = ($srcFiles | Measure-Object -Property Length -Sum).Sum
$srcSizeGB = [math]::Round($srcTotalSize / 1GB, 2)

Write-Status "Scanning destination folder..."

$dstItems = Get-ChildItem $DestPath -Recurse -Force -ErrorAction SilentlyContinue
$dstFiles = $dstItems | Where-Object { -not $_.PSIsContainer }
$dstFolders = $dstItems | Where-Object { $_.PSIsContainer }
$dstFileCount = ($dstFiles | Measure-Object).Count
$dstFolderCount = ($dstFolders | Measure-Object).Count
$dstTotalSize = ($dstFiles | Measure-Object -Property Length -Sum).Sum
$dstSizeGB = [math]::Round($dstTotalSize / 1GB, 2)

Write-Host ""
Write-Host "             SOURCE          DESTINATION      MATCH" -ForegroundColor Gray
Write-Host "  Files:     $($srcFileCount.ToString().PadLeft(10))    $($dstFileCount.ToString().PadLeft(10))        $(if($srcFileCount -eq $dstFileCount){'[OK]'}else{'[X]'})"
Write-Host "  Folders:   $($srcFolderCount.ToString().PadLeft(10))    $($dstFolderCount.ToString().PadLeft(10))        $(if($srcFolderCount -eq $dstFolderCount){'[OK]'}else{'[X]'})"
Write-Host "  Size (GB): $($srcSizeGB.ToString().PadLeft(10))    $($dstSizeGB.ToString().PadLeft(10))        $(if([math]::Abs($srcSizeGB - $dstSizeGB) -lt 0.01){'[OK]'}else{'[X]'})"
Write-Host ""

$results.Summary = @{
    SourceFiles = $srcFileCount
    SourceFolders = $srcFolderCount
    SourceSizeGB = $srcSizeGB
    DestFiles = $dstFileCount
    DestFolders = $dstFolderCount
    DestSizeGB = $dstSizeGB
    FilesMatch = ($srcFileCount -eq $dstFileCount)
    FoldersMatch = ($srcFolderCount -eq $dstFolderCount)
    SizeMatch = ([math]::Abs($srcSizeGB - $dstSizeGB) -lt 0.01)
}

if ($srcFileCount -ne $dstFileCount) {
    $diff = $srcFileCount - $dstFileCount
    if ($diff -gt 0) {
        Write-Status "Missing $diff files in destination" "WARN"
        $results.Issues += "Missing $diff files in destination"
    } else {
        Write-Status "Extra $([math]::Abs($diff)) files in destination" "WARN"
        $results.Issues += "Extra $([math]::Abs($diff)) files in destination"
    }
}

# PHASE 2: Missing File Detection
Write-Host "--- PHASE 2: MISSING FILE DETECTION ---" -ForegroundColor Yellow
Write-Status "Building file index..."

# Create relative path lookup
$srcRelPaths = @{}
foreach ($file in $srcFiles) {
    $relPath = $file.FullName.Substring($SourcePath.Length).TrimStart('\','/')
    $srcRelPaths[$relPath] = $file
}

$dstRelPaths = @{}
foreach ($file in $dstFiles) {
    $relPath = $file.FullName.Substring($DestPath.Length).TrimStart('\','/')
    $dstRelPaths[$relPath] = $file
}

# Find missing in destination
$missingInDest = @()
foreach ($relPath in $srcRelPaths.Keys) {
    if (-not $dstRelPaths.ContainsKey($relPath)) {
        $missingInDest += $relPath
    }
}

# Find extra in destination
$extraInDest = @()
foreach ($relPath in $dstRelPaths.Keys) {
    if (-not $srcRelPaths.ContainsKey($relPath)) {
        $extraInDest += $relPath
    }
}

if ($missingInDest.Count -gt 0) {
    Write-Status "$($missingInDest.Count) files missing in destination" "WARN"
    if ($missingInDest.Count -le 10) {
        foreach ($f in $missingInDest) {
            Write-Host "         - $f" -ForegroundColor Yellow
        }
    } else {
        foreach ($f in $missingInDest[0..9]) {
            Write-Host "         - $f" -ForegroundColor Yellow
        }
        Write-Host "         ... and $($missingInDest.Count - 10) more" -ForegroundColor Yellow
    }
    $results.Issues += "Missing files: $($missingInDest.Count)"
    $results.MissingFiles = $missingInDest
} else {
    Write-Status "No missing files detected" "OK"
}

if ($extraInDest.Count -gt 0) {
    Write-Status "$($extraInDest.Count) extra files in destination" "WARN"
    $results.Issues += "Extra files: $($extraInDest.Count)"
    $results.ExtraFiles = $extraInDest
}

Write-Host ""

# PHASE 3: Spot Check (Size + Optional Hash)
Write-Host "--- PHASE 3: SPOT CHECK VERIFICATION ---" -ForegroundColor Yellow

# Get common files for spot checking
$commonPaths = $srcRelPaths.Keys | Where-Object { $dstRelPaths.ContainsKey($_) }
$sampleSize = [math]::Min($SpotCheckCount, $commonPaths.Count)

if ($sampleSize -gt 0) {
    Write-Status "Selecting $sampleSize random files for verification..."

    $spotCheckFiles = $commonPaths | Get-Random -Count $sampleSize
    $spotCheckResults = @()
    $sizeMismatches = 0
    $hashMismatches = 0
    $passed = 0

    $i = 0
    foreach ($relPath in $spotCheckFiles) {
        $i++
        Write-Progress -Activity "Spot Check" -Status "$i of $sampleSize" -PercentComplete (($i / $sampleSize) * 100)

        $srcFile = $srcRelPaths[$relPath]
        $dstFile = $dstRelPaths[$relPath]

        $check = @{
            Path = $relPath
            SrcSize = $srcFile.Length
            DstSize = $dstFile.Length
            SizeMatch = ($srcFile.Length -eq $dstFile.Length)
            Status = "OK"
        }

        if (-not $check.SizeMatch) {
            $sizeMismatches++
            $check.Status = "SIZE_MISMATCH"
        }
        elseif ($IncludeHashCheck) {
            # Optional: Hash check for critical files
            try {
                $srcHash = (Get-FileHash $srcFile.FullName -Algorithm MD5).Hash
                $dstHash = (Get-FileHash $dstFile.FullName -Algorithm MD5).Hash
                $check.SrcHash = $srcHash
                $check.DstHash = $dstHash
                $check.HashMatch = ($srcHash -eq $dstHash)

                if (-not $check.HashMatch) {
                    $hashMismatches++
                    $check.Status = "HASH_MISMATCH"
                }
            } catch {
                $check.Status = "HASH_ERROR"
            }
        }

        if ($check.Status -eq "OK") { $passed++ }
        $spotCheckResults += $check
    }

    Write-Progress -Activity "Spot Check" -Completed

    Write-Host ""
    Write-Host "  Spot Check Results:" -ForegroundColor Gray
    Write-Host "    Passed:         $passed / $sampleSize"
    Write-Host "    Size Mismatch:  $sizeMismatches"
    if ($IncludeHashCheck) {
        Write-Host "    Hash Mismatch:  $hashMismatches"
    }

    if ($sizeMismatches -gt 0 -or $hashMismatches -gt 0) {
        Write-Status "Some files failed verification" "WARN"
        $results.Issues += "Spot check failures: $($sizeMismatches + $hashMismatches)"
    } else {
        Write-Status "All spot checks passed" "OK"
    }

    $results.SpotChecks = $spotCheckResults
    $results.SpotCheckSummary = @{
        Total = $sampleSize
        Passed = $passed
        SizeMismatches = $sizeMismatches
        HashMismatches = $hashMismatches
    }
} else {
    Write-Status "No common files to spot check" "WARN"
}

Write-Host ""

# FINAL STATUS
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$issueCount = $results.Issues.Count
if ($issueCount -eq 0) {
    $results.Status = "PASSED"
    Write-Host ""
    Write-Host "  STATUS: PASSED" -ForegroundColor Green
    Write-Host "  All checks completed successfully" -ForegroundColor Green
} elseif ($missingInDest.Count -eq 0 -and $sizeMismatches -eq 0) {
    $results.Status = "PASSED_WITH_WARNINGS"
    Write-Host ""
    Write-Host "  STATUS: PASSED WITH WARNINGS" -ForegroundColor Yellow
    Write-Host "  Migration appears complete with minor differences" -ForegroundColor Yellow
} else {
    $results.Status = "FAILED"
    Write-Host ""
    Write-Host "  STATUS: FAILED" -ForegroundColor Red
    Write-Host "  $issueCount issue(s) detected - review required" -ForegroundColor Red
}

Write-Host ""
Write-Host "  Issues Found: $issueCount" -ForegroundColor $(if($issueCount -eq 0){"Green"}else{"Yellow"})
foreach ($issue in $results.Issues) {
    Write-Host "    - $issue" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Export report if requested
if ($ExportReport -ne "") {
    $results | ConvertTo-Json -Depth 5 | Out-File $ExportReport -Encoding UTF8
    Write-Status "Report exported to: $ExportReport" "INFO"
}

# Return exit code for NinjaOne
if ($results.Status -eq "PASSED") {
    exit 0
} elseif ($results.Status -eq "PASSED_WITH_WARNINGS") {
    exit 0
} else {
    exit 1
}
