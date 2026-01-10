@echo off
REM MeetingMind First-Time Setup for Windows
REM Run this before using MeetingMind for the first time

echo.
echo ============================================
echo    MeetingMind - First Time Setup
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Checking for embedded Python...
    if exist "python\python.exe" (
        set PYTHON=python\python.exe
    ) else (
        echo.
        echo WARNING: Python not found!
        echo.
        echo MeetingMind requires Python 3.10+
        echo Download from: https://www.python.org/downloads/
        echo.
        echo Or use the pre-built EXE version instead.
        echo.
        pause
        exit /b 1
    )
) else (
    set PYTHON=python
)

REM Run setup script
%PYTHON% setup.py

pause
