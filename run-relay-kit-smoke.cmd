@echo off
setlocal
cd /d "%~dp0"

echo [Relay-kit] Running onboarding smoke...
python scripts\smoke_onboarding.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
  echo Smoke PASS.
) else (
  echo Smoke FAIL. Exit code: %EXIT_CODE%
)

echo.
pause
exit /b %EXIT_CODE%
