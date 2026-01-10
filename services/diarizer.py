"""
Speaker Diarization Service
Identifies different speakers in audio using pyannote-audio
"""
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

# Try to import pyannote
try:
    from pyannote.audio import Pipeline
    from pyannote.audio.pipelines.utils.hook import ProgressHook
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    print("Warning: pyannote-audio not available. Install with: pip install pyannote.audio")

import torch


@dataclass
class SpeakerSegment:
    """A segment of audio attributed to a speaker"""
    start: float  # Start time in seconds
    end: float    # End time in seconds
    speaker: str  # Speaker ID (e.g., "SPEAKER_00")
    
    @property
    def duration(self) -> float:
        return self.end - self.start


class DiarizerService:
    """
    Service for speaker diarization using pyannote-audio
    
    Identifies who spoke when in an audio file, returning
    timestamped segments with speaker labels.
    """
    
    def __init__(
        self,
        model_name: str = "pyannote/speaker-diarization-3.1",
        use_auth_token: Optional[str] = None,
        device: str = "auto"
    ):
        """
        Initialize diarization service
        
        Args:
            model_name: Pyannote model to use
            use_auth_token: HuggingFace token (required for first download)
            device: Device to use ('auto', 'cpu', 'cuda')
        """
        self.model_name = model_name
        self.use_auth_token = use_auth_token or os.environ.get("HF_TOKEN")
        self.device = self._get_device(device)
        self._pipeline: Optional[Pipeline] = None
        
        print(f"DiarizerService initialized (device: {self.device})")
    
    def _get_device(self, device: str) -> str:
        """Determine device to use"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _load_pipeline(self) -> Pipeline:
        """Load pyannote pipeline (lazy loading)"""
        if self._pipeline is None:
            if not PYANNOTE_AVAILABLE:
                raise RuntimeError("pyannote-audio is not installed")
            
            print(f"Loading diarization model: {self.model_name}...")
            
            try:
                self._pipeline = Pipeline.from_pretrained(
                    self.model_name,
                    use_auth_token=self.use_auth_token
                )
                self._pipeline.to(torch.device(self.device))
                print("Diarization model loaded successfully!")
            except Exception as e:
                if "401" in str(e) or "token" in str(e).lower():
                    raise RuntimeError(
                        "HuggingFace authentication required. Please:\n"
                        "1. Create account at https://huggingface.co\n"
                        "2. Accept model terms at https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                        "3. Create token at https://huggingface.co/settings/tokens\n"
                        "4. Set HF_TOKEN environment variable or pass use_auth_token"
                    )
                raise
        
        return self._pipeline
    
    def diarize(
        self,
        audio_path: str,
        min_speakers: int = None,
        max_speakers: int = None,
        num_speakers: int = None
    ) -> Dict[str, Any]:
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_path: Path to audio file
            min_speakers: Minimum expected speakers
            max_speakers: Maximum expected speakers
            num_speakers: Exact number of speakers (if known)
        
        Returns:
            dict: {
                'segments': List[SpeakerSegment],
                'num_speakers': int,
                'speakers': List[str],
                'speaker_stats': Dict[str, float]  # speaking time per speaker
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Diarizing audio: {Path(audio_path).name}")
        
        # Load pipeline
        pipeline = self._load_pipeline()
        
        # Run diarization
        diarization_params = {}
        if num_speakers is not None:
            diarization_params["num_speakers"] = num_speakers
        else:
            if min_speakers is not None:
                diarization_params["min_speakers"] = min_speakers
            if max_speakers is not None:
                diarization_params["max_speakers"] = max_speakers
        
        # Run with progress hook if available
        try:
            diarization = pipeline(audio_path, **diarization_params)
        except Exception as e:
            print(f"Diarization error: {e}")
            raise
        
        # Parse results
        segments = []
        speakers = set()
        speaker_times = {}
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment = SpeakerSegment(
                start=turn.start,
                end=turn.end,
                speaker=speaker
            )
            segments.append(segment)
            speakers.add(speaker)
            
            # Track speaking time
            if speaker not in speaker_times:
                speaker_times[speaker] = 0
            speaker_times[speaker] += segment.duration
        
        # Sort segments by start time
        segments.sort(key=lambda s: s.start)
        
        # Convert to list of dicts for serialization
        segments_dict = [
            {
                'start': s.start,
                'end': s.end,
                'speaker': s.speaker,
                'duration': s.duration
            }
            for s in segments
        ]
        
        result = {
            'segments': segments_dict,
            'num_speakers': len(speakers),
            'speakers': sorted(list(speakers)),
            'speaker_stats': speaker_times
        }
        
        print(f"Diarization complete: {len(speakers)} speakers, {len(segments)} segments")
        
        return result
    
    def get_speaker_segments(
        self,
        diarization_result: Dict,
        speaker_id: str
    ) -> List[Dict]:
        """Get all segments for a specific speaker"""
        return [
            s for s in diarization_result['segments']
            if s['speaker'] == speaker_id
        ]
    
    def get_speaker_sample_segment(
        self,
        diarization_result: Dict,
        speaker_id: str,
        min_duration: float = 3.0,
        max_duration: float = 8.0
    ) -> Optional[Dict]:
        """
        Find a good segment to use as a voice sample for speaker identification
        
        Args:
            diarization_result: Result from diarize()
            speaker_id: Speaker to find sample for
            min_duration: Minimum segment duration
            max_duration: Maximum segment duration (will be trimmed)
        
        Returns:
            dict: Best segment for voice sample, or None
        """
        speaker_segments = self.get_speaker_segments(diarization_result, speaker_id)
        
        if not speaker_segments:
            return None
        
        # Find segments that are long enough
        good_segments = [
            s for s in speaker_segments
            if s['duration'] >= min_duration
        ]
        
        if not good_segments:
            # Fall back to longest segment
            good_segments = sorted(speaker_segments, key=lambda s: s['duration'], reverse=True)
        
        # Pick from middle of the recording (usually clearer audio)
        mid_idx = len(good_segments) // 2
        best_segment = good_segments[mid_idx] if good_segments else speaker_segments[0]
        
        # Trim to max duration if needed
        if best_segment['duration'] > max_duration:
            # Take from the middle of the segment
            center = (best_segment['start'] + best_segment['end']) / 2
            half_duration = max_duration / 2
            return {
                'start': center - half_duration,
                'end': center + half_duration,
                'speaker': best_segment['speaker'],
                'duration': max_duration
            }
        
        return best_segment
    
    def merge_close_segments(
        self,
        segments: List[Dict],
        max_gap: float = 0.5
    ) -> List[Dict]:
        """
        Merge segments from same speaker that are close together
        
        Args:
            segments: List of segment dicts
            max_gap: Maximum gap between segments to merge (seconds)
        
        Returns:
            List of merged segments
        """
        if not segments:
            return []
        
        merged = []
        current = dict(segments[0])
        
        for segment in segments[1:]:
            # Same speaker and close enough?
            if (segment['speaker'] == current['speaker'] and
                segment['start'] - current['end'] <= max_gap):
                # Merge
                current['end'] = segment['end']
                current['duration'] = current['end'] - current['start']
            else:
                merged.append(current)
                current = dict(segment)
        
        merged.append(current)
        return merged
    
    def is_available(self) -> bool:
        """Check if diarization is available"""
        return PYANNOTE_AVAILABLE


# Alternative lightweight diarization (for fallback)
class SimpleDiarizer:
    """
    Simple diarization fallback using energy-based voice activity detection
    
    NOTE: This is a basic fallback that doesn't actually identify different speakers.
    It only detects speech vs. silence. Use pyannote for real speaker diarization.
    """
    
    def __init__(self):
        print("Warning: Using SimpleDiarizer - no speaker identification available")
    
    def diarize(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Basic VAD-based segmentation (no speaker ID)"""
        import numpy as np
        import wave
        
        # Load audio
        with wave.open(audio_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_data = np.frombuffer(wf.readframes(n_frames), dtype=np.int16)
        
        # Simple energy-based VAD
        frame_size = int(sample_rate * 0.025)  # 25ms frames
        hop_size = int(sample_rate * 0.010)    # 10ms hop
        
        segments = []
        in_speech = False
        speech_start = 0
        
        threshold = np.percentile(np.abs(audio_data), 70)  # Adaptive threshold
        
        for i in range(0, len(audio_data) - frame_size, hop_size):
            frame = audio_data[i:i + frame_size]
            energy = np.sqrt(np.mean(frame.astype(float) ** 2))
            
            time_sec = i / sample_rate
            
            if energy > threshold and not in_speech:
                in_speech = True
                speech_start = time_sec
            elif energy <= threshold and in_speech:
                in_speech = False
                if time_sec - speech_start > 0.3:  # Min 300ms
                    segments.append({
                        'start': speech_start,
                        'end': time_sec,
                        'speaker': 'SPEAKER_00',  # Can't distinguish speakers
                        'duration': time_sec - speech_start
                    })
        
        # Close final segment
        if in_speech:
            segments.append({
                'start': speech_start,
                'end': len(audio_data) / sample_rate,
                'speaker': 'SPEAKER_00',
                'duration': len(audio_data) / sample_rate - speech_start
            })
        
        return {
            'segments': segments,
            'num_speakers': 1,
            'speakers': ['SPEAKER_00'],
            'speaker_stats': {'SPEAKER_00': sum(s['duration'] for s in segments)}
        }
