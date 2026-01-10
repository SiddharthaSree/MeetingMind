"""
System Tray Application
Provides quick access to recording controls from system tray
"""
import sys
import threading
import webbrowser
from typing import Callable, Optional
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    print("pystray not available. System tray disabled.")


class SystemTrayApp:
    """
    System tray application for MeetingMind
    
    Provides:
    - Quick recording start/stop
    - Status indicator (idle/recording/processing)
    - Open web UI
    - Exit application
    """
    
    def __init__(
        self,
        on_start_recording: Callable = None,
        on_stop_recording: Callable = None,
        on_open_ui: Callable = None,
        on_exit: Callable = None,
        ui_port: int = 7860
    ):
        """
        Initialize system tray app
        
        Args:
            on_start_recording: Callback when Start Recording clicked
            on_stop_recording: Callback when Stop Recording clicked
            on_open_ui: Callback when Open UI clicked
            on_exit: Callback when Exit clicked
            ui_port: Port where Gradio UI is running
        """
        self.on_start_recording = on_start_recording
        self.on_stop_recording = on_stop_recording
        self.on_open_ui = on_open_ui
        self.on_exit = on_exit
        self.ui_port = ui_port
        
        self.is_recording = False
        self.is_processing = False
        self.icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None
        
        # Status colors
        self.COLOR_IDLE = (100, 100, 100)  # Gray
        self.COLOR_RECORDING = (220, 50, 50)  # Red
        self.COLOR_PROCESSING = (50, 150, 220)  # Blue
    
    def _create_icon_image(self, color: tuple = None) -> Image:
        """Create tray icon with status color"""
        color = color or self.COLOR_IDLE
        
        # Create 64x64 icon
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw microphone-like shape
        # Background circle
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color
        )
        
        # Inner lighter area
        inner_margin = 16
        inner_color = tuple(min(255, c + 60) for c in color)
        draw.ellipse(
            [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
            fill=inner_color
        )
        
        # Mic stand
        draw.rectangle(
            [size//2 - 3, size//2, size//2 + 3, size - 12],
            fill=(255, 255, 255)
        )
        
        # Mic head
        draw.ellipse(
            [size//2 - 10, 12, size//2 + 10, size//2 + 5],
            fill=(255, 255, 255)
        )
        
        return image
    
    def _create_menu(self) -> pystray.Menu:
        """Create tray menu"""
        return pystray.Menu(
            pystray.MenuItem(
                "MeetingMind",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🔴 Start Recording",
                self._handle_start_recording,
                visible=lambda item: not self.is_recording and not self.is_processing
            ),
            pystray.MenuItem(
                "⏹️ Stop Recording",
                self._handle_stop_recording,
                visible=lambda item: self.is_recording
            ),
            pystray.MenuItem(
                "⏳ Processing...",
                None,
                enabled=False,
                visible=lambda item: self.is_processing
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🌐 Open UI",
                self._handle_open_ui
            ),
            pystray.MenuItem(
                "📁 Open Meetings Folder",
                self._handle_open_folder
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "❌ Exit",
                self._handle_exit
            )
        )
    
    def _handle_start_recording(self, icon, item):
        """Handle start recording menu click"""
        print("Tray: Start recording")
        self.set_recording(True)
        if self.on_start_recording:
            threading.Thread(target=self.on_start_recording, daemon=True).start()
    
    def _handle_stop_recording(self, icon, item):
        """Handle stop recording menu click"""
        print("Tray: Stop recording")
        self.set_recording(False)
        self.set_processing(True)
        if self.on_stop_recording:
            threading.Thread(target=self.on_stop_recording, daemon=True).start()
    
    def _handle_open_ui(self, icon, item):
        """Handle open UI menu click"""
        url = f"http://localhost:{self.ui_port}"
        print(f"Tray: Opening {url}")
        webbrowser.open(url)
        if self.on_open_ui:
            self.on_open_ui()
    
    def _handle_open_folder(self, icon, item):
        """Open meetings folder in file explorer"""
        try:
            from core.config import MEETINGS_DIR
            meetings_path = Path(MEETINGS_DIR)
            meetings_path.mkdir(parents=True, exist_ok=True)
            
            if sys.platform == 'win32':
                import os
                os.startfile(str(meetings_path))
            else:
                webbrowser.open(f"file://{meetings_path}")
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def _handle_exit(self, icon, item):
        """Handle exit menu click"""
        print("Tray: Exiting")
        if self.on_exit:
            self.on_exit()
        self.stop()
    
    def set_recording(self, recording: bool):
        """Update recording state and icon"""
        self.is_recording = recording
        self.is_processing = False
        self._update_icon()
    
    def set_processing(self, processing: bool):
        """Update processing state and icon"""
        self.is_processing = processing
        self.is_recording = False
        self._update_icon()
    
    def set_idle(self):
        """Set to idle state"""
        self.is_recording = False
        self.is_processing = False
        self._update_icon()
    
    def _update_icon(self):
        """Update icon based on current state"""
        if self.icon is None:
            return
        
        if self.is_recording:
            color = self.COLOR_RECORDING
            self.icon.title = "MeetingMind - Recording..."
        elif self.is_processing:
            color = self.COLOR_PROCESSING
            self.icon.title = "MeetingMind - Processing..."
        else:
            color = self.COLOR_IDLE
            self.icon.title = "MeetingMind"
        
        self.icon.icon = self._create_icon_image(color)
        self.icon.update_menu()
    
    def show_notification(self, title: str, message: str):
        """Show system notification"""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"Notification error: {e}")
    
    def start(self, blocking: bool = False):
        """
        Start the system tray app
        
        Args:
            blocking: If True, runs in main thread (blocks)
                     If False, runs in background thread
        """
        if not PYSTRAY_AVAILABLE:
            print("System tray not available (pystray not installed)")
            return
        
        self.icon = pystray.Icon(
            "MeetingMind",
            self._create_icon_image(),
            "MeetingMind",
            menu=self._create_menu()
        )
        
        if blocking:
            print("Starting system tray (blocking)...")
            self.icon.run()
        else:
            self._thread = threading.Thread(target=self.icon.run, daemon=True)
            self._thread.start()
            print("System tray started in background")
    
    def stop(self):
        """Stop the system tray app"""
        if self.icon:
            self.icon.stop()
            self.icon = None
            print("System tray stopped")


def create_tray_with_controller(controller, ui_port: int = 7860) -> SystemTrayApp:
    """
    Factory function to create system tray connected to controller
    
    Args:
        controller: MeetingMindController instance
        ui_port: Gradio UI port
    
    Returns:
        SystemTrayApp instance
    """
    tray = SystemTrayApp(
        on_start_recording=controller.start_recording,
        on_stop_recording=controller.stop_recording,
        ui_port=ui_port
    )
    
    # Connect controller events to tray updates
    from core.events import EventType
    
    controller.events.on(EventType.RECORDING_STARTED, lambda e: tray.set_recording(True))
    controller.events.on(EventType.RECORDING_STOPPED, lambda e: tray.set_processing(True))
    controller.events.on(EventType.PROCESSING_COMPLETE, lambda e: tray.set_idle())
    controller.events.on(EventType.QA_COMPLETE, lambda e: tray.set_idle())
    controller.events.on(
        EventType.SUMMARY_READY,
        lambda e: tray.show_notification("Meeting Ready", "Your meeting notes are ready!")
    )
    
    return tray


if __name__ == "__main__":
    # Test the system tray
    def on_start():
        print("Recording started!")
    
    def on_stop():
        print("Recording stopped!")
        import time
        time.sleep(2)
        tray.set_idle()
    
    tray = SystemTrayApp(
        on_start_recording=on_start,
        on_stop_recording=on_stop
    )
    
    print("Starting system tray. Right-click the icon to access menu.")
    tray.start(blocking=True)
