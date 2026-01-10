"""
MeetingMind Services Package
Contains all service modules for audio capture, transcription, diarization, etc.
"""
from .audio_capture import AudioCaptureService
from .transcriber import TranscriberService
from .diarizer import DiarizerService
from .summarizer import SummarizerService
from .qa_engine import QAEngine
from .meeting_detector import MeetingDetector
from .templates import TemplateManager, MeetingTemplate
from .exporter import ExportService
from .history import MeetingHistoryService

__all__ = [
    'AudioCaptureService',
    'TranscriberService',
    'DiarizerService',
    'SummarizerService',
    'QAEngine',
    'MeetingDetector',
    'TemplateManager',
    'MeetingTemplate',
    'ExportService',
    'MeetingHistoryService'
]
