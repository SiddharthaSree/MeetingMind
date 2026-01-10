"""
Meeting Chat Service
Ask questions about past meetings using local LLM
"""
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """A chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    meeting_context: Optional[str] = None


class MeetingChatService:
    """
    Chat with your meetings using local LLM
    
    Features:
    - Ask questions about specific meetings
    - Search across all meetings
    - Get summaries and action items
    - Find what someone said
    """
    
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.conversation_history: List[ChatMessage] = []
        self._meeting_context: Optional[Dict] = None
    
    def set_meeting_context(self, meeting_data: Dict[str, Any]):
        """Set the current meeting context for questions"""
        self._meeting_context = meeting_data
        self.conversation_history = []  # Reset conversation
    
    def clear_context(self):
        """Clear meeting context"""
        self._meeting_context = None
        self.conversation_history = []
    
    def _build_context_prompt(self) -> str:
        """Build context from meeting data"""
        if not self._meeting_context:
            return ""
        
        meeting = self._meeting_context
        
        context = "MEETING INFORMATION:\n\n"
        
        # Add metadata
        context += f"Date: {meeting.get('created_at', 'Unknown')}\n"
        
        # Add participants
        speakers = meeting.get('speaker_names', {})
        if speakers:
            context += f"Participants: {', '.join(speakers.values())}\n"
        
        context += "\n"
        
        # Add summary
        summary = meeting.get('summary', {})
        if isinstance(summary, dict):
            context += f"SUMMARY:\n{summary.get('summary', 'No summary')}\n\n"
            context += f"KEY POINTS:\n{summary.get('key_points', 'None')}\n\n"
            
            actions = summary.get('action_items', [])
            if actions:
                context += "ACTION ITEMS:\n"
                for item in actions:
                    if isinstance(item, dict):
                        context += f"- {item.get('description', item)}\n"
                    else:
                        context += f"- {item}\n"
                context += "\n"
        
        # Add transcript (truncated if needed)
        transcript = meeting.get('transcript', {})
        if isinstance(transcript, dict):
            segments = transcript.get('segments', [])
            if segments:
                context += "TRANSCRIPT:\n"
                for seg in segments[:100]:  # Limit segments
                    speaker = seg.get('speaker', 'Unknown')
                    text = seg.get('text', '')
                    context += f"[{speaker}]: {text}\n"
                
                if len(segments) > 100:
                    context += f"\n... ({len(segments) - 100} more segments)\n"
        
        return context
    
    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response
        
        Args:
            user_message: User's question
        
        Returns:
            Assistant's response
        """
        try:
            import ollama
        except ImportError:
            return "Error: Ollama not installed. Run: pip install ollama"
        
        # Build system prompt
        system_prompt = """You are a helpful meeting assistant. You help users understand and extract information from their meeting notes.

When answering:
- Be concise and direct
- Reference specific parts of the meeting when relevant
- If you don't know something from the context, say so
- Format action items and decisions clearly
"""
        
        # Add meeting context if available
        context = self._build_context_prompt()
        if context:
            system_prompt += f"\n\n{context}"
        
        # Build messages for Ollama
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history (last 10 messages)
        for msg in self.conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            
            assistant_message = response['message']['content']
            
            # Save to history
            self.conversation_history.append(ChatMessage(
                role="user",
                content=user_message
            ))
            self.conversation_history.append(ChatMessage(
                role="assistant",
                content=assistant_message
            ))
            
            return assistant_message
            
        except Exception as e:
            return f"Error: {str(e)}\n\nMake sure Ollama is running: ollama serve"
    
    def quick_question(self, question: str, meeting_data: Dict) -> str:
        """
        Ask a one-off question about a meeting (no history)
        
        Args:
            question: The question to ask
            meeting_data: Meeting data dict
        
        Returns:
            Answer string
        """
        # Temporarily set context
        old_context = self._meeting_context
        old_history = self.conversation_history
        
        self._meeting_context = meeting_data
        self.conversation_history = []
        
        response = self.chat(question)
        
        # Restore
        self._meeting_context = old_context
        self.conversation_history = old_history
        
        return response
    
    def search_across_meetings(
        self,
        query: str,
        meetings: List[Dict[str, Any]]
    ) -> str:
        """
        Search for information across multiple meetings
        
        Args:
            query: What to search for
            meetings: List of meeting data dicts
        
        Returns:
            Search results
        """
        try:
            import ollama
        except ImportError:
            return "Error: Ollama not installed"
        
        # Build context from all meetings
        context = f"SEARCHING ACROSS {len(meetings)} MEETINGS:\n\n"
        
        for i, meeting in enumerate(meetings[:10], 1):  # Limit to 10
            context += f"--- Meeting {i} ---\n"
            context += f"Date: {meeting.get('created_at', 'Unknown')[:10]}\n"
            
            summary = meeting.get('summary', {})
            if isinstance(summary, dict):
                context += f"Summary: {summary.get('summary', 'N/A')[:500]}\n"
            
            context += "\n"
        
        prompt = f"""Based on the following meetings, answer this question:
        
Question: {query}

{context}

Provide a clear answer, referencing which meeting(s) the information comes from."""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a meeting search assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response['message']['content']
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions based on meeting context"""
        if not self._meeting_context:
            return [
                "What meetings do I have saved?",
                "Show me recent action items",
                "What decisions were made last week?"
            ]
        
        return [
            "What were the main topics discussed?",
            "List all action items from this meeting",
            "What decisions were made?",
            "Summarize what each person said",
            "What are the next steps?",
            "Were there any concerns raised?",
            "What deadlines were mentioned?"
        ]
