"""
Audio Capture Service
Captures system audio using WASAPI loopback on Windows
"""
import os
import wave
import threading
import queue
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

import numpy as np

# Try to import Windows-specific audio libraries
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("Warning: sounddevice not available")

try:
    import pyaudiowpatch as pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    try:
        import pyaudio
        PYAUDIO_AVAILABLE = True
    except ImportError:
        PYAUDIO_AVAILABLE = False
        print("Warning: pyaudio/pyaudiowpatch not available")


class AudioCaptureService:
    """
    Service for capturing system audio on Windows
    
    Uses WASAPI loopback to capture audio from any application
    (Teams, Zoom, browser, etc.) without microphone
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize audio capture service
        
        Args:
            sample_rate: Sample rate for recording (16000 recommended for Whisper)
            channels: Number of channels (1 = mono, 2 = stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._audio_queue = queue.Queue()
        self._recording_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._recorded_frames = []
        self._start_time: Optional[float] = None
        self._duration: float = 0
        
        # Determine which backend to use
        self._backend = self._detect_backend()
        print(f"Audio capture backend: {self._backend}")
    
    def _detect_backend(self) -> str:
        """Detect available audio backend"""
        if PYAUDIO_AVAILABLE:
            return "pyaudio"
        elif SOUNDDEVICE_AVAILABLE:
            return "sounddevice"
        else:
            return "none"
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """
        List available audio devices
        
        Returns:
            List of device info dictionaries
        """
        devices = []
        
        if self._backend == "pyaudio":
            devices = self._list_devices_pyaudio()
        elif self._backend == "sounddevice":
            devices = self._list_devices_sounddevice()
        
        return devices
    
    def _list_devices_pyaudio(self) -> List[Dict[str, Any]]:
        """List devices using PyAudio"""
        devices = []
        try:
            p = pyaudio.PyAudio()
            
            # Look for WASAPI loopback devices
            for i in range(p.get_device_count()):
                try:
                    info = p.get_device_info_by_index(i)
                    
                    # Check if it's a loopback device (for system audio)
                    is_loopback = False
                    if hasattr(pyaudio, 'paWASAPI'):
                        try:
                            # pyaudiowpatch has loopback support
                            is_loopback = info.get('isLoopbackDevice', False)
                        except:
                            pass
                    
                    devices.append({
                        'id': i,
                        'name': info['name'],
                        'channels': info['maxInputChannels'],
                        'sample_rate': int(info['defaultSampleRate']),
                        'is_loopback': is_loopback,
                        'is_input': info['maxInputChannels'] > 0,
                        'is_output': info['maxOutputChannels'] > 0,
                        'host_api': info.get('hostApi', -1)
                    })
                except Exception as e:
                    continue
            
            p.terminate()
        except Exception as e:
            print(f"Error listing PyAudio devices: {e}")
        
        return devices
    
    def _list_devices_sounddevice(self) -> List[Dict[str, Any]]:
        """List devices using sounddevice"""
        devices = []
        try:
            device_list = sd.query_devices()
            for i, info in enumerate(device_list):
                devices.append({
                    'id': i,
                    'name': info['name'],
                    'channels': info['max_input_channels'],
                    'sample_rate': int(info['default_samplerate']),
                    'is_loopback': 'loopback' in info['name'].lower(),
                    'is_input': info['max_input_channels'] > 0,
                    'is_output': info['max_output_channels'] > 0,
                    'host_api': info.get('hostapi', -1)
                })
        except Exception as e:
            print(f"Error listing sounddevice devices: {e}")
        
        return devices
    
    def get_default_loopback_device(self) -> Optional[int]:
        """Find the default loopback device for system audio capture"""
        devices = self.list_devices()
        
        # First, try to find a WASAPI loopback device
        for device in devices:
            if device.get('is_loopback'):
                return device['id']
        
        # Fallback: look for device with "loopback" in name
        for device in devices:
            if 'loopback' in device['name'].lower():
                return device['id']
        
        # Fallback: look for stereo mix
        for device in devices:
            name_lower = device['name'].lower()
            if 'stereo mix' in name_lower or 'what u hear' in name_lower:
                return device['id']
        
        return None
    
    def start_recording(self, device_id: int = None) -> bool:
        """
        Start recording audio
        
        Args:
            device_id: Audio device ID (None = auto-detect loopback)
        
        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            print("Already recording")
            return False
        
        if self._backend == "none":
            print("No audio backend available")
            return False
        
        # Auto-detect loopback device if not specified
        if device_id is None:
            device_id = self.get_default_loopback_device()
            if device_id is None:
                print("No loopback device found. Using default input.")
        
        self._stop_event.clear()
        self._recorded_frames = []
        self._start_time = time.time()
        
        # Start recording in background thread
        self._recording_thread = threading.Thread(
            target=self._record_audio,
            args=(device_id,),
            daemon=True
        )
        self._recording_thread.start()
        self.is_recording = True
        
        return True
    
    def _record_audio(self, device_id: int):
        """Recording thread function"""
        if self._backend == "pyaudio":
            self._record_pyaudio(device_id)
        elif self._backend == "sounddevice":
            self._record_sounddevice(device_id)
    
    def _record_pyaudio(self, device_id: int):
        """Record using PyAudio/pyaudiowpatch"""
        try:
            p = pyaudio.PyAudio()
            
            # Get device info
            if device_id is not None:
                device_info = p.get_device_info_by_index(device_id)
                channels = min(self.channels, device_info['maxInputChannels'])
                if channels == 0:
                    channels = 1
            else:
                device_info = p.get_default_input_device_info()
                channels = self.channels
                device_id = device_info['index']
            
            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_id,
                frames_per_buffer=1024
            )
            
            print(f"Recording from: {device_info['name']}")
            
            while not self._stop_event.is_set():
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    self._recorded_frames.append(data)
                except Exception as e:
                    if not self._stop_event.is_set():
                        print(f"Recording error: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"PyAudio recording error: {e}")
            self.is_recording = False
    
    def _record_sounddevice(self, device_id: int):
        """Record using sounddevice"""
        try:
            def callback(indata, frames, time_info, status):
                if status:
                    print(f"Sounddevice status: {status}")
                self._recorded_frames.append(indata.copy())
            
            with sd.InputStream(
                device=device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                callback=callback
            ):
                while not self._stop_event.is_set():
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Sounddevice recording error: {e}")
            self.is_recording = False
    
    def stop_recording(self, output_path: str = None) -> Optional[str]:
        """
        Stop recording and save to file
        
        Args:
            output_path: Path to save the recording (auto-generated if None)
        
        Returns:
            str: Path to saved audio file
        """
        if not self.is_recording:
            print("Not currently recording")
            return None
        
        # Signal stop
        self._stop_event.set()
        self.is_recording = False
        
        # Wait for recording thread
        if self._recording_thread:
            self._recording_thread.join(timeout=2)
        
        # Calculate duration
        if self._start_time:
            self._duration = time.time() - self._start_time
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"recording_{timestamp}.wav"
        
        # Save to WAV file
        if self._recorded_frames:
            self._save_wav(output_path)
            print(f"Recording saved: {output_path} ({self._duration:.1f}s)")
            return output_path
        else:
            print("No audio recorded")
            return None
    
    def _save_wav(self, output_path: str):
        """Save recorded frames to WAV file"""
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            
            if self._backend == "pyaudio":
                wf.writeframes(b''.join(self._recorded_frames))
            else:
                # sounddevice returns numpy arrays
                audio_data = np.concatenate(self._recorded_frames, axis=0)
                wf.writeframes(audio_data.tobytes())
    
    def get_duration(self) -> float:
        """Get duration of last recording in seconds"""
        return self._duration
    
    def is_available(self) -> bool:
        """Check if audio capture is available"""
        return self._backend != "none"


# Convenience function
def record_system_audio(duration: float, output_path: str = None) -> Optional[str]:
    """
    Quick function to record system audio for a specified duration
    
    Args:
        duration: Recording duration in seconds
        output_path: Output file path
    
    Returns:
        str: Path to recorded file
    """
    service = AudioCaptureService()
    
    if not service.start_recording():
        return None
    
    time.sleep(duration)
    return service.stop_recording(output_path)
