# MeetingMind - Technical Design Document

## Overview

This document outlines the technical implementation details for MeetingMind v2.0.

---

## 🏗️ System Architecture

### High-Level Components

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
│  │  System Tray   │  │   Gradio UI    │  │  Notification  │         │
│  │  (pystray)     │  │   (Web)        │  │  (plyer)       │         │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘         │
└──────────┼───────────────────┼───────────────────┼───────────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    MeetingMindController                        │ │
│  │  • Orchestrates all operations                                  │ │
│  │  • Manages state (idle, recording, processing)                  │ │
│  │  • Handles events and callbacks                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                                 │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │AudioCapture  │  │ Transcriber  │  │  Diarizer    │              │
│  │Service       │  │ Service      │  │  Service     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Summarizer   │  │   Q&A        │  │  Export      │              │
│  │ Service      │  │   Engine     │  │  Service     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐                                 │
│  │ Meeting      │  │  Storage     │                                 │
│  │ Detector     │  │  Service     │                                 │
│  └──────────────┘  └──────────────┘                                 │
└──────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE LAYER                          │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Whisper    │  │  pyannote    │  │   Ollama     │              │
│  │   (STT)      │  │  (Diarize)   │  │   (LLM)      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  WASAPI      │  │   FFmpeg     │  │  SQLite      │              │
│  │  (Audio)     │  │  (Convert)   │  │  (Storage)   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure (v2.0)

```
MeetingMind/
│
├── app.py                      # Main entry point
├── main.py                     # Desktop app launcher
│
├── core/                       # Core application logic
│   ├── __init__.py
│   ├── controller.py           # Main orchestrator
│   ├── config.py               # Configuration management
│   └── events.py               # Event system
│
├── services/                   # Service modules
│   ├── __init__.py
│   ├── audio_capture.py        # System audio recording
│   ├── transcriber.py          # Whisper transcription
│   ├── diarizer.py             # Speaker diarization
│   ├── summarizer.py           # LLM summarization
│   ├── qa_engine.py            # Post-meeting Q&A
│   ├── meeting_detector.py     # Detect meeting apps
│   ├── storage.py              # Data persistence
│   └── exporter.py             # Export formats
│
├── ui/                         # User interface
│   ├── __init__.py
│   ├── gradio_app.py           # Web UI
│   ├── system_tray.py          # System tray icon
│   └── notifications.py        # Desktop notifications
│
├── models/                     # Data models
│   ├── __init__.py
│   ├── meeting.py              # Meeting data class
│   ├── transcript.py           # Transcript data class
│   └── speaker.py              # Speaker data class
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── audio_utils.py          # Audio processing helpers
│   ├── file_utils.py           # File operations
│   └── time_utils.py           # Time formatting
│
├── data/                       # Local data storage
│   ├── meetings/               # Saved meeting files
│   ├── profiles/               # Speaker voice profiles
│   └── config.json             # User configuration
│
├── tests/                      # Unit tests
│   ├── test_audio_capture.py
│   ├── test_transcriber.py
│   ├── test_diarizer.py
│   └── test_qa_engine.py
│
├── docs/                       # Documentation
│   ├── PRD.md                  # Product requirements
│   ├── TECHNICAL_DESIGN.md     # This file
│   ├── PROJECT_TRACKER.md      # Sprint tracking
│   ├── ARCHITECTURE.md         # Architecture overview
│   ├── API.md                  # API reference
│   └── ROADMAP.md              # Future plans
│
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── README.md                   # Project readme
├── CONTRIBUTING.md             # Contribution guide
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```

---

## 🔧 Component Details

### 1. Audio Capture Service

**File:** `services/audio_capture.py`

**Purpose:** Capture system audio (WASAPI loopback) on Windows

**Technology:**
- `sounddevice` with WASAPI backend
- `pyaudiowpatch` for Windows audio loopback
- `numpy` for audio buffer handling

**Interface:**
```python
class AudioCaptureService:
    def __init__(self, sample_rate: int = 16000)
    def list_devices(self) -> List[AudioDevice]
    def start_recording(self, device_id: int = None) -> None
    def stop_recording(self) -> str  # Returns file path
    def is_recording(self) -> bool
    def get_duration(self) -> float
```

**Key Implementation Details:**
- Uses WASAPI loopback to capture system audio
- Captures at 16kHz mono (Whisper optimal)
- Saves to WAV format
- Thread-safe recording with queue

---

### 2. Diarizer Service

**File:** `services/diarizer.py`

**Purpose:** Identify different speakers in audio

**Technology:**
- `pyannote.audio` (offline speaker diarization)
- Hugging Face model: `pyannote/speaker-diarization-3.1`

**Interface:**
```python
class DiarizerService:
    def __init__(self, model_name: str = "pyannote/speaker-diarization-3.1")
    def diarize(self, audio_path: str) -> List[SpeakerSegment]
    def get_speaker_count(self) -> int
```

**Output Format:**
```python
[
    SpeakerSegment(start=0.0, end=5.2, speaker="SPEAKER_00"),
    SpeakerSegment(start=5.2, end=12.8, speaker="SPEAKER_01"),
    SpeakerSegment(start=12.8, end=18.5, speaker="SPEAKER_00"),
    ...
]
```

**Note:** Requires Hugging Face token for first download (free)

---

### 3. Transcriber Service (Enhanced)

**File:** `services/transcriber.py`

**Purpose:** Transcribe audio with speaker attribution

**Enhancement:** Merge Whisper output with diarization

**Interface:**
```python
class TranscriberService:
    def __init__(self, model_name: str = "base")
    def transcribe(self, audio_path: str) -> TranscriptResult
    def transcribe_with_speakers(
        self, 
        audio_path: str, 
        diarization: List[SpeakerSegment]
    ) -> TranscriptResult
```

**Output Format:**
```python
TranscriptResult(
    text="Full transcript...",
    segments=[
        TranscriptSegment(
            start=0.0,
            end=5.2,
            text="Hello everyone, let's get started.",
            speaker="SPEAKER_00"
        ),
        ...
    ],
    speakers=["SPEAKER_00", "SPEAKER_01"],
    language="en"
)
```

---

### 4. Q&A Engine

**File:** `services/qa_engine.py`

**Purpose:** Generate clarifying questions after meeting

**Technology:**
- Ollama LLM for question generation
- Pattern matching for common ambiguities

**Interface:**
```python
class QAEngine:
    def __init__(self, model_name: str = "llama3.2")
    def analyze_transcript(self, transcript: TranscriptResult) -> List[Question]
    def process_answer(self, question_id: str, answer: str) -> None
    def get_enhanced_summary(self) -> EnhancedSummary
```

**Question Types:**
```python
class QuestionType(Enum):
    AMBIGUOUS_REFERENCE = "ambiguous"      # "the deadline" - which one?
    MISSING_DETAIL = "missing"              # "John will do it" - do what?
    UNCLEAR_OWNERSHIP = "ownership"         # Who is responsible?
    DATE_CLARIFICATION = "date"             # Specific dates/times
    ACRONYM_EXPANSION = "acronym"           # What does XYZ mean?
    ACTION_CONFIRMATION = "action"          # Confirm action items
```

**Example Questions Generated:**
```python
[
    Question(
        id="q1",
        type=QuestionType.DATE_CLARIFICATION,
        text="You mentioned 'the deadline' - what is the specific date?",
        context="We need to finish before the deadline",
        speaker="SPEAKER_01"
    ),
    Question(
        id="q2", 
        type=QuestionType.UNCLEAR_OWNERSHIP,
        text="Who is 'John' that was mentioned? (John Smith from Engineering or John Doe from Sales?)",
        context="John will handle the client presentation",
        speaker="SPEAKER_00"
    )
]
```

---

### 5. Meeting Detector

**File:** `services/meeting_detector.py`

**Purpose:** Detect when meeting apps start/end

**Technology:**
- `psutil` for process monitoring
- Windows API for window detection

**Interface:**
```python
class MeetingDetector:
    def __init__(self)
    def start_monitoring(self, callback: Callable) -> None
    def stop_monitoring(self) -> None
    def get_active_meeting_app(self) -> Optional[str]
```

**Detected Applications:**
- Microsoft Teams
- Zoom
- Google Meet (Chrome)
- Slack Huddle
- Discord
- WebEx

---

### 6. System Tray UI

**File:** `ui/system_tray.py`

**Purpose:** System tray application for quick access

**Technology:**
- `pystray` for system tray
- `Pillow` for icon generation

**Interface:**
```python
class SystemTrayApp:
    def __init__(self, controller: MeetingMindController)
    def run(self) -> None
    def update_status(self, status: str) -> None
    def show_notification(self, title: str, message: str) -> None
```

**Menu Items:**
```
┌─────────────────────────┐
│ 🔴 Start Recording      │
│ ⬛ Stop Recording       │
│ ─────────────────────── │
│ 📁 Open Meetings Folder │
│ ⚙️ Settings             │
│ 📖 Open Full UI         │
│ ─────────────────────── │
│ ❌ Exit                 │
└─────────────────────────┘
```

---

## 🔄 Data Flow

### Recording Flow
```
1. User clicks "Start Recording"
   │
2. AudioCaptureService.start_recording()
   │ └── WASAPI loopback captures system audio
   │ └── Audio buffered to memory/temp file
   │
3. User clicks "Stop Recording"
   │
4. AudioCaptureService.stop_recording()
   │ └── Returns path to WAV file
   │
5. Controller triggers processing pipeline
```

### Processing Flow
```
1. Audio file ready
   │
2. DiarizerService.diarize(audio_path)
   │ └── Returns List[SpeakerSegment]
   │
3. TranscriberService.transcribe_with_speakers(audio_path, segments)
   │ └── Returns TranscriptResult with speaker labels
   │
4. SummarizerService.summarize(transcript)
   │ └── Returns Summary, KeyPoints, ActionItems
   │
5. QAEngine.analyze_transcript(transcript)
   │ └── Returns List[Question]
   │
6. UI displays results + Q&A dialog
   │
7. User answers questions (optional)
   │
8. QAEngine.get_enhanced_summary()
   │ └── Returns enhanced summary with clarifications
   │
9. StorageService.save_meeting(meeting_data)
```

---

## 💾 Data Models

### Meeting Model
```python
@dataclass
class Meeting:
    id: str
    created_at: datetime
    audio_path: str
    duration: float
    transcript: TranscriptResult
    summary: Summary
    action_items: List[ActionItem]
    qa_responses: Dict[str, str]
    speakers: Dict[str, str]  # SPEAKER_00 -> "John Smith"
    metadata: Dict[str, Any]
```

### Action Item Model
```python
@dataclass
class ActionItem:
    id: str
    description: str
    assignee: Optional[str]  # Speaker name
    due_date: Optional[str]
    status: str  # "pending", "completed"
    source_segment: TranscriptSegment
```

---

## ⚙️ Configuration

**File:** `data/config.json`

```json
{
    "whisper": {
        "model": "base",
        "language": null
    },
    "ollama": {
        "model": "llama3.2",
        "host": "http://localhost:11434"
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "device_id": null
    },
    "diarization": {
        "model": "pyannote/speaker-diarization-3.1",
        "min_speakers": 1,
        "max_speakers": 10
    },
    "ui": {
        "theme": "light",
        "auto_process": true,
        "show_notifications": true
    },
    "storage": {
        "meetings_dir": "./data/meetings",
        "max_storage_gb": 10,
        "auto_cleanup_days": 30
    }
}
```

---

## 🔒 Security Considerations

1. **No Network Calls** - All processing is local
2. **No Telemetry** - No usage data collected
3. **Local Storage Only** - Files stay on user's machine
4. **Memory Cleanup** - Audio buffers cleared after processing
5. **File Permissions** - Standard user permissions only

---

## 📦 Dependencies

### Production
```
openai-whisper>=20231117
pyannote.audio>=3.1.0
gradio>=4.0.0
ollama>=0.1.0
torch>=2.0.0
numpy>=1.24.0
sounddevice>=0.4.6
pyaudiowpatch>=0.2.12  # Windows only
pystray>=0.19.0
Pillow>=10.0.0
plyer>=2.1.0
psutil>=5.9.0
ffmpeg-python>=0.2.0
```

### Development
```
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
```

---

## 🧪 Testing Strategy

### Unit Tests
- Each service module has corresponding test file
- Mock external dependencies (Whisper, Ollama)
- Test edge cases (empty audio, single speaker, etc.)

### Integration Tests
- Full pipeline tests with sample audio
- System tray functionality
- UI interactions

### Manual Testing
- Real meeting recordings
- Various audio qualities
- Multiple speakers

---

## 🚀 Deployment

### Development
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
python app.py
```

### Production (Future)
- PyInstaller for .exe packaging
- Inno Setup for Windows installer
- Auto-update mechanism (future)

---

*Document Version: 1.0*
*Last Updated: January 10, 2026*
