@echo off
rem houdini launcher 

rem source global vars
call ../globals.bat

rem set Houdini paths
set "HOUDINI_VERSION=Houdini 15.5.632"
rem set "HOUDINI_OTLSCAN_PATH=@/otls;%PIPELINE%/houdini/otls;&"
rem set "HOUDINI_TOOLBAR_PATH=%PIPELINE%/houdini/toolbar;&"
rem set "HOUDINI_SCRIPT_PATH=&;%PIPELINE%/houdini/scripts;"
set "HOUDINI_PATH=&;%PIPELINE%/houdini"
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
set "MEGASCANS=%JOB%/20_assets/10_megascans/Megascans/"
set "MEGASCANS=%MEGASCANS:\=/%"

rem create temp dir for houdini user if it does not exist, also convert to forwardslashes
set "TMP=%HOUDINI_TEMP_DIR%"
set "TMP=%TMP:/=\%"
IF not exist %TMP% (mkdir %TMP%)

rem run Houdini
set "HOUDINI_DIR=C:\Program Files\Side Effects Software\%HOUDINI_VERSION%\bin"
set "PATH=%HOUDINI_DIR%;%PATH%"
cd ../../
start houdinifx