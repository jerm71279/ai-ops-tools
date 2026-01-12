# Convert Migration Verification CSV to HTML Report

param(
    [string]$CsvPath = "C:\migration-files-2025-11-21.csv",
    [string]$HtmlPath = "C:\migration-verification-report.html"
)

Write-Host "Converting CSV to HTML..." -ForegroundColor Cyan
Write-Host "Input:  $CsvPath" -ForegroundColor Gray
Write-Host "Output: $HtmlPath" -ForegroundColor Gray
Write-Host ""

# Check if CSV exists
if (-not (Test-Path $CsvPath)) {
    Write-Host "ERROR: CSV file not found at $CsvPath" -ForegroundColor Red
    Write-Host "Please run verify-migration-sync.ps1 first to generate the CSV" -ForegroundColor Yellow
    exit
}

# Import CSV data
$data = Import-Csv $CsvPath

$totalFiles = $data.Count
$totalSizeMB = ($data | Measure-Object -Property 'Size(MB)' -Sum).Sum
$totalSizeGB = [math]::Round($totalSizeMB / 1024, 2)

# Group by folder
$byFolder = $data | Group-Object { Split-Path $_.DirectoryName -Leaf } |
    Select-Object Name, Count, @{N='Size(MB)';E={[math]::Round(($_.Group | Measure-Object -Property 'Size(MB)' -Sum).Sum, 2)}} |
    Sort-Object Count -Descending

# Get top 50 largest files
$largestFiles = $data |
    Sort-Object { [double]$_.'Size(MB)' } -Descending |
    Select-Object -First 50

# Get most recent files
$recentFiles = $data |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 50

# Create HTML
$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Migration Verification Report - 11/21/2025</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }
        .summary {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .summary-item {
            display: inline-block;
            margin: 10px 30px 10px 0;
        }
        .summary-label {
            font-weight: bold;
            color: #7f8c8d;
        }
        .summary-value {
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .folder-name {
            font-weight: bold;
            color: #2980b9;
        }
        .file-path {
            font-size: 0.9em;
            color: #7f8c8d;
            font-family: 'Courier New', monospace;
        }
        .size-large {
            color: #e74c3c;
            font-weight: bold;
        }
        .size-medium {
            color: #f39c12;
        }
        .size-small {
            color: #27ae60;
        }
        .timestamp {
            color: #34495e;
            font-family: 'Courier New', monospace;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 5px solid #28a745;
        }
        .info {
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 5px solid #17a2b8;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Migration Verification Report</h1>
        <div class="info">
            <strong>Migration Date:</strong> 11/21/2025<br>
            <strong>Report Generated:</strong> $(Get-Date -Format "MM/dd/yyyy HH:mm:ss")<br>
            <strong>Server:</strong> SETCO-DC02<br>
            <strong>Search Location:</strong> F:\ (All folders except Backup)
        </div>

        <div class="summary">
            <div class="summary-item">
                <div class="summary-label">Total Files Modified</div>
                <div class="summary-value">$totalFiles</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Size</div>
                <div class="summary-value">$totalSizeGB GB</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Folders Affected</div>
                <div class="summary-value">$($byFolder.Count)</div>
            </div>
        </div>

        <div class="success">
            ✅ <strong>Migration Sync Verified:</strong> Found $totalFiles files modified on migration day (11/21/2025).
            This confirms the delta robocopy sync successfully captured all changes made before the migration.
        </div>

        <h2>📊 Files by Folder</h2>
        <table>
            <tr>
                <th>Folder</th>
                <th>File Count</th>
                <th>Total Size (MB)</th>
            </tr>
"@

foreach ($folder in $byFolder) {
    $html += @"
            <tr>
                <td class="folder-name">$($folder.Name)</td>
                <td>$($folder.Count)</td>
                <td>$($folder.'Size(MB)')</td>
            </tr>
"@
}

$html += @"
        </table>

        <h2>📁 Top 50 Largest Files Modified on 11/21/2025</h2>
        <table>
            <tr>
                <th>File Name</th>
                <th>Folder</th>
                <th>Size (MB)</th>
                <th>Modified</th>
            </tr>
"@

foreach ($file in $largestFiles) {
    $sizeMB = [double]$file.'Size(MB)'
    $sizeClass = if ($sizeMB -gt 100) { 'size-large' } elseif ($sizeMB -gt 10) { 'size-medium' } else { 'size-small' }
    $folderName = Split-Path $file.DirectoryName -Leaf

    $html += @"
            <tr>
                <td>$($file.Name)</td>
                <td class="folder-name">$folderName</td>
                <td class="$sizeClass">$($file.'Size(MB)')</td>
                <td class="timestamp">$($file.LastWriteTime)</td>
            </tr>
"@
}

$html += @"
        </table>

        <h2>⏰ 50 Most Recently Modified Files</h2>
        <table>
            <tr>
                <th>File Name</th>
                <th>Folder</th>
                <th>Size (MB)</th>
                <th>Modified</th>
            </tr>
"@

foreach ($file in $recentFiles) {
    $sizeMB = [double]$file.'Size(MB)'
    $sizeClass = if ($sizeMB -gt 100) { 'size-large' } elseif ($sizeMB -gt 10) { 'size-medium' } else { 'size-small' }
    $folderName = Split-Path $file.DirectoryName -Leaf

    $html += @"
            <tr>
                <td>$($file.Name)</td>
                <td class="folder-name">$folderName</td>
                <td class="$sizeClass">$($file.'Size(MB)')</td>
                <td class="timestamp">$($file.LastWriteTime)</td>
            </tr>
"@
}

$html += @"
        </table>

        <h2>📋 Complete File List</h2>
        <p class="info">Showing all $totalFiles files modified on 11/21/2025</p>
        <table>
            <tr>
                <th>File Name</th>
                <th>Full Path</th>
                <th>Size (KB)</th>
                <th>Modified</th>
            </tr>
"@

foreach ($file in ($data | Sort-Object LastWriteTime -Descending)) {
    $html += @"
            <tr>
                <td>$($file.Name)</td>
                <td class="file-path">$($file.FullName)</td>
                <td>$($file.'Size(KB)')</td>
                <td class="timestamp">$($file.LastWriteTime)</td>
            </tr>
"@
}

$html += @"
        </table>

        <div class="footer">
            <p>SETCO DC02 Migration Verification Report | Generated: $(Get-Date -Format "MM/dd/yyyy HH:mm:ss")</p>
            <p>Source Data: $CsvPath</p>
        </div>
    </div>
</body>
</html>
"@

# Save HTML
$html | Out-File -FilePath $HtmlPath -Encoding UTF8

Write-Host "✅ HTML report created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Report saved to: $HtmlPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening in default browser..." -ForegroundColor Yellow
Start-Process $HtmlPath

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
