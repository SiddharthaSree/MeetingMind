@echo off
REM MeetingMind Launcher
REM Double-click this to start MeetingMind

title MeetingMind - Starting...

echo.
echo  ========================================
echo    Starting MeetingMind...
echo  ========================================
echo.

REM Check if running as EXE or Python
if exist "MeetingMind.exe" (
    start "" "MeetingMind.exe"
    exit
)

REM Try Python
python main.py
if errorlevel 1 (
    echo.
    echo  Error starting MeetingMind!
    echo  Make sure Python is installed.
    echo.
    pause
)
