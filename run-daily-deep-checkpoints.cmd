@echo off
setlocal

set "REPO_ROOT=C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit"
set "CHECKPOINT_ROOT=D:\relay-kit-checkpoint"
set "TEMP_ROOT=D:\relay-kit-temp"

if not exist "%CHECKPOINT_ROOT%" mkdir "%CHECKPOINT_ROOT%"
if not exist "%TEMP_ROOT%" mkdir "%TEMP_ROOT%"

set "TEMP=%TEMP_ROOT%"
set "TMP=%TEMP_ROOT%"

cd /d "%REPO_ROOT%"
py -3.12 scripts\startup_deep_checkpoint.py --count 5 --gap-sec 10 --output-root "%CHECKPOINT_ROOT%" --temp-root "%TEMP_ROOT%"

endlocal
