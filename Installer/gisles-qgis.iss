; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "������ ��� QGIS"
#define MyAppVersion "1.0"
#define MyAppPublisher "RUE Belgosles"
#define MyAppURL "https://belgosles.by"
#define MyAppExeName "GisLes.exe"
#define PsqlPass "loo98Yt5"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{771766A0-DD45-4B93-9E19-2C437DA7C706}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
CreateAppDir=no
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputDir=C:\Users\omelchuk-ev\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\trial_area\Installer
OutputBaseFilename=GisLes-for-QGIS
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: ".\vc_redist.x64.exe"; DestDir: {tmp}; Flags: dontcopy
Source: ".\QGIS-OSGeo4W-3.10.11-2-Setup-x86_64.exe"; DestDir: {tmp}
Source: ".\postgresql-13.2-1-windows-x64.exe"; DestDir: {tmp}
Source: ".\postgis-bundle-pg13x64-setup-3.1.1-2.exe"; DestDir: {tmp}
Source: ".\qgis-ltr-bin.env"; DestDir: "C:/Program Files/QGIS 3.10/bin/"
Source: ".\trial_area.zip"; DestDir: {tmp}
Source: ".\unzip.exe"; DestDir: {tmp}

[Tasks]
Name: postgresql; Description: "���������� PostgreSQL ��������"; Flags: unchecked

[Run]   
Filename: "{tmp}\vc_redist.x64.exe"; StatusMsg: "��������� VC Redist 2015"; \
  Parameters: "/q /norestart"; Check: VC2017RedistNeedsInstall ; Flags: waituntilterminated
 
Filename: "{tmp}\QGIS-OSGeo4W-3.10.11-2-Setup-x86_64.exe"; StatusMsg: "��������� QGIS Desktop"; \
  Parameters: "/S"; Flags: waituntilterminated

Filename: "{tmp}\postgresql-13.2-1-windows-x64.exe"; StatusMsg: "��������� PostgreSQL"; \
  Parameters: " --mode unattended --unattendedmodeui none --superpassword {#PsqlPass}"; Flags: waituntilterminated; Tasks: postgresql

Filename: "{tmp}\postgis-bundle-pg13x64-setup-3.1.1-2.exe"; StatusMsg: "��������� PostGis"; \
  Parameters: "/S"; Flags: waituntilterminated; Tasks: postgresql
  
Filename: "{tmp}\unzip.exe"; StatusMsg: "��������� �������"; \
  Parameters: "-qq {tmp}\trial_area.zip -d {%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins"; \
  Flags: waituntilterminated

[Code]
function VC2017RedistNeedsInstall: Boolean;
var 
  Version: String;
begin
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
       'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Version', Version) then
  begin
    // Is the installed version at least 14.14 ? 
    Log('VC Redist Version check : found ' + Version);
    Result := (CompareStr(Version, 'v14.14.26429.03')<0);
  end
  else 
  begin
    // Not even an old version installed
    Result := True;
  end;
  if (Result) then
  begin
    ExtractTemporaryFile('vc_redist.x64.exe');
  end;
end;

[Dirs]
Name: "{%USERPROFILE}\AppData\Roaming"
Name: "{%USERPROFILE}\AppData\Roaming\QGIS"
Name: "{%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\"
Name: "{%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\profiles"
Name: "{%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\profiles\default"
Name: "{%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\profiles\default\python"
Name: "{%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins"

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

