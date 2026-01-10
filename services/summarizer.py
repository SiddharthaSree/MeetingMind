"""
Enhanced Summarizer Service
Generates meeting summaries using Ollama with Q&A context integration
"""
import re
from typing import Dict, List, Any, Optional

import ollama


class SummarizerService:
    """
    Service for generating meeting summaries using local LLM (Ollama)
    
    Integrates Q&A responses to produce enriched, accurate summaries
    with action items assigned to specific speakers.
    """
    
    def __init__(
        self,
        model_name: str = "llama3.2",
        host: str = "http://localhost:11434"
    ):
        """
        Initialize summarizer service
        
        Args:
            model_name: Ollama model to use
            host: Ollama server host
        """
        self.model_name = model_name
        self.host = host
        
        print(f"SummarizerService initialized (model: {model_name})")
    
    def generate_summary(
        self,
        transcript: Dict[str, Any],
        qa_responses: Dict[str, Any] = None,
        speaker_names: Dict[str, str] = None,
        meeting_type: str = None
    ) -> Dict[str, Any]:
        """
        Generate meeting summary with Q&A context
        
        Args:
            transcript: Merged transcript with speaker labels
            qa_responses: Answers from Q&A session
            speaker_names: Mapping of speaker IDs to names
            meeting_type: Type of meeting for tailored summary
        
        Returns:
            dict: {
                'summary': str,
                'key_points': str,
                'action_items': List[dict],
                'decisions': List[str]
            }
        """
        qa_responses = qa_responses or {}
        speaker_names = speaker_names or {}
        
        # Build the prompt with all context
        prompt = self._build_summary_prompt(
            transcript,
            qa_responses,
            speaker_names,
            meeting_type
        )
        
        print("Generating meeting summary...")
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'system',
                    'content': self._get_system_prompt()
                }, {
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.3,  # Lower temperature for more consistent output
                    'num_predict': 2000
                }
            )
            
            result_text = response['message']['content']
            
            # Parse the response into structured format
            parsed = self._parse_summary_response(result_text)
            
            print("Summary generated successfully!")
            return parsed
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'key_points': "Could not generate key points",
                'action_items': [],
                'decisions': []
            }
    
    def _get_system_prompt(self) -> str:
        """System prompt for the LLM"""
        return """You are an expert meeting assistant. Your job is to analyze meeting transcripts and produce clear, actionable meeting notes.

You always:
- Write in professional, clear language
- Attribute action items to specific people when mentioned
- Include any clarified details provided
- Focus on decisions made and next steps
- Be concise but complete

Format your output with clear sections:
1. SUMMARY - A 2-3 paragraph executive summary
2. KEY POINTS - Bullet points of main discussion topics
3. ACTION ITEMS - Tasks with assignees and deadlines if mentioned
4. DECISIONS - Key decisions that were made"""

    def _build_summary_prompt(
        self,
        transcript: Dict,
        qa_responses: Dict,
        speaker_names: Dict,
        meeting_type: str = None
    ) -> str:
        """Build the complete prompt for summary generation"""
        
        # Get labeled text or build from segments
        if 'labeled_text' in transcript:
            transcript_text = transcript['labeled_text']
        else:
            # Build from segments
            lines = []
            for seg in transcript.get('segments', []):
                speaker = seg.get('speaker', 'Unknown')
                # Replace with actual name if available
                if speaker in speaker_names:
                    speaker = speaker_names[speaker]
                text = seg.get('text', '')
                lines.append(f"[{speaker}]: {text}")
            transcript_text = '\n'.join(lines)
        
        # Replace speaker IDs with names in transcript
        for speaker_id, name in speaker_names.items():
            transcript_text = transcript_text.replace(f"[{speaker_id}]", f"[{name}]")
        
        # Build Q&A context section
        qa_context = ""
        if qa_responses:
            qa_lines = ["CLARIFICATIONS PROVIDED:"]
            for question_id, answer in qa_responses.items():
                if isinstance(answer, dict):
                    qa_lines.append(f"- {answer.get('question', question_id)}: {answer.get('answer', '')}")
                else:
                    qa_lines.append(f"- {question_id}: {answer}")
            qa_context = '\n'.join(qa_lines) + '\n\n'
        
        # Build speaker mapping context
        speaker_context = ""
        if speaker_names:
            speaker_lines = ["MEETING PARTICIPANTS:"]
            for speaker_id, name in speaker_names.items():
                speaker_lines.append(f"- {name}")
            speaker_context = '\n'.join(speaker_lines) + '\n\n'
        
        # Meeting type context
        type_context = ""
        if meeting_type:
            type_context = f"MEETING TYPE: {meeting_type}\n\n"
        
        prompt = f"""{type_context}{speaker_context}{qa_context}MEETING TRANSCRIPT:
{transcript_text}

---

Please analyze this meeting transcript and provide:

1. **SUMMARY**: A concise 2-3 paragraph summary of what was discussed

2. **KEY POINTS**: The main topics and discussion points as bullet points

3. **ACTION ITEMS**: Any tasks or follow-ups mentioned. Format each as:
   - [Assignee]: Task description (Due: date if mentioned)

4. **DECISIONS**: Any decisions or conclusions reached

Make sure to use the actual participant names provided and incorporate any clarifications given."""

        return prompt
    
    def _parse_summary_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        
        summary = ""
        key_points = ""
        action_items = []
        decisions = []
        
        # Split by sections
        sections = {
            'summary': '',
            'key_points': '',
            'action_items': '',
            'decisions': ''
        }
        
        current_section = None
        lines = response_text.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if 'summary' in line_lower and ('**' in line or '#' in line or line_lower.startswith('summary')):
                current_section = 'summary'
                continue
            elif 'key point' in line_lower or 'key discussion' in line_lower:
                current_section = 'key_points'
                continue
            elif 'action item' in line_lower:
                current_section = 'action_items'
                continue
            elif 'decision' in line_lower:
                current_section = 'decisions'
                continue
            
            # Add content to current section
            if current_section and line.strip():
                sections[current_section] += line + '\n'
        
        # Process action items into structured format
        action_items_raw = sections.get('action_items', '')
        action_items = self._parse_action_items(action_items_raw)
        
        # Process decisions into list
        decisions_raw = sections.get('decisions', '')
        decisions = [
            line.strip().lstrip('•-*').strip()
            for line in decisions_raw.split('\n')
            if line.strip() and not line.strip().startswith('#')
        ]
        
        return {
            'summary': sections.get('summary', '').strip() or response_text,
            'key_points': sections.get('key_points', '').strip(),
            'action_items': action_items,
            'decisions': decisions
        }
    
    def _parse_action_items(self, action_items_text: str) -> List[Dict]:
        """Parse action items text into structured format"""
        items = []
        
        for line in action_items_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Remove bullet points
            line = line.lstrip('•-*').strip()
            
            # Try to extract assignee (formats: "[Name]:", "Name:", etc.)
            assignee = None
            description = line
            due_date = None
            
            # Pattern: [Name]: description or Name: description
            match = re.match(r'\[?([^\]:\[]+)\]?\s*:\s*(.+)', line)
            if match:
                assignee = match.group(1).strip()
                description = match.group(2).strip()
            
            # Try to extract due date
            due_match = re.search(r'\(Due:?\s*([^)]+)\)', description, re.IGNORECASE)
            if due_match:
                due_date = due_match.group(1).strip()
                description = description.replace(due_match.group(0), '').strip()
            
            if description:
                items.append({
                    'description': description,
                    'assignee': assignee,
                    'due_date': due_date,
                    'status': 'pending'
                })
        
        return items
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            models = ollama.list()
            model_names = [m['name'].split(':')[0] for m in models.get('models', [])]
            
            if self.model_name not in model_names:
                print(f"Model {self.model_name} not found. Available: {model_names}")
                return False
            
            return True
        except Exception as e:
            print(f"Ollama not accessible: {e}")
            return False
    
    def generate_quick_summary(self, transcript: Dict) -> str:
        """Generate a quick one-paragraph summary"""
        text = transcript.get('labeled_text', transcript.get('text', ''))
        
        prompt = f"""Summarize this meeting in one concise paragraph (3-4 sentences):

{text[:3000]}  # Limit context

Summary:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3, 'num_predict': 200}
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"Error: {e}"
