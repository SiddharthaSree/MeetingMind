"""
Meeting Highlights & Bookmarks Service
Mark important moments during or after meetings
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class HighlightType(Enum):
    """Types of highlights"""
    IMPORTANT = "important"
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    QUESTION = "question"
    FOLLOWUP = "followup"
    BOOKMARK = "bookmark"


@dataclass
class Highlight:
    """A highlighted moment in a meeting"""
    id: str
    meeting_id: str
    timestamp: float  # seconds into the meeting
    end_timestamp: Optional[float]  # for ranges
    type: HighlightType
    text: str  # the highlighted text
    note: str  # user's note
    speaker: Optional[str]
    created_at: str
    tags: List[str]


class HighlightsService:
    """
    Service for managing meeting highlights and bookmarks
    
    Features:
    - Mark important moments with timestamp
    - Different highlight types (action, decision, question)
    - Add notes to highlights
    - Search across all highlights
    - Export highlights as summary
    """
    
    def __init__(self, storage_dir: str = None):
        from core.config import MEETINGS_DIR
        self.storage_dir = Path(storage_dir or MEETINGS_DIR) / "highlights"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self._highlights: Dict[str, List[Highlight]] = {}  # meeting_id -> highlights
        self._load_all()
    
    def _get_file_path(self, meeting_id: str) -> Path:
        return self.storage_dir / f"{meeting_id}_highlights.json"
    
    def _load_all(self):
        """Load all highlights from storage"""
        for file_path in self.storage_dir.glob("*_highlights.json"):
            meeting_id = file_path.stem.replace("_highlights", "")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self._highlights[meeting_id] = [
                        Highlight(
                            **{**h, 'type': HighlightType(h['type'])}
                        ) for h in data
                    ]
            except Exception as e:
                print(f"Error loading highlights for {meeting_id}: {e}")
    
    def _save(self, meeting_id: str):
        """Save highlights for a meeting"""
        highlights = self._highlights.get(meeting_id, [])
        file_path = self._get_file_path(meeting_id)
        
        data = [
            {**asdict(h), 'type': h.type.value}
            for h in highlights
        ]
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_highlight(
        self,
        meeting_id: str,
        timestamp: float,
        text: str,
        highlight_type: HighlightType = HighlightType.BOOKMARK,
        note: str = "",
        speaker: str = None,
        end_timestamp: float = None,
        tags: List[str] = None
    ) -> Highlight:
        """
        Add a highlight to a meeting
        
        Args:
            meeting_id: Meeting ID
            timestamp: Time in seconds
            text: The highlighted text
            highlight_type: Type of highlight
            note: User's note about this highlight
            speaker: Who said this
            end_timestamp: End time for ranges
            tags: Optional tags
        
        Returns:
            The created Highlight
        """
        highlight = Highlight(
            id=f"h_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            meeting_id=meeting_id,
            timestamp=timestamp,
            end_timestamp=end_timestamp,
            type=highlight_type,
            text=text,
            note=note,
            speaker=speaker,
            created_at=datetime.now().isoformat(),
            tags=tags or []
        )
        
        if meeting_id not in self._highlights:
            self._highlights[meeting_id] = []
        
        self._highlights[meeting_id].append(highlight)
        self._save(meeting_id)
        
        return highlight
    
    def get_highlights(
        self,
        meeting_id: str,
        highlight_type: HighlightType = None
    ) -> List[Highlight]:
        """Get highlights for a meeting, optionally filtered by type"""
        highlights = self._highlights.get(meeting_id, [])
        
        if highlight_type:
            highlights = [h for h in highlights if h.type == highlight_type]
        
        # Sort by timestamp
        return sorted(highlights, key=lambda h: h.timestamp)
    
    def delete_highlight(self, meeting_id: str, highlight_id: str) -> bool:
        """Delete a highlight"""
        if meeting_id not in self._highlights:
            return False
        
        original_len = len(self._highlights[meeting_id])
        self._highlights[meeting_id] = [
            h for h in self._highlights[meeting_id]
            if h.id != highlight_id
        ]
        
        if len(self._highlights[meeting_id]) < original_len:
            self._save(meeting_id)
            return True
        return False
    
    def update_highlight(
        self,
        meeting_id: str,
        highlight_id: str,
        note: str = None,
        tags: List[str] = None,
        highlight_type: HighlightType = None
    ) -> Optional[Highlight]:
        """Update a highlight"""
        highlights = self._highlights.get(meeting_id, [])
        
        for h in highlights:
            if h.id == highlight_id:
                if note is not None:
                    h.note = note
                if tags is not None:
                    h.tags = tags
                if highlight_type is not None:
                    h.type = highlight_type
                self._save(meeting_id)
                return h
        
        return None
    
    def search_highlights(
        self,
        query: str,
        highlight_type: HighlightType = None,
        meeting_id: str = None
    ) -> List[Highlight]:
        """
        Search across all highlights
        
        Args:
            query: Search text
            highlight_type: Filter by type
            meeting_id: Filter by meeting
        
        Returns:
            Matching highlights
        """
        results = []
        query_lower = query.lower()
        
        meetings_to_search = [meeting_id] if meeting_id else self._highlights.keys()
        
        for mid in meetings_to_search:
            for h in self._highlights.get(mid, []):
                if highlight_type and h.type != highlight_type:
                    continue
                
                # Search in text, note, and tags
                if (query_lower in h.text.lower() or
                    query_lower in h.note.lower() or
                    any(query_lower in tag.lower() for tag in h.tags)):
                    results.append(h)
        
        return results
    
    def get_action_items(self, meeting_id: str = None) -> List[Highlight]:
        """Get all action items, optionally for a specific meeting"""
        if meeting_id:
            return self.get_highlights(meeting_id, HighlightType.ACTION_ITEM)
        
        all_actions = []
        for mid in self._highlights:
            all_actions.extend(
                self.get_highlights(mid, HighlightType.ACTION_ITEM)
            )
        return all_actions
    
    def get_decisions(self, meeting_id: str = None) -> List[Highlight]:
        """Get all decisions, optionally for a specific meeting"""
        if meeting_id:
            return self.get_highlights(meeting_id, HighlightType.DECISION)
        
        all_decisions = []
        for mid in self._highlights:
            all_decisions.extend(
                self.get_highlights(mid, HighlightType.DECISION)
            )
        return all_decisions
    
    def export_highlights_markdown(self, meeting_id: str) -> str:
        """Export highlights as markdown"""
        highlights = self.get_highlights(meeting_id)
        
        if not highlights:
            return "No highlights for this meeting."
        
        md = "# Meeting Highlights\n\n"
        
        # Group by type
        by_type: Dict[HighlightType, List[Highlight]] = {}
        for h in highlights:
            if h.type not in by_type:
                by_type[h.type] = []
            by_type[h.type].append(h)
        
        type_names = {
            HighlightType.DECISION: "📋 Decisions",
            HighlightType.ACTION_ITEM: "✅ Action Items",
            HighlightType.IMPORTANT: "⭐ Important Points",
            HighlightType.QUESTION: "❓ Questions",
            HighlightType.FOLLOWUP: "📌 Follow-ups",
            HighlightType.BOOKMARK: "🔖 Bookmarks"
        }
        
        for htype in HighlightType:
            if htype in by_type:
                md += f"## {type_names.get(htype, htype.value)}\n\n"
                for h in by_type[htype]:
                    time_str = self._format_time(h.timestamp)
                    speaker_str = f" ({h.speaker})" if h.speaker else ""
                    md += f"- **[{time_str}]**{speaker_str} {h.text}\n"
                    if h.note:
                        md += f"  - *Note: {h.note}*\n"
                md += "\n"
        
        return md
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
