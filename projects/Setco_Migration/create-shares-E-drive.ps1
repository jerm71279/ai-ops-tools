# Create all shares on E: drive
# Run this ON SETCO-DC02 as Domain Administrator

Write-Host "Creating E: drive shares..." -ForegroundColor Cyan

New-SmbShare -Name "E" -Path "E:\" -ReadAccess "Everyone" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] E" -ForegroundColor Green

New-SmbShare -Name "FTP Data" -Path "E:\FTP Data" -FullAccess "Everyone"
Write-Host "[OK] FTP Data" -ForegroundColor Green

New-SmbShare -Name "HomeDirs" -Path "E:\HomeDirs" -ReadAccess "Domain Users" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] HomeDirs" -ForegroundColor Green

New-SmbShare -Name "Legal" -Path "E:\HomeDirs\Legal" -ReadAccess "Domain Users" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] Legal" -ForegroundColor Green

New-SmbShare -Name "PostClosing" -Path "E:\PostClosing" -ReadAccess "Domain Users" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] PostClosing" -ForegroundColor Green

New-SmbShare -Name "Qbooks" -Path "E:\Qbooks" -ReadAccess "Domain Users" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] Qbooks" -ForegroundColor Green

New-SmbShare -Name "SeaCrestScans" -Path "E:\SeaCrestScans" -FullAccess "Everyone"
Write-Host "[OK] SeaCrestScans" -ForegroundColor Green

New-SmbShare -Name "SetcoDocs" -Path "E:\SetcoDocs" -FullAccess "Everyone"
Write-Host "[OK] SetcoDocs" -ForegroundColor Green

New-SmbShare -Name "Versacheck" -Path "E:\Versacheck" -ReadAccess "Domain Users" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] Versacheck" -ForegroundColor Green

New-SmbShare -Name "Whole Life Fitness" -Path "E:\Whole Life Fitness" -ReadAccess "Domain Users" -FullAccess "Domain Admins","Administrators"
Write-Host "[OK] Whole Life Fitness" -ForegroundColor Green

New-SmbShare -Name "worddocs" -Path "E:\NTSYS\worddocs" -FullAccess "Everyone"
Write-Host "[OK] worddocs" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying shares..." -ForegroundColor Yellow
Get-SmbShare | Where-Object {$_.Path -like 'E:*'} | Format-Table Name, Path -AutoSize
