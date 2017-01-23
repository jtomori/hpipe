@echo off
rem houdini launcher 

rem source global vars
call \\bigfoot\jellyfish\00_pipeline\globals.bat

rem set Houdini paths
set "HOUDINI_VERSION=Houdini 15.5.632"
set "HOUDINI_PATH=&;%PIPELINE%/houdini"
set "HOUDINI_OTLSCAN_PATH=&;%ROOT%/20_assets/otls"
set "HOUDINI_SPLASH_FILE=%PIPELINE%/houdini/splash.jpg"
set "HOUDINI_SPLASH_MESSAGE= | JELLY FISH | %HOUDINI_VERSION% | %USERNAME% |"
set "JOB=%ROOT%"
set "HOUDINI_BACKUP_FILENAME=$BASENAME_bak_$N"
set "HOUDINI_BACKUP_DIR=bak"
set "HOUDINI_NO_START_PAGE_SPLASH=1"
set "HOUDINI_ANONYMOUS_STATISTICS=0"
set "HOME=%ROOT%/05_user/%USERNAME%"
set "HOUDINI_DESK_PATH=&;C:/Users/%USERNAME%/Documents/houdini15.5/desktop"
set "HOUDINI_TEMP_DIR=%HOME%/tmp"
set "HOUDINI_BUFFERED_SAVE=1"
set "MEGASCANS=%JOB%/20_assets/megascans/Megascans/"
set "MEGASCANS3D=%MEGASCANS%3d/"
set "MEGASCANS=%MEGASCANS:\=/%"
set "MEGASCANS3D=%MEGASCANS3D:\=/%"

rem run Houdini
set "HOUDINI_DIR=C:\Program Files\Side Effects Software\%HOUDINI_VERSION%\bin"
set "PATH=%HOUDINI_DIR%;%PATH%"