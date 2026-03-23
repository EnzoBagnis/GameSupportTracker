; ============================================================================
; Inno Setup Script for Game Support Tracker
; ============================================================================
; Prerequisites: Install Inno Setup from https://jrsoftware.org/isinfo.php
;
; To compile the installer:
;   1. Open this file in Inno Setup Compiler
;   2. Click "Compile" (Ctrl+F9)
;   OR via command line:
;      "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
; ============================================================================

#define MyAppName "Game Support Tracker"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "IUTlago"
#define MyAppExeName "main.exe"
#define MyAppURL "https://github.com/EnzoB/GameSupportTracker"

[Setup]
; Unique application identifier (do not change after first release)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; No program folder selection page if unnecessary
AllowNoIcons=yes
; Installer output folder
OutputDir=dist
OutputBaseFilename=GameSupportTrackerSetup
; Installer icon
SetupIconFile=logo.ico
; Maximum compression
Compression=lzma2/ultra64
SolidCompression=yes
; Modern style
WizardStyle=modern
; Privileges: installation possible without admin (in AppData)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Uninstall info
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
; Minimum Windows version
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable
Source: "dist\main.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

; Icon (uncomment if logo.ico exists)
; Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent