@echo off
setlocal
cd /d "%~dp0"

echo [Relay-kit] Dang cap nhat phan tong hop...
python scripts\summarize_compat_cycle.py --write-summary
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
  echo Hoan tat. Da cap nhat phan tong hop trong:
  echo   C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\docs\relay-kit-compatibility-log.md
) else (
  echo Co loi khi cap nhat tong hop. Ma loi: %EXIT_CODE%
)

echo.
pause
exit /b %EXIT_CODE%
