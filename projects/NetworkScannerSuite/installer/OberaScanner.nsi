; Obera Network Scanner Installer
; NSIS Installer Script
; Build with: makensis OberaScanner.nsi

!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; General
Name "Obera Network Scanner"
OutFile "OberaNetworkScanner-Setup.exe"
InstallDir "$PROGRAMFILES\OberaTools\NetworkScanner"
InstallDirRegKey HKLM "Software\OberaTools\NetworkScanner" "InstallPath"
RequestExecutionLevel admin

; Version Info
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Obera Network Scanner"
VIAddVersionKey "CompanyName" "Obera Technologies"
VIAddVersionKey "FileDescription" "Network Scanner Installation"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"
VIAddVersionKey "LegalCopyright" "Copyright (c) 2024 Obera Technologies"

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "assets\obera-icon.ico"
!define MUI_UNICON "assets\obera-icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\welcome.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "assets\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Variables
Var WebPort
Var ServiceName

; Installer Sections
Section "Main Application" SecMain
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Copy service files
    SetOutPath "$INSTDIR\service"
    File /r "..\service\*.*"

    ; Copy web UI
    SetOutPath "$INSTDIR\web-ui"
    File /r "..\web-ui\*.*"

    ; Copy Python embedded
    SetOutPath "$INSTDIR\python"
    File /r "python-embedded\*.*"

    ; Enable pip in embedded Python
    FileOpen $0 "$INSTDIR\python\python311._pth" a
    FileSeek $0 0 END
    FileWrite $0 "$\r$\nimport site$\r$\n"
    FileClose $0

    ; Install pip
    nsExec::ExecToLog '"$INSTDIR\python\python.exe" "$INSTDIR\python\get-pip.py"'

    ; Install Python dependencies
    nsExec::ExecToLog '"$INSTDIR\python\python.exe" -m pip install -r "$INSTDIR\service\requirements.txt" --no-warn-script-location'

    ; Create scans directory
    CreateDirectory "$INSTDIR\service\scans"

    ; Write configuration file
    SetOutPath "$INSTDIR"
    FileOpen $0 "$INSTDIR\config.ini" w
    FileWrite $0 "[service]$\r$\n"
    FileWrite $0 "port=8080$\r$\n"
    FileWrite $0 "host=0.0.0.0$\r$\n"
    FileWrite $0 "$\r$\n[paths]$\r$\n"
    FileWrite $0 "scans_dir=$INSTDIR\service\scans$\r$\n"
    FileWrite $0 "nmap_path=$INSTDIR\nmap\nmap.exe$\r$\n"
    FileClose $0

    ; Create start script
    FileOpen $0 "$INSTDIR\start_scanner.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 "cd /d $\"$INSTDIR\service$\"$\r$\n"
    FileWrite $0 "$\"$INSTDIR\python\python.exe$\" scanner_service.py$\r$\n"
    FileClose $0

    ; Create stop script
    FileOpen $0 "$INSTDIR\stop_scanner.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 "taskkill /F /IM python.exe /FI $\"WINDOWTITLE eq Obera*$\"$\r$\n"
    FileClose $0

    ; Write registry keys
    WriteRegStr HKLM "Software\OberaTools\NetworkScanner" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\OberaTools\NetworkScanner" "Version" "1.0.0"

    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Add to Programs and Features
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                     "DisplayName" "Obera Network Scanner"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                     "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                     "DisplayIcon" "$INSTDIR\assets\obera-icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                     "Publisher" "Obera Technologies"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                     "DisplayVersion" "1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                      "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                      "NoRepair" 1

    ; Calculate installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner" \
                      "EstimatedSize" "$0"
SectionEnd

Section "Nmap" SecNmap
    SetOutPath "$INSTDIR\nmap"

    ; Check if Nmap files are included
    IfFileExists "nmap\nmap.exe" 0 DownloadNmap
        File /r "nmap\*.*"
        Goto NmapDone

    DownloadNmap:
        ; Download Nmap if not bundled
        DetailPrint "Downloading Nmap..."
        NSISdl::download "https://nmap.org/dist/nmap-7.94-win32.zip" "$TEMP\nmap.zip"
        Pop $R0
        StrCmp $R0 "success" +3
            MessageBox MB_OK "Nmap download failed: $R0"
            Abort

        ; Extract Nmap
        DetailPrint "Extracting Nmap..."
        nsisunz::Unzip "$TEMP\nmap.zip" "$INSTDIR"

        ; Rename extracted folder
        Rename "$INSTDIR\nmap-7.94" "$INSTDIR\nmap"
        Delete "$TEMP\nmap.zip"

    NmapDone:
        ; Add Nmap to system PATH
        EnVar::AddValue "PATH" "$INSTDIR\nmap"
SectionEnd

Section "Create Windows Service" SecService
    ; Create scheduled task for auto-start
    DetailPrint "Creating Windows service..."

    ; Create task XML
    FileOpen $0 "$TEMP\scanner_task.xml" w
    FileWrite $0 '<?xml version="1.0" encoding="UTF-16"?>$\r$\n'
    FileWrite $0 '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">$\r$\n'
    FileWrite $0 '  <RegistrationInfo>$\r$\n'
    FileWrite $0 '    <Description>Obera Network Scanner Service</Description>$\r$\n'
    FileWrite $0 '  </RegistrationInfo>$\r$\n'
    FileWrite $0 '  <Triggers>$\r$\n'
    FileWrite $0 '    <BootTrigger>$\r$\n'
    FileWrite $0 '      <Enabled>true</Enabled>$\r$\n'
    FileWrite $0 '    </BootTrigger>$\r$\n'
    FileWrite $0 '  </Triggers>$\r$\n'
    FileWrite $0 '  <Principals>$\r$\n'
    FileWrite $0 '    <Principal id="Author">$\r$\n'
    FileWrite $0 '      <UserId>S-1-5-18</UserId>$\r$\n'
    FileWrite $0 '      <RunLevel>HighestAvailable</RunLevel>$\r$\n'
    FileWrite $0 '    </Principal>$\r$\n'
    FileWrite $0 '  </Principals>$\r$\n'
    FileWrite $0 '  <Settings>$\r$\n'
    FileWrite $0 '    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>$\r$\n'
    FileWrite $0 '    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>$\r$\n'
    FileWrite $0 '    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>$\r$\n'
    FileWrite $0 '    <AllowHardTerminate>true</AllowHardTerminate>$\r$\n'
    FileWrite $0 '    <StartWhenAvailable>true</StartWhenAvailable>$\r$\n'
    FileWrite $0 '    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>$\r$\n'
    FileWrite $0 '    <AllowStartOnDemand>true</AllowStartOnDemand>$\r$\n'
    FileWrite $0 '    <Enabled>true</Enabled>$\r$\n'
    FileWrite $0 '    <Hidden>false</Hidden>$\r$\n'
    FileWrite $0 '    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>$\r$\n'
    FileWrite $0 '    <Priority>7</Priority>$\r$\n'
    FileWrite $0 '  </Settings>$\r$\n'
    FileWrite $0 '  <Actions Context="Author">$\r$\n'
    FileWrite $0 '    <Exec>$\r$\n'
    FileWrite $0 '      <Command>$INSTDIR\start_scanner.bat</Command>$\r$\n'
    FileWrite $0 '      <WorkingDirectory>$INSTDIR\service</WorkingDirectory>$\r$\n'
    FileWrite $0 '    </Exec>$\r$\n'
    FileWrite $0 '  </Actions>$\r$\n'
    FileWrite $0 '</Task>$\r$\n'
    FileClose $0

    ; Register scheduled task
    nsExec::ExecToLog 'schtasks /Create /TN "OberaNetworkScanner" /XML "$TEMP\scanner_task.xml" /F'
    Delete "$TEMP\scanner_task.xml"

    ; Configure firewall
    DetailPrint "Configuring firewall..."
    nsExec::ExecToLog 'netsh advfirewall firewall add rule name="Obera Network Scanner" dir=in action=allow protocol=TCP localport=8080'
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\Obera Network Scanner.lnk" \
                   "http://localhost:8080" \
                   "" \
                   "$INSTDIR\assets\obera-icon.ico" \
                   0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\Obera Tools"
    CreateShortCut "$SMPROGRAMS\Obera Tools\Network Scanner.lnk" \
                   "http://localhost:8080" \
                   "" \
                   "$INSTDIR\assets\obera-icon.ico" \
                   0
    CreateShortCut "$SMPROGRAMS\Obera Tools\Start Scanner Service.lnk" \
                   "$INSTDIR\start_scanner.bat" \
                   "" \
                   "$INSTDIR\assets\obera-icon.ico" \
                   0
    CreateShortCut "$SMPROGRAMS\Obera Tools\Stop Scanner Service.lnk" \
                   "$INSTDIR\stop_scanner.bat" \
                   "" \
                   "$INSTDIR\assets\obera-icon.ico" \
                   0
    CreateShortCut "$SMPROGRAMS\Obera Tools\Uninstall.lnk" \
                   "$INSTDIR\Uninstall.exe"
SectionEnd

; Post-install actions
Section "-PostInstall"
    ; Start the service
    DetailPrint "Starting scanner service..."
    nsExec::ExecToLog 'schtasks /Run /TN "OberaNetworkScanner"'

    ; Wait for service to start
    Sleep 3000

    ; Open browser to scanner
    ExecShell "open" "http://localhost:8080"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Stop and remove service
    nsExec::ExecToLog 'schtasks /End /TN "OberaNetworkScanner"'
    nsExec::ExecToLog 'schtasks /Delete /TN "OberaNetworkScanner" /F'

    ; Remove firewall rule
    nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="Obera Network Scanner"'

    ; Remove from PATH
    EnVar::DeleteValue "PATH" "$INSTDIR\nmap"

    ; Remove files
    RMDir /r "$INSTDIR\service"
    RMDir /r "$INSTDIR\web-ui"
    RMDir /r "$INSTDIR\python"
    RMDir /r "$INSTDIR\nmap"
    RMDir /r "$INSTDIR\assets"
    Delete "$INSTDIR\config.ini"
    Delete "$INSTDIR\start_scanner.bat"
    Delete "$INSTDIR\stop_scanner.bat"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\Obera Network Scanner.lnk"
    RMDir /r "$SMPROGRAMS\Obera Tools"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\OberaTools\NetworkScanner"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OberaNetworkScanner"
SectionEnd

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecNmap} "Nmap network scanner (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecService} "Install as Windows service (recommended)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create desktop shortcut"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create Start Menu shortcuts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END
