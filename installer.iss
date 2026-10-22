; Inno Setup script for yadisk-downloader
; Compile: iscc installer.iss [/DBundleDir=dist\windows\yadisk-downloader] [/DMyAppVersion=1.3.0]
; Requires the Windows onedir bundle to exist (python build.py --platform windows).

#ifndef BundleDir
#define BundleDir "dist\windows\yadisk-downloader"
#endif

#ifndef MyAppVersion
#define MyAppVersion "1.3.0"
#endif

#define MyAppName "yadisk-downloader"
#define MyAppExeName "yadisk-downloader.exe"
#define MyAppPublisher "retvil"
#define MyAppURL "https://github.com/retvil/yadisk-downloader"

[Setup]
AppId={{53DAC1DC-88A6-4911-81F6-FA7992B63FD9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=releases
OutputBaseFilename=yadisk-downloader-{#MyAppVersion}-windows-setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BundleDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
