rem build the standalone Dronekit.exe for Windows.
rem This assumes Python2 is installed in C:\Python27
rem This assumes Inno Setup 5 is installed in C:\Program Files (x86)\Inno Setup 5
SETLOCAL enableextensions

rem get the version
for /f "tokens=*" %%a in (
 'python returnVersion.py'
 ) do (
 set VERSION=%%a
 )

rem -----Build the Installer-----
"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" /dMyAppVersion=%VERSION% dronekit_installer.iss
