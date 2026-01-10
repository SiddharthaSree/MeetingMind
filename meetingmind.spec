# -*- mode: python ; coding: utf-8 -*-
"""
MeetingMind PyInstaller Spec File
Builds a standalone Windows executable with all dependencies
"""
import sys
import os
from pathlib import Path

# Get the project root
project_root = Path(SPECPATH)

# Analysis - collect all Python files and dependencies
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include package data
        ('assets', 'assets'),  # Icons and images
        ('templates', 'templates'),  # HTML templates if any
    ],
    hiddenimports=[
        # Core dependencies
        'gradio',
        'gradio.themes',
        'gradio.components',
        'ollama',
        'torch',
        'numpy',
        
        # Whisper and speech processing
        'whisper',
        'whisper.model',
        'whisper.audio',
        'whisper.transcribe',
        
        # Speaker diarization
        'pyannote',
        'pyannote.audio',
        'pyannote.audio.pipelines',
        'speechbrain',
        
        # Audio
        'soundfile',
        'sounddevice',
        'pyaudiowpatch',
        'ffmpeg',
        
        # Export formats
        'docx',
        'docx.shared',
        'docx.enum.text',
        'weasyprint',
        'jinja2',
        
        # System
        'psutil',
        'pystray',
        'PIL',
        'PIL.Image',
        
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
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries/data
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
    icon='assets/icon.ico',  # App icon
    version='version_info.txt',  # Version info
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
