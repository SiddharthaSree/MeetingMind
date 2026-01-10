"""
Real-Time Transcription Service
Live transcription during recording with streaming display
"""
import threading
import queue
import time
import numpy as np
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class TranscriptChunk:
    """A chunk of real-time transcription"""
    text: str
    timestamp: float
    is_final: bool
    speaker: Optional[str] = None


class RealtimeTranscriber:
    """
    Real-time transcription using Whisper
    
    Transcribes audio in chunks as it's being recorded,
    providing live updates to the UI.
    """
    
    def __init__(
        self,
        model_name: str = "base",
        chunk_duration: float = 5.0,  # seconds per chunk
        overlap: float = 0.5,  # overlap between chunks
        on_transcript: Callable[[TranscriptChunk], None] = None
    ):
        self.model_name = model_name
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.on_transcript = on_transcript
        
        self._model = None
        self._audio_queue = queue.Queue()
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        
        # Buffer for audio data
        self._audio_buffer = []
        self._sample_rate = 16000
        
        # Full transcript accumulator
        self.full_transcript = []
    
    def _load_model(self):
        """Lazy load Whisper model"""
        if self._model is None:
            import whisper
            print(f"Loading Whisper model '{self.model_name}' for real-time...")
            self._model = whisper.load_model(self.model_name)
        return self._model
    
    def start(self):
        """Start real-time transcription thread"""
        if self._is_running:
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._transcription_loop, daemon=True)
        self._thread.start()
        print("Real-time transcription started")
    
    def stop(self) -> str:
        """Stop transcription and return full transcript"""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        
        # Return accumulated transcript
        return " ".join([chunk.text for chunk in self.full_transcript])
    
    def add_audio(self, audio_data: np.ndarray, sample_rate: int = 16000):
        """Add audio data to be transcribed"""
        if sample_rate != self._sample_rate:
            # Resample if needed
            import scipy.signal
            audio_data = scipy.signal.resample(
                audio_data,
                int(len(audio_data) * self._sample_rate / sample_rate)
            )
        
        self._audio_queue.put(audio_data)
    
    def _transcription_loop(self):
        """Main transcription loop running in background"""
        model = self._load_model()
        buffer = np.array([], dtype=np.float32)
        chunk_samples = int(self.chunk_duration * self._sample_rate)
        overlap_samples = int(self.overlap * self._sample_rate)
        
        while self._is_running:
            try:
                # Get audio from queue
                audio = self._audio_queue.get(timeout=0.5)
                buffer = np.concatenate([buffer, audio.astype(np.float32)])
                
                # Process when we have enough audio
                while len(buffer) >= chunk_samples:
                    # Extract chunk
                    chunk = buffer[:chunk_samples]
                    
                    # Transcribe
                    try:
                        result = model.transcribe(
                            chunk,
                            language=None,  # Auto-detect
                            fp16=False,
                            condition_on_previous_text=True
                        )
                        
                        text = result.get('text', '').strip()
                        if text:
                            transcript_chunk = TranscriptChunk(
                                text=text,
                                timestamp=time.time(),
                                is_final=True
                            )
                            self.full_transcript.append(transcript_chunk)
                            
                            if self.on_transcript:
                                self.on_transcript(transcript_chunk)
                    
                    except Exception as e:
                        print(f"Transcription error: {e}")
                    
                    # Keep overlap for continuity
                    buffer = buffer[chunk_samples - overlap_samples:]
            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Real-time transcription error: {e}")
    
    def get_current_transcript(self) -> str:
        """Get the current accumulated transcript"""
        return " ".join([chunk.text for chunk in self.full_transcript])


class LiveCaptionDisplay:
    """
    Manages live caption display with smooth updates
    """
    
    def __init__(self, max_lines: int = 5):
        self.max_lines = max_lines
        self.lines = []
        self._lock = threading.Lock()
    
    def add_text(self, text: str, speaker: str = None):
        """Add new transcribed text"""
        with self._lock:
            prefix = f"[{speaker}] " if speaker else ""
            self.lines.append(f"{prefix}{text}")
            
            # Keep only recent lines
            if len(self.lines) > self.max_lines * 2:
                self.lines = self.lines[-self.max_lines:]
    
    def get_display(self) -> str:
        """Get formatted display text"""
        with self._lock:
            recent = self.lines[-self.max_lines:]
            return "\n".join(recent)
    
    def clear(self):
        """Clear the display"""
        with self._lock:
            self.lines = []
