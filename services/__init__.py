"""
MeetingMind Services Package
Contains all service modules for audio capture, transcription, diarization, etc.
"""
# Core services
from .audio_capture import AudioCaptureService
from .transcriber import TranscriberService
from .diarizer import DiarizerService
from .summarizer import SummarizerService
from .qa_engine import QAEngine

# Meeting management
from .meeting_detector import MeetingDetector
from .templates import TemplateManager, MeetingTemplate
from .exporter import ExportService
from .history import MeetingHistoryService

# Phase 3: Market-competitive features
from .realtime_transcriber import RealtimeTranscriber
from .highlights import HighlightsManager, Highlight, HighlightType
from .analytics import MeetingAnalytics
from .meeting_chat import MeetingChat
from .integrations import IntegrationsService
from .shortcuts import KeyboardShortcuts, ShortcutAction, get_shortcuts
from .calendar_integration import CalendarIntegration, CalendarEvent

__all__ = [
    # Core
    'AudioCaptureService',
    'TranscriberService',
    'DiarizerService',
    'SummarizerService',
    'QAEngine',
    
    # Meeting management
    'MeetingDetector',
    'TemplateManager',
    'MeetingTemplate',
    'ExportService',
    'MeetingHistoryService',
    
    # Phase 3 features
    'RealtimeTranscriber',
    'HighlightsManager',
    'Highlight',
    'HighlightType',
    'MeetingAnalytics',
    'MeetingChat',
    'IntegrationsService',
    'KeyboardShortcuts',
    'ShortcutAction',
    'get_shortcuts',
    'CalendarIntegration',
    'CalendarEvent'
]
