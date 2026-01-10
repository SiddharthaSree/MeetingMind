"""
Meeting Templates Service
Provides different summary styles for various meeting types
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MeetingType(Enum):
    """Types of meetings with different summary styles"""
    GENERAL = "general"
    STANDUP = "standup"
    ONE_ON_ONE = "one_on_one"
    CLIENT_CALL = "client_call"
    INTERVIEW = "interview"
    BRAINSTORM = "brainstorm"
    REVIEW = "review"
    PLANNING = "planning"
    RETROSPECTIVE = "retrospective"


@dataclass
class MeetingTemplate:
    """Template defining how to summarize a specific meeting type"""
    type: MeetingType
    name: str
    description: str
    
    # Summary structure
    sections: List[str] = field(default_factory=list)
    
    # LLM prompts
    system_prompt: str = ""
    extraction_prompt: str = ""
    
    # Focus areas
    focus_on: List[str] = field(default_factory=list)
    ignore: List[str] = field(default_factory=list)
    
    # Output customization
    max_summary_length: int = 500
    include_timestamps: bool = False
    group_by_speaker: bool = False
    extract_metrics: bool = False


# Pre-defined templates
TEMPLATES: Dict[MeetingType, MeetingTemplate] = {
    
    MeetingType.GENERAL: MeetingTemplate(
        type=MeetingType.GENERAL,
        name="General Meeting",
        description="Standard meeting summary format",
        sections=["Summary", "Key Points", "Action Items", "Decisions"],
        system_prompt="""You are a meeting assistant. Summarize this meeting clearly and concisely.
Focus on: main topics discussed, key decisions, and action items with owners.""",
        extraction_prompt="""Analyze this meeting transcript and provide:

1. **Summary** (2-3 paragraphs): What was discussed?
2. **Key Points** (bullet points): Main topics and highlights
3. **Action Items**: Tasks with assignees if mentioned
4. **Decisions**: What was decided?""",
        focus_on=["decisions", "action items", "key topics"],
        max_summary_length=500
    ),
    
    MeetingType.STANDUP: MeetingTemplate(
        type=MeetingType.STANDUP,
        name="Daily Standup",
        description="Quick daily sync format (Yesterday, Today, Blockers)",
        sections=["Updates by Person", "Blockers", "Follow-ups"],
        system_prompt="""You are summarizing a daily standup meeting. 
Extract what each person did yesterday, what they're doing today, and any blockers.
Keep it brief and structured.""",
        extraction_prompt="""Summarize this standup. For each speaker, extract:

**[Speaker Name]**
- Yesterday: What they completed
- Today: What they're working on
- Blockers: Any impediments

Then list:
**Team Blockers**: Issues affecting multiple people
**Follow-ups Needed**: Items requiring follow-up""",
        focus_on=["progress", "blockers", "today's plan"],
        ignore=["small talk", "off-topic"],
        max_summary_length=300,
        group_by_speaker=True
    ),
    
    MeetingType.ONE_ON_ONE: MeetingTemplate(
        type=MeetingType.ONE_ON_ONE,
        name="1:1 Meeting",
        description="Manager-report or peer 1:1 format",
        sections=["Discussion Topics", "Feedback Given", "Action Items", "Follow-up Items"],
        system_prompt="""You are summarizing a 1:1 meeting. Focus on:
- Topics discussed and concerns raised
- Feedback exchanged
- Career/growth discussions
- Agreed action items
Keep the tone professional but note any personal context shared.""",
        extraction_prompt="""Summarize this 1:1 meeting:

**Topics Discussed**: Main subjects covered
**Concerns Raised**: Issues or challenges mentioned
**Feedback**: Any feedback given (positive or constructive)
**Growth/Career**: Career development topics if discussed
**Action Items**: Next steps for each person
**Follow-up**: Items to revisit in next 1:1""",
        focus_on=["feedback", "concerns", "growth", "personal items"],
        max_summary_length=400
    ),
    
    MeetingType.CLIENT_CALL: MeetingTemplate(
        type=MeetingType.CLIENT_CALL,
        name="Client Meeting",
        description="External client/stakeholder meeting format",
        sections=["Meeting Purpose", "Client Requests", "Commitments Made", "Next Steps", "Risks/Concerns"],
        system_prompt="""You are summarizing a client meeting. Be precise about:
- What the client asked for
- What was promised or committed
- Deadlines mentioned
- Any concerns or risks
This summary may be shared with leadership.""",
        extraction_prompt="""Summarize this client meeting professionally:

**Meeting Purpose**: Why we met
**Attendees**: Who was present (client side vs our side)
**Client Requests**: What the client asked for or needs
**Our Commitments**: What we agreed to deliver
**Timeline**: Any dates or deadlines mentioned
**Risks/Concerns**: Potential issues flagged
**Next Steps**: Immediate actions required
**Follow-up Meeting**: If scheduled""",
        focus_on=["commitments", "deadlines", "client needs", "risks"],
        ignore=["internal jokes", "off-topic"],
        max_summary_length=600
    ),
    
    MeetingType.INTERVIEW: MeetingTemplate(
        type=MeetingType.INTERVIEW,
        name="Interview",
        description="Candidate interview debrief format",
        sections=["Candidate Background", "Technical Assessment", "Cultural Fit", "Concerns", "Recommendation"],
        system_prompt="""You are summarizing a job interview. Focus on:
- Candidate's experience and skills discussed
- Technical or role-specific questions asked
- How well they'd fit the team
- Any red flags or concerns
Be objective and fact-based.""",
        extraction_prompt="""Summarize this interview:

**Candidate**: Name if mentioned
**Role**: Position discussed
**Experience Discussed**: Background and relevant experience
**Skills Demonstrated**: Technical or soft skills shown
**Questions Asked**: Key questions and quality of answers
**Cultural Fit Signals**: Team/company fit indicators
**Concerns**: Any red flags or gaps
**Strengths**: Notable positives
**Interviewer Recommendation**: Hire/No-hire signals if expressed""",
        focus_on=["skills", "experience", "fit", "concerns"],
        max_summary_length=500
    ),
    
    MeetingType.BRAINSTORM: MeetingTemplate(
        type=MeetingType.BRAINSTORM,
        name="Brainstorming Session",
        description="Creative ideation session format",
        sections=["Problem Statement", "Ideas Generated", "Top Ideas", "Next Steps"],
        system_prompt="""You are summarizing a brainstorming session. Capture:
- The problem being solved
- All ideas mentioned (even wild ones)
- Which ideas got traction
- Next steps to explore ideas
Preserve creative energy in the summary.""",
        extraction_prompt="""Summarize this brainstorm:

**Problem/Goal**: What we're trying to solve
**Ideas Generated**: All ideas mentioned (brief bullet each)
**Most Discussed Ideas**: Ideas that got the most attention
**Promising Directions**: Ideas the group seemed excited about
**Ideas to Explore Further**: What to research or prototype
**Assigned Owners**: Who's taking what forward
**Next Session**: If another brainstorm is planned""",
        focus_on=["ideas", "creativity", "enthusiasm"],
        ignore=["criticism of ideas", "feasibility debates"],
        max_summary_length=500,
        extract_metrics=True
    ),
    
    MeetingType.REVIEW: MeetingTemplate(
        type=MeetingType.REVIEW,
        name="Review Meeting",
        description="Code review, design review, or document review",
        sections=["What Was Reviewed", "Feedback Given", "Changes Requested", "Approved Items", "Next Steps"],
        system_prompt="""You are summarizing a review meeting (code, design, or document review).
Focus on specific feedback given, changes requested, and what was approved.""",
        extraction_prompt="""Summarize this review:

**Subject of Review**: What was being reviewed
**Reviewers**: Who provided feedback
**Positive Feedback**: What was praised
**Changes Requested**: Specific modifications needed
**Questions Raised**: Clarifications needed
**Blocked Items**: What can't proceed
**Approved Items**: What's ready to go
**Next Review**: If another review is needed""",
        focus_on=["feedback", "changes", "approvals", "blockers"],
        max_summary_length=400
    ),
    
    MeetingType.PLANNING: MeetingTemplate(
        type=MeetingType.PLANNING,
        name="Planning Meeting",
        description="Sprint planning, project planning, or roadmap session",
        sections=["Goals", "Items Planned", "Assignments", "Capacity", "Risks", "Dependencies"],
        system_prompt="""You are summarizing a planning meeting. Capture:
- What's being planned (sprint, project, quarter)
- Items committed to
- Who owns what
- Capacity or timeline concerns
- Dependencies and risks""",
        extraction_prompt="""Summarize this planning session:

**Planning Period**: What timeframe (sprint, quarter, etc.)
**Goals/Objectives**: What we're trying to achieve
**Items Committed**: Work items or stories planned
**Assignments**: Who's doing what
**Capacity Notes**: Team availability or concerns
**Dependencies**: External dependencies identified
**Risks**: Potential blockers or concerns
**Stretch Goals**: Nice-to-haves if time permits""",
        focus_on=["commitments", "assignments", "dependencies", "risks"],
        max_summary_length=500,
        extract_metrics=True
    ),
    
    MeetingType.RETROSPECTIVE: MeetingTemplate(
        type=MeetingType.RETROSPECTIVE,
        name="Retrospective",
        description="Team retrospective format (What went well, What didn't, Actions)",
        sections=["What Went Well", "What Didn't Go Well", "Action Items", "Shoutouts"],
        system_prompt="""You are summarizing a team retrospective. Capture both positives and areas for improvement.
Note specific action items to address issues. Include any team shoutouts or appreciation.""",
        extraction_prompt="""Summarize this retrospective:

**What Went Well** 👍
- Positive things mentioned

**What Didn't Go Well** 👎  
- Challenges or frustrations

**Action Items for Improvement**
- Specific changes to make (with owners)

**Shoutouts/Kudos** 🎉
- Team member appreciation

**Key Theme**: Overall sentiment of the retro""",
        focus_on=["positives", "negatives", "improvements", "appreciation"],
        max_summary_length=400,
        group_by_speaker=False
    )
}


class TemplateService:
    """Service for managing and applying meeting templates"""
    
    def __init__(self):
        self.templates = TEMPLATES.copy()
        self._custom_templates: Dict[str, MeetingTemplate] = {}
    
    def get_template(self, meeting_type: MeetingType) -> MeetingTemplate:
        """Get template for a meeting type"""
        return self.templates.get(meeting_type, self.templates[MeetingType.GENERAL])
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates"""
        return [
            {
                'type': t.type.value,
                'name': t.name,
                'description': t.description
            }
            for t in self.templates.values()
        ]
    
    def detect_meeting_type(self, transcript: str) -> MeetingType:
        """
        Auto-detect meeting type from transcript content
        
        Uses keyword matching and patterns to guess meeting type
        """
        transcript_lower = transcript.lower()
        
        # Keyword patterns for each type
        patterns = {
            MeetingType.STANDUP: ['yesterday', 'today', 'blocker', 'standup', 'daily'],
            MeetingType.ONE_ON_ONE: ['feedback', 'career', 'growth', '1:1', 'one on one', 'check-in'],
            MeetingType.CLIENT_CALL: ['client', 'customer', 'proposal', 'contract', 'deliverable'],
            MeetingType.INTERVIEW: ['candidate', 'interview', 'hiring', 'resume', 'experience'],
            MeetingType.BRAINSTORM: ['idea', 'brainstorm', 'creative', 'what if', 'possibility'],
            MeetingType.REVIEW: ['review', 'feedback', 'approve', 'changes', 'lgtm'],
            MeetingType.PLANNING: ['sprint', 'planning', 'story points', 'capacity', 'backlog'],
            MeetingType.RETROSPECTIVE: ['retro', 'went well', 'improve', 'what worked', 'kudos']
        }
        
        scores = {t: 0 for t in MeetingType}
        
        for meeting_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword in transcript_lower:
                    scores[meeting_type] += 1
        
        # Find best match
        best_type = max(scores, key=scores.get)
        
        # Only return specific type if confidence is high enough
        if scores[best_type] >= 2:
            return best_type
        
        return MeetingType.GENERAL
    
    def get_prompt_for_template(self, template: MeetingTemplate) -> Dict[str, str]:
        """Get the prompts to use with summarizer for a template"""
        return {
            'system': template.system_prompt,
            'user': template.extraction_prompt
        }
    
    def add_custom_template(self, template: MeetingTemplate) -> None:
        """Add a custom template"""
        self._custom_templates[template.type.value] = template
    
    def format_summary_for_template(
        self,
        raw_summary: Dict[str, Any],
        template: MeetingTemplate
    ) -> str:
        """Format a raw summary according to template structure"""
        
        output_lines = [f"# {template.name} Notes\n"]
        
        for section in template.sections:
            section_key = section.lower().replace(' ', '_')
            
            if section_key in raw_summary:
                content = raw_summary[section_key]
                output_lines.append(f"## {section}")
                
                if isinstance(content, list):
                    for item in content:
                        output_lines.append(f"- {item}")
                else:
                    output_lines.append(str(content))
                
                output_lines.append("")
        
        return '\n'.join(output_lines)
