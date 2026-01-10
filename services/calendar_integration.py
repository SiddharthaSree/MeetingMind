"""
Calendar Integration Service
Sync with Google Calendar and Outlook for meeting context
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class CalendarProvider(Enum):
    """Supported calendar providers"""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    ICAL = "ical"


@dataclass
class CalendarEvent:
    """A calendar event"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    description: str = ""
    location: str = ""
    meeting_url: str = ""
    organizer: str = ""
    provider: CalendarProvider = CalendarProvider.GOOGLE
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'attendees': self.attendees,
            'description': self.description,
            'location': self.location,
            'meeting_url': self.meeting_url,
            'organizer': self.organizer,
            'provider': self.provider.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CalendarEvent':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            attendees=data.get('attendees', []),
            description=data.get('description', ''),
            location=data.get('location', ''),
            meeting_url=data.get('meeting_url', ''),
            organizer=data.get('organizer', ''),
            provider=CalendarProvider(data.get('provider', 'google'))
        )


class CalendarIntegration:
    """
    Calendar integration for meeting context
    
    Provides:
    - Sync with Google Calendar (via OAuth or API key)
    - Sync with Outlook Calendar (via Microsoft Graph)
    - Import from iCal files
    - Auto-populate meeting titles and attendees
    - Smart meeting matching
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".meetingmind" / "calendar_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cached events
        self._events: List[CalendarEvent] = []
        self._load_cached_events()
        
        # Provider configurations
        self.google_config: Dict = {}
        self.outlook_config: Dict = {}
    
    def _load_cached_events(self):
        """Load cached events from disk"""
        cache_file = self.cache_dir / "events.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self._events = [CalendarEvent.from_dict(e) for e in data]
            except Exception as e:
                print(f"Error loading calendar cache: {e}")
                self._events = []
    
    def _save_cached_events(self):
        """Save events to cache"""
        cache_file = self.cache_dir / "events.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump([e.to_dict() for e in self._events], f, indent=2)
        except Exception as e:
            print(f"Error saving calendar cache: {e}")
    
    # =========================================================================
    # Google Calendar
    # =========================================================================
    
    def configure_google(self, credentials_file: str):
        """
        Configure Google Calendar integration
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON
        """
        self.google_config = {
            'credentials_file': credentials_file,
            'scopes': ['https://www.googleapis.com/auth/calendar.readonly']
        }
    
    def sync_google_calendar(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """
        Sync events from Google Calendar
        
        Requires google-api-python-client and google-auth-oauthlib
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            creds = None
            token_file = self.cache_dir / "google_token.json"
            
            # Load existing token
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file))
            
            # Get new token if needed
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.google_config['credentials_file'],
                    self.google_config['scopes']
                )
                creds = flow.run_local_server(port=0)
                
                # Save token
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())
            
            # Build service
            service = build('calendar', 'v3', credentials=creds)
            
            # Get events
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for item in events_result.get('items', []):
                event = CalendarEvent(
                    id=item['id'],
                    title=item.get('summary', 'Untitled'),
                    start_time=datetime.fromisoformat(
                        item['start'].get('dateTime', item['start'].get('date')).replace('Z', '+00:00')
                    ),
                    end_time=datetime.fromisoformat(
                        item['end'].get('dateTime', item['end'].get('date')).replace('Z', '+00:00')
                    ),
                    attendees=[a.get('email', '') for a in item.get('attendees', [])],
                    description=item.get('description', ''),
                    location=item.get('location', ''),
                    meeting_url=self._extract_meeting_url(item),
                    organizer=item.get('organizer', {}).get('email', ''),
                    provider=CalendarProvider.GOOGLE
                )
                events.append(event)
            
            # Update cache
            self._events = [e for e in self._events if e.provider != CalendarProvider.GOOGLE]
            self._events.extend(events)
            self._save_cached_events()
            
            return events
            
        except ImportError:
            print("Google Calendar API libraries not installed.")
            print("Install with: pip install google-api-python-client google-auth-oauthlib")
            return []
        except Exception as e:
            print(f"Error syncing Google Calendar: {e}")
            return []
    
    # =========================================================================
    # Outlook Calendar
    # =========================================================================
    
    def configure_outlook(self, client_id: str, client_secret: str):
        """
        Configure Outlook Calendar integration via Microsoft Graph
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
        """
        self.outlook_config = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scopes': ['Calendars.Read']
        }
    
    def sync_outlook_calendar(self, days_ahead: int = 7) -> List[CalendarEvent]:
        """
        Sync events from Outlook Calendar via Microsoft Graph
        
        Requires msal library
        """
        try:
            import msal
            import requests
            
            # Create app
            app = msal.PublicClientApplication(
                self.outlook_config['client_id'],
                authority="https://login.microsoftonline.com/common"
            )
            
            # Try to get cached token
            accounts = app.get_accounts()
            result = None
            
            if accounts:
                result = app.acquire_token_silent(
                    self.outlook_config['scopes'],
                    account=accounts[0]
                )
            
            if not result:
                # Interactive login
                result = app.acquire_token_interactive(
                    scopes=self.outlook_config['scopes']
                )
            
            if 'access_token' not in result:
                print("Failed to get Outlook access token")
                return []
            
            # Get calendar events
            headers = {
                'Authorization': f"Bearer {result['access_token']}",
                'Content-Type': 'application/json'
            }
            
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            response = requests.get(
                f"https://graph.microsoft.com/v1.0/me/calendarview"
                f"?startDateTime={time_min}&endDateTime={time_max}",
                headers=headers
            )
            
            events = []
            for item in response.json().get('value', []):
                event = CalendarEvent(
                    id=item['id'],
                    title=item.get('subject', 'Untitled'),
                    start_time=datetime.fromisoformat(
                        item['start']['dateTime'].replace('Z', '+00:00')
                    ),
                    end_time=datetime.fromisoformat(
                        item['end']['dateTime'].replace('Z', '+00:00')
                    ),
                    attendees=[a.get('emailAddress', {}).get('address', '') 
                              for a in item.get('attendees', [])],
                    description=item.get('bodyPreview', ''),
                    location=item.get('location', {}).get('displayName', ''),
                    meeting_url=item.get('onlineMeeting', {}).get('joinUrl', ''),
                    organizer=item.get('organizer', {}).get('emailAddress', {}).get('address', ''),
                    provider=CalendarProvider.OUTLOOK
                )
                events.append(event)
            
            # Update cache
            self._events = [e for e in self._events if e.provider != CalendarProvider.OUTLOOK]
            self._events.extend(events)
            self._save_cached_events()
            
            return events
            
        except ImportError:
            print("Microsoft Graph libraries not installed.")
            print("Install with: pip install msal requests")
            return []
        except Exception as e:
            print(f"Error syncing Outlook Calendar: {e}")
            return []
    
    # =========================================================================
    # iCal Import
    # =========================================================================
    
    def import_ical(self, ical_path: str) -> List[CalendarEvent]:
        """
        Import events from an iCal (.ics) file
        
        Requires icalendar library
        """
        try:
            from icalendar import Calendar
            
            with open(ical_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())
            
            events = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    start = component.get('dtstart').dt
                    end = component.get('dtend').dt if component.get('dtend') else start
                    
                    # Ensure datetime (not date)
                    if not isinstance(start, datetime):
                        start = datetime.combine(start, datetime.min.time())
                    if not isinstance(end, datetime):
                        end = datetime.combine(end, datetime.min.time())
                    
                    attendees = []
                    for attendee in component.get('attendee', []):
                        email = str(attendee).replace('mailto:', '')
                        attendees.append(email)
                    
                    event = CalendarEvent(
                        id=str(component.get('uid', '')),
                        title=str(component.get('summary', 'Untitled')),
                        start_time=start,
                        end_time=end,
                        attendees=attendees,
                        description=str(component.get('description', '')),
                        location=str(component.get('location', '')),
                        meeting_url='',
                        organizer=str(component.get('organizer', '')).replace('mailto:', ''),
                        provider=CalendarProvider.ICAL
                    )
                    events.append(event)
            
            # Update cache
            self._events.extend(events)
            self._save_cached_events()
            
            return events
            
        except ImportError:
            print("iCalendar library not installed.")
            print("Install with: pip install icalendar")
            return []
        except Exception as e:
            print(f"Error importing iCal: {e}")
            return []
    
    # =========================================================================
    # Meeting Matching
    # =========================================================================
    
    def get_current_meeting(self, tolerance_minutes: int = 10) -> Optional[CalendarEvent]:
        """
        Get the meeting happening now (with some tolerance)
        
        Args:
            tolerance_minutes: Allow matching meetings that started/ended within this window
        """
        now = datetime.now()
        tolerance = timedelta(minutes=tolerance_minutes)
        
        for event in self._events:
            # Check if now is within event time (with tolerance)
            start_with_tolerance = event.start_time - tolerance
            end_with_tolerance = event.end_time + tolerance
            
            if start_with_tolerance <= now <= end_with_tolerance:
                return event
        
        return None
    
    def get_upcoming_meetings(self, hours: int = 24) -> List[CalendarEvent]:
        """Get meetings in the next N hours"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        
        upcoming = [
            e for e in self._events
            if now <= e.start_time <= cutoff
        ]
        
        return sorted(upcoming, key=lambda e: e.start_time)
    
    def find_meeting_by_title(self, title: str) -> Optional[CalendarEvent]:
        """Find a meeting by title (fuzzy match)"""
        title_lower = title.lower()
        
        for event in self._events:
            if title_lower in event.title.lower():
                return event
        
        return None
    
    def find_meeting_by_attendees(self, attendees: List[str]) -> Optional[CalendarEvent]:
        """Find a meeting that has all specified attendees"""
        attendees_lower = [a.lower() for a in attendees]
        
        for event in self._events:
            event_attendees = [a.lower() for a in event.attendees]
            if all(a in event_attendees for a in attendees_lower):
                return event
        
        return None
    
    def get_meeting_context(self, event: CalendarEvent) -> Dict[str, Any]:
        """
        Get rich context for a meeting to pre-populate notes
        
        Returns meeting title, attendees, agenda (from description), etc.
        """
        return {
            'title': event.title,
            'attendees': event.attendees,
            'organizer': event.organizer,
            'scheduled_start': event.start_time.strftime('%Y-%m-%d %H:%M'),
            'scheduled_end': event.end_time.strftime('%Y-%m-%d %H:%M'),
            'duration_minutes': (event.end_time - event.start_time).seconds // 60,
            'location': event.location,
            'meeting_url': event.meeting_url,
            'agenda': event.description,
            'provider': event.provider.value
        }
    
    def _extract_meeting_url(self, google_event: Dict) -> str:
        """Extract meeting URL from Google Calendar event"""
        # Check for Google Meet
        if 'conferenceData' in google_event:
            for ep in google_event['conferenceData'].get('entryPoints', []):
                if ep.get('entryPointType') == 'video':
                    return ep.get('uri', '')
        
        # Check description for common meeting URLs
        description = google_event.get('description', '')
        import re
        
        patterns = [
            r'https://meet\.google\.com/[a-z-]+',
            r'https://zoom\.us/j/\d+',
            r'https://teams\.microsoft\.com/l/meetup-join/[^\s]+',
            r'https://\w+\.webex\.com/\w+/j\.php\?[^\s]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        return ''
    
    def all_events(self) -> List[CalendarEvent]:
        """Get all cached events"""
        return self._events
    
    def clear_cache(self):
        """Clear all cached events"""
        self._events = []
        cache_file = self.cache_dir / "events.json"
        if cache_file.exists():
            cache_file.unlink()


# Manual event creation for users without calendar integration
def create_manual_event(
    title: str,
    start_time: datetime,
    duration_minutes: int = 60,
    attendees: List[str] = None,
    description: str = ""
) -> CalendarEvent:
    """Create a manual calendar event"""
    return CalendarEvent(
        id=f"manual_{datetime.now().timestamp()}",
        title=title,
        start_time=start_time,
        end_time=start_time + timedelta(minutes=duration_minutes),
        attendees=attendees or [],
        description=description,
        provider=CalendarProvider.ICAL
    )
