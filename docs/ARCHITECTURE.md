# MeetingMind v2.0 Architecture

## Overview

MeetingMind is a fully offline meeting assistant with a modular, event-driven architecture that enables:
- System audio capture from Teams/Zoom
- Speaker diarization with audio snippet identification
- Q&A workflow for enhanced accuracy
- Intelligent summarization with action items

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MEETINGMIND v2.0                               │
├─────────────────────────────────────────────────────────────────────────┤
│    UI LAYER: Gradio App + System Tray                                    │
│                          │                                               │
│    CONTROLLER: AppState + EventEmitter + Config                          │
│                          │                                               │
│    SERVICES: Audio Capture | Transcriber | Diarizer | Q&A | Summarizer  │
│                          │                                               │
│    EXTERNAL: FFmpeg | Whisper Models | Ollama LLM                        │
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

## UI Layer (`ui/`)

### `gradio_app.py` - Full-featured web interface

### `system_tray.py` - Windows system tray with recording controls

## Data Flow

1. **Recording**: AudioCapture → WAV file
2. **Processing**: Transcriber + Diarizer → Merged transcript
3. **Q&A**: QAEngine generates speaker ID + clarification questions
4. **Summary**: Summarizer creates notes with Q&A context
5. **Output**: Markdown/JSON export

## File Structure

```
MeetingMind/
├── main.py                 # Entry point
├── core/                   # Core modules
├── services/               # Service layer
├── ui/                     # UI components
├── data/meetings/          # Saved meetings
└── docs/                   # Documentation
```

