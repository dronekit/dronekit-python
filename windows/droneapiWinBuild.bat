rem build the standalone Dronekit.exe for Windows.
rem This assumes Python is installed in C:\Python27
SETLOCAL enableextensions

rem get the version
for /f "tokens=*" %%a in (
 'python returnVersion.py'
 ) do (
 set VERSION=%%a
 )

rem -----Get protobuf and unzip-----
C:\python27\scripts\pip.exe install --download .\ protobuf
rem get the protobuf fullname
for /f "tokens=*" %%a in (
 'dir /B protobuf-*'
 ) do (
 set PROTOBUFFULL=%%a
 )

rem Use 7zip to unzip files. Works for both 32 and 64 bit versions
"C:\Program Files\7-zip\7z.exe" x -y %PROTOBUFFULL%
"C:\Program Files\7-zip\7z.exe" x -y .\dist\protobuf*
"C:\Program Files (x86)\7-zip\7z.exe" x -y %PROTOBUFFULL%
"C:\Program Files (x86)\7-zip\7z.exe" x -y .\dist\protobuf*

rem get the protobuf fullname
for /f "tokens=*" %%a in (
 'dir /A:D /B protobuf-*'
 ) do (
 set PROTOBUFDIR=%%a
 )
xcopy /E /Y %PROTOBUFDIR%\google .\google\


rem -----Build the Installer-----
"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" /dMyAppVersion=%VERSION% dronekit_installer.iss
