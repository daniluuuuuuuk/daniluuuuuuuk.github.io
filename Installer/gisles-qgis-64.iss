; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "������ ��� QGIS"
#define MyAppVersion "1.0"
#define MyAppPublisher "RUE Belgosles"
#define MyAppURL "https://belgosles.by"
#define MyAppExeName "GisLes.exe"

#define architecture "x64"

#define vc_redist_file "vc_redist.x64.exe"
#define QGIS_setup_file "QGIS-OSGeo4W-3.10.11-2-Setup-x86_64.exe"
#define postgresql_file "postgresql-13.2-1-windows-x64.exe"
#define postgis_file "postgis-bundle-pg13x64-setup-3.1.1-2.exe"
#define module_file "trial_area_x64.zip"
#define dbeaver_file "dbeaver-ce-21.0.1-x86_64-setup.exe"

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
PrivilegesRequiredOverridesAllowed=commandline
OutputDir=C:\Users\omelchuk-ev\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\trial_area\Installer
OutputBaseFilename="GisLes-for-QGIS-{#architecture}"
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
WizardImageFile=logo.bmp

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Messages]
WelcomeLabel2=����������� ����������� ��� ������ � �������� �������� ������� ����� ������ ��� QGIS ��������������� ��� ������������� ��������� ����������� ������ �������� ������� ����� � �������� ��������. ��������� ������� �����, �����, �������������� � �������� ������.

[Files]
Source: ".\{#vc_redist_file}"; DestDir: {tmp}; Flags: dontcopy
Source: ".\{#QGIS_setup_file}"; DestDir: {tmp}
Source: ".\{#postgresql_file}"; DestDir: {tmp}
Source: ".\{#postgis_file}"; DestDir: {tmp}
Source: ".\qgis-ltr-bin.env"; DestDir: "C:/Program Files/QGIS 3.10/bin/"
Source: ".\{#module_file}"; DestDir: {tmp}
Source: ".\unzip.exe"; DestDir: {tmp}
Source: ".\{#dbeaver_file}"; DestDir: {tmp}
Source: "logo.bmp"; DestDir: "{app}"; Flags: dontcopy

[Tasks]
Name: qgis; Description: "��������� QGIS Desktop"
Name: module; Description: "��������� ������ ������ ��� QGIS"
Name: postgresql; Description: "��������� PostgreSQL ��������"
Name: dbeaver; Description: "��������� ������� �� DBeaver CE"; Flags: unchecked

[Run]   
Filename: "{tmp}\{#vc_redist_file}"; StatusMsg: "��������� VC Redist 2015"; \
  Parameters: "/q /norestart"; Check: VC2015RedistNeedsInstall ; Flags: waituntilterminated
 
Filename: "{tmp}\{#QGIS_setup_file}"; StatusMsg: "�������� QGIS Desktop"; \
  Parameters: "/S"; Flags: waituntilterminated;  Tasks: qgis

Filename: "{tmp}\{#postgresql_file}"; StatusMsg: "��������� PostgreSQL"; \
  Parameters: " --mode unattended --unattendedmodeui none --superpassword {#PsqlPass}"; Flags: waituntilterminated; Tasks: postgresql

Filename: "{tmp}\{#postgis_file}"; StatusMsg: "��������� PostGis"; \
  Parameters: "/S"; Flags: waituntilterminated; Tasks: postgresql
  
Filename: "{tmp}\unzip.exe"; StatusMsg: "��������� ������ ������ ��� QGIS"; \
  Parameters: "-qq {tmp}\{#module_file} -d {%USERPROFILE}\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins"; \
  Flags: waituntilterminated; Tasks: module

Filename: "{tmp}\{#dbeaver_file}"; StatusMsg: "��������� DBeaver"; \
  Parameters: " /allusers /S"; \
  Flags: waituntilterminated; Tasks: dbeaver

[Code]
function VC2015RedistNeedsInstall: Boolean;
var 
  Version: String;
begin
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
       'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\{#architecture}', 'Version', Version) then
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
    ExtractTemporaryFile('{#vc_redist_file}');
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


