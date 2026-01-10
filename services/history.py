"""
Meeting History Storage Service
Manages saved meetings with search and retrieval
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class MeetingRecord:
    """Represents a saved meeting"""
    id: str
    title: str
    date: str
    duration_seconds: float
    participants: List[str]
    summary_preview: str
    audio_path: Optional[str]
    has_transcript: bool
    has_summary: bool
    tags: List[str]
    meeting_type: str
    created_at: str
    updated_at: str


class MeetingHistoryService:
    """
    Service for storing and retrieving meeting history
    
    Features:
    - Save meetings with metadata
    - Search by date, participant, keyword
    - Browse meeting history
    - Delete old meetings
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize history service
        
        Args:
            storage_dir: Directory to store meeting data
        """
        from core.config import MEETINGS_DIR
        self.storage_dir = Path(storage_dir or MEETINGS_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.storage_dir / "index.json"
        self._index: Dict[str, MeetingRecord] = {}
        
        self._load_index()
    
    def _load_index(self):
        """Load meeting index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._index = {
                        k: MeetingRecord(**v) for k, v in data.items()
                    }
            except Exception as e:
                print(f"Error loading meeting index: {e}")
                self._index = {}
        else:
            self._index = {}
    
    def _save_index(self):
        """Save meeting index to disk"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                data = {k: asdict(v) for k, v in self._index.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving meeting index: {e}")
    
    def _generate_id(self, data: Dict) -> str:
        """Generate unique ID for a meeting"""
        timestamp = datetime.now().isoformat()
        content = f"{timestamp}-{data.get('title', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def save_meeting(
        self,
        meeting_data: Dict[str, Any],
        audio_path: str = None,
        title: str = None
    ) -> str:
        """
        Save a meeting to history
        
        Args:
            meeting_data: Full meeting data (transcript, summary, etc.)
            audio_path: Path to audio file (will be copied to storage)
            title: Meeting title (auto-generated if not provided)
        
        Returns:
            Meeting ID
        """
        meeting_id = self._generate_id(meeting_data)
        meeting_dir = self.storage_dir / meeting_id
        meeting_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract metadata
        summary = meeting_data.get('summary', {})
        transcript = meeting_data.get('transcript', {})
        metadata = meeting_data.get('metadata', {})
        
        # Generate title if not provided
        if not title:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            title = f"Meeting - {date_str}"
            
            # Try to extract title from summary
            if summary.get('summary'):
                first_line = summary['summary'].split('.')[0][:50]
                if first_line:
                    title = first_line
        
        # Copy audio file if provided
        stored_audio_path = None
        if audio_path and os.path.exists(audio_path):
            ext = Path(audio_path).suffix
            stored_audio_path = str(meeting_dir / f"audio{ext}")
            shutil.copy2(audio_path, stored_audio_path)
        
        # Get participants from speaker mappings
        participants = []
        if 'speaker_names' in meeting_data:
            participants = list(meeting_data['speaker_names'].values())
        
        # Create summary preview
        summary_preview = ""
        if summary.get('summary'):
            summary_preview = summary['summary'][:200]
            if len(summary['summary']) > 200:
                summary_preview += "..."
        
        # Create record
        now = datetime.now().isoformat()
        record = MeetingRecord(
            id=meeting_id,
            title=title,
            date=metadata.get('date', datetime.now().strftime("%Y-%m-%d")),
            duration_seconds=metadata.get('duration', 0),
            participants=participants,
            summary_preview=summary_preview,
            audio_path=stored_audio_path,
            has_transcript=bool(transcript),
            has_summary=bool(summary),
            tags=metadata.get('tags', []),
            meeting_type=metadata.get('meeting_type', 'general'),
            created_at=now,
            updated_at=now
        )
        
        # Save full data
        data_file = meeting_dir / "data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(meeting_data, f, indent=2, default=str)
        
        # Update index
        self._index[meeting_id] = record
        self._save_index()
        
        print(f"Saved meeting: {meeting_id} - {title}")
        return meeting_id
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full meeting data by ID
        
        Args:
            meeting_id: Meeting ID
        
        Returns:
            Meeting data or None if not found
        """
        if meeting_id not in self._index:
            return None
        
        data_file = self.storage_dir / meeting_id / "data.json"
        if not data_file.exists():
            return None
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading meeting {meeting_id}: {e}")
            return None
    
    def get_meeting_record(self, meeting_id: str) -> Optional[MeetingRecord]:
        """Get meeting record (metadata only) by ID"""
        return self._index.get(meeting_id)
    
    def list_meetings(
        self,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = 'date',
        descending: bool = True
    ) -> List[MeetingRecord]:
        """
        List meetings with pagination
        
        Args:
            limit: Max number of results
            offset: Skip first N results
            sort_by: Field to sort by (date, title, duration)
            descending: Sort order
        
        Returns:
            List of MeetingRecord objects
        """
        records = list(self._index.values())
        
        # Sort
        if sort_by == 'date':
            records.sort(key=lambda r: r.date, reverse=descending)
        elif sort_by == 'title':
            records.sort(key=lambda r: r.title.lower(), reverse=descending)
        elif sort_by == 'duration':
            records.sort(key=lambda r: r.duration_seconds, reverse=descending)
        else:
            records.sort(key=lambda r: r.created_at, reverse=descending)
        
        # Paginate
        return records[offset:offset + limit]
    
    def search_meetings(
        self,
        query: str = None,
        participant: str = None,
        date_from: str = None,
        date_to: str = None,
        meeting_type: str = None,
        tags: List[str] = None
    ) -> List[MeetingRecord]:
        """
        Search meetings by various criteria
        
        Args:
            query: Text search in title and summary
            participant: Filter by participant name
            date_from: Filter from date (YYYY-MM-DD)
            date_to: Filter to date (YYYY-MM-DD)
            meeting_type: Filter by meeting type
            tags: Filter by tags
        
        Returns:
            List of matching MeetingRecord objects
        """
        results = []
        
        for record in self._index.values():
            # Text search
            if query:
                query_lower = query.lower()
                if not (
                    query_lower in record.title.lower() or
                    query_lower in record.summary_preview.lower() or
                    any(query_lower in p.lower() for p in record.participants)
                ):
                    continue
            
            # Participant filter
            if participant:
                if not any(participant.lower() in p.lower() for p in record.participants):
                    continue
            
            # Date range filter
            if date_from and record.date < date_from:
                continue
            if date_to and record.date > date_to:
                continue
            
            # Meeting type filter
            if meeting_type and record.meeting_type != meeting_type:
                continue
            
            # Tags filter
            if tags and not any(t in record.tags for t in tags):
                continue
            
            results.append(record)
        
        # Sort by date descending
        results.sort(key=lambda r: r.date, reverse=True)
        
        return results
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """
        Delete a meeting
        
        Args:
            meeting_id: Meeting ID
        
        Returns:
            True if deleted, False if not found
        """
        if meeting_id not in self._index:
            return False
        
        # Remove from index
        del self._index[meeting_id]
        self._save_index()
        
        # Delete files
        meeting_dir = self.storage_dir / meeting_id
        if meeting_dir.exists():
            shutil.rmtree(meeting_dir)
        
        print(f"Deleted meeting: {meeting_id}")
        return True
    
    def update_meeting(
        self,
        meeting_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update meeting metadata
        
        Args:
            meeting_id: Meeting ID
            updates: Fields to update (title, tags, etc.)
        
        Returns:
            True if updated, False if not found
        """
        if meeting_id not in self._index:
            return False
        
        record = self._index[meeting_id]
        
        # Update allowed fields
        if 'title' in updates:
            record.title = updates['title']
        if 'tags' in updates:
            record.tags = updates['tags']
        if 'meeting_type' in updates:
            record.meeting_type = updates['meeting_type']
        if 'participants' in updates:
            record.participants = updates['participants']
        
        record.updated_at = datetime.now().isoformat()
        
        self._save_index()
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get meeting history statistics"""
        records = list(self._index.values())
        
        if not records:
            return {
                'total_meetings': 0,
                'total_duration_hours': 0,
                'unique_participants': 0,
                'meetings_by_type': {},
                'meetings_by_month': {}
            }
        
        total_duration = sum(r.duration_seconds for r in records)
        all_participants = set()
        for r in records:
            all_participants.update(r.participants)
        
        # Group by type
        by_type = {}
        for r in records:
            by_type[r.meeting_type] = by_type.get(r.meeting_type, 0) + 1
        
        # Group by month
        by_month = {}
        for r in records:
            month = r.date[:7]  # YYYY-MM
            by_month[month] = by_month.get(month, 0) + 1
        
        return {
            'total_meetings': len(records),
            'total_duration_hours': round(total_duration / 3600, 1),
            'unique_participants': len(all_participants),
            'meetings_by_type': by_type,
            'meetings_by_month': dict(sorted(by_month.items()))
        }
    
    def cleanup_old_meetings(self, days: int = 90) -> int:
        """
        Delete meetings older than specified days
        
        Args:
            days: Delete meetings older than this
        
        Returns:
            Number of meetings deleted
        """
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        to_delete = [
            r.id for r in self._index.values()
            if r.date < cutoff
        ]
        
        for meeting_id in to_delete:
            self.delete_meeting(meeting_id)
        
        return len(to_delete)
