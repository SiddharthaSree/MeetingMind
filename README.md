# 🎙️ MeetingMind

A **100% free, offline meeting notes assistant** that captures system audio from Teams/Zoom calls, transcribes with speaker identification, and generates intelligent summaries with action items - all running locally on your machine!

<p align="center">
  <a href="https://github.com/SiddharthaSree/MeetingMind/releases">
    <img src="https://img.shields.io/badge/Download-Windows%20EXE-blue?style=for-the-badge&logo=windows" alt="Download Windows">
  </a>
</p>

---

## 📥 Quick Download

| Platform | Download | Requirements |
|----------|----------|--------------|
| **Windows** | [📦 Download EXE](https://github.com/SiddharthaSree/MeetingMind/releases) | Windows 10/11, [Ollama](https://ollama.ai), [FFmpeg](https://ffmpeg.org) |

### First Time Setup
1. **Download** the latest release ZIP
2. **Extract** to any folder
3. **Install Ollama** from https://ollama.ai
4. **Open terminal** and run: `ollama pull llama3.2`
5. **Run** `MeetingMind.exe`
6. **Done!** 🎉

> 💡 See [INSTALL.md](INSTALL.md) for detailed setup instructions

---

## ✨ Features

### 🎤 Audio Capture
- **System Audio Recording** - Capture audio from Teams, Zoom, or any application (Windows WASAPI loopback)
- **Auto-Detect Meetings** - Automatically start recording when Teams/Zoom/Meet opens
- **Real-Time Transcription** - See text as you speak during meetings ⚡ NEW
- **Upload Support** - Drag & drop existing audio/video files
- **System Tray** - Quick recording controls from your taskbar

### 🎯 Transcription & Speaker ID
- **Accurate Transcription** - Uses OpenAI Whisper (runs 100% offline)
- **Speaker Diarization** - Identifies who's speaking using pyannote-audio
- **Audio Snippets** - Listen to clips to identify unknown speakers
- **Word-Level Timestamps** - Precise timing for each word ⚡ NEW

### 🌟 Highlights & Bookmarks ⚡ NEW
- **Manual Bookmarks** - Mark important moments with Ctrl+Shift+B
- **Auto-Detection** - AI identifies action items, decisions, questions
- **Clip Extraction** - Export audio clips for specific highlights
- **Quick Navigation** - Jump to highlighted moments

### 🤖 Smart Q&A Workflow
- **Speaker Identification** - Audio clips help you name each speaker
- **Clarifying Questions** - AI asks questions to improve note accuracy
- **Quick or Detailed Mode** - Choose 3-5 or 5-10 questions

### 📋 Intelligent Summaries
- **Smart Summaries** - Powered by Ollama LLMs (llama3.2, mistral, etc.)
- **Meeting Templates** - Standup, planning, retrospective, 1:1 templates
- **Action Items** - Automatically extracts tasks with assignees
- **Key Decisions** - Highlights important decisions made

### 💬 Meeting Chat ⚡ NEW
- **Ask Questions** - Query your past meetings with AI
- **Semantic Search** - Find meetings by meaning, not just keywords
- **Context-Aware** - Understands follow-up questions
- **Cross-Meeting Insights** - Find patterns across meetings

### 📊 Analytics Dashboard ⚡ NEW
- **Meeting Statistics** - Duration, participants, word count
- **Speaker Analytics** - Talk time per person
- **Meeting Trends** - Patterns by day, week, month
- **Productivity Score** - Based on action items and decisions

### 🔗 Integrations ⚡ NEW
- **Slack** - Send notes via webhook
- **Microsoft Teams** - Share to Teams channels
- **Notion** - Export to Notion databases
- **Email** - Send via SMTP
- **Calendar Sync** - Google Calendar & Outlook

### ⌨️ Keyboard Shortcuts ⚡ NEW
- **Ctrl+Shift+R** - Toggle recording
- **Ctrl+Shift+B** - Add bookmark
- **Ctrl+Shift+A** - Mark action item
- **Ctrl+Shift+D** - Mark decision

### 📥 Export Options
- **Markdown** - Clean, portable format
- **HTML** - Styled web pages
- **JSON** - For integrations
- **DOCX** - Word documents
- **PDF** - Professional reports

### 📚 Meeting History
- **Search & Browse** - Find past meetings by date, participant, or keyword
- **Statistics** - Track meeting duration and frequency
- **Quick Reload** - Re-open and export any saved meeting

### 🔒 Privacy First
- **100% Offline** - Everything runs locally, no API calls
- **No Data Collection** - Your meetings stay on your machine
- **Completely Free** - No API costs, no subscriptions

---

## 📋 Requirements

- **Windows 10/11** (for system audio capture)
- **Ollama** (local LLM runtime) - [Download](https://ollama.ai)
- **FFmpeg** (for audio processing) - [Download](https://ffmpeg.org)
- **8GB+ RAM** recommended (16GB for larger models)

---

## 🚀 Installation

### Option A: Download Pre-built EXE (Easiest!)

1. Go to [**Releases**](https://github.com/SiddharthaSree/MeetingMind/releases)
2. Download `MeetingMind-Windows.zip`
3. Extract the ZIP file
4. Install [Ollama](https://ollama.ai) and run `ollama pull llama3.2`
5. Double-click `MeetingMind.exe`
6. Your browser opens to http://localhost:7860

### Option B: Run from Source (For Developers)

#### 1. Install FFmpeg

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

### 2. Install Ollama

Download and install from: **https://ollama.ai**

**After installation, pull a model:**
```bash
ollama pull llama3.2
# or
ollama pull mistral
```

**Start Ollama server:**
```bash
ollama serve
```

> 💡 Keep the Ollama server running while using MeetingMind!

### 3. Clone/Download MeetingMind

```bash
cd MeetingMind
```

### 4. Install Python Dependencies

```powershell
# Create a virtual environment (recommended)
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate      # macOS/Linux

# Install packages
pip install -r requirements.txt
```

> ⏱️ First install may take 5-10 minutes (Whisper models are ~150MB)

### 5. Run the App

```powershell
python main.py
```

The app will open automatically in your browser at `http://127.0.0.1:7860`

A system tray icon will appear for quick recording controls!

## 🎯 How to Use

### Recording a Meeting

1. **Start Recording**
   - Click "🔴 Start Recording" in the web UI, OR
   - Right-click the system tray icon → "Start Recording"
   
2. **During the Meeting**
   - Join your Teams/Zoom call as normal
   - MeetingMind captures all system audio

3. **Stop Recording**
   - Click "⏹️ Stop Recording" when done
   - Processing starts automatically

### Q&A Workflow (Key Feature!)

After processing, you'll be guided through a Q&A session:

1. **Speaker Identification**
   - Listen to audio clips of each speaker
   - Enter their name (e.g., "John Smith")
   - This improves meeting notes accuracy

2. **Clarifying Questions**
   - AI asks about unclear action items, decisions
   - Answer or skip questions as needed
   - Choose "Skip All" to generate notes immediately

3. **Review Results**
   - Executive summary
   - Key points and decisions
   - Action items with assignees

### Uploading Existing Audio

1. Go to "📝 New Meeting" tab
2. Upload your audio/video file (mp3, wav, m4a, mp4, etc.)
3. Click "Process Upload"
4. Complete Q&A workflow
5. Export results

## 📁 Project Structure

```
MeetingMind/
├── main.py                 # Main entry point
├── app.py                  # Alternative entry (runs Gradio only)
├── build.bat               # Windows EXE build script
├── build.py                # Python build script
├── meetingmind.spec        # PyInstaller configuration
├── core/
│   ├── config.py          # Configuration management
│   ├── controller.py      # Main app controller (orchestrates all services)
│   └── events.py          # Event system for async communication
├── services/
│   ├── audio_capture.py   # WASAPI system audio recording
│   ├── transcriber.py     # Whisper transcription
│   ├── diarizer.py        # Speaker diarization
│   ├── summarizer.py      # Ollama summarization
│   ├── qa_engine.py       # Q&A generation & management
│   ├── meeting_detector.py # Auto-detect Teams/Zoom/Meet
│   ├── templates.py       # Meeting templates (standup, planning, etc.)
│   ├── exporter.py        # Export to MD/HTML/JSON/DOCX/PDF
│   └── history.py         # Meeting history storage & search
├── ui/
│   ├── gradio_app.py      # Web interface
│   └── system_tray.py     # System tray application
├── data/
│   ├── meetings/          # Saved meeting notes
│   └── profiles/          # Speaker profiles
├── assets/                 # Icons and images
├── docs/                   # Documentation
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

### Command Line Options

```powershell
python main.py --help

Options:
  --port, -p    Port to run web UI (default: 7860)
  --share       Create public share link
  --no-tray     Disable system tray icon
  --no-browser  Don't open browser automatically
  --check       Check dependencies and exit
```

### Q&A Modes

In Settings tab:
- **Quick Mode**: 3-5 questions (faster)
- **Detailed Mode**: 5-10 questions (more accurate)

### Whisper Models (Speed vs Accuracy)

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|----------------|
| tiny | 39 MB | ⚡⚡⚡⚡ | ⭐⭐ | Quick tests |
| base | 74 MB | ⚡⚡⚡ | ⭐⭐⭐ | **Most users** |
| small | 244 MB | ⚡⚡ | ⭐⭐⭐⭐ | Better accuracy |
| medium | 769 MB | ⚡ | ⭐⭐⭐⭐⭐ | Professional use |
| large | 1550 MB | 🐌 | ⭐⭐⭐⭐⭐ | Maximum accuracy |

### Ollama Models

Popular choices:
- **llama3.2** (3B) - Fast, good quality ⚡ (Recommended)
- **llama3.1** (8B) - Better quality, slower
- **mistral** (7B) - Good balance

Install with: `ollama pull <model-name>`

## 🔧 Troubleshooting

### "Ollama not accessible" error
- Make sure Ollama is running: `ollama serve`
- Check if model is installed: `ollama list`
- Pull model if needed: `ollama pull llama3.2`

### "FFmpeg not found" error
- Install FFmpeg (see installation steps above)
- Restart terminal after installation

### No audio being captured
- Make sure you're on Windows 10/11
- Check audio device in Settings
- Try refreshing audio devices

### Slow transcription
- Use smaller Whisper model (tiny or base)
- For GPU acceleration, install CUDA-enabled PyTorch:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  ```

### Memory issues
- Use smaller models (tiny Whisper + llama3.2)
- Close other applications
- Process shorter audio files

## 🎨 Supported Audio Formats

- MP3, WAV, M4A, MP4 (audio extracted)
- WEBM, OGG, FLAC
- Any format supported by FFmpeg

## 💡 Tips

- **First-time users**: Start with `base` Whisper model and `llama3.2`
- **Speaker ID**: Clearer audio = better speaker separation
- **Long meetings**: Works best with meetings under 2 hours
- **Multiple languages**: Whisper auto-detects language
- **Background noise**: Better audio = better results

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - Free to use, modify, and distribute!

## 🙏 Credits

Built with:
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Ollama](https://ollama.ai) - Local LLM runtime
- [Gradio](https://gradio.app) - UI framework

## 📧 Support

Having issues? Check:
1. This README
2. GitHub Issues
3. Ollama documentation: https://ollama.ai/docs

---

**Made with ❤️ for productive meetings** | 100% Free | 100% Offline | 100% Private
