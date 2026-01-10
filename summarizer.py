"""
Summarizer module - Generates meeting summaries using Ollama (local LLM)
"""
import ollama
from typing import Dict, List


class Summarizer:
    def __init__(self, model_name="llama3.2"):
        """
        Initialize the Ollama summarizer
        
        Args:
            model_name (str): Ollama model to use (llama3.2, mistral, llama2, etc.)
        """
        self.model_name = model_name
        print(f"Using Ollama model: {model_name}")
    
    def summarize_transcript(self, transcript: str) -> Dict[str, str]:
        """
        Generate a meeting summary with action items from transcript
        
        Args:
            transcript (str): The meeting transcript text
        
        Returns:
            dict: Contains 'summary', 'action_items', and 'key_points'
        """
        if not transcript or transcript.strip() == "":
            return {
                'summary': "No transcript provided",
                'action_items': "None",
                'key_points': "None"
            }
        
        print("Generating meeting summary...")
        
        # Create comprehensive prompt for the LLM
        prompt = f"""You are a professional meeting assistant. Analyze the following meeting transcript and provide:

1. A concise summary (2-3 paragraphs)
2. Key discussion points (bullet points)
3. Action items with responsible parties if mentioned

Transcript:
{transcript}

Please format your response as follows:

SUMMARY:
[Write a clear, concise summary here]

KEY POINTS:
- [Point 1]
- [Point 2]
- [Point 3]
...

ACTION ITEMS:
- [Action item 1]
- [Action item 2]
...

If there are no clear action items, write "No specific action items identified."
"""
        
        try:
            # Call Ollama API
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            result_text = response['message']['content']
            
            # Parse the response
            parsed = self._parse_response(result_text)
            
            print("Summary generated successfully!")
            return parsed
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'action_items': "Could not generate action items due to error",
                'key_points': "Could not generate key points due to error"
            }
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the LLM response into structured sections
        
        Args:
            response_text (str): Raw response from LLM
        
        Returns:
            dict: Parsed sections
        """
        summary = ""
        key_points = ""
        action_items = ""
        
        # Split by sections
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line_upper = line.strip().upper()
            
            if 'SUMMARY:' in line_upper:
                current_section = 'summary'
                continue
            elif 'KEY POINTS:' in line_upper or 'KEY DISCUSSION POINTS:' in line_upper:
                current_section = 'key_points'
                continue
            elif 'ACTION ITEMS:' in line_upper or 'ACTION ITEM:' in line_upper:
                current_section = 'action_items'
                continue
            
            # Add content to appropriate section
            if current_section == 'summary' and line.strip():
                summary += line + '\n'
            elif current_section == 'key_points' and line.strip():
                key_points += line + '\n'
            elif current_section == 'action_items' and line.strip():
                action_items += line + '\n'
        
        # Fallback if parsing failed
        if not summary and not key_points and not action_items:
            summary = response_text
            key_points = "Could not parse key points"
            action_items = "Could not parse action items"
        
        return {
            'summary': summary.strip() or "No summary generated",
            'key_points': key_points.strip() or "No key points identified",
            'action_items': action_items.strip() or "No action items identified"
        }
    
    def check_ollama_status(self) -> bool:
        """
        Check if Ollama is running and model is available
        
        Returns:
            bool: True if Ollama is accessible
        """
        try:
            ollama.list()
            return True
        except Exception as e:
            print(f"Ollama not accessible: {e}")
            return False


# Convenience function
def summarize_text(transcript: str, model_name="llama3.2") -> Dict[str, str]:
    """
    Quick summarization function
    
    Args:
        transcript (str): Meeting transcript
        model_name (str): Ollama model name
    
    Returns:
        dict: Summary, key points, and action items
    """
    summarizer = Summarizer(model_name=model_name)
    return summarizer.summarize_transcript(transcript)
