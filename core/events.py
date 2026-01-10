"""
Event system for MeetingMind
Simple pub/sub pattern for component communication
"""
from dataclasses import dataclass
from typing import Callable, Dict, List, Any
from enum import Enum
from datetime import datetime


class EventType(Enum):
    """Types of events in the system"""
    # Recording events
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    RECORDING_PAUSED = "recording_paused"
    RECORDING_RESUMED = "recording_resumed"
    
    # Processing events
    PROCESSING_STARTED = "processing_started"
    PROCESSING_PROGRESS = "processing_progress"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_ERROR = "processing_error"
    
    # Transcription events
    TRANSCRIPTION_STARTED = "transcription_started"
    TRANSCRIPTION_COMPLETED = "transcription_completed"
    
    # Diarization events
    DIARIZATION_STARTED = "diarization_started"
    DIARIZATION_COMPLETED = "diarization_completed"
    
    # Q&A events
    QA_SESSION_STARTED = "qa_session_started"
    QA_QUESTION_ASKED = "qa_question_asked"
    QA_ANSWER_RECEIVED = "qa_answer_received"
    QA_SESSION_COMPLETED = "qa_session_completed"
    QA_SESSION_SKIPPED = "qa_session_skipped"
    
    # Summary events
    SUMMARY_STARTED = "summary_started"
    SUMMARY_COMPLETED = "summary_completed"
    
    # Meeting detection events
    MEETING_DETECTED = "meeting_detected"
    MEETING_ENDED = "meeting_ended"
    
    # UI events
    UI_NOTIFICATION = "ui_notification"
    UI_STATUS_UPDATE = "ui_status_update"
    
    # System events
    APP_STARTED = "app_started"
    APP_SHUTDOWN = "app_shutdown"
    CONFIG_CHANGED = "config_changed"
    ERROR = "error"


@dataclass
class Event:
    """Event data container"""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventEmitter:
    """
    Simple event emitter for pub/sub pattern
    
    Usage:
        emitter = EventEmitter()
        
        # Subscribe
        def on_recording_started(event):
            print(f"Recording started: {event.data}")
        
        emitter.on(EventType.RECORDING_STARTED, on_recording_started)
        
        # Emit
        emitter.emit(EventType.RECORDING_STARTED, {"file": "recording.wav"})
    """
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._once_listeners: Dict[EventType, List[Callable[[Event], None]]] = {}
    
    def on(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Subscribe to an event type"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def once(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Subscribe to an event type, but only fire once"""
        if event_type not in self._once_listeners:
            self._once_listeners[event_type] = []
        self._once_listeners[event_type].append(callback)
    
    def off(self, event_type: EventType, callback: Callable[[Event], None] = None) -> None:
        """Unsubscribe from an event type"""
        if callback is None:
            # Remove all listeners for this event type
            self._listeners.pop(event_type, None)
            self._once_listeners.pop(event_type, None)
        else:
            # Remove specific callback
            if event_type in self._listeners:
                self._listeners[event_type] = [
                    cb for cb in self._listeners[event_type] if cb != callback
                ]
            if event_type in self._once_listeners:
                self._once_listeners[event_type] = [
                    cb for cb in self._once_listeners[event_type] if cb != callback
                ]
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None) -> None:
        """Emit an event to all subscribers"""
        event = Event(type=event_type, data=data or {})
        
        # Call regular listeners
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event listener for {event_type}: {e}")
        
        # Call once listeners and remove them
        if event_type in self._once_listeners:
            for callback in self._once_listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in once listener for {event_type}: {e}")
            self._once_listeners[event_type] = []
    
    def clear(self) -> None:
        """Remove all listeners"""
        self._listeners.clear()
        self._once_listeners.clear()


# Global event emitter instance
_emitter: EventEmitter = None


def get_emitter() -> EventEmitter:
    """Get global event emitter instance"""
    global _emitter
    if _emitter is None:
        _emitter = EventEmitter()
    return _emitter
