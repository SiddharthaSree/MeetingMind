"""
Meeting Detection Service
Auto-detects when Teams, Zoom, or Google Meet starts and prompts to record
"""
import time
import threading
from typing import Callable, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available. Meeting detection disabled.")


class MeetingApp(Enum):
    """Supported meeting applications"""
    TEAMS = "teams"
    ZOOM = "zoom"
    MEET = "meet"
    WEBEX = "webex"
    SLACK = "slack"
    UNKNOWN = "unknown"


@dataclass
class MeetingProcess:
    """Represents a detected meeting process"""
    app: MeetingApp
    process_name: str
    pid: int
    window_title: Optional[str] = None
    start_time: Optional[float] = None


# Process patterns for each meeting app
MEETING_PATTERNS = {
    MeetingApp.TEAMS: {
        'processes': ['Teams.exe', 'ms-teams.exe', 'Teams'],
        'window_patterns': [r'meeting', r'call', r'\|.*Microsoft Teams'],
        'audio_indicators': ['Teams AudioDevice']
    },
    MeetingApp.ZOOM: {
        'processes': ['Zoom.exe', 'zoom', 'CptHost.exe'],
        'window_patterns': [r'Zoom Meeting', r'Zoom Webinar'],
        'audio_indicators': ['Zoom Audio']
    },
    MeetingApp.MEET: {
        'processes': ['chrome.exe', 'msedge.exe', 'firefox.exe'],
        'window_patterns': [r'Meet -', r'Google Meet'],
        'url_patterns': ['meet.google.com']
    },
    MeetingApp.WEBEX: {
        'processes': ['CiscoCollabHost.exe', 'webex.exe', 'atmgr.exe'],
        'window_patterns': [r'Webex', r'Cisco Webex'],
        'audio_indicators': []
    },
    MeetingApp.SLACK: {
        'processes': ['slack.exe', 'Slack'],
        'window_patterns': [r'Huddle', r'Slack call'],
        'audio_indicators': []
    }
}


class MeetingDetector:
    """
    Service for detecting active meetings
    
    Monitors running processes and window titles to detect
    when a meeting application is actively in a call.
    """
    
    def __init__(
        self,
        on_meeting_detected: Callable[[MeetingProcess], None] = None,
        on_meeting_ended: Callable[[MeetingProcess], None] = None,
        check_interval: float = 5.0
    ):
        """
        Initialize meeting detector
        
        Args:
            on_meeting_detected: Callback when meeting starts
            on_meeting_ended: Callback when meeting ends
            check_interval: Seconds between checks
        """
        self.on_meeting_detected = on_meeting_detected
        self.on_meeting_ended = on_meeting_ended
        self.check_interval = check_interval
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._active_meetings: Dict[int, MeetingProcess] = {}
        self._seen_pids: Set[int] = set()
        
        # Cooldown to prevent rapid re-detection
        self._last_detection_time: Dict[MeetingApp, float] = {}
        self._detection_cooldown = 60.0  # seconds
        
        print("MeetingDetector initialized")
    
    def start(self):
        """Start monitoring for meetings"""
        if not PSUTIL_AVAILABLE:
            print("Cannot start meeting detection: psutil not installed")
            return
        
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print("Meeting detection started")
    
    def stop(self):
        """Stop monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        print("Meeting detection stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                self._check_for_meetings()
            except Exception as e:
                print(f"Error in meeting detection: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_for_meetings(self):
        """Check for active meeting processes"""
        current_meeting_pids = set()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                pid = proc.info['pid']
                
                # Check if this matches a meeting app
                meeting_app = self._identify_meeting_app(proc_name)
                
                if meeting_app != MeetingApp.UNKNOWN:
                    # Check if actually in a meeting (not just app running)
                    if self._is_in_active_meeting(proc, meeting_app):
                        current_meeting_pids.add(pid)
                        
                        if pid not in self._active_meetings:
                            # New meeting detected
                            meeting = MeetingProcess(
                                app=meeting_app,
                                process_name=proc_name,
                                pid=pid,
                                start_time=time.time()
                            )
                            
                            # Check cooldown
                            last_time = self._last_detection_time.get(meeting_app, 0)
                            if time.time() - last_time > self._detection_cooldown:
                                self._active_meetings[pid] = meeting
                                self._last_detection_time[meeting_app] = time.time()
                                
                                print(f"Meeting detected: {meeting_app.value}")
                                if self.on_meeting_detected:
                                    self.on_meeting_detected(meeting)
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for ended meetings
        ended_pids = set(self._active_meetings.keys()) - current_meeting_pids
        for pid in ended_pids:
            meeting = self._active_meetings.pop(pid)
            print(f"Meeting ended: {meeting.app.value}")
            if self.on_meeting_ended:
                self.on_meeting_ended(meeting)
    
    def _identify_meeting_app(self, process_name: str) -> MeetingApp:
        """Identify which meeting app a process belongs to"""
        process_lower = process_name.lower()
        
        for app, patterns in MEETING_PATTERNS.items():
            for pattern in patterns['processes']:
                if pattern.lower() in process_lower:
                    return app
        
        return MeetingApp.UNKNOWN
    
    def _is_in_active_meeting(self, proc, app: MeetingApp) -> bool:
        """
        Check if the app is actually in a meeting (not just running)
        
        Uses heuristics like:
        - Audio device usage
        - Window title patterns
        - Network activity
        """
        try:
            # For Teams/Zoom, check if audio is being used
            # This is a simplified check - real implementation would
            # monitor audio device usage
            
            # Check CPU usage as proxy for active call
            cpu_percent = proc.cpu_percent(interval=0.1)
            
            # Active meeting usually has higher CPU due to audio/video
            if app in [MeetingApp.TEAMS, MeetingApp.ZOOM]:
                return cpu_percent > 5.0  # Threshold for active meeting
            
            # For browser-based (Meet), harder to detect
            # Would need to check window titles
            if app == MeetingApp.MEET:
                return True  # Assume active if Chrome/Edge with Meet detected
            
            return cpu_percent > 3.0
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_active_meetings(self) -> List[MeetingProcess]:
        """Get list of currently active meetings"""
        return list(self._active_meetings.values())
    
    def is_in_meeting(self) -> bool:
        """Check if currently in any meeting"""
        return len(self._active_meetings) > 0


class MeetingWatcher:
    """
    Higher-level meeting watcher that integrates with the controller
    
    Provides:
    - Meeting detection with notifications
    - Auto-record prompts
    - Meeting end detection for auto-processing
    """
    
    def __init__(
        self,
        controller=None,
        auto_record: bool = False,
        auto_process: bool = True
    ):
        """
        Initialize meeting watcher
        
        Args:
            controller: MeetingMindController instance
            auto_record: Automatically start recording on meeting detection
            auto_process: Automatically process when meeting ends
        """
        self.controller = controller
        self.auto_record = auto_record
        self.auto_process = auto_process
        
        self.detector = MeetingDetector(
            on_meeting_detected=self._on_meeting_detected,
            on_meeting_ended=self._on_meeting_ended
        )
        
        self._pending_prompt: Optional[MeetingProcess] = None
        self._recording_meeting: Optional[MeetingProcess] = None
    
    def start(self):
        """Start watching for meetings"""
        self.detector.start()
    
    def stop(self):
        """Stop watching"""
        self.detector.stop()
    
    def _on_meeting_detected(self, meeting: MeetingProcess):
        """Handle meeting detection"""
        print(f"🎤 Meeting detected: {meeting.app.value}")
        
        if self.auto_record and self.controller:
            # Auto-start recording
            self.controller.start_recording()
            self._recording_meeting = meeting
            print("Auto-recording started")
        else:
            # Store for prompt
            self._pending_prompt = meeting
            # UI will check this and show prompt
    
    def _on_meeting_ended(self, meeting: MeetingProcess):
        """Handle meeting end"""
        print(f"📴 Meeting ended: {meeting.app.value}")
        
        if self._recording_meeting and self._recording_meeting.pid == meeting.pid:
            if self.controller:
                # Stop recording and optionally auto-process
                audio_path = self.controller.stop_recording()
                
                if self.auto_process and audio_path:
                    print("Auto-processing meeting...")
                    self.controller.process_audio(audio_path)
            
            self._recording_meeting = None
    
    def has_pending_prompt(self) -> bool:
        """Check if there's a pending meeting prompt"""
        return self._pending_prompt is not None
    
    def get_pending_prompt(self) -> Optional[MeetingProcess]:
        """Get and clear the pending prompt"""
        prompt = self._pending_prompt
        self._pending_prompt = None
        return prompt
    
    def accept_prompt(self):
        """User accepted the recording prompt"""
        if self._pending_prompt and self.controller:
            self.controller.start_recording()
            self._recording_meeting = self._pending_prompt
            self._pending_prompt = None
    
    def dismiss_prompt(self):
        """User dismissed the recording prompt"""
        self._pending_prompt = None


def create_meeting_watcher(controller, auto_record=False, auto_process=True) -> MeetingWatcher:
    """Factory function to create meeting watcher"""
    return MeetingWatcher(
        controller=controller,
        auto_record=auto_record,
        auto_process=auto_process
    )
