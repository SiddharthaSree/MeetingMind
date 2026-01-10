@echo off
REM MeetingMind Build Script for Windows
REM Creates a standalone executable using PyInstaller

echo ============================================
echo    MeetingMind EXE Build Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from the MeetingMind directory.
    pause
    exit /b 1
)

REM Create/activate virtual environment (optional but recommended)
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Install PyInstaller if not present
pip install pyinstaller>=6.0.0

REM Create assets folder if not exists
if not exist "assets" mkdir assets

REM Create a simple icon placeholder if not exists
if not exist "assets\icon.ico" (
    echo Creating placeholder icon...
    echo Note: Replace assets\icon.ico with your own icon for branding
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Run PyInstaller
echo.
echo ============================================
echo Building MeetingMind executable...
echo This may take several minutes...
echo ============================================
echo.

pyinstaller meetingmind.spec --noconfirm

REM Check if build succeeded
if exist "dist\MeetingMind\MeetingMind.exe" (
    echo.
    echo ============================================
    echo BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Your executable is at: dist\MeetingMind\MeetingMind.exe
    echo.
    echo To distribute the app, zip the entire dist\MeetingMind folder
    echo.
    
    REM Create a simple README for distribution
    echo Creating distribution README...
    (
        echo MeetingMind - AI Meeting Notes Assistant
        echo =========================================
        echo.
        echo INSTALLATION:
        echo 1. Extract this folder to your desired location
        echo 2. Run MeetingMind.exe
        echo.
        echo REQUIREMENTS:
        echo - Windows 10/11
        echo - Ollama installed and running ^(for AI summaries^)
        echo   Download from: https://ollama.ai
        echo - Hugging Face token ^(optional, for speaker diarization^)
        echo.
        echo FIRST RUN:
        echo 1. Start Ollama and pull a model: ollama pull llama3.2
        echo 2. Launch MeetingMind.exe
        echo 3. The web interface will open in your browser
        echo.
        echo For support, visit: https://github.com/SiddharthaSree/MeetingMind
    ) > dist\MeetingMind\README.txt
    
    echo.
    echo Build completed! Press any key to exit...
) else (
    echo.
    echo ============================================
    echo BUILD FAILED!
    echo ============================================
    echo.
    echo Check the output above for errors.
    echo Common issues:
    echo - Missing dependencies
    echo - Antivirus blocking PyInstaller
    echo - Insufficient disk space
    echo.
)

pause
