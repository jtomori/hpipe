@echo off
rem nuke launcher 

rem set Nuke version
set "NUKE_VERSION=Nuke10.5v1"

call \\bigfoot\jellyfish\00_pipeline\nuke\nuke.bat

start Nuke10.5.exe --nukex