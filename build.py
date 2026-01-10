#!/usr/bin/env python3
"""
MeetingMind Build Script
Alternative Python-based build script for creating the EXE
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_requirements():
    """Check if all requirements are met"""
    print("Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10+ required")
        return False
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("ERROR: main.py not found. Run from MeetingMind directory.")
        return False
    
    print("✓ Requirements check passed")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"
        ], check=True)
        
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False


def clean_build():
    """Clean previous build artifacts"""
    print("\nCleaning previous builds...")
    
    for folder in ["build", "dist"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    
    # Remove __pycache__ folders
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
    
    print("✓ Clean complete")


def create_assets():
    """Create assets folder and placeholder files"""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple placeholder icon note
    readme = assets_dir / "README.txt"
    if not readme.exists():
        readme.write_text("Place your icon.ico file here for custom branding.\n")
    
    print("✓ Assets folder ready")


def run_pyinstaller():
    """Run PyInstaller to create the executable"""
    print("\n" + "="*50)
    print("Building MeetingMind executable...")
    print("This may take several minutes...")
    print("="*50 + "\n")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "meetingmind.spec",
            "--noconfirm"
        ], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: PyInstaller failed: {e}")
        return False


def create_distribution_readme():
    """Create README for distribution"""
    readme_content = """MeetingMind - AI Meeting Notes Assistant
=========================================

INSTALLATION:
1. Extract this folder to your desired location
2. Run MeetingMind.exe

REQUIREMENTS:
- Windows 10/11
- Ollama installed and running (for AI summaries)
  Download from: https://ollama.ai
- Hugging Face token (optional, for speaker diarization)

FIRST RUN:
1. Start Ollama and pull a model: ollama pull llama3.2
2. Launch MeetingMind.exe
3. The web interface will open in your browser

FEATURES:
- Record system audio from meetings
- Automatic speaker identification
- AI-powered meeting summaries
- Export to Markdown, HTML, JSON, DOCX, PDF
- Meeting history and search
- Auto-detect Teams/Zoom/Meet meetings

For support, visit: https://github.com/SiddharthaSree/MeetingMind
"""
    
    dist_path = Path("dist/MeetingMind")
    if dist_path.exists():
        (dist_path / "README.txt").write_text(readme_content)
        print("✓ Distribution README created")


def verify_build():
    """Verify the build was successful"""
    exe_path = Path("dist/MeetingMind/MeetingMind.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        print(f"\nExecutable: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")
        print("\nTo distribute: Zip the entire dist/MeetingMind folder")
        return True
    else:
        print("\n" + "="*50)
        print("BUILD FAILED!")
        print("="*50)
        print("\nCheck the output above for errors.")
        return False


def main():
    """Main build process"""
    print("="*50)
    print("MeetingMind EXE Build Script")
    print("="*50)
    
    if not check_requirements():
        return 1
    
    if not install_dependencies():
        return 1
    
    clean_build()
    create_assets()
    
    if not run_pyinstaller():
        return 1
    
    create_distribution_readme()
    
    if verify_build():
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
