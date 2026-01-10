# MeetingMind - Project Tracker

## 📊 Project Status Dashboard

| Metric | Status |
|--------|--------|
| **Current Phase** | Phase 1 - MVP |
| **Version** | v1.0.0-dev |
| **Sprint** | Sprint 1 |
| **Last Updated** | January 10, 2026 |

---

## 🎯 Sprint 1: Foundation (Jan 10 - Jan 24, 2026)

### Goals
- [ ] Set up project structure for v2 architecture
- [ ] Implement system audio capture
- [ ] Implement speaker diarization
- [ ] Integrate with existing transcription

### Tasks

| ID | Task | Priority | Status | Assignee | Notes |
|----|------|----------|--------|----------|-------|
| S1-01 | Create v2 project structure | P0 | 🔄 In Progress | - | New modules for audio capture, diarization |
| S1-02 | Implement WASAPI audio capture | P0 | ⬜ Not Started | - | Windows system audio |
| S1-03 | Add pyannote speaker diarization | P0 | ⬜ Not Started | - | Offline speaker detection |
| S1-04 | Merge diarization with transcription | P0 | ⬜ Not Started | - | Speaker-labeled transcript |
| S1-05 | Create system tray launcher | P0 | ⬜ Not Started | - | Quick start/stop |
| S1-06 | Update requirements.txt | P0 | ⬜ Not Started | - | New dependencies |
| S1-07 | Write unit tests for audio capture | P1 | ⬜ Not Started | - | Basic test coverage |

---

## 🎯 Sprint 2: Core Pipeline (Jan 25 - Feb 7, 2026)

### Goals
- [ ] Complete processing pipeline
- [ ] Implement post-meeting Q&A
- [ ] Create basic UI

### Tasks

| ID | Task | Priority | Status | Assignee | Notes |
|----|------|----------|--------|----------|-------|
| S2-01 | Build processing pipeline orchestrator | P0 | ⬜ Not Started | - | Coordinates all modules |
| S2-02 | Implement post-meeting Q&A engine | P0 | ⬜ Not Started | - | Analyzes transcript for ambiguities |
| S2-03 | Create Q&A prompts library | P0 | ⬜ Not Started | - | Smart question generation |
| S2-04 | Build main Gradio UI v2 | P0 | ⬜ Not Started | - | With recording controls |
| S2-05 | Add speaker renaming feature | P1 | ⬜ Not Started | - | Replace "Speaker 1" with names |
| S2-06 | Implement save/export options | P1 | ⬜ Not Started | - | TXT, MD, JSON formats |

---

## 🎯 Sprint 3: Polish & Release (Feb 8 - Feb 21, 2026)

### Goals
- [ ] Testing and bug fixes
- [ ] Documentation
- [ ] v1.0 release

### Tasks

| ID | Task | Priority | Status | Assignee | Notes |
|----|------|----------|--------|----------|-------|
| S3-01 | End-to-end testing | P0 | ⬜ Not Started | - | Full workflow tests |
| S3-02 | Performance optimization | P1 | ⬜ Not Started | - | Memory, speed improvements |
| S3-03 | Update all documentation | P0 | ⬜ Not Started | - | README, API docs |
| S3-04 | Create installation guide | P0 | ⬜ Not Started | - | Step-by-step setup |
| S3-05 | Build Windows installer | P2 | ⬜ Not Started | - | Optional .exe package |
| S3-06 | v1.0.0 Release | P0 | ⬜ Not Started | - | Tag and release |

---

## 📋 Backlog (Future Sprints)

### High Priority (Phase 2)

| ID | Feature | Description | Effort |
|----|---------|-------------|--------|
| BL-01 | Meeting Detection | Auto-detect Teams/Zoom launch | Medium |
| BL-02 | Auto-Process | Start processing when meeting ends | Medium |
| BL-03 | Speaker Profiles | Learn and remember voices | Large |
| BL-04 | Meeting Templates | Standup, 1:1, Client call formats | Small |
| BL-05 | Hotkey Support | Global start/stop shortcuts | Small |

### Medium Priority (Phase 2-3)

| ID | Feature | Description | Effort |
|----|---------|-------------|--------|
| BL-06 | Notion Export | Send notes to Notion | Medium |
| BL-07 | Todoist Integration | Create tasks from action items | Medium |
| BL-08 | Meeting History | Browse past meetings | Medium |
| BL-09 | Search | Search across all transcripts | Medium |
| BL-10 | Full Desktop App | PyQt6 native application | Large |

### Low Priority (Future)

| ID | Feature | Description | Effort |
|----|---------|-------------|--------|
| BL-11 | Mac Support | macOS audio capture | Large |
| BL-12 | Linux Support | Linux audio capture | Large |
| BL-13 | Meeting Analytics | Insights dashboard | Large |
| BL-14 | Calendar Integration | Sync with Outlook/Google | Large |
| BL-15 | Real-time Mode | Live transcription | Extra Large |

---

## 🐛 Bug Tracker

| ID | Description | Severity | Status | Version Found |
|----|-------------|----------|--------|---------------|
| - | No bugs reported yet | - | - | - |

---

## 💡 Ideas Parking Lot

Ideas to evaluate later:

1. **Voice commands** - "Hey MeetingMind, start recording"
2. **Auto-email summary** - Send notes to meeting participants
3. **Sentiment analysis** - Detect meeting mood/tension
4. **Meeting scoring** - Rate meeting effectiveness
5. **Recurring meeting comparison** - Compare standups over time
6. **Multi-language support** - Transcribe non-English meetings
7. **Custom LLM prompts** - User-defined summary formats
8. **Slack integration** - Post summaries to channels

---

## 📈 Progress Chart

```
Phase 1 MVP Progress
====================
[░░░░░░░░░░░░░░░░░░░░] 5% - Project setup

Sprint 1: [░░░░░░░░░░░░░░░░░░░░] 5%
Sprint 2: [░░░░░░░░░░░░░░░░░░░░] 0%
Sprint 3: [░░░░░░░░░░░░░░░░░░░░] 0%
```

---

## 📝 Meeting Notes

### Jan 10, 2026 - Project Kickoff
- Defined MVP scope
- Agreed on Phase 1 features
- Key decisions:
  - Windows-first approach
  - System audio capture priority
  - Post-meeting Q&A is killer feature
  - Offline/privacy-first architecture

---

## 🔗 Quick Links

| Document | Description |
|----------|-------------|
| [PRD.md](./PRD.md) | Product Requirements Document |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Technical Architecture |
| [API.md](./API.md) | API Reference |
| [ROADMAP.md](./ROADMAP.md) | Future Plans |
| [../README.md](../README.md) | Project README |
| [../CHANGELOG.md](../CHANGELOG.md) | Version History |

---

## ✅ Definition of Done

A feature is considered "done" when:
- [ ] Code is written and tested
- [ ] Documentation is updated
- [ ] No known bugs
- [ ] Code review completed (if applicable)
- [ ] Works offline
- [ ] Doesn't break existing features

---

*Last updated: January 10, 2026*
