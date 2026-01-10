"""
MeetingMind Controller
Main orchestrator that coordinates all services and manages application state
"""
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from enum import Enum

from .config import Config, get_config, save_config, MEETINGS_DIR, TEMP_DIR
from .events import EventEmitter, EventType, get_emitter


class AppState(Enum):
    """Application states"""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    QA_SESSION = "qa_session"
    GENERATING = "generating"
    MONITORING = "monitoring"  # Monitoring for meetings
    LIVE_TRANSCRIBING = "live_transcribing"  # Real-time transcription mode
    ERROR = "error"


class MeetingMindController:
    """
    Central controller that orchestrates all MeetingMind operations
    
    Responsibilities:
    - Manage application state
    - Coordinate between services (audio, transcription, diarization, Q&A, summary)
    - Handle the Q&A-driven workflow
    - Manage meeting data
    - Auto-detect and process meetings
    - Real-time transcription and highlights
    - Calendar integration and keyboard shortcuts
    """
    
    def __init__(self, config: Config = None):
        self.config = config or get_config()
        self.emitter = get_emitter()
        self.state = AppState.IDLE
        
        # Core services (lazy loaded)
        self._audio_service = None
        self._transcriber = None
        self._diarizer = None
        self._summarizer = None
        self._qa_engine = None
        self._meeting_detector = None
        self._template_manager = None
        self._export_service = None
        self._history_service = None
        
        # Phase 3 services (lazy loaded)
        self._realtime_transcriber = None
        self._highlights_manager = None
        self._analytics = None
        self._meeting_chat = None
        self._integrations = None
        self._shortcuts = None
        self._calendar = None
        
        # Current session data
        self.current_recording_path: Optional[str] = None
        self.current_transcript = None
        self.current_diarization = None
        self.current_summary = None
        self.current_qa_responses: Dict[str, Any] = {}
        self.speaker_names: Dict[str, str] = {}  # SPEAKER_00 -> "John"
        self.current_template: str = "general"  # Current meeting template
        self.current_meeting_app: Optional[str] = None  # Detected meeting app
        self.current_calendar_event = None  # Calendar event for current meeting
        
        # Auto-recording state
        self._auto_record_enabled = False
        self._was_in_meeting = False
        
        # Processing thread
        self._processing_thread: Optional[threading.Thread] = None
        
        print("MeetingMindController initialized")
    
    # ==================== Service Accessors ====================
    
    @property
    def audio_service(self):
        """Lazy load audio capture service"""
        if self._audio_service is None:
            from services.audio_capture import AudioCaptureService
            self._audio_service = AudioCaptureService(
                sample_rate=self.config.audio.sample_rate,
                channels=self.config.audio.channels
            )
        return self._audio_service
    
    @property
    def transcriber(self):
        """Lazy load transcriber service"""
        if self._transcriber is None:
            from services.transcriber import TranscriberService
            self._transcriber = TranscriberService(
                model_name=self.config.whisper.model
            )
        return self._transcriber
    
    @property
    def diarizer(self):
        """Lazy load diarizer service"""
        if self._diarizer is None:
            from services.diarizer import DiarizerService
            self._diarizer = DiarizerService(
                use_auth_token=self.config.diarization.use_auth_token
            )
        return self._diarizer
    
    @property
    def summarizer(self):
        """Lazy load summarizer service"""
        if self._summarizer is None:
            from services.summarizer import SummarizerService
            self._summarizer = SummarizerService(
                model_name=self.config.ollama.model
            )
        return self._summarizer
    
    @property
    def qa_engine(self):
        """Lazy load Q&A engine"""
        if self._qa_engine is None:
            from services.qa_engine import QAEngine
            self._qa_engine = QAEngine(
                config=self.config.qa,
                llm_model=self.config.ollama.model
            )
        return self._qa_engine
    
    @property
    def meeting_detector(self):
        """Lazy load meeting detector service"""
        if self._meeting_detector is None:
            from services.meeting_detector import MeetingDetector
            self._meeting_detector = MeetingDetector()
        return self._meeting_detector
    
    @property
    def template_manager(self):
        """Lazy load template manager"""
        if self._template_manager is None:
            from services.templates import TemplateManager
            self._template_manager = TemplateManager()
        return self._template_manager
    
    @property
    def export_service(self):
        """Lazy load export service"""
        if self._export_service is None:
            from services.exporter import ExportService
            self._export_service = ExportService()
        return self._export_service
    
    @property
    def history_service(self):
        """Lazy load history service"""
        if self._history_service is None:
            from services.history import MeetingHistoryService
            self._history_service = MeetingHistoryService()
        return self._history_service
    
    # ==================== Phase 3 Service Accessors ====================
    
    @property
    def realtime_transcriber(self):
        """Lazy load real-time transcriber"""
        if self._realtime_transcriber is None:
            from services.realtime_transcriber import RealtimeTranscriber
            self._realtime_transcriber = RealtimeTranscriber(
                model_name=self.config.whisper.model
            )
        return self._realtime_transcriber
    
    @property
    def highlights_manager(self):
        """Lazy load highlights manager"""
        if self._highlights_manager is None:
            from services.highlights import HighlightsManager
            self._highlights_manager = HighlightsManager()
        return self._highlights_manager
    
    @property
    def analytics(self):
        """Lazy load meeting analytics"""
        if self._analytics is None:
            from services.analytics import MeetingAnalytics
            self._analytics = MeetingAnalytics(
                history_dir=Path(self.config.storage.meetings_dir)
            )
        return self._analytics
    
    @property
    def meeting_chat(self):
        """Lazy load meeting chat service"""
        if self._meeting_chat is None:
            from services.meeting_chat import MeetingChat
            self._meeting_chat = MeetingChat(
                history_dir=Path(self.config.storage.meetings_dir),
                model_name=self.config.ollama.model
            )
        return self._meeting_chat
    
    @property
    def integrations(self):
        """Lazy load integrations service"""
        if self._integrations is None:
            from services.integrations import IntegrationsService
            self._integrations = IntegrationsService()
        return self._integrations
    
    @property
    def shortcuts(self):
        """Lazy load keyboard shortcuts"""
        if self._shortcuts is None:
            from services.shortcuts import get_shortcuts, ShortcutAction
            self._shortcuts = get_shortcuts()
            # Register default shortcuts
            self._shortcuts.register(ShortcutAction.TOGGLE_RECORDING, self._toggle_recording)
            self._shortcuts.register(ShortcutAction.ADD_BOOKMARK, self._add_bookmark)
        return self._shortcuts
    
    @property
    def calendar(self):
        """Lazy load calendar integration"""
        if self._calendar is None:
            from services.calendar_integration import CalendarIntegration
            self._calendar = CalendarIntegration()
        return self._calendar
    
    def _toggle_recording(self):
        """Toggle recording on/off (for keyboard shortcut)"""
        if self.state == AppState.RECORDING:
            self.stop_recording()
        elif self.state in [AppState.IDLE, AppState.MONITORING]:
            self.start_recording()
    
    def _add_bookmark(self):
        """Add a bookmark at current time (for keyboard shortcut)"""
        if self.state == AppState.RECORDING:
            timestamp = self.audio_service.get_duration() if self._audio_service else 0
            self.highlights_manager.add_highlight(
                timestamp=timestamp,
                text="[Bookmark]",
                highlight_type="bookmark"
            )
    
    # ==================== Recording Methods ====================
    
    def start_recording(self, device_id: int = None) -> bool:
        """Start recording system audio"""
        if self.state != AppState.IDLE:
            print(f"Cannot start recording in state: {self.state}")
            return False
        
        try:
            self.audio_service.start_recording(device_id=device_id)
            self.state = AppState.RECORDING
            self.emitter.emit(EventType.RECORDING_STARTED, {
                "device_id": device_id,
                "timestamp": datetime.now().isoformat()
            })
            print("Recording started")
            return True
        except Exception as e:
            self.state = AppState.ERROR
            self.emitter.emit(EventType.ERROR, {"error": str(e), "context": "start_recording"})
            print(f"Error starting recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and return the audio file path"""
        if self.state != AppState.RECORDING:
            print(f"Cannot stop recording in state: {self.state}")
            return None
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{timestamp}.wav"
            output_path = str(TEMP_DIR / filename)
            
            # Stop recording
            self.audio_service.stop_recording(output_path)
            self.current_recording_path = output_path
            self.state = AppState.IDLE
            
            self.emitter.emit(EventType.RECORDING_STOPPED, {
                "file_path": output_path,
                "duration": self.audio_service.get_duration()
            })
            print(f"Recording saved to: {output_path}")
            return output_path
        except Exception as e:
            self.state = AppState.ERROR
            self.emitter.emit(EventType.ERROR, {"error": str(e), "context": "stop_recording"})
            print(f"Error stopping recording: {e}")
            return None
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.state == AppState.RECORDING
    
    # ==================== Processing Pipeline ====================
    
    def process_audio(self, audio_path: str = None, async_mode: bool = True) -> bool:
        """
        Start processing an audio file through the full pipeline
        
        Args:
            audio_path: Path to audio file (uses current recording if None)
            async_mode: Run in background thread
        
        Returns:
            bool: True if processing started successfully
        """
        audio_path = audio_path or self.current_recording_path
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return False
        
        if self.state not in [AppState.IDLE, AppState.ERROR]:
            print(f"Cannot start processing in state: {self.state}")
            return False
        
        self.current_recording_path = audio_path
        
        if async_mode:
            self._processing_thread = threading.Thread(
                target=self._run_processing_pipeline,
                args=(audio_path,),
                daemon=True
            )
            self._processing_thread.start()
        else:
            self._run_processing_pipeline(audio_path)
        
        return True
    
    def _run_processing_pipeline(self, audio_path: str):
        """
        Run the full processing pipeline (called in background thread)
        
        Pipeline:
        1. Transcribe with Whisper
        2. Diarize with pyannote
        3. Merge transcription with speaker labels
        4. Wait for Q&A session
        5. Generate final summary with Q&A answers
        """
        try:
            self.state = AppState.PROCESSING
            self.emitter.emit(EventType.PROCESSING_STARTED, {"file": audio_path})
            
            # Step 1: Transcription
            self.emitter.emit(EventType.TRANSCRIPTION_STARTED, {})
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "transcription",
                "progress": 0,
                "message": "Transcribing audio..."
            })
            
            transcript_result = self.transcriber.transcribe(audio_path)
            self.current_transcript = transcript_result
            
            self.emitter.emit(EventType.TRANSCRIPTION_COMPLETED, {
                "text_length": len(transcript_result.get('text', '')),
                "language": transcript_result.get('language', 'unknown')
            })
            
            # Step 2: Diarization
            self.emitter.emit(EventType.DIARIZATION_STARTED, {})
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "diarization",
                "progress": 33,
                "message": "Identifying speakers..."
            })
            
            diarization_result = self.diarizer.diarize(audio_path)
            self.current_diarization = diarization_result
            
            self.emitter.emit(EventType.DIARIZATION_COMPLETED, {
                "num_speakers": diarization_result.get('num_speakers', 0),
                "segments": len(diarization_result.get('segments', []))
            })
            
            # Step 3: Merge transcription with speaker labels
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "merging",
                "progress": 50,
                "message": "Merging transcript with speaker labels..."
            })
            
            merged_transcript = self.transcriber.merge_with_diarization(
                transcript_result,
                diarization_result
            )
            self.current_transcript = merged_transcript
            
            # Step 4: Extract speaker audio samples
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "extracting_samples",
                "progress": 60,
                "message": "Extracting speaker voice samples..."
            })
            
            speaker_samples = self.qa_engine.extract_speaker_samples(
                audio_path,
                diarization_result
            )
            
            # Step 5: Generate Q&A questions
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "generating_questions",
                "progress": 70,
                "message": "Analyzing transcript for clarifications..."
            })
            
            questions = self.qa_engine.generate_questions(merged_transcript)
            
            # Processing complete - ready for Q&A
            self.state = AppState.QA_SESSION
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "qa_ready",
                "progress": 80,
                "message": "Ready for Q&A session"
            })
            
            self.emitter.emit(EventType.QA_SESSION_STARTED, {
                "num_speakers": len(speaker_samples),
                "num_questions": len(questions),
                "speaker_samples": speaker_samples,
                "questions": questions,
                "transcript": merged_transcript
            })
            
            # Note: Q&A session is handled by UI
            # When Q&A is complete, UI calls finalize_meeting()
            
        except Exception as e:
            self.state = AppState.ERROR
            self.emitter.emit(EventType.PROCESSING_ERROR, {
                "error": str(e),
                "step": "pipeline"
            })
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== Q&A Session Methods ====================
    
    def set_speaker_name(self, speaker_id: str, name: str):
        """Set the name for a detected speaker"""
        self.speaker_names[speaker_id] = name
        self.emitter.emit(EventType.QA_ANSWER_RECEIVED, {
            "type": "speaker_name",
            "speaker_id": speaker_id,
            "name": name
        })
    
    def answer_question(self, question_id: str, answer: str):
        """Record an answer to a Q&A question"""
        self.current_qa_responses[question_id] = answer
        self.emitter.emit(EventType.QA_ANSWER_RECEIVED, {
            "type": "clarification",
            "question_id": question_id,
            "answer": answer
        })
    
    def skip_qa_session(self):
        """Skip the Q&A session and generate summary with defaults"""
        self.emitter.emit(EventType.QA_SESSION_SKIPPED, {})
        self.finalize_meeting()
    
    # ==================== Final Summary Generation ====================
    
    def finalize_meeting(self) -> Dict[str, Any]:
        """
        Generate final meeting notes with Q&A answers incorporated
        
        Returns:
            dict: Final meeting output with transcript, summary, action items
        """
        if self.state not in [AppState.QA_SESSION, AppState.PROCESSING]:
            print(f"Cannot finalize in state: {self.state}")
            return {}
        
        try:
            self.state = AppState.GENERATING
            self.emitter.emit(EventType.SUMMARY_STARTED, {})
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "generating_summary",
                "progress": 90,
                "message": "Generating final meeting notes..."
            })
            
            # Apply speaker names to transcript
            final_transcript = self._apply_speaker_names(self.current_transcript)
            
            # Generate summary with Q&A context
            summary_result = self.summarizer.generate_summary(
                transcript=final_transcript,
                qa_responses=self.current_qa_responses,
                speaker_names=self.speaker_names
            )
            
            self.current_summary = summary_result
            
            # Create final meeting object
            meeting_data = {
                "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "created_at": datetime.now().isoformat(),
                "audio_path": self.current_recording_path,
                "transcript": final_transcript,
                "summary": summary_result.get("summary", ""),
                "key_points": summary_result.get("key_points", ""),
                "action_items": summary_result.get("action_items", []),
                "speaker_names": self.speaker_names,
                "qa_responses": self.current_qa_responses,
                "language": self.current_transcript.get("language", "unknown")
            }
            
            # Save meeting
            self._save_meeting(meeting_data)
            
            self.state = AppState.IDLE
            self.emitter.emit(EventType.SUMMARY_COMPLETED, meeting_data)
            self.emitter.emit(EventType.PROCESSING_COMPLETED, meeting_data)
            self.emitter.emit(EventType.PROCESSING_PROGRESS, {
                "step": "complete",
                "progress": 100,
                "message": "Meeting notes generated!"
            })
            
            return meeting_data
            
        except Exception as e:
            self.state = AppState.ERROR
            self.emitter.emit(EventType.PROCESSING_ERROR, {
                "error": str(e),
                "step": "finalize"
            })
            print(f"Error finalizing meeting: {e}")
            return {}
    
    def _apply_speaker_names(self, transcript: Dict) -> Dict:
        """Replace speaker IDs with actual names in transcript"""
        if not self.speaker_names:
            return transcript
        
        # Deep copy transcript
        import copy
        result = copy.deepcopy(transcript)
        
        # Replace in segments
        for segment in result.get("segments", []):
            speaker_id = segment.get("speaker", "")
            if speaker_id in self.speaker_names:
                segment["speaker"] = self.speaker_names[speaker_id]
                segment["original_speaker_id"] = speaker_id
        
        # Replace in full text
        full_text = result.get("text", "")
        for speaker_id, name in self.speaker_names.items():
            full_text = full_text.replace(f"[{speaker_id}]", f"[{name}]")
        result["text"] = full_text
        
        return result
    
    def _save_meeting(self, meeting_data: Dict):
        """Save meeting data to file"""
        import json
        
        meeting_id = meeting_data["id"]
        meeting_dir = Path(self.config.storage.meetings_dir) / meeting_id
        meeting_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON data
        json_path = meeting_dir / "meeting.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(meeting_data, f, indent=2, ensure_ascii=False)
        
        # Save human-readable transcript
        txt_path = meeting_dir / "transcript.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(self._format_transcript_text(meeting_data))
        
        # Move audio file if configured to save
        if self.config.storage.save_audio and self.current_recording_path:
            import shutil
            audio_dest = meeting_dir / Path(self.current_recording_path).name
            if Path(self.current_recording_path).exists():
                shutil.copy2(self.current_recording_path, audio_dest)
        
        print(f"Meeting saved to: {meeting_dir}")
    
    def _format_transcript_text(self, meeting_data: Dict) -> str:
        """Format meeting data as readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append("MEETINGMIND - MEETING NOTES")
        lines.append(f"Generated: {meeting_data['created_at']}")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(meeting_data.get("summary", "No summary generated"))
        lines.append("")
        
        # Key Points
        lines.append("KEY POINTS")
        lines.append("-" * 80)
        lines.append(meeting_data.get("key_points", "No key points identified"))
        lines.append("")
        
        # Action Items
        lines.append("ACTION ITEMS")
        lines.append("-" * 80)
        action_items = meeting_data.get("action_items", [])
        if isinstance(action_items, list):
            for item in action_items:
                if isinstance(item, dict):
                    lines.append(f"• {item.get('description', item)}")
                    if item.get('assignee'):
                        lines.append(f"  Assignee: {item['assignee']}")
                else:
                    lines.append(f"• {item}")
        else:
            lines.append(str(action_items))
        lines.append("")
        
        # Transcript
        lines.append("FULL TRANSCRIPT")
        lines.append("-" * 80)
        transcript = meeting_data.get("transcript", {})
        for segment in transcript.get("segments", []):
            speaker = segment.get("speaker", "Unknown")
            text = segment.get("text", "")
            start = segment.get("start", 0)
            lines.append(f"[{self._format_time(start)}] {speaker}: {text}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    # ==================== Utility Methods ====================
    
    def reset(self):
        """Reset controller state for new session"""
        self.state = AppState.IDLE
        self.current_recording_path = None
        self.current_transcript = None
        self.current_diarization = None
        self.current_summary = None
        self.current_qa_responses = {}
        self.speaker_names = {}
    
    def get_state(self) -> AppState:
        """Get current application state"""
        return self.state
    
    def get_available_audio_devices(self) -> List[Dict]:
        """Get list of available audio devices"""
        return self.audio_service.list_devices()
    
    # ==================== Meeting Detection & Auto-Record ====================
    
    def enable_auto_record(self):
        """Enable automatic recording when meetings are detected"""
        self._auto_record_enabled = True
        
        def on_meeting_status(is_active: bool, app_name: str):
            """Callback when meeting status changes"""
            if is_active and not self._was_in_meeting:
                # Meeting started
                self._was_in_meeting = True
                self.current_meeting_app = app_name
                self.emitter.emit(EventType.RECORDING_STARTED, {
                    "auto_detected": True,
                    "app": app_name,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"Meeting detected in {app_name}, starting recording...")
                self.start_recording()
                
            elif not is_active and self._was_in_meeting:
                # Meeting ended
                self._was_in_meeting = False
                self.emitter.emit(EventType.RECORDING_STOPPED, {
                    "auto_detected": True,
                    "app": self.current_meeting_app
                })
                print(f"Meeting ended, stopping recording...")
                audio_path = self.stop_recording()
                if audio_path:
                    # Auto-process the recording
                    self.process_audio(audio_path)
        
        self.meeting_detector.start_monitoring(callback=on_meeting_status)
        self.state = AppState.MONITORING
        print("Auto-record enabled, monitoring for meetings...")
    
    def disable_auto_record(self):
        """Disable automatic recording"""
        self._auto_record_enabled = False
        self.meeting_detector.stop_monitoring()
        if self.state == AppState.MONITORING:
            self.state = AppState.IDLE
        print("Auto-record disabled")
    
    def is_auto_record_enabled(self) -> bool:
        """Check if auto-record is enabled"""
        return self._auto_record_enabled
    
    def check_running_meetings(self) -> List[Dict]:
        """Check which meeting apps are currently running"""
        return self.meeting_detector.check_running_meetings()
    
    # ==================== Template Methods ====================
    
    def set_template(self, template_name: str):
        """Set the current meeting template"""
        if self.template_manager.get_template(template_name):
            self.current_template = template_name
            print(f"Template set to: {template_name}")
        else:
            print(f"Unknown template: {template_name}")
    
    def get_template(self, name: str = None):
        """Get a meeting template"""
        return self.template_manager.get_template(name or self.current_template)
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return self.template_manager.list_templates()
    
    def get_template_qa_prompts(self, template_name: str = None) -> List[str]:
        """Get Q&A prompts for current/specified template"""
        return self.template_manager.get_qa_prompts(template_name or self.current_template)
    
    # ==================== Export Methods ====================
    
    def export_meeting(
        self,
        meeting_data: Dict[str, Any],
        output_path: str,
        format: str = "markdown"
    ) -> str:
        """
        Export a meeting to various formats
        
        Args:
            meeting_data: Meeting data dictionary
            output_path: Output file path (without extension)
            format: Export format (markdown, html, json, docx, pdf)
        
        Returns:
            Path to exported file
        """
        return self.export_service.export(meeting_data, output_path, format)
    
    def export_current_meeting(self, output_path: str, format: str = "markdown") -> str:
        """Export the current meeting session"""
        if not self.current_summary:
            print("No current meeting to export")
            return ""
        
        meeting_data = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "created_at": datetime.now().isoformat(),
            "audio_path": self.current_recording_path,
            "transcript": self.current_transcript,
            "summary": self.current_summary.get("summary", ""),
            "key_points": self.current_summary.get("key_points", ""),
            "action_items": self.current_summary.get("action_items", []),
            "speaker_names": self.speaker_names,
            "qa_responses": self.current_qa_responses
        }
        
        return self.export_meeting(meeting_data, output_path, format)
    
    # ==================== History Methods ====================
    
    def save_to_history(self, meeting_data: Dict[str, Any], title: str = None) -> str:
        """Save a meeting to history"""
        return self.history_service.save_meeting(
            meeting_data,
            audio_path=meeting_data.get('audio_path'),
            title=title
        )
    
    def get_meeting_history(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get meeting history list"""
        records = self.history_service.list_meetings(limit, offset)
        return [
            {
                "id": r.id,
                "title": r.title,
                "date": r.date,
                "duration_seconds": r.duration_seconds,
                "participants": r.participants,
                "summary_preview": r.summary_preview,
                "meeting_type": r.meeting_type
            }
            for r in records
        ]
    
    def search_history(
        self,
        query: str = None,
        participant: str = None,
        date_from: str = None,
        date_to: str = None
    ) -> List[Dict]:
        """Search meeting history"""
        records = self.history_service.search_meetings(
            query=query,
            participant=participant,
            date_from=date_from,
            date_to=date_to
        )
        return [
            {
                "id": r.id,
                "title": r.title,
                "date": r.date,
                "summary_preview": r.summary_preview,
                "participants": r.participants
            }
            for r in records
        ]
    
    def get_history_meeting(self, meeting_id: str) -> Optional[Dict]:
        """Get full meeting data from history"""
        return self.history_service.get_meeting(meeting_id)
    
    def delete_from_history(self, meeting_id: str) -> bool:
        """Delete a meeting from history"""
        return self.history_service.delete_meeting(meeting_id)
    
    def get_history_statistics(self) -> Dict[str, Any]:
        """Get meeting history statistics"""
        return self.history_service.get_statistics()
    
    # ==================== Real-Time Transcription ====================
    
    def start_live_transcription(
        self,
        device_id: int = None,
        callback: Callable[[str, float], None] = None
    ) -> bool:
        """
        Start recording with real-time transcription
        
        Args:
            device_id: Audio device to record from
            callback: Called with (text, timestamp) for each transcribed segment
        """
        if self.state not in [AppState.IDLE, AppState.MONITORING]:
            print(f"Cannot start live transcription in state: {self.state}")
            return False
        
        try:
            # Start recording
            self.audio_service.start_recording(device_id=device_id)
            
            # Start real-time transcriber
            def on_transcript(text: str, timestamp: float, word_timestamps: List):
                if callback:
                    callback(text, timestamp)
                self.emitter.emit(EventType.TRANSCRIPTION_COMPLETED, {
                    "text": text,
                    "timestamp": timestamp,
                    "live": True
                })
            
            self.realtime_transcriber.start(
                sample_rate=self.config.audio.sample_rate,
                callback=on_transcript
            )
            
            self.state = AppState.LIVE_TRANSCRIBING
            self.emitter.emit(EventType.RECORDING_STARTED, {
                "live_transcription": True,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.state = AppState.ERROR
            self.emitter.emit(EventType.ERROR, {"error": str(e)})
            return False
    
    def stop_live_transcription(self) -> Optional[str]:
        """Stop live transcription and return audio file path"""
        if self.state != AppState.LIVE_TRANSCRIBING:
            return self.stop_recording()
        
        try:
            # Stop real-time transcriber
            self.realtime_transcriber.stop()
            
            # Stop recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{timestamp}.wav"
            output_path = str(TEMP_DIR / filename)
            
            self.audio_service.stop_recording(output_path)
            self.current_recording_path = output_path
            self.state = AppState.IDLE
            
            self.emitter.emit(EventType.RECORDING_STOPPED, {
                "file_path": output_path
            })
            
            return output_path
            
        except Exception as e:
            self.state = AppState.ERROR
            return None
    
    def feed_audio_chunk(self, audio_data: bytes):
        """Feed audio data to real-time transcriber"""
        if self._realtime_transcriber:
            self.realtime_transcriber.feed_audio(audio_data)
    
    # ==================== Highlights ====================
    
    def add_highlight(
        self,
        timestamp: float,
        text: str,
        highlight_type: str = "manual",
        speaker: str = None
    ):
        """Add a highlight to the current meeting"""
        from services.highlights import HighlightType
        
        hl_type = HighlightType(highlight_type) if isinstance(highlight_type, str) else highlight_type
        self.highlights_manager.add_highlight(
            timestamp=timestamp,
            text=text,
            highlight_type=hl_type,
            speaker=speaker
        )
        
        self.emitter.emit(EventType.QA_ANSWER_RECEIVED, {
            "type": "highlight",
            "timestamp": timestamp,
            "text": text,
            "highlight_type": highlight_type
        })
    
    def get_highlights(self) -> List[Dict]:
        """Get all highlights for current meeting"""
        return [h.to_dict() for h in self.highlights_manager.get_all_highlights()]
    
    def auto_detect_highlights(self, transcript: Dict = None):
        """Auto-detect important moments from transcript"""
        transcript = transcript or self.current_transcript
        if transcript:
            self.highlights_manager.auto_detect_highlights(transcript)
    
    def extract_highlight_clip(
        self,
        highlight_id: str,
        audio_path: str = None,
        padding_seconds: float = 3.0
    ) -> Optional[str]:
        """Extract audio clip for a highlight"""
        audio_path = audio_path or self.current_recording_path
        if not audio_path:
            return None
        return self.highlights_manager.extract_highlight_clip(
            highlight_id=highlight_id,
            audio_path=audio_path,
            output_dir=str(TEMP_DIR / "clips"),
            padding_seconds=padding_seconds
        )
    
    # ==================== Analytics ====================
    
    def get_meeting_analytics(self, meeting_data: Dict = None) -> Dict[str, Any]:
        """Get analytics for a meeting"""
        if meeting_data:
            return self.analytics.analyze_meeting(meeting_data)
        elif self.current_transcript:
            return self.analytics.analyze_meeting({
                "transcript": self.current_transcript,
                "summary": self.current_summary or {},
                "speaker_names": self.speaker_names
            })
        return {}
    
    def get_overall_analytics(self) -> Dict[str, Any]:
        """Get overall meeting analytics and trends"""
        return {
            "stats": self.analytics.get_overall_stats(),
            "trends": self.analytics.get_meeting_trends(),
            "productivity": self.analytics.get_productivity_report()
        }
    
    def get_speaker_analytics(self, speaker: str = None) -> Dict[str, Any]:
        """Get analytics for a specific speaker or all speakers"""
        if speaker:
            return self.analytics.get_speaker_stats(speaker)
        return self.analytics.get_all_speaker_stats()
    
    # ==================== Meeting Chat ====================
    
    def chat_about_meetings(self, question: str) -> str:
        """Ask questions about past meetings"""
        return self.meeting_chat.chat(question)
    
    def search_meetings_semantic(self, query: str, limit: int = 5) -> List[Dict]:
        """Semantic search across meeting history"""
        return self.meeting_chat.search_meetings(query, limit)
    
    def get_meeting_context(self, meeting_id: str) -> Dict:
        """Get context for a specific meeting for chat"""
        return self.meeting_chat.get_meeting_context(meeting_id)
    
    def clear_chat_memory(self):
        """Clear chat conversation memory"""
        self.meeting_chat.clear_memory()
    
    # ==================== Integrations ====================
    
    def configure_integration(
        self,
        platform: str,
        **config
    ):
        """
        Configure an integration
        
        Examples:
            configure_integration('slack', webhook_url='https://...')
            configure_integration('notion', api_key='...', database_id='...')
            configure_integration('email', smtp_server='...', username='...')
        """
        self.integrations.configure(platform, **config)
    
    def send_to_integration(
        self,
        platform: str,
        meeting_data: Dict = None,
        **kwargs
    ) -> bool:
        """
        Send meeting to an integration platform
        
        Args:
            platform: 'slack', 'teams', 'notion', 'email'
            meeting_data: Meeting data (uses current if None)
            **kwargs: Additional platform-specific options
        """
        data = meeting_data or {
            "summary": self.current_summary,
            "transcript": self.current_transcript,
            "highlights": self.get_highlights()
        }
        
        return self.integrations.send(platform, data, **kwargs)
    
    def test_integration(self, platform: str) -> bool:
        """Test an integration connection"""
        return self.integrations.test_connection(platform)
    
    # ==================== Keyboard Shortcuts ====================
    
    def enable_shortcuts(self):
        """Enable global keyboard shortcuts"""
        self.shortcuts.start()
        print("Keyboard shortcuts enabled")
        print(self.shortcuts.get_shortcuts_help())
    
    def disable_shortcuts(self):
        """Disable global keyboard shortcuts"""
        self.shortcuts.stop()
    
    def set_shortcut(self, action: str, key_combo: str):
        """Change a keyboard shortcut"""
        from services.shortcuts import ShortcutAction
        try:
            action_enum = ShortcutAction(action)
            self.shortcuts.set_shortcut(action_enum, key_combo)
        except ValueError:
            print(f"Unknown action: {action}")
    
    def get_shortcuts_list(self) -> Dict[str, Dict]:
        """Get all keyboard shortcuts"""
        return self.shortcuts.list_shortcuts()
    
    # ==================== Calendar Integration ====================
    
    def sync_calendar(self, provider: str = "google", days_ahead: int = 7):
        """
        Sync calendar events
        
        Args:
            provider: 'google', 'outlook', or 'ical'
            days_ahead: Number of days to sync
        """
        if provider == "google":
            return self.calendar.sync_google_calendar(days_ahead)
        elif provider == "outlook":
            return self.calendar.sync_outlook_calendar(days_ahead)
        return []
    
    def import_ical(self, ical_path: str):
        """Import events from iCal file"""
        return self.calendar.import_ical(ical_path)
    
    def get_current_calendar_event(self):
        """Get the calendar event happening now"""
        event = self.calendar.get_current_meeting()
        if event:
            self.current_calendar_event = event
        return event
    
    def get_upcoming_meetings(self, hours: int = 24) -> List[Dict]:
        """Get upcoming meetings from calendar"""
        events = self.calendar.get_upcoming_meetings(hours)
        return [e.to_dict() for e in events]
    
    def get_calendar_context_for_recording(self) -> Dict:
        """Get calendar context to pre-populate meeting info"""
        event = self.get_current_calendar_event()
        if event:
            return self.calendar.get_meeting_context(event)
        return {}
    
    def configure_google_calendar(self, credentials_file: str):
        """Configure Google Calendar integration"""
        self.calendar.configure_google(credentials_file)
    
    def configure_outlook_calendar(self, client_id: str, client_secret: str):
        """Configure Outlook Calendar integration"""
        self.calendar.configure_outlook(client_id, client_secret)
