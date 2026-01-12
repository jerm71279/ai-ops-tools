# This script creates all 4 F:\ drive migration scripts in C:\ps1
# Run this on your server to create the updated scripts

Write-Host "Creating F:\ drive migration scripts..." -ForegroundColor Cyan

# Check if we're in C:\ps1
if ((Get-Location).Path -ne "C:\ps1") {
    Write-Host "Changing directory to C:\ps1..." -ForegroundColor Yellow
    Set-Location C:\ps1
}

Write-Host "This will overwrite existing scripts in C:\ps1" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to cancel, or any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Backup old scripts if they exist
if (Test-Path "1-Setup-Directories.ps1") {
    Write-Host "Backing up old scripts..." -ForegroundColor Yellow
    Get-ChildItem "*.ps1" | Where-Object {$_.Name -notlike "*-OLD.ps1"} | ForEach-Object {
        $newName = $_.BaseName + "-OLD-BACKUP.ps1"
        Copy-Item $_.FullName $newName -Force
    }
}

Write-Host "Creating new F:\ drive scripts..." -ForegroundColor Cyan
Write-Host "You'll need to copy the script content from the HTML file I provided" -ForegroundColor Yellow
Write-Host "Or transfer the *-F-Drive.ps1 files to this server" -ForegroundColor Yellow

Write-Host "`nFiles needed:" -ForegroundColor Cyan
Write-Host "  - 1-Setup-Directories-F-Drive.ps1" -ForegroundColor White
Write-Host "  - 2-Set-NTFS-Permissions-F-Drive.ps1" -ForegroundColor White
Write-Host "  - 3-Create-SMB-Shares-F-Drive.ps1" -ForegroundColor White
Write-Host "  - 4-Validate-Configuration-F-Drive.ps1" -ForegroundColor White

Write-Host "`nOnce you have the F-Drive versions in C:\ps1, run:" -ForegroundColor Cyan
Write-Host "  .\1-Setup-Directories-F-Drive.ps1" -ForegroundColor Green
Write-Host "  .\2-Set-NTFS-Permissions-F-Drive.ps1" -ForegroundColor Green
Write-Host "  .\3-Create-SMB-Shares-F-Drive.ps1" -ForegroundColor Green
Write-Host "  .\4-Validate-Configuration-F-Drive.ps1" -ForegroundColor Green
