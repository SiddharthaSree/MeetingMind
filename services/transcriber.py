"""
Enhanced Transcriber Service
Transcribes audio using Whisper and merges with speaker diarization
"""
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

import whisper
import torch


class TranscriberService:
    """
    Service for transcribing audio using OpenAI Whisper
    
    Supports merging transcription with speaker diarization
    to produce speaker-labeled transcripts.
    """
    
    def __init__(
        self,
        model_name: str = "base",
        device: str = "auto",
        language: Optional[str] = None
    ):
        """
        Initialize transcriber service
        
        Args:
            model_name: Whisper model (tiny, base, small, medium, large)
            device: Device to use ('auto', 'cpu', 'cuda')
            language: Language code or None for auto-detect
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.language = language
        self._model = None
        
        print(f"TranscriberService initialized (model: {model_name}, device: {self.device})")
    
    def _get_device(self, device: str) -> str:
        """Determine device to use"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if self._model is None:
            print(f"Loading Whisper model: {self.model_name}...")
            self._model = whisper.load_model(self.model_name, device=self.device)
            print("Whisper model loaded successfully!")
        return self._model
    
    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detect)
            task: 'transcribe' or 'translate'
        
        Returns:
            dict: {
                'text': str,
                'segments': List[dict],
                'language': str
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Transcribing: {Path(audio_path).name}")
        
        model = self._load_model()
        
        # Transcribe
        result = model.transcribe(
            audio_path,
            language=language or self.language,
            task=task,
            verbose=False
        )
        
        # Format segments
        segments = []
        for seg in result.get('segments', []):
            segments.append({
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'].strip(),
                'speaker': None  # Will be filled by merge_with_diarization
            })
        
        output = {
            'text': result['text'].strip(),
            'segments': segments,
            'language': result.get('language', 'unknown')
        }
        
        print(f"Transcription complete! Language: {output['language']}")
        
        return output
    
    def merge_with_diarization(
        self,
        transcription: Dict[str, Any],
        diarization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge transcription segments with speaker diarization
        
        Args:
            transcription: Result from transcribe()
            diarization: Result from DiarizerService.diarize()
        
        Returns:
            dict: Transcription with speaker labels added to segments
        """
        transcript_segments = transcription['segments']
        diarization_segments = diarization['segments']
        
        # For each transcript segment, find the best matching speaker
        for t_seg in transcript_segments:
            t_start = t_seg['start']
            t_end = t_seg['end']
            t_mid = (t_start + t_end) / 2
            
            # Find overlapping diarization segments
            overlapping = []
            for d_seg in diarization_segments:
                overlap_start = max(t_start, d_seg['start'])
                overlap_end = min(t_end, d_seg['end'])
                
                if overlap_start < overlap_end:
                    overlap_duration = overlap_end - overlap_start
                    overlapping.append({
                        'speaker': d_seg['speaker'],
                        'overlap': overlap_duration
                    })
            
            if overlapping:
                # Assign speaker with most overlap
                best_match = max(overlapping, key=lambda x: x['overlap'])
                t_seg['speaker'] = best_match['speaker']
            else:
                # Fallback: find nearest speaker segment
                nearest = min(
                    diarization_segments,
                    key=lambda d: min(
                        abs(d['start'] - t_mid),
                        abs(d['end'] - t_mid)
                    )
                )
                t_seg['speaker'] = nearest['speaker']
        
        # Build speaker-labeled text
        labeled_text = self._build_labeled_text(transcript_segments)
        
        result = {
            'text': transcription['text'],
            'labeled_text': labeled_text,
            'segments': transcript_segments,
            'language': transcription['language'],
            'speakers': diarization['speakers'],
            'speaker_stats': diarization['speaker_stats']
        }
        
        return result
    
    def _build_labeled_text(self, segments: List[Dict]) -> str:
        """Build formatted text with speaker labels"""
        lines = []
        current_speaker = None
        current_text = []
        
        for seg in segments:
            speaker = seg.get('speaker', 'Unknown')
            text = seg.get('text', '').strip()
            
            if speaker != current_speaker:
                # Flush current speaker's text
                if current_text:
                    lines.append(f"[{current_speaker}]: {' '.join(current_text)}")
                current_speaker = speaker
                current_text = [text] if text else []
            else:
                if text:
                    current_text.append(text)
        
        # Flush last speaker
        if current_text:
            lines.append(f"[{current_speaker}]: {' '.join(current_text)}")
        
        return '\n\n'.join(lines)
    
    def get_segment_by_time(
        self,
        transcription: Dict,
        start_time: float,
        end_time: float
    ) -> str:
        """Get transcript text for a specific time range"""
        segments = transcription.get('segments', [])
        
        relevant_text = []
        for seg in segments:
            # Check overlap
            if seg['start'] < end_time and seg['end'] > start_time:
                relevant_text.append(seg.get('text', ''))
        
        return ' '.join(relevant_text).strip()
    
    def get_speaker_text(
        self,
        transcription: Dict,
        speaker_id: str
    ) -> str:
        """Get all text spoken by a specific speaker"""
        segments = transcription.get('segments', [])
        
        speaker_text = []
        for seg in segments:
            if seg.get('speaker') == speaker_id:
                speaker_text.append(seg.get('text', ''))
        
        return ' '.join(speaker_text).strip()
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper models"""
        return ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
