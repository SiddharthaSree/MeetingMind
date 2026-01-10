# 🎙️ MeetingMind

A **100% free, offline meeting notes assistant** that captures system audio from Teams/Zoom calls, transcribes with speaker identification, and generates intelligent summaries with action items - all running locally on your machine!

## ✨ Features

### 🎤 Audio Capture
- **System Audio Recording** - Capture audio from Teams, Zoom, or any application (Windows WASAPI loopback)
- **Upload Support** - Drag & drop existing audio/video files
- **System Tray** - Quick recording controls from your taskbar

### 🎯 Transcription & Speaker ID
- **Accurate Transcription** - Uses OpenAI Whisper (runs 100% offline)
- **Speaker Diarization** - Identifies who's speaking using pyannote-audio
- **Audio Snippets** - Listen to clips to identify unknown speakers

### 🤖 Smart Q&A Workflow
- **Speaker Identification** - Audio clips help you name each speaker
- **Clarifying Questions** - AI asks questions to improve note accuracy
- **Quick or Detailed Mode** - Choose 3-5 or 5-10 questions

### 📋 Intelligent Summaries
- **Smart Summaries** - Powered by Ollama LLMs (llama3.2, mistral, etc.)
- **Action Items** - Automatically extracts tasks with assignees
- **Key Decisions** - Highlights important decisions made
- **Export Options** - Markdown, JSON, or copy to clipboard

### 🔒 Privacy First
- **100% Offline** - Everything runs locally, no API calls
- **No Data Collection** - Your meetings stay on your machine
- **Completely Free** - No API costs, no subscriptions

## 📋 Requirements

- **Python 3.10 or higher**
- **Windows 10/11** (for system audio capture)
- **FFmpeg** (for audio processing)
- **Ollama** (local LLM runtime)
- **8GB+ RAM** recommended (16GB for larger models)

## 🚀 Quick Start

### 1. Install FFmpeg

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
├── core/
│   ├── config.py          # Configuration management
│   ├── controller.py      # Main app controller
│   └── events.py          # Event system
├── services/
│   ├── audio_capture.py   # WASAPI system audio recording
│   ├── transcriber.py     # Whisper transcription
│   ├── diarizer.py        # Speaker diarization
│   ├── summarizer.py      # Ollama summarization
│   └── qa_engine.py       # Q&A generation & management
├── ui/
│   ├── gradio_app.py      # Web interface
│   └── system_tray.py     # System tray application
├── data/
│   ├── meetings/          # Saved meeting notes
│   └── profiles/          # Speaker profiles
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
