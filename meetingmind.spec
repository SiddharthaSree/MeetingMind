# -*- mode: python ; coding: utf-8 -*-
"""
MeetingMind PyInstaller Spec File
Builds a standalone Windows executable with all dependencies

Build command: pyinstaller meetingmind.spec --noconfirm
"""
import sys
import os
from pathlib import Path

# Get the project root
project_root = Path(SPECPATH)

# Collect data files
datas = []

# Add assets if they exist
assets_path = project_root / 'assets'
if assets_path.exists():
    datas.append(('assets', 'assets'))

# Add any templates
templates_path = project_root / 'templates'
if templates_path.exists():
    datas.append(('templates', 'templates'))

# Analysis - collect all Python files and dependencies
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Core dependencies
        'gradio',
        'gradio.themes',
        'gradio.themes.soft',
        'gradio.components',
        'gradio.blocks',
        'ollama',
        'torch',
        'numpy',
        'tqdm',
        
        # Whisper and speech processing
        'whisper',
        'whisper.model',
        'whisper.audio',
        'whisper.transcribe',
        'whisper.tokenizer',
        
        # Speaker diarization
        'pyannote',
        'pyannote.audio',
        'pyannote.audio.pipelines',
        'pyannote.core',
        'speechbrain',
        
        # Audio
        'soundfile',
        'sounddevice',
        'pyaudiowpatch',
        
        # Export formats
        'docx',
        'docx.shared',
        'docx.enum.text',
        'docx.enum.style',
        'jinja2',
        'markupsafe',
        
        # System
        'psutil',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        
        # Web/networking
        'httpx',
        'httpcore',
        'anyio',
        'starlette',
        'fastapi',
        'uvicorn',
        
        # Our modules
        'core',
        'core.config',
        'core.controller',
        'core.events',
        'services',
        'services.audio_capture',
        'services.transcriber',
        'services.diarizer',
        'services.summarizer',
        'services.qa_engine',
        'services.meeting_detector',
        'services.templates',
        'services.exporter',
        'services.history',
        'ui',
        'ui.gradio_app',
        'ui.system_tray',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries/data
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Check if icon exists
icon_path = project_root / 'assets' / 'icon.ico'
icon_file = str(icon_path) if icon_path.exists() else None

# Check if version info exists
version_path = project_root / 'version_info.txt'
version_file = str(version_path) if version_path.exists() else None

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MeetingMind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version=version_file,
)

# Collect all files into dist folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MeetingMind',
)
