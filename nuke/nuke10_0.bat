@echo off
rem nuke launcher 

rem set Nuke version
set "NUKE_VERSION=Nuke10.0v5"

call \\bigfoot\jellyfish\00_pipeline\nuke\nuke.bat

start Nuke10.0.exe --nukex