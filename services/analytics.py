"""
Meeting Analytics Service
Track meeting patterns, talk time, and productivity metrics
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class MeetingMetrics:
    """Metrics for a single meeting"""
    meeting_id: str
    date: str
    duration_minutes: float
    num_participants: int
    num_action_items: int
    num_decisions: int
    talk_time_by_speaker: Dict[str, float]  # speaker -> seconds
    topics_discussed: List[str]
    sentiment_score: float  # -1 to 1


@dataclass  
class AnalyticsSummary:
    """Summary analytics over a period"""
    total_meetings: int
    total_hours: float
    avg_duration_minutes: float
    total_action_items: int
    total_decisions: int
    meetings_by_day: Dict[str, int]  # day of week -> count
    meetings_by_hour: Dict[int, int]  # hour -> count
    top_participants: List[Tuple[str, int]]  # (name, meeting_count)
    avg_participants: float
    talk_time_distribution: Dict[str, float]  # speaker -> percentage


class AnalyticsService:
    """
    Service for meeting analytics and insights
    
    Features:
    - Track meeting frequency and duration
    - Analyze talk time distribution
    - Identify meeting patterns
    - Generate productivity insights
    - Compare week-over-week metrics
    """
    
    def __init__(self, storage_dir: str = None):
        from core.config import MEETINGS_DIR
        self.storage_dir = Path(storage_dir or MEETINGS_DIR) / "analytics"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.storage_dir / "metrics.json"
        self._metrics: Dict[str, MeetingMetrics] = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Load saved metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    for mid, m in data.items():
                        self._metrics[mid] = MeetingMetrics(**m)
            except Exception as e:
                print(f"Error loading analytics: {e}")
    
    def _save_metrics(self):
        """Save metrics to disk"""
        data = {}
        for mid, m in self._metrics.items():
            data[mid] = {
                'meeting_id': m.meeting_id,
                'date': m.date,
                'duration_minutes': m.duration_minutes,
                'num_participants': m.num_participants,
                'num_action_items': m.num_action_items,
                'num_decisions': m.num_decisions,
                'talk_time_by_speaker': m.talk_time_by_speaker,
                'topics_discussed': m.topics_discussed,
                'sentiment_score': m.sentiment_score
            }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_meeting(
        self,
        meeting_id: str,
        meeting_data: Dict[str, Any]
    ) -> MeetingMetrics:
        """
        Record analytics for a completed meeting
        
        Args:
            meeting_id: Meeting ID
            meeting_data: Full meeting data from controller
        
        Returns:
            MeetingMetrics for the meeting
        """
        # Extract data
        transcript = meeting_data.get('transcript', {})
        summary = meeting_data.get('summary', {})
        
        # Calculate talk time by speaker
        talk_time = defaultdict(float)
        for segment in transcript.get('segments', []):
            speaker = segment.get('speaker', 'Unknown')
            start = segment.get('start', 0)
            end = segment.get('end', start)
            talk_time[speaker] += (end - start)
        
        # Get participants
        participants = list(talk_time.keys())
        
        # Count action items
        action_items = summary.get('action_items', [])
        num_actions = len(action_items) if isinstance(action_items, list) else 0
        
        # Simple sentiment analysis (placeholder - could use LLM)
        sentiment = 0.0  # Neutral
        
        # Get duration
        duration = meeting_data.get('metadata', {}).get('duration', 0)
        if not duration and transcript.get('segments'):
            segments = transcript['segments']
            duration = max(s.get('end', 0) for s in segments)
        
        metrics = MeetingMetrics(
            meeting_id=meeting_id,
            date=meeting_data.get('created_at', datetime.now().isoformat())[:10],
            duration_minutes=duration / 60,
            num_participants=len(participants),
            num_action_items=num_actions,
            num_decisions=len(summary.get('decisions', [])) if isinstance(summary.get('decisions'), list) else 0,
            talk_time_by_speaker=dict(talk_time),
            topics_discussed=summary.get('topics', []),
            sentiment_score=sentiment
        )
        
        self._metrics[meeting_id] = metrics
        self._save_metrics()
        
        return metrics
    
    def get_summary(
        self,
        days: int = 30,
        start_date: str = None,
        end_date: str = None
    ) -> AnalyticsSummary:
        """
        Get analytics summary for a time period
        
        Args:
            days: Number of days to look back (ignored if dates provided)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            AnalyticsSummary
        """
        # Determine date range
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start = end - timedelta(days=days)
        
        # Filter metrics in range
        filtered = []
        for m in self._metrics.values():
            try:
                m_date = datetime.strptime(m.date, "%Y-%m-%d")
                if start <= m_date <= end:
                    filtered.append(m)
            except:
                continue
        
        if not filtered:
            return AnalyticsSummary(
                total_meetings=0,
                total_hours=0,
                avg_duration_minutes=0,
                total_action_items=0,
                total_decisions=0,
                meetings_by_day={},
                meetings_by_hour={},
                top_participants=[],
                avg_participants=0,
                talk_time_distribution={}
            )
        
        # Calculate stats
        total_minutes = sum(m.duration_minutes for m in filtered)
        total_actions = sum(m.num_action_items for m in filtered)
        total_decisions = sum(m.num_decisions for m in filtered)
        total_participants = sum(m.num_participants for m in filtered)
        
        # Meetings by day of week
        by_day = defaultdict(int)
        days_map = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for m in filtered:
            try:
                d = datetime.strptime(m.date, "%Y-%m-%d")
                by_day[days_map[d.weekday()]] += 1
            except:
                pass
        
        # Meetings by hour (placeholder - would need time data)
        by_hour = defaultdict(int)
        
        # Talk time aggregation
        total_talk_time = defaultdict(float)
        for m in filtered:
            for speaker, seconds in m.talk_time_by_speaker.items():
                total_talk_time[speaker] += seconds
        
        # Convert to percentages
        total_seconds = sum(total_talk_time.values())
        talk_distribution = {}
        if total_seconds > 0:
            for speaker, seconds in total_talk_time.items():
                talk_distribution[speaker] = round(seconds / total_seconds * 100, 1)
        
        # Top participants
        participant_count = defaultdict(int)
        for m in filtered:
            for speaker in m.talk_time_by_speaker.keys():
                participant_count[speaker] += 1
        
        top_participants = sorted(
            participant_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return AnalyticsSummary(
            total_meetings=len(filtered),
            total_hours=round(total_minutes / 60, 1),
            avg_duration_minutes=round(total_minutes / len(filtered), 1),
            total_action_items=total_actions,
            total_decisions=total_decisions,
            meetings_by_day=dict(by_day),
            meetings_by_hour=dict(by_hour),
            top_participants=top_participants,
            avg_participants=round(total_participants / len(filtered), 1),
            talk_time_distribution=talk_distribution
        )
    
    def get_talk_time_analysis(self, meeting_id: str) -> Dict[str, Any]:
        """
        Get detailed talk time analysis for a meeting
        
        Returns:
            Dict with talk time stats per speaker
        """
        metrics = self._metrics.get(meeting_id)
        if not metrics:
            return {}
        
        total_time = sum(metrics.talk_time_by_speaker.values())
        
        analysis = {
            'total_duration_seconds': total_time,
            'speakers': []
        }
        
        for speaker, seconds in sorted(
            metrics.talk_time_by_speaker.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = (seconds / total_time * 100) if total_time > 0 else 0
            analysis['speakers'].append({
                'name': speaker,
                'seconds': round(seconds, 1),
                'percentage': round(percentage, 1),
                'formatted': f"{int(seconds // 60)}:{int(seconds % 60):02d}"
            })
        
        return analysis
    
    def get_productivity_score(self, meeting_id: str) -> Dict[str, Any]:
        """
        Calculate a productivity score for a meeting
        
        Factors:
        - Number of action items generated
        - Decisions made
        - Talk time balance (more balanced = better)
        - Meeting duration efficiency
        """
        metrics = self._metrics.get(meeting_id)
        if not metrics:
            return {'score': 0, 'factors': {}}
        
        # Score factors (0-100 each)
        scores = {}
        
        # Action items (more is better, up to ~10)
        scores['action_items'] = min(metrics.num_action_items * 10, 100)
        
        # Decisions (more is better, up to ~5)
        scores['decisions'] = min(metrics.num_decisions * 20, 100)
        
        # Talk time balance (Gini coefficient - lower is more equal)
        if metrics.talk_time_by_speaker:
            times = list(metrics.talk_time_by_speaker.values())
            n = len(times)
            if n > 1 and sum(times) > 0:
                times.sort()
                cum_times = [sum(times[:i+1]) for i in range(n)]
                gini = (n + 1 - 2 * sum(cum_times) / cum_times[-1]) / n
                scores['talk_balance'] = int((1 - gini) * 100)
            else:
                scores['talk_balance'] = 50
        else:
            scores['talk_balance'] = 50
        
        # Duration efficiency (15-45 min is ideal)
        duration = metrics.duration_minutes
        if 15 <= duration <= 45:
            scores['duration'] = 100
        elif duration < 15:
            scores['duration'] = int(duration / 15 * 100)
        else:
            scores['duration'] = max(0, int(100 - (duration - 45) * 2))
        
        # Overall score (weighted average)
        weights = {
            'action_items': 0.3,
            'decisions': 0.25,
            'talk_balance': 0.25,
            'duration': 0.2
        }
        
        overall = sum(scores[k] * weights[k] for k in scores)
        
        return {
            'score': round(overall),
            'factors': scores,
            'interpretation': self._interpret_score(overall)
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpret productivity score"""
        if score >= 80:
            return "Excellent! This was a highly productive meeting."
        elif score >= 60:
            return "Good meeting with clear outcomes."
        elif score >= 40:
            return "Average meeting. Consider setting clearer agendas."
        else:
            return "This meeting could benefit from better structure."
    
    def compare_periods(
        self,
        period1_start: str,
        period1_end: str,
        period2_start: str,
        period2_end: str
    ) -> Dict[str, Any]:
        """Compare metrics between two time periods"""
        summary1 = self.get_summary(start_date=period1_start, end_date=period1_end)
        summary2 = self.get_summary(start_date=period2_start, end_date=period2_end)
        
        def calc_change(old, new):
            if old == 0:
                return 100 if new > 0 else 0
            return round((new - old) / old * 100, 1)
        
        return {
            'period1': {
                'start': period1_start,
                'end': period1_end,
                'meetings': summary1.total_meetings,
                'hours': summary1.total_hours
            },
            'period2': {
                'start': period2_start,
                'end': period2_end,
                'meetings': summary2.total_meetings,
                'hours': summary2.total_hours
            },
            'changes': {
                'meetings': calc_change(summary1.total_meetings, summary2.total_meetings),
                'hours': calc_change(summary1.total_hours, summary2.total_hours),
                'avg_duration': calc_change(summary1.avg_duration_minutes, summary2.avg_duration_minutes),
                'action_items': calc_change(summary1.total_action_items, summary2.total_action_items)
            }
        }
