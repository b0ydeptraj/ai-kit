@echo off
setlocal
cd /d "%~dp0"

echo [Relay-kit] Dang cap nhat bao cao tuong thich...
python scripts\summarize_compat_cycle.py --checkpoint
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
  echo Hoan tat. Da cap nhat:
  echo   C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\docs\relay-kit-compatibility-log.md
) else (
  echo Co loi khi cap nhat checkpoint. Ma loi: %EXIT_CODE%
)

echo.
pause
exit /b %EXIT_CODE%
