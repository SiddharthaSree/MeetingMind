"""
Q&A Engine Service
Generates clarifying questions and handles speaker identification with audio snippets
"""
import io
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

import ollama


class QuestionType(Enum):
    """Types of Q&A questions"""
    SPEAKER_ID = "speaker_identification"
    CLARIFICATION = "clarification"
    ACTION_ITEM = "action_item"
    TOPIC = "topic"
    DECISION = "decision"


@dataclass
class Question:
    """Represents a Q&A question"""
    id: str
    type: QuestionType
    question: str
    context: str = ""
    speaker_id: Optional[str] = None  # For SPEAKER_ID questions
    audio_snippet_path: Optional[str] = None  # Path to audio snippet
    audio_snippet_b64: Optional[str] = None  # Base64 audio for UI
    options: List[str] = field(default_factory=list)  # For multiple choice
    timestamp: Optional[float] = None  # Reference timestamp in audio
    answered: bool = False
    answer: Optional[str] = None


class QAEngine:
    """
    Service for generating and managing Q&A flow
    
    Key responsibilities:
    1. Extract audio snippets for unknown speakers
    2. Generate clarifying questions about meeting content
    3. Process user answers to enrich meeting notes
    """
    
    def __init__(
        self,
        model_name: str = "llama3.2",
        mode: str = "quick"  # "quick" (3-5 questions) or "detailed" (5-10 questions)
    ):
        """
        Initialize Q&A Engine
        
        Args:
            model_name: Ollama model for question generation
            mode: "quick" for 3-5 questions, "detailed" for 5-10
        """
        self.model_name = model_name
        self.mode = mode
        self.questions: List[Question] = []
        self.answers: Dict[str, Any] = {}
        
        # Question limits based on mode
        self.max_questions = 5 if mode == "quick" else 10
        self.max_speaker_questions = 3 if mode == "quick" else 5
        self.max_content_questions = 2 if mode == "quick" else 5
        
        print(f"QAEngine initialized (mode: {mode}, max questions: {self.max_questions})")
    
    def generate_questions(
        self,
        transcript: Dict[str, Any],
        diarization_result: Dict[str, Any],
        audio_path: str = None
    ) -> List[Question]:
        """
        Generate all questions for Q&A session
        
        Args:
            transcript: Merged transcript with speaker labels
            diarization_result: Speaker diarization results
            audio_path: Path to audio file for snippet extraction
        
        Returns:
            List of Question objects
        """
        self.questions = []
        
        # 1. Generate speaker identification questions (priority)
        speaker_questions = self._generate_speaker_questions(
            diarization_result,
            audio_path
        )
        self.questions.extend(speaker_questions[:self.max_speaker_questions])
        
        # 2. Generate content clarification questions
        remaining_slots = self.max_questions - len(self.questions)
        if remaining_slots > 0:
            content_questions = self._generate_content_questions(
                transcript,
                max_questions=min(remaining_slots, self.max_content_questions)
            )
            self.questions.extend(content_questions)
        
        print(f"Generated {len(self.questions)} questions")
        return self.questions
    
    def _generate_speaker_questions(
        self,
        diarization_result: Dict,
        audio_path: str = None
    ) -> List[Question]:
        """Generate questions for speaker identification with audio snippets"""
        questions = []
        
        speaker_segments = diarization_result.get('speakers', {})
        
        for speaker_id, segments in speaker_segments.items():
            if not segments:
                continue
            
            # Find best sample segment (longest or clearest)
            sample_segment = self._find_best_sample_segment(segments)
            
            if sample_segment is None:
                continue
            
            # Extract audio snippet if audio file available
            snippet_path = None
            snippet_b64 = None
            
            if audio_path:
                snippet_data = self._extract_audio_snippet(
                    audio_path,
                    sample_segment['start'],
                    min(sample_segment['end'], sample_segment['start'] + 5.0)  # Max 5 sec
                )
                if snippet_data:
                    snippet_b64 = snippet_data.get('base64')
                    snippet_path = snippet_data.get('path')
            
            question = Question(
                id=f"speaker_{speaker_id}",
                type=QuestionType.SPEAKER_ID,
                question=f"Who is this speaker? (Listen to audio clip)",
                context=f"This speaker appears {len(segments)} times in the meeting",
                speaker_id=speaker_id,
                audio_snippet_path=snippet_path,
                audio_snippet_b64=snippet_b64,
                timestamp=sample_segment['start']
            )
            questions.append(question)
        
        return questions
    
    def _find_best_sample_segment(self, segments: List[Dict]) -> Optional[Dict]:
        """Find the best segment to use as audio sample"""
        if not segments:
            return None
        
        # Prefer segments that are:
        # 1. At least 2 seconds long
        # 2. Not too long (cap at 10 seconds)
        # 3. Clear (no overlap if we had that info)
        
        valid_segments = []
        for seg in segments:
            duration = seg['end'] - seg['start']
            if 2.0 <= duration <= 15.0:
                valid_segments.append(seg)
        
        # If no ideal segments, use the longest one
        if not valid_segments:
            valid_segments = sorted(segments, key=lambda s: s['end'] - s['start'], reverse=True)
        
        return valid_segments[0] if valid_segments else segments[0]
    
    def _extract_audio_snippet(
        self,
        audio_path: str,
        start_time: float,
        end_time: float
    ) -> Optional[Dict]:
        """
        Extract audio snippet for speaker identification
        
        Returns dict with 'base64' and optionally 'path'
        """
        try:
            import soundfile as sf
            import numpy as np
            
            # Read the audio segment
            info = sf.info(audio_path)
            sample_rate = info.samplerate
            
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            
            data, sr = sf.read(audio_path, start=start_sample, stop=end_sample)
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            # Write to in-memory buffer as WAV
            buffer = io.BytesIO()
            sf.write(buffer, data, sr, format='WAV')
            buffer.seek(0)
            
            # Encode as base64 for UI playback
            audio_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            
            return {
                'base64': audio_b64,
                'sample_rate': sr,
                'duration': end_time - start_time
            }
            
        except Exception as e:
            print(f"Error extracting audio snippet: {e}")
            return None
    
    def _generate_content_questions(
        self,
        transcript: Dict,
        max_questions: int = 3
    ) -> List[Question]:
        """Generate clarifying questions about meeting content using LLM"""
        
        # Get transcript text
        text = transcript.get('labeled_text', transcript.get('text', ''))
        
        if not text:
            return []
        
        # Truncate for LLM context
        text = text[:4000]
        
        prompt = f"""Analyze this meeting transcript and generate {max_questions} clarifying questions that would help create better meeting notes.

Focus on:
1. Unclear action items - who owns them, what's the deadline?
2. Vague decisions - what exactly was decided?
3. Missing context - what project/topic is being discussed?

Transcript:
{text}

Generate exactly {max_questions} questions, one per line, starting with a number:
1. 
2. 
"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'system',
                    'content': 'You are a meeting assistant that asks clarifying questions to improve meeting notes. Keep questions specific and actionable.'
                }, {
                    'role': 'user',
                    'content': prompt
                }],
                options={'temperature': 0.5, 'num_predict': 500}
            )
            
            # Parse questions from response
            questions = []
            response_text = response['message']['content']
            
            for line in response_text.split('\n'):
                line = line.strip()
                # Match lines starting with number
                if line and line[0].isdigit() and '.' in line:
                    q_text = line.split('.', 1)[1].strip()
                    if q_text:
                        # Determine question type
                        q_type = QuestionType.CLARIFICATION
                        if any(word in q_text.lower() for word in ['action', 'task', 'responsible', 'deadline']):
                            q_type = QuestionType.ACTION_ITEM
                        elif any(word in q_text.lower() for word in ['decide', 'decision', 'agreed']):
                            q_type = QuestionType.DECISION
                        elif any(word in q_text.lower() for word in ['topic', 'project', 'about']):
                            q_type = QuestionType.TOPIC
                        
                        questions.append(Question(
                            id=f"content_{len(questions)+1}",
                            type=q_type,
                            question=q_text
                        ))
            
            return questions[:max_questions]
            
        except Exception as e:
            print(f"Error generating content questions: {e}")
            return []
    
    def answer_question(self, question_id: str, answer: str) -> bool:
        """
        Record answer to a question
        
        Args:
            question_id: ID of the question being answered
            answer: User's answer
        
        Returns:
            bool: Success status
        """
        for q in self.questions:
            if q.id == question_id:
                q.answered = True
                q.answer = answer
                self.answers[question_id] = {
                    'question': q.question,
                    'answer': answer,
                    'type': q.type.value,
                    'speaker_id': q.speaker_id
                }
                print(f"Answered question: {question_id}")
                return True
        
        print(f"Question not found: {question_id}")
        return False
    
    def get_unanswered_questions(self) -> List[Question]:
        """Get all unanswered questions"""
        return [q for q in self.questions if not q.answered]
    
    def get_answered_questions(self) -> List[Question]:
        """Get all answered questions"""
        return [q for q in self.questions if q.answered]
    
    def get_speaker_mappings(self) -> Dict[str, str]:
        """
        Get speaker ID to name mappings from answered questions
        
        Returns:
            dict: {speaker_id: name}
        """
        mappings = {}
        for q in self.questions:
            if q.type == QuestionType.SPEAKER_ID and q.answered and q.answer:
                mappings[q.speaker_id] = q.answer
        return mappings
    
    def get_all_answers(self) -> Dict[str, Any]:
        """Get all answers for summary generation"""
        return self.answers
    
    def skip_question(self, question_id: str) -> bool:
        """Skip a question without answering"""
        for q in self.questions:
            if q.id == question_id:
                q.answered = True
                q.answer = None
                print(f"Skipped question: {question_id}")
                return True
        return False
    
    def skip_all_remaining(self) -> None:
        """Skip all unanswered questions"""
        for q in self.questions:
            if not q.answered:
                q.answered = True
                q.answer = None
        print("Skipped all remaining questions")
    
    def is_complete(self) -> bool:
        """Check if Q&A session is complete"""
        return all(q.answered for q in self.questions)
    
    def get_progress(self) -> Dict[str, int]:
        """Get Q&A progress stats"""
        total = len(self.questions)
        answered = len(self.get_answered_questions())
        return {
            'total': total,
            'answered': answered,
            'remaining': total - answered
        }
