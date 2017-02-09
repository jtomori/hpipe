@echo off
rem nuke launcher 

rem source global vars
call \\bigfoot\jellyfish\00_pipeline\globals.bat

rem set Nuke paths
set "NUKE_VERSION=Nuke10.5v1"
set "NUKE_PATH=%PIPELINE%/nuke"
set "NUKE_PATH=%NUKE_PATH:\=/%"
set "HOME=%ROOT%/05_user/%USERNAME%"

rem run Nuke
set "NUKE_DIR=C:\Program Files\%NUKE_VERSION%\"
set "PATH=%NUKE_DIR%;%PATH%"
cd ../../
start Nuke10.5.exe --nukex