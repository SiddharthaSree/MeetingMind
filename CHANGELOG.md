# Changelog

All notable changes to MeetingMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time transcription during recording
- Speaker profile learning (remember voices)
- Batch processing for multiple files
- Cross-platform support (macOS, Linux)

---

## [2.1.0] - 2025-01-11

### 🚀 Phase 2 Features + Standalone EXE

### Added

#### 🤖 Auto-Detect Meetings (F8)
- **Meeting App Detection** - Automatically detects Teams, Zoom, Meet, Webex, Slack
- **Auto-Record Mode** - Optional auto-start recording when meetings begin
- **Auto-Process** - Automatically process recording when meeting ends
- **Process Monitoring** - Background monitoring for meeting applications

#### 📑 Meeting Templates (F11)
- **Template System** - Pre-configured templates for different meeting types
- **Standup Template** - Daily standup format (blockers, progress, plans)
- **Planning Template** - Sprint/project planning structure
- **Retrospective Template** - What went well, improvements, actions
- **One-on-One Template** - Manager/report meeting format
- **General Template** - Default all-purpose format
- **Custom Q&A Prompts** - Each template has specialized questions

#### 📥 Export Formats (F12)
- **Markdown Export** - Clean, portable format
- **HTML Export** - Styled web pages with embedded CSS
- **JSON Export** - Machine-readable format for integrations
- **DOCX Export** - Microsoft Word documents
- **PDF Export** - Professional reports (requires WeasyPrint)

#### 📚 Meeting History (F13)
- **History Storage** - Save and organize past meetings
- **Search** - Find meetings by title, participant, keyword
- **Date Filtering** - Filter by date range
- **Statistics** - Track total meetings, duration, participants
- **Quick Load** - Re-open and export any saved meeting
- **Delete Management** - Clean up old meetings

#### 🏗️ Standalone EXE Build
- **PyInstaller Support** - Build standalone Windows executable
- **build.bat** - One-click Windows build script
- **build.py** - Python build script for more control
- **meetingmind.spec** - PyInstaller configuration
- **Version Info** - Embedded version metadata in EXE

### Changed
- **Enhanced Controller** - Integrated all new services
- **Updated UI** - New tabs and features for history, templates, export
- **Improved History Tab** - Search, statistics, and meeting details

### New Files
- `services/meeting_detector.py` - Meeting app detection service
- `services/templates.py` - Meeting templates manager
- `services/exporter.py` - Multi-format export service
- `services/history.py` - Meeting history storage
- `build.bat` - Windows EXE build script
- `build.py` - Python build script
- `meetingmind.spec` - PyInstaller spec file
- `version_info.txt` - EXE version metadata

### Dependencies Added
- `psutil` - Process detection
- `python-docx` - DOCX export
- `weasyprint` - PDF export
- `pyinstaller` - EXE building

---

## [2.0.0] - 2025-01-11

### 🚀 Major Release - Full Meeting Assistant

### Added

#### 🎤 System Audio Capture
- **WASAPI Loopback Recording** - Capture audio from Teams, Zoom, or any app
- **pyaudiowpatch Integration** - Windows system audio support
- **Audio Device Selection** - Choose input device in settings
- **System Tray App** - Quick recording controls from taskbar

#### 🎯 Speaker Diarization
- **pyannote-audio Integration** - Offline speaker identification
- **Speaker Segmentation** - Know who said what and when
- **Audio Snippet Extraction** - Listen to clips to identify speakers

#### ❓ Q&A Workflow (Key Feature!)
- **Speaker Identification Flow** - Audio clips help name each speaker
- **Clarifying Questions** - AI asks questions to improve accuracy
- **Quick/Detailed Modes** - Choose 3-5 or 5-10 questions
- **Skip Options** - Skip individual questions or generate immediately

#### 📋 Enhanced Summaries
- **Q&A Context Integration** - Better summaries from user answers
- **Action Items with Assignees** - Tasks linked to specific people
- **Decision Tracking** - Key decisions highlighted
- **Export Options** - Markdown, JSON, clipboard

#### 🏗️ New Architecture
- **core/** - Config, events, controller modules
- **services/** - Modular service architecture
- **ui/** - Separated UI components
- **Event System** - Real-time status updates

### Changed
- Entry point changed to `main.py`
- Configuration via YAML/dataclasses
- Improved error handling throughout

### Technical
- Python 3.10+ (Windows recommended)
- New dependencies: pyannote.audio, pyaudiowpatch, pystray, soundfile

---

## [1.0.0] - 2025-01-10

### Added
- 🎉 **Initial Release**
- **Audio Upload** - Support for multiple formats (mp3, wav, m4a, mp4, webm, ogg, flac)
- **Audio Recording** - Built-in microphone recording directly in the UI
- **Whisper Transcription** - Offline transcription using OpenAI Whisper
  - Support for models: tiny, base, small, medium, large
  - Auto language detection
- **Ollama Summarization** - Local LLM-powered summaries
  - Support for llama3.2, llama3.1, mistral, llama2
  - Generates meeting summary, key points, and action items
- **Gradio UI** - Clean, modern web interface
  - Tabbed interface for upload vs record
  - Separate tabs for transcript, summary, key points, action items
  - Copy to clipboard buttons on all outputs
- **Save to File** - Export complete meeting notes to text files
  - Auto-generated filenames with timestamps
  - Saved to `meeting_outputs/` directory
- **100% Offline** - No API calls, no data leaves your machine
- **Model Selection** - Choose Whisper and Ollama models in UI

### Technical
- Python 3.10+ support
- Modular architecture (transcriber.py, summarizer.py, app.py)
- Error handling and status messages
- Comprehensive documentation

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 2.1.0 | 2025-01-11 | Auto-detect meetings, templates, multi-format export, history, EXE build |
| 2.0.0 | 2025-01-11 | System audio capture, speaker diarization, Q&A workflow |
| 1.0.0 | 2025-01-10 | Initial release with transcription, summarization, and recording |

---

## Upgrade Notes

### From 0.x to 1.0.0
This is the initial release, no upgrade needed.

### Future Upgrades
Future versions will include migration guides if breaking changes occur.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute changes.

## Reporting Issues

Found a bug? Please [open an issue](https://github.com/YOUR_USERNAME/MeetingMind/issues) with:
- Your environment (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
