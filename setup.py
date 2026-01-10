"""
MeetingMind First Run Setup
Guides users through initial configuration
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header():
    print("\n" + "="*60)
    print("  🎙️  MeetingMind - First Time Setup")
    print("="*60 + "\n")


def check_ollama():
    """Check if Ollama is installed and running"""
    print("Checking Ollama...")
    
    # Check if ollama command exists
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        print("  ❌ Ollama not found!")
        print("\n  Please install Ollama:")
        print("  1. Go to https://ollama.ai/download")
        print("  2. Download and install for Windows")
        print("  3. Run this setup again\n")
        return False
    
    print(f"  ✓ Ollama found at: {ollama_path}")
    
    # Check if ollama is running
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  ✓ Ollama is running")
            
            # Check for models
            if "llama" in result.stdout.lower() or "mistral" in result.stdout.lower():
                print("  ✓ AI model found")
                return True
            else:
                print("  ⚠ No AI model installed")
                print("\n  Installing recommended model...")
                subprocess.run(["ollama", "pull", "llama3.2"], check=False)
                return True
        else:
            print("  ⚠ Ollama not responding")
            print("  Starting Ollama server...")
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True
    except subprocess.TimeoutExpired:
        print("  ⚠ Ollama timeout - may need to start manually")
        return True
    except Exception as e:
        print(f"  ⚠ Could not check Ollama: {e}")
        return True


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg...")
    
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"  ✓ FFmpeg found at: {ffmpeg_path}")
        return True
    else:
        print("  ❌ FFmpeg not found!")
        print("\n  Please install FFmpeg:")
        print("  Option 1 (with Chocolatey):")
        print("    choco install ffmpeg")
        print("\n  Option 2 (Manual):")
        print("    1. Download from https://ffmpeg.org/download.html")
        print("    2. Extract to C:\\ffmpeg")
        print("    3. Add C:\\ffmpeg\\bin to your PATH")
        print("    4. Restart your computer\n")
        return False


def create_data_folders():
    """Create necessary data folders"""
    print("\nCreating data folders...")
    
    folders = [
        "data/meetings",
        "data/profiles", 
        "data/temp",
        "data/exports"
    ]
    
    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {folder}")
    
    return True


def show_quick_start():
    """Show quick start guide"""
    print("\n" + "="*60)
    print("  ✅ Setup Complete!")
    print("="*60)
    print("""
  🚀 QUICK START:
  
  1. Make sure Ollama is running
     (Check your system tray or run: ollama serve)
  
  2. Launch MeetingMind
     - Double-click MeetingMind.exe, OR
     - Run: python main.py
  
  3. Open your browser to:
     http://localhost:7860
  
  4. Start recording your meeting!
     - Click "🔴 Start Recording"
     - Join your Teams/Zoom call
     - Click "⏹️ Stop Recording" when done
  
  📖 Need help? Visit:
     https://github.com/SiddharthaSree/MeetingMind

""")


def main():
    print_header()
    
    all_good = True
    
    # Check dependencies
    if not check_ollama():
        all_good = False
    
    if not check_ffmpeg():
        all_good = False
    
    # Create folders
    create_data_folders()
    
    if all_good:
        show_quick_start()
        return 0
    else:
        print("\n" + "="*60)
        print("  ⚠️  Some dependencies are missing")
        print("="*60)
        print("\n  Please install the missing items above,")
        print("  then run this setup again.\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        input("Press Enter to continue...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
