"""
MeetingMind - Offline Meeting Notes Assistant
Main entry point for the application

Run with: python main.py
"""
import sys
import argparse
import threading
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    # Core dependencies
    try:
        import gradio
    except ImportError:
        missing.append("gradio")
    
    try:
        import whisper
    except ImportError:
        missing.append("openai-whisper")
    
    try:
        import ollama
    except ImportError:
        missing.append("ollama")
    
    # Optional but recommended
    optional_missing = []
    try:
        import pyaudiowpatch
    except ImportError:
        optional_missing.append("pyaudiowpatch (for system audio recording)")
    
    try:
        import pystray
    except ImportError:
        optional_missing.append("pystray (for system tray)")
    
    if missing:
        print("❌ Missing required dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\nRun: pip install -r requirements.txt")
        return False
    
    if optional_missing:
        print("⚠️  Optional dependencies missing (some features unavailable):")
        for dep in optional_missing:
            print(f"   - {dep}")
        print()
    
    return True


def check_ollama():
    """Check if Ollama is running"""
    try:
        import ollama
        models = ollama.list()
        model_names = [m['name'].split(':')[0] for m in models.get('models', [])]
        
        if not model_names:
            print("⚠️  No Ollama models found. Install with: ollama pull llama3.2")
            return False
        
        print(f"✅ Ollama ready (models: {', '.join(model_names[:3])})")
        return True
    except Exception as e:
        print(f"⚠️  Ollama not accessible: {e}")
        print("   Start Ollama and pull a model: ollama pull llama3.2")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MeetingMind - Offline Meeting Notes Assistant"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=7860,
        help="Port to run web UI on (default: 7860)"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create public share link"
    )
    parser.add_argument(
        "--no-tray",
        action="store_true",
        help="Disable system tray icon"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and exit"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════╗
    ║  🎙️  MeetingMind v2.0                   ║
    ║  Offline Meeting Notes Assistant         ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    check_ollama()  # Warning only, don't exit
    
    if args.check:
        print("\n✅ Dependency check complete")
        sys.exit(0)
    
    # Initialize controller
    print("\nInitializing MeetingMind...")
    from core.controller import MeetingMindController
    controller = MeetingMindController()
    
    # Start system tray (if available and not disabled)
    tray = None
    if not args.no_tray:
        try:
            from ui.system_tray import create_tray_with_controller
            tray = create_tray_with_controller(controller, args.port)
            tray.start(blocking=False)
            print("✅ System tray started")
        except Exception as e:
            print(f"⚠️  System tray disabled: {e}")
    
    # Launch Gradio UI
    print(f"\n🌐 Starting web UI on port {args.port}...")
    
    from ui.gradio_app import create_gradio_app
    app = create_gradio_app(controller)
    
    try:
        app.launch(
            server_port=args.port,
            share=args.share,
            inbrowser=not args.no_browser,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down MeetingMind...")
    finally:
        if tray:
            tray.stop()


if __name__ == "__main__":
    main()
