"""
MeetingMind Core Package
Central application logic and orchestration
"""
from .controller import MeetingMindController
from .config import Config, load_config, save_config
from .events import EventEmitter, Event

__all__ = [
    'MeetingMindController',
    'Config',
    'load_config',
    'save_config',
    'EventEmitter',
    'Event'
]
