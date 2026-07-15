@echo off
REM One-click setup for Windows. Double-click this file from the
REM project root.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python setup.py
    goto :end
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    python3 setup.py
    goto :end
)

echo Python is required but was not found.
echo Install it from https://www.python.org/downloads/ and re-run this script.

:end
pause
