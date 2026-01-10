# MeetingMind v2.1 Architecture

## Overview

MeetingMind is a fully offline meeting assistant with a modular, event-driven architecture that enables:
- System audio capture from Teams/Zoom with auto-detection
- Speaker diarization with audio snippet identification
- Q&A workflow for enhanced accuracy
- Meeting templates for different meeting types
- Multi-format export (MD, HTML, JSON, DOCX, PDF)
- Meeting history with search and statistics
- Standalone Windows EXE distribution

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MEETINGMIND v2.1                               │
├─────────────────────────────────────────────────────────────────────────┤
│    UI LAYER: Gradio App + System Tray                                    │
│                          │                                               │
│    CONTROLLER: AppState + EventEmitter + Config                          │
│                          │                                               │
│    SERVICES:                                                             │
│      Audio Capture | Transcriber | Diarizer | Q&A | Summarizer          │
│      Meeting Detector | Templates | Exporter | History                   │
│                          │                                               │
│    EXTERNAL: FFmpeg | Whisper Models | Ollama LLM | pyannote            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Layer (`core/`)

### `config.py` - Configuration management with dataclasses

### `events.py` - Pub/sub event system for real-time status updates

### `controller.py` - Main application orchestrator managing app state

## Services Layer (`services/`)

### `audio_capture.py` - Windows WASAPI loopback recording

### `transcriber.py` - Whisper transcription with speaker merge

### `diarizer.py` - pyannote-audio speaker diarization

### `qa_engine.py` - Q&A session with audio snippets

### `summarizer.py` - Ollama LLM summarization with Q&A context

### `meeting_detector.py` - Auto-detect Teams/Zoom/Meet/Webex (v2.1)

### `templates.py` - Meeting templates for standup, planning, retro (v2.1)

### `exporter.py` - Multi-format export: MD, HTML, JSON, DOCX, PDF (v2.1)

### `history.py` - Meeting history storage with search (v2.1)

## UI Layer (`ui/`)

### `gradio_app.py` - Full-featured web interface with 5 tabs

### `system_tray.py` - Windows system tray with recording controls

## Data Flow

1. **Detection** (Optional): MeetingDetector monitors for meeting apps
2. **Recording**: AudioCapture → WAV file
3. **Processing**: Transcriber + Diarizer → Merged transcript
4. **Q&A**: QAEngine generates speaker ID + clarification questions
5. **Summary**: Summarizer creates notes using template + Q&A context
6. **Storage**: History service saves meeting data
7. **Output**: Exporter generates MD/HTML/JSON/DOCX/PDF

## File Structure

```
MeetingMind/
├── main.py                 # Entry point
├── build.bat               # Windows EXE build script
├── build.py                # Python build script
├── meetingmind.spec        # PyInstaller configuration
├── core/                   # Core modules
│   ├── config.py
│   ├── controller.py
│   └── events.py
├── services/               # Service layer
│   ├── audio_capture.py
│   ├── transcriber.py
│   ├── diarizer.py
│   ├── qa_engine.py
│   ├── summarizer.py
│   ├── meeting_detector.py
│   ├── templates.py
│   ├── exporter.py
│   └── history.py
├── ui/                     # UI components
│   ├── gradio_app.py
│   └── system_tray.py
├── data/meetings/          # Saved meetings
├── assets/                 # Icons for EXE
└── docs/                   # Documentation
```

## Building Standalone EXE

```powershell
# Option 1: Using batch script
.\build.bat

# Option 2: Using Python script
python build.py

# Option 3: Manual PyInstaller
pyinstaller meetingmind.spec --noconfirm
```

The built EXE and all dependencies will be in `dist/MeetingMind/`.

