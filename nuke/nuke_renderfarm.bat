@echo off
rem nuke launcher 

rem source global vars
call \\bigfoot\jellyfish\00_pipeline\globals.bat

rem set Nuke paths
set "NUKE_PATH=%PIPELINE%/nuke"
set "NUKE_PATH=%NUKE_PATH:\=/%"
set "HOME=%ROOT%/05_user/%USERNAME%"