"""
Configuration management for MeetingMind
Handles loading, saving, and default configuration values
"""
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from pathlib import Path


# Default paths
APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"
MEETINGS_DIR = DATA_DIR / "meetings"
PROFILES_DIR = DATA_DIR / "profiles"
TEMP_DIR = DATA_DIR / "temp"


@dataclass
class WhisperConfig:
    """Whisper transcription settings"""
    model: str = "base"  # tiny, base, small, medium, large
    language: Optional[str] = None  # Auto-detect if None
    device: str = "auto"  # auto, cpu, cuda


@dataclass
class OllamaConfig:
    """Ollama LLM settings"""
    model: str = "llama3.2"
    host: str = "http://localhost:11434"
    timeout: int = 120


@dataclass
class AudioConfig:
    """Audio capture settings"""
    sample_rate: int = 16000
    channels: int = 1
    device_id: Optional[int] = None  # None = default device
    format: str = "wav"


@dataclass
class DiarizationConfig:
    """Speaker diarization settings"""
    model: str = "pyannote/speaker-diarization-3.1"
    min_speakers: int = 1
    max_speakers: int = 10
    use_auth_token: Optional[str] = None  # HuggingFace token


@dataclass
class QAConfig:
    """Q&A session settings"""
    mode: str = "quick"  # "quick" (3-5 questions) or "detailed" (5-10 questions)
    max_questions_quick: int = 5
    max_questions_detailed: int = 10
    speaker_sample_duration: float = 5.0  # seconds
    auto_skip_after: int = 60  # Skip Q&A if user doesn't respond in 60s (0 = never)
    ask_speaker_names: bool = True
    ask_clarifications: bool = True


@dataclass
class UIConfig:
    """UI settings"""
    theme: str = "soft"  # Gradio theme
    dark_mode: bool = False
    show_notifications: bool = True
    auto_open_browser: bool = True
    server_port: int = 7860


@dataclass
class StorageConfig:
    """Storage settings"""
    meetings_dir: str = str(MEETINGS_DIR)
    max_storage_gb: float = 10.0
    auto_cleanup_days: int = 30  # Delete meetings older than X days (0 = never)
    save_audio: bool = True  # Keep audio files after processing


@dataclass
class Config:
    """Main configuration class"""
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    diarization: DiarizationConfig = field(default_factory=DiarizationConfig)
    qa: QAConfig = field(default_factory=QAConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # App metadata
    version: str = "2.0.0"
    first_run: bool = True


def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [DATA_DIR, MEETINGS_DIR, PROFILES_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load configuration from file or create default"""
    ensure_directories()
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse nested configs
            config = Config(
                whisper=WhisperConfig(**data.get('whisper', {})),
                ollama=OllamaConfig(**data.get('ollama', {})),
                audio=AudioConfig(**data.get('audio', {})),
                diarization=DiarizationConfig(**data.get('diarization', {})),
                qa=QAConfig(**data.get('qa', {})),
                ui=UIConfig(**data.get('ui', {})),
                storage=StorageConfig(**data.get('storage', {})),
                version=data.get('version', '2.0.0'),
                first_run=data.get('first_run', True)
            )
            return config
        except Exception as e:
            print(f"Error loading config, using defaults: {e}")
            return Config()
    else:
        # Create default config
        config = Config()
        save_config(config)
        return config


def save_config(config: Config) -> None:
    """Save configuration to file"""
    ensure_directories()
    
    # Convert to dict
    data = {
        'whisper': asdict(config.whisper),
        'ollama': asdict(config.ollama),
        'audio': asdict(config.audio),
        'diarization': asdict(config.diarization),
        'qa': asdict(config.qa),
        'ui': asdict(config.ui),
        'storage': asdict(config.storage),
        'version': config.version,
        'first_run': config.first_run
    }
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def update_config(updates: Dict[str, Any]) -> Config:
    """Update specific config values and save"""
    config = load_config()
    
    for key, value in updates.items():
        if '.' in key:
            # Handle nested keys like 'whisper.model'
            parts = key.split('.')
            obj = config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
        else:
            setattr(config, key, value)
    
    save_config(config)
    return config


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> Config:
    """Reload config from file"""
    global _config
    _config = load_config()
    return _config
