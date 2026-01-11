"""
Create demo data for testing MeetingMind
Generates sample audio files and meeting JSON data
"""
import os
import json
import wave
import struct
import math
from pathlib import Path
from datetime import datetime, timedelta
import random

# Create directories
DATA_DIR = Path("data")
MEETINGS_DIR = DATA_DIR / "meetings"
EXPORTS_DIR = DATA_DIR / "exports"
TEMP_DIR = DATA_DIR / "temp"

for d in [MEETINGS_DIR, EXPORTS_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def generate_tone_audio(filename, duration_sec=5, frequency=440, sample_rate=44100):
    """Generate a simple tone WAV file for testing"""
    n_samples = int(duration_sec * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes = 16 bits
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            # Generate sine wave with some variation
            t = i / sample_rate
            # Add some variation to make it more interesting
            freq = frequency * (1 + 0.1 * math.sin(2 * math.pi * 0.5 * t))
            value = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))
            wav_file.writeframes(struct.pack('<h', value))
    
    print(f"✓ Created audio file: {filename}")

def generate_speech_like_audio(filename, duration_sec=10, sample_rate=16000):
    """Generate speech-like audio with varying frequencies"""
    n_samples = int(duration_sec * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes = 16 bits
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            # Simulate speech-like patterns with multiple frequencies
            base_freq = 150 + 100 * math.sin(2 * math.pi * 0.3 * t)  # Varying fundamental
            harmonic1 = 0.3 * math.sin(2 * math.pi * base_freq * 2 * t)
            harmonic2 = 0.2 * math.sin(2 * math.pi * base_freq * 3 * t)
            
            # Add some noise for realism
            noise = random.uniform(-0.05, 0.05)
            
            # Amplitude envelope (speech-like pauses)
            envelope = 0.5 * (1 + math.sin(2 * math.pi * 0.5 * t))
            
            value = envelope * (math.sin(2 * math.pi * base_freq * t) + harmonic1 + harmonic2 + noise)
            value = int(32767 * 0.4 * value)
            value = max(-32767, min(32767, value))
            wav_file.writeframes(struct.pack('<h', value))
    
    print(f"✓ Created speech-like audio: {filename}")

def create_sample_meeting(meeting_id, title, participants, segments, summary=None):
    """Create a sample meeting JSON file"""
    meeting_data = {
        "id": meeting_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "duration_seconds": sum(seg.get("end", 0) - seg.get("start", 0) for seg in segments),
        "participants": participants,
        "transcript": {
            "segments": segments,
            "full_text": " ".join(seg["text"] for seg in segments)
        },
        "summary": summary or generate_summary(segments),
        "action_items": generate_action_items(participants),
        "key_points": generate_key_points(),
        "metadata": {
            "language": "en",
            "model": "demo",
            "processed_at": datetime.now().isoformat()
        }
    }
    
    meeting_file = MEETINGS_DIR / f"{meeting_id}.json"
    with open(meeting_file, 'w', encoding='utf-8') as f:
        json.dump(meeting_data, f, indent=2)
    
    print(f"✓ Created meeting file: {meeting_file}")
    return meeting_data

def generate_summary(segments):
    """Generate a basic summary"""
    return {
        "brief": "This was a productive meeting discussing project updates and next steps.",
        "detailed": "The team met to discuss current project progress, identify blockers, and plan upcoming work. Key decisions were made regarding timeline adjustments and resource allocation.",
        "topics": ["Project Updates", "Timeline Discussion", "Resource Planning", "Next Steps"]
    }

def generate_action_items(participants):
    """Generate sample action items"""
    actions = [
        "Review the quarterly report by end of week",
        "Schedule follow-up meeting with stakeholders",
        "Update project timeline in tracking system",
        "Share meeting notes with the team",
        "Prepare demo for next sprint review"
    ]
    return [
        {
            "task": action,
            "assignee": random.choice(participants),
            "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
            "priority": random.choice(["high", "medium", "low"])
        }
        for action in random.sample(actions, min(3, len(actions)))
    ]

def generate_key_points():
    """Generate sample key points"""
    return [
        "Project is on track for Q1 delivery",
        "Additional resources approved for development",
        "Customer feedback has been positive",
        "New feature requests prioritized for next sprint",
        "Team velocity has improved by 15%"
    ]

def main():
    print("=" * 50)
    print("Creating MeetingMind Demo Data")
    print("=" * 50)
    print()
    
    # 1. Create test audio files
    print("📁 Creating test audio files...")
    
    # Simple test tone
    generate_tone_audio("test_audio.wav", duration_sec=3)
    
    # Longer speech-like audio
    generate_speech_like_audio("demo_meeting_audio.wav", duration_sec=15)
    
    # Create a shorter test file
    generate_tone_audio("short_test.wav", duration_sec=1)
    
    print()
    
    # 2. Create sample meeting data
    print("📁 Creating sample meeting records...")
    
    # Meeting 1: Sprint Planning
    create_sample_meeting(
        meeting_id="meeting_20260110_sprint_planning",
        title="Sprint Planning - Q1 2026",
        participants=["Alice Johnson", "Bob Smith", "Carol Williams"],
        segments=[
            {"start": 0.0, "end": 5.2, "speaker": "Alice Johnson", "text": "Good morning everyone, let's get started with our sprint planning."},
            {"start": 5.5, "end": 12.1, "speaker": "Bob Smith", "text": "Thanks Alice. I've prepared the backlog items for this sprint. We have about 45 story points to discuss."},
            {"start": 12.5, "end": 20.0, "speaker": "Carol Williams", "text": "I reviewed the items yesterday. I think we should prioritize the authentication improvements first."},
            {"start": 20.5, "end": 28.3, "speaker": "Alice Johnson", "text": "Agreed. Security is our top priority this quarter. Bob, can you walk us through the technical requirements?"},
            {"start": 28.8, "end": 40.0, "speaker": "Bob Smith", "text": "Sure. We need to implement OAuth 2.0 integration, add multi-factor authentication, and improve our session management. I estimate about 20 story points for all of this."},
            {"start": 40.5, "end": 50.2, "speaker": "Carol Williams", "text": "That sounds reasonable. I can take the MFA implementation if someone else handles the OAuth work."},
            {"start": 50.8, "end": 60.0, "speaker": "Alice Johnson", "text": "Perfect. Let's assign tasks and wrap up. I'll send out the summary after the meeting."},
        ]
    )
    
    # Meeting 2: Product Review
    create_sample_meeting(
        meeting_id="meeting_20260109_product_review",
        title="Product Review - Feature Demo",
        participants=["David Chen", "Emma Davis", "Frank Miller", "Grace Lee"],
        segments=[
            {"start": 0.0, "end": 8.0, "speaker": "David Chen", "text": "Welcome to our monthly product review. Today we'll be demoing the new transcription features."},
            {"start": 8.5, "end": 18.0, "speaker": "Emma Davis", "text": "I'm excited to show what we've built. The real-time transcription accuracy has improved to 95% in our latest tests."},
            {"start": 18.5, "end": 25.0, "speaker": "Frank Miller", "text": "That's impressive! How does it handle multiple speakers in a noisy environment?"},
            {"start": 25.5, "end": 35.0, "speaker": "Emma Davis", "text": "Great question. We've added speaker diarization that can identify up to 10 different speakers with 90% accuracy."},
            {"start": 35.5, "end": 45.0, "speaker": "Grace Lee", "text": "The customer feedback has been very positive. They especially love the automatic summarization feature."},
            {"start": 45.5, "end": 55.0, "speaker": "David Chen", "text": "Excellent work team. Let's discuss the roadmap for Q2 and prioritize the enhancement requests."},
        ]
    )
    
    # Meeting 3: Team Standup
    create_sample_meeting(
        meeting_id="meeting_20260111_standup",
        title="Daily Standup - January 11",
        participants=["Alice Johnson", "Bob Smith", "Carol Williams", "David Chen"],
        segments=[
            {"start": 0.0, "end": 3.0, "speaker": "Alice Johnson", "text": "Good morning! Let's do a quick standup. Bob, would you like to start?"},
            {"start": 3.5, "end": 12.0, "speaker": "Bob Smith", "text": "Yesterday I finished the API documentation. Today I'm working on the deployment scripts. No blockers."},
            {"start": 12.5, "end": 22.0, "speaker": "Carol Williams", "text": "I completed the unit tests for the transcription module. Today I'm starting integration tests. I might need help with the test data."},
            {"start": 22.5, "end": 30.0, "speaker": "David Chen", "text": "I can help with test data Carol. I was working on that yesterday. Let's sync after this meeting."},
            {"start": 30.5, "end": 38.0, "speaker": "Alice Johnson", "text": "Great teamwork! I'll be in meetings most of today but ping me on Slack if you need anything."},
        ]
    )
    
    print()
    
    # 3. Create a sample export
    print("📁 Creating sample export...")
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "format": "json",
        "meetings_count": 3,
        "total_duration_minutes": 15
    }
    
    export_file = EXPORTS_DIR / "sample_export.json"
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    print(f"✓ Created export file: {export_file}")
    
    print()
    print("=" * 50)
    print("✅ Demo data creation complete!")
    print("=" * 50)
    print()
    print("Created files:")
    print("  📄 test_audio.wav - Simple test tone (3 seconds)")
    print("  📄 demo_meeting_audio.wav - Speech-like audio (15 seconds)")
    print("  📄 short_test.wav - Short test (1 second)")
    print("  📄 data/meetings/meeting_20260110_sprint_planning.json")
    print("  📄 data/meetings/meeting_20260109_product_review.json")
    print("  📄 data/meetings/meeting_20260111_standup.json")
    print("  📄 data/exports/sample_export.json")
    print()
    print("You can now:")
    print("  1. Upload test_audio.wav to test the web interface")
    print("  2. View sample meetings in the data/meetings folder")
    print("  3. Use demo_meeting_audio.wav for transcription testing")

if __name__ == "__main__":
    main()
