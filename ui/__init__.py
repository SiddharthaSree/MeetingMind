"""
UI Package for MeetingMind
Contains system tray and Gradio web interface
"""

from ui.system_tray import SystemTrayApp
from ui.gradio_app import create_gradio_app

__all__ = ['SystemTrayApp', 'create_gradio_app']
