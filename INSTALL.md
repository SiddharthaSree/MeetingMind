# 🚀 MeetingMind Installation Guide

## Quick Start (Recommended)

### Option 1: Download Pre-built EXE (Easiest!)

1. Go to [**Releases**](https://github.com/SiddharthaSree/MeetingMind/releases)
2. Download `MeetingMind-v2.1.0-Windows.zip`
3. Extract the ZIP file
4. Run `MeetingMind.exe`
5. Done! 🎉

### Option 2: Run from Source (For Developers)

See detailed instructions below.

---

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 5 GB free | 10 GB free |
| **CPU** | 4 cores | 8+ cores |
| **GPU** | Not required | NVIDIA (for faster processing) |

---

## 🔧 Required Software

### 1. Ollama (Required for AI Summaries)

Ollama runs the AI models locally on your computer.

**Installation:**
1. Download from: **https://ollama.ai/download**
2. Run the installer
3. Open Command Prompt and run:
   ```
   ollama pull llama3.2
   ```
4. Keep Ollama running when using MeetingMind

**Verify installation:**
```
ollama list
```
You should see `llama3.2` in the list.

### 2. FFmpeg (Required for Audio Processing)

**Easy Install with Chocolatey:**
```powershell
choco install ffmpeg
```

**Manual Install:**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your System PATH

**Verify installation:**
```
ffmpeg -version
```

---

## 🎯 Running MeetingMind

### From EXE (Downloaded Release)

1. Extract the ZIP file to any folder (e.g., `C:\MeetingMind`)
2. Double-click `MeetingMind.exe`
3. Your browser will open to `http://localhost:7860`
4. Start recording your meetings!

### From Source Code

```powershell
# Clone the repository
git clone https://github.com/SiddharthaSree/MeetingMind.git
cd MeetingMind

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

## 🏗️ Building the EXE Yourself

If you want to build the executable from source:

```powershell
# Make sure you're in the MeetingMind folder
cd MeetingMind

# Run the build script
.\build.bat
```

The EXE will be created in `dist\MeetingMind\MeetingMind.exe`

---

## ❓ Troubleshooting

### "Ollama not accessible"
- Make sure Ollama is running (check system tray)
- Run `ollama serve` in a terminal
- Pull a model: `ollama pull llama3.2`

### "FFmpeg not found"
- Install FFmpeg (see above)
- Restart your computer after installation

### "No audio being captured"
- Only works on Windows 10/11
- Check your audio device in Settings tab
- Make sure something is playing audio

### App won't start
- Try running as Administrator
- Check if antivirus is blocking it
- Make sure all files were extracted

### Slow transcription
- Use a smaller Whisper model (Settings → "tiny" or "base")
- Close other applications
- Consider using GPU acceleration

---

## 📞 Getting Help

- **GitHub Issues**: https://github.com/SiddharthaSree/MeetingMind/issues
- **Documentation**: https://github.com/SiddharthaSree/MeetingMind#readme

---

**Made with ❤️ for productive meetings**
