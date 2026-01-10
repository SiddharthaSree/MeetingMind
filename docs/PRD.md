# MeetingMind - Product Requirements Document (PRD)

## Document Info
| Field | Value |
|-------|-------|
| Version | 1.0 |
| Last Updated | January 10, 2026 |
| Status | In Development |
| Owner | Product Team |

---

## 🎯 Vision Statement

**MeetingMind** is a 100% free, offline meeting assistant that captures, transcribes, and intelligently summarizes your meetings - even when your company doesn't have recording features enabled.

> "Your personal meeting memory that works when corporate tools don't."

---

## 🎪 Problem Statement

### The Pain Points

1. **No Recording Access**
   - Many companies use basic Teams/Zoom plans without recording
   - Free plans don't include cloud recording
   - IT policies may disable recording features

2. **Privacy Concerns with Official Recording**
   - "Recording started" notifications change meeting dynamics
   - Some attendees become guarded when recorded
   - Personal notes shouldn't require company approval

3. **Post-Meeting Memory Loss**
   - Details forgotten within hours
   - Action items unclear
   - "Who said they'd do that?" confusion

4. **Existing Tools Are Expensive**
   - Otter.ai, Fireflies.ai charge monthly fees
   - They send data to cloud servers
   - Privacy-conscious users have no alternative

---

## 👥 Target Users

### Primary Persona: Corporate Employee
- Works at company with basic Microsoft 365/Zoom license
- Attends 5-10 meetings per week
- Needs personal meeting notes
- Can't or won't use official recording

### Secondary Persona: Freelancer/Consultant
- Uses free Zoom/Teams/Meet
- Client meetings need documentation
- Can't afford paid transcription services
- Values privacy (client confidentiality)

### Tertiary Persona: Student/Researcher
- Records lectures, interviews, research calls
- Limited budget
- Needs speaker identification
- Wants searchable archive

---

## 🏗️ Product Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         MEETINGMIND v2.0                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   System    │  │   Meeting   │  │   Auto      │                │
│  │   Tray App  │──│   Detector  │──│   Upload    │                │
│  │   (PyQt6)   │  │             │  │   Service   │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│         │                                  │                       │
│         ▼                                  ▼                       │
│  ┌─────────────────────────────────────────────────────┐          │
│  │              AUDIO CAPTURE ENGINE                    │          │
│  │  ┌───────────────┐  ┌───────────────┐               │          │
│  │  │ System Audio  │  │  Microphone   │               │          │
│  │  │ (WASAPI)      │  │  (Optional)   │               │          │
│  │  └───────────────┘  └───────────────┘               │          │
│  └─────────────────────────────────────────────────────┘          │
│                            │                                       │
│                            ▼                                       │
│  ┌─────────────────────────────────────────────────────┐          │
│  │              PROCESSING PIPELINE                     │          │
│  │                                                      │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │          │
│  │  │ Whisper  │─▶│ Speaker  │─▶│ Ollama   │          │          │
│  │  │ (STT)    │  │ Diarize  │  │ (LLM)    │          │          │
│  │  └──────────┘  └──────────┘  └──────────┘          │          │
│  │                                    │                │          │
│  │                                    ▼                │          │
│  │                          ┌──────────────┐          │          │
│  │                          │  Post-Call   │          │          │
│  │                          │  Q&A Engine  │          │          │
│  │                          └──────────────┘          │          │
│  └─────────────────────────────────────────────────────┘          │
│                            │                                       │
│                            ▼                                       │
│  ┌─────────────────────────────────────────────────────┐          │
│  │                    OUTPUT                            │          │
│  │  • Transcript with Speaker Labels                   │          │
│  │  • Meeting Summary                                  │          │
│  │  • Action Items (assigned to speakers)              │          │
│  │  • Q&A Clarifications                               │          │
│  │  • Export (TXT, MD, PDF, Notion, Todoist)          │          │
│  └─────────────────────────────────────────────────────┘          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Feature Specifications

### Phase 1: MVP (v1.0) - Core Features

#### F1: System Audio Capture
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Record system audio from any application (Teams, Zoom, Meet, etc.) |
| Technical | WASAPI loopback on Windows |
| User Story | As a user, I want to capture meeting audio without using in-app recording |

#### F2: File Import
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Upload existing audio/video files for processing |
| Formats | MP3, WAV, M4A, MP4, WEBM, OGG, FLAC |
| User Story | As a user, I want to process recordings I already have |

#### F3: Speaker Diarization
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Identify different speakers in the meeting |
| Technical | pyannote-audio (offline, free) |
| Output | Speaker 1, Speaker 2, etc. with option to rename |
| User Story | As a user, I want to know who said what |

#### F4: Transcription with Speaker Labels
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Convert speech to text with speaker attribution |
| Technical | Whisper (offline) |
| Output | Timestamped transcript with speaker labels |
| User Story | As a user, I want a readable transcript showing who spoke |

#### F5: Smart Summary Generation
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Generate meeting summary, key points, action items |
| Technical | Ollama with llama3.2/mistral |
| Output | Summary, key points, action items per speaker |
| User Story | As a user, I want to quickly understand what happened |

#### F6: Post-Meeting Q&A (Interactive Workflow)
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Interactive Q&A session that drives final output generation |
| Mode | User-configurable: "Quick" (3-5 questions) or "Detailed" (5-10 questions) |
| Speaker ID | Play audio snippet of each speaker, ask user to name them |
| Clarifications | Ask about ambiguous dates, owners, acronyms, action items |
| Workflow | Processing → Q&A → User Answers → THEN Generate Final Notes |
| Examples | "🎧 Who is this person? [Play Audio]", "What is the specific deadline date?" |
| User Story | As a user, I want to clarify ambiguities while I remember, so my final notes are accurate |

#### F7: System Tray Application
| Field | Description |
|-------|-------------|
| Priority | P0 (Must Have) |
| Description | Lightweight system tray app for quick access |
| Features | Start/Stop recording, Status indicator, Quick settings |
| User Story | As a user, I want easy access without opening a full app |

### Phase 2: Enhanced (v1.1)

#### F8: Meeting Detection
| Field | Description |
|-------|-------------|
| Priority | P1 (Should Have) |
| Description | Auto-detect when Teams/Zoom/Meet opens |
| Behavior | Prompt: "Meeting detected. Start recording?" |
| User Story | As a user, I don't want to forget to start recording |

#### F9: Auto-Process on Meeting End
| Field | Description |
|-------|-------------|
| Priority | P1 (Should Have) |
| Description | Detect meeting end and auto-start processing |
| Behavior | Meeting app closes → Processing begins → Q&A appears |
| User Story | As a user, I want seamless transition from meeting to notes |

#### F10: Speaker Name Assignment
| Field | Description |
|-------|-------------|
| Priority | P1 (Should Have) |
| Description | Assign real names to detected speakers |
| Features | Voice profile learning, Manual assignment, Suggestions |
| User Story | As a user, I want names instead of "Speaker 1" |

#### F11: Meeting Templates
| Field | Description |
|-------|-------------|
| Priority | P2 (Nice to Have) |
| Description | Different summary styles for different meeting types |
| Types | Standup, 1:1, Client Call, Interview, Brainstorm |
| User Story | As a user, I want summaries tailored to meeting type |

#### F12: Export Integrations
| Field | Description |
|-------|-------------|
| Priority | P2 (Nice to Have) |
| Description | Send outputs to external tools |
| Integrations | Notion, Todoist, Jira, Email, Markdown file |
| User Story | As a user, I want action items in my task manager |

### Phase 3: Advanced (v2.0)

#### F13: Full Desktop Application
| Field | Description |
|-------|-------------|
| Priority | P2 (Nice to Have) |
| Description | Complete native Windows application |
| Features | Meeting history, Search, Settings UI, Updates |

#### F14: Voice Profiles
| Field | Description |
|-------|-------------|
| Priority | P3 (Future) |
| Description | Learn and recognize regular meeting participants |
| Behavior | Auto-assign names to known voices |

#### F15: Meeting Analytics
| Field | Description |
|-------|-------------|
| Priority | P3 (Future) |
| Description | Insights about meeting patterns |
| Metrics | Talk time per person, meeting frequency, action item completion |

---

## 🚫 Out of Scope (For Now)

| Feature | Reason |
|---------|--------|
| Real-time transcription | Resource intensive, not critical for MVP |
| Mac/Linux support | Focus on Windows first, expand later |
| Cloud sync | Privacy-first approach, keep offline |
| Mobile app | Desktop is primary use case |
| Video recording | Audio sufficient, video adds complexity |

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Transcription Accuracy | >90% | Word Error Rate |
| Speaker Identification | >85% | Correct attribution |
| Processing Time | <2x audio length | Benchmark tests |
| User Satisfaction | >4.5/5 | User feedback |
| Daily Active Users | 100+ (if published) | Usage tracking |

---

## 🔐 Privacy & Security

### Principles
1. **100% Offline** - No data ever leaves the user's machine
2. **No Telemetry** - No usage tracking or analytics
3. **Local Storage** - All files stored locally
4. **User Control** - User decides what to save/delete
5. **Open Source** - Full code transparency

### Legal Considerations
- Users responsible for compliance with local recording laws
- App includes disclaimer about consent requirements
- Not responsible for misuse

---

## 📅 Timeline

| Phase | Features | Target Date | Status |
|-------|----------|-------------|--------|
| Phase 1 | MVP (F1-F7) | Feb 2026 | 🔄 In Progress |
| Phase 2 | Enhanced (F8-F12) | Apr 2026 | 📋 Planned |
| Phase 3 | Advanced (F13-F15) | Q3 2026 | 🔮 Future |

---

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-10 | 1.0 | Initial PRD created |

