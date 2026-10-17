#define AppVersion "1.0.0"
[Setup]
AppId={{4083FC7B-04CD-4A51-9D30-A56B828C1E64}
AppName=FolderLister
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\FolderLister
DefaultGroupName=FolderLister
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\..\dist
OutputBaseFilename=FolderLister-{#AppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\FolderLister.exe
[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked
[Files]
Source: "..\..\dist\FolderLister.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\THIRD_PARTY_NOTICES\*"; DestDir: "{app}\THIRD_PARTY_NOTICES"; Flags: recursesubdirs createallsubdirs
Source: "..\..\README.md"; DestDir: "{app}"
Source: "..\..\LICENSE.template"; DestDir: "{app}"
[Icons]
Name: "{group}\FolderLister"; Filename: "{app}\FolderLister.exe"
Name: "{autodesktop}\FolderLister"; Filename: "{app}\FolderLister.exe"; Tasks: desktopicon
