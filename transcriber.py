"""
Transcriber module - Handles audio transcription using OpenAI Whisper
"""
import whisper
import os
from pathlib import Path


class Transcriber:
    def __init__(self, model_name="base"):
        """
        Initialize the Whisper transcriber
        
        Args:
            model_name (str): Whisper model to use (tiny, base, small, medium, large)
                             'base' is a good balance of speed and accuracy
        """
        print(f"Loading Whisper model: {model_name}...")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded successfully!")
    
    def transcribe_audio(self, audio_path, language=None):
        """
        Transcribe an audio file to text
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language code (e.g., 'en', 'es', 'fr')
                                     If None, Whisper will auto-detect
        
        Returns:
            dict: Transcription result with 'text', 'segments', and 'language'
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Transcribing audio file: {Path(audio_path).name}")
        
        # Transcribe with Whisper
        result = self.model.transcribe(
            audio_path,
            language=language,
            verbose=False
        )
        
        print(f"Transcription complete! Detected language: {result.get('language', 'unknown')}")
        
        return {
            'text': result['text'].strip(),
            'segments': result.get('segments', []),
            'language': result.get('language', 'unknown')
        }
    
    def get_available_models(self):
        """
        Get list of available Whisper models
        
        Returns:
            list: Available model names
        """
        return ['tiny', 'base', 'small', 'medium', 'large']


# Convenience function for quick transcription
def transcribe_file(audio_path, model_name="base", language=None):
    """
    Quick transcription function without class initialization
    
    Args:
        audio_path (str): Path to audio file
        model_name (str): Whisper model name
        language (str, optional): Language code
    
    Returns:
        str: Transcribed text
    """
    transcriber = Transcriber(model_name=model_name)
    result = transcriber.transcribe_audio(audio_path, language=language)
    return result['text']
