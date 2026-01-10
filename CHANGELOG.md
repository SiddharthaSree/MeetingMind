# Changelog

All notable changes to MeetingMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time transcription during recording
- Export to PDF/DOCX formats
- Custom summarization templates
- Speaker profile learning (remember voices)
- Batch processing for multiple files

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
| 1.0.0 | 2026-01-10 | Initial release with transcription, summarization, and recording |

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
