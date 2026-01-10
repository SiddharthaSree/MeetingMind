"""
Gradio Web Interface for MeetingMind
Full-featured UI with Q&A workflow and audio snippet playback
"""
import os
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json

import gradio as gr

from core.controller import MeetingMindController, AppState
from core.config import get_config, MEETINGS_DIR
from services.qa_engine import Question, QuestionType


class MeetingMindUI:
    """
    Gradio-based web interface for MeetingMind
    
    Features:
    - Record from system audio or upload file
    - Real-time status updates
    - Speaker identification with audio playback
    - Q&A workflow for clarifications
    - Meeting notes display and export
    """
    
    def __init__(self, controller: MeetingMindController = None):
        """
        Initialize UI
        
        Args:
            controller: Optional pre-configured controller
        """
        self.controller = controller or MeetingMindController()
        self.config = get_config()
        
        # State tracking
        self.current_questions: List[Question] = []
        self.current_question_idx = 0
        
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        
        with gr.Blocks(
            title="MeetingMind - Meeting Notes Assistant",
            theme=gr.themes.Soft(),
            css=self._get_custom_css()
        ) as app:
            
            # Header
            gr.Markdown("""
            # 🎙️ MeetingMind
            ### Your offline, AI-powered meeting notes assistant
            """)
            
            # Main tabs
            with gr.Tabs() as tabs:
                
                # Tab 1: Recording / Upload
                with gr.Tab("📝 New Meeting", id="new_meeting"):
                    self._build_recording_tab()
                
                # Tab 2: Q&A Session
                with gr.Tab("❓ Q&A Session", id="qa_session"):
                    self._build_qa_tab()
                
                # Tab 3: Meeting Notes
                with gr.Tab("📋 Meeting Notes", id="notes"):
                    self._build_notes_tab()
                
                # Tab 4: History
                with gr.Tab("📚 History", id="history"):
                    self._build_history_tab()
                
                # Tab 5: Settings
                with gr.Tab("⚙️ Settings", id="settings"):
                    self._build_settings_tab()
            
            # Status bar
            with gr.Row():
                self.status_text = gr.Markdown("Ready", elem_id="status_bar")
        
        return app
    
    def _build_recording_tab(self):
        """Build the recording/upload tab"""
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 🎤 Record Meeting Audio")
                
                # Auto-record toggle
                with gr.Row():
                    self.auto_record_toggle = gr.Checkbox(
                        label="🤖 Auto-detect meetings (Teams/Zoom/Meet)",
                        value=False,
                        info="Automatically start recording when meetings are detected"
                    )
                    self.meeting_status = gr.Markdown("", visible=False)
                
                # Meeting template selection
                with gr.Row():
                    self.template_dropdown = gr.Dropdown(
                        label="Meeting Template",
                        choices=self._get_templates(),
                        value="general",
                        info="Choose a template for better summaries"
                    )
                
                with gr.Row():
                    self.record_btn = gr.Button(
                        "🔴 Start Recording",
                        variant="primary",
                        size="lg"
                    )
                    self.stop_btn = gr.Button(
                        "⏹️ Stop Recording",
                        variant="stop",
                        size="lg",
                        visible=False
                    )
                
                self.recording_status = gr.Markdown("Click to start recording system audio")
                
                # Device selection
                with gr.Accordion("Audio Device Settings", open=False):
                    self.device_dropdown = gr.Dropdown(
                        label="Audio Device",
                        choices=self._get_audio_devices(),
                        value="default"
                    )
                    self.refresh_devices_btn = gr.Button("🔄 Refresh Devices")
                
            with gr.Column(scale=1):
                gr.Markdown("### Or Upload Audio File")
                self.upload_audio = gr.Audio(
                    label="Upload Recording",
                    type="filepath",
                    sources=["upload"]
                )
                self.process_upload_btn = gr.Button("Process Upload", variant="secondary")
        
        # Processing status
        gr.Markdown("### Processing Status")
        self.progress_bar = gr.Progress()
        self.processing_log = gr.Textbox(
            label="Processing Log",
            lines=5,
            interactive=False,
            show_label=False
        )
        
        # Event handlers
        self.auto_record_toggle.change(
            fn=self._toggle_auto_record,
            inputs=[self.auto_record_toggle],
            outputs=[self.meeting_status, self.recording_status]
        )
        
        self.template_dropdown.change(
            fn=self._set_template,
            inputs=[self.template_dropdown],
            outputs=[self.recording_status]
        )
        
        self.record_btn.click(
            fn=self._start_recording,
            outputs=[self.record_btn, self.stop_btn, self.recording_status, self.processing_log]
        )
        
        self.stop_btn.click(
            fn=self._stop_recording,
            outputs=[self.record_btn, self.stop_btn, self.recording_status, self.processing_log]
        )
        
        self.process_upload_btn.click(
            fn=self._process_upload,
            inputs=[self.upload_audio],
            outputs=[self.processing_log]
        )
        
        self.refresh_devices_btn.click(
            fn=self._refresh_devices,
            outputs=[self.device_dropdown]
        )
    
    def _build_qa_tab(self):
        """Build the Q&A session tab"""
        
        gr.Markdown("""
        ### 🎯 Speaker Identification & Clarifications
        Help improve your meeting notes by identifying speakers and answering a few questions.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Speaker ID Section
                gr.Markdown("#### 🎧 Who is this speaker?")
                
                self.speaker_audio = gr.Audio(
                    label="Listen to this clip",
                    interactive=False,
                    visible=False
                )
                
                self.speaker_name_input = gr.Textbox(
                    label="Enter speaker's name",
                    placeholder="e.g., John Smith",
                    visible=False
                )
                
                # General question section
                gr.Markdown("#### 💬 Clarification Question")
                self.question_text = gr.Markdown("No questions yet")
                
                self.answer_input = gr.Textbox(
                    label="Your answer",
                    placeholder="Type your answer here...",
                    lines=2
                )
                
                with gr.Row():
                    self.submit_answer_btn = gr.Button("✅ Submit", variant="primary")
                    self.skip_btn = gr.Button("⏭️ Skip")
                    self.skip_all_btn = gr.Button("⏩ Skip All & Generate")
            
            with gr.Column(scale=1):
                gr.Markdown("#### Progress")
                self.qa_progress = gr.Markdown("0 / 0 questions answered")
                
                gr.Markdown("#### Identified Speakers")
                self.speakers_list = gr.Markdown("_No speakers identified yet_")
        
        # Event handlers
        self.submit_answer_btn.click(
            fn=self._submit_answer,
            inputs=[self.answer_input, self.speaker_name_input],
            outputs=[
                self.question_text, self.answer_input, self.speaker_name_input,
                self.speaker_audio, self.qa_progress, self.speakers_list
            ]
        )
        
        self.skip_btn.click(
            fn=self._skip_question,
            outputs=[
                self.question_text, self.answer_input, self.speaker_name_input,
                self.speaker_audio, self.qa_progress
            ]
        )
        
        self.skip_all_btn.click(
            fn=self._skip_all_generate,
            outputs=[self.question_text, self.qa_progress]
        )
    
    def _build_notes_tab(self):
        """Build the meeting notes display tab"""
        
        gr.Markdown("### 📋 Your Meeting Notes")
        
        with gr.Row():
            with gr.Column(scale=2):
                self.summary_display = gr.Markdown(
                    "_Process a meeting to see notes here_",
                    elem_id="summary_display"
                )
                
                gr.Markdown("#### 📌 Key Points")
                self.key_points_display = gr.Markdown("")
                
                gr.Markdown("#### ✅ Action Items")
                self.action_items_display = gr.Markdown("")
                
                gr.Markdown("#### 🎯 Decisions")
                self.decisions_display = gr.Markdown("")
                
            with gr.Column(scale=1):
                gr.Markdown("#### 📝 Full Transcript")
                self.transcript_display = gr.Textbox(
                    label="",
                    lines=15,
                    interactive=False
                )
        
        # Export section with multiple formats
        gr.Markdown("### 📥 Export Options")
        with gr.Row():
            self.export_format = gr.Dropdown(
                label="Export Format",
                choices=["markdown", "html", "json", "docx", "pdf"],
                value="markdown"
            )
            self.meeting_title_input = gr.Textbox(
                label="Meeting Title (for export)",
                placeholder="Optional: Enter a title for this meeting"
            )
        
        with gr.Row():
            self.export_btn = gr.Button("📥 Export Meeting", variant="primary")
            self.save_history_btn = gr.Button("💾 Save to History")
            self.copy_btn = gr.Button("📋 Copy to Clipboard")
        
        self.export_file = gr.File(label="Download", visible=False)
        self.export_status = gr.Markdown("")
        
        # Event handlers
        self.export_btn.click(
            fn=self._export_meeting,
            inputs=[self.export_format, self.meeting_title_input],
            outputs=[self.export_file, self.export_status]
        )
        
        self.save_history_btn.click(
            fn=self._save_to_history,
            inputs=[self.meeting_title_input],
            outputs=[self.export_status]
        )
    
    def _build_history_tab(self):
        """Build the meeting history tab"""
        
        gr.Markdown("### 📚 Past Meetings")
        
        # Search section
        with gr.Row():
            self.history_search = gr.Textbox(
                label="Search",
                placeholder="Search by title, participant, or keyword...",
                scale=2
            )
            self.history_date_from = gr.Textbox(
                label="From Date",
                placeholder="YYYY-MM-DD",
                scale=1
            )
            self.history_date_to = gr.Textbox(
                label="To Date",
                placeholder="YYYY-MM-DD",
                scale=1
            )
            self.search_history_btn = gr.Button("🔍 Search", scale=1)
        
        # Statistics
        with gr.Accordion("📊 Statistics", open=False):
            self.history_stats = gr.Markdown("_Loading statistics..._")
        
        self.history_list = gr.Dataframe(
            headers=["ID", "Date", "Title", "Duration", "Participants", "Type"],
            datatype=["str", "str", "str", "str", "str", "str"],
            row_count=(10, "dynamic"),
            col_count=(6, "fixed"),
            interactive=False
        )
        
        with gr.Row():
            self.refresh_history_btn = gr.Button("🔄 Refresh")
            self.load_meeting_btn = gr.Button("📂 Load Selected", variant="primary")
            self.delete_meeting_btn = gr.Button("🗑️ Delete Selected", variant="stop")
        
        # Meeting details section
        with gr.Accordion("📄 Meeting Details", open=False):
            self.history_meeting_details = gr.Markdown("_Select a meeting to view details_")
            self.history_export_btn = gr.Button("📥 Export Selected Meeting")
        
        # Event handlers
        self.refresh_history_btn.click(
            fn=self._load_history,
            outputs=[self.history_list, self.history_stats]
        )
        
        self.search_history_btn.click(
            fn=self._search_history,
            inputs=[self.history_search, self.history_date_from, self.history_date_to],
            outputs=[self.history_list]
        )
        
        self.load_meeting_btn.click(
            fn=self._load_selected_meeting,
            inputs=[self.history_list],
            outputs=[self.history_meeting_details]
        )
        
        self.delete_meeting_btn.click(
            fn=self._delete_selected_meeting,
            inputs=[self.history_list],
            outputs=[self.history_list, self.history_stats]
        )
    
    def _build_settings_tab(self):
        """Build the settings tab"""
        
        gr.Markdown("### ⚙️ Configuration")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### 🎤 Transcription (Whisper)")
                self.whisper_model = gr.Dropdown(
                    label="Model Size",
                    choices=["tiny", "base", "small", "medium", "large"],
                    value=self.config.whisper.model_size
                )
                
                gr.Markdown("#### 🤖 LLM (Ollama)")
                self.ollama_model = gr.Textbox(
                    label="Model Name",
                    value=self.config.ollama.model_name
                )
                self.ollama_host = gr.Textbox(
                    label="Ollama Host",
                    value=self.config.ollama.host
                )
            
            with gr.Column():
                gr.Markdown("#### ❓ Q&A Settings")
                self.qa_mode = gr.Radio(
                    label="Q&A Mode",
                    choices=["quick", "detailed"],
                    value=self.config.qa.mode,
                    info="Quick: 3-5 questions | Detailed: 5-10 questions"
                )
                
                gr.Markdown("#### 🎧 Audio Settings")
                self.sample_rate = gr.Number(
                    label="Sample Rate (Hz)",
                    value=self.config.audio.sample_rate
                )
        
        self.save_settings_btn = gr.Button("💾 Save Settings", variant="primary")
        self.settings_status = gr.Markdown("")
        
        self.save_settings_btn.click(
            fn=self._save_settings,
            inputs=[
                self.whisper_model, self.ollama_model, self.ollama_host,
                self.qa_mode, self.sample_rate
            ],
            outputs=[self.settings_status]
        )
    
    # ==================== Event Handlers ====================
    
    def _get_templates(self) -> List[str]:
        """Get available meeting templates"""
        try:
            return self.controller.list_templates()
        except:
            return ["general", "standup", "planning", "retrospective", "one_on_one"]
    
    def _toggle_auto_record(self, enabled: bool):
        """Toggle auto-record mode"""
        try:
            if enabled:
                self.controller.enable_auto_record()
                running = self.controller.check_running_meetings()
                if running:
                    apps = ", ".join([m['app'] for m in running])
                    return (
                        gr.update(visible=True, value=f"🟢 Monitoring... Detected: {apps}"),
                        "Auto-record enabled. Will start when meetings begin."
                    )
                return (
                    gr.update(visible=True, value="🟢 Monitoring for meetings..."),
                    "Auto-record enabled. Waiting for meeting app..."
                )
            else:
                self.controller.disable_auto_record()
                return (
                    gr.update(visible=False),
                    "Auto-record disabled."
                )
        except Exception as e:
            return (
                gr.update(visible=True, value=f"❌ Error: {str(e)}"),
                f"Error: {str(e)}"
            )
    
    def _set_template(self, template_name: str):
        """Set meeting template"""
        try:
            self.controller.set_template(template_name)
            template = self.controller.get_template(template_name)
            if template:
                return f"Template: **{template.name}** - {template.description}"
            return f"Template set to: {template_name}"
        except Exception as e:
            return f"Error setting template: {str(e)}"
    
    def _start_recording(self):
        """Start recording system audio"""
        try:
            self.controller.start_recording()
            return (
                gr.update(visible=False),  # hide record btn
                gr.update(visible=True),   # show stop btn
                "🔴 **Recording...** Click Stop when done.",
                "Recording started. Capturing system audio..."
            )
        except Exception as e:
            return (
                gr.update(visible=True),
                gr.update(visible=False),
                f"❌ Error: {str(e)}",
                f"Failed to start recording: {str(e)}"
            )
    
    def _stop_recording(self):
        """Stop recording and start processing"""
        try:
            audio_path = self.controller.stop_recording()
            return (
                gr.update(visible=True),   # show record btn
                gr.update(visible=False),  # hide stop btn
                "⏳ **Processing...** This may take a few minutes.",
                f"Recording saved. Processing audio...\nFile: {audio_path}"
            )
        except Exception as e:
            return (
                gr.update(visible=True),
                gr.update(visible=False),
                f"❌ Error: {str(e)}",
                f"Error: {str(e)}"
            )
    
    def _process_upload(self, audio_path: str):
        """Process uploaded audio file"""
        if not audio_path:
            return "No file uploaded"
        
        try:
            self.controller.process_audio(audio_path)
            return f"Processing: {audio_path}\nThis may take a few minutes..."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _refresh_devices(self):
        """Refresh audio device list"""
        devices = self._get_audio_devices()
        return gr.update(choices=devices)
    
    def _get_audio_devices(self) -> List[str]:
        """Get list of audio devices"""
        try:
            from services.audio_capture import AudioCaptureService
            capture = AudioCaptureService()
            devices = capture.list_devices()
            return [d['name'] for d in devices] or ["default"]
        except:
            return ["default"]
    
    def _submit_answer(self, answer: str, speaker_name: str):
        """Submit answer to current question"""
        if not self.current_questions or self.current_question_idx >= len(self.current_questions):
            return self._get_qa_display_state()
        
        current_q = self.current_questions[self.current_question_idx]
        
        # Use speaker name for speaker ID questions
        if current_q.type == QuestionType.SPEAKER_ID and speaker_name:
            self.controller.set_speaker_name(current_q.speaker_id, speaker_name)
            self.controller.qa_engine.answer_question(current_q.id, speaker_name)
        else:
            self.controller.qa_engine.answer_question(current_q.id, answer)
        
        self.current_question_idx += 1
        
        # Check if Q&A complete
        if self.current_question_idx >= len(self.current_questions):
            self._finalize_meeting()
        
        return self._get_qa_display_state()
    
    def _skip_question(self):
        """Skip current question"""
        if self.current_questions and self.current_question_idx < len(self.current_questions):
            current_q = self.current_questions[self.current_question_idx]
            self.controller.qa_engine.skip_question(current_q.id)
            self.current_question_idx += 1
        
        return self._get_qa_display_state()
    
    def _skip_all_generate(self):
        """Skip remaining questions and generate summary"""
        if self.controller.qa_engine:
            self.controller.qa_engine.skip_all_remaining()
        self._finalize_meeting()
        return ("Generating meeting notes...", "All questions skipped")
    
    def _get_qa_display_state(self):
        """Get current Q&A display state"""
        if not self.current_questions or self.current_question_idx >= len(self.current_questions):
            return (
                "✅ **All questions answered!** Generating meeting notes...",
                "",  # answer input
                gr.update(visible=False),  # speaker name input
                gr.update(visible=False),  # speaker audio
                f"{len(self.current_questions)} / {len(self.current_questions)} completed",
                self._format_speakers_list()
            )
        
        q = self.current_questions[self.current_question_idx]
        
        # Format question display
        q_display = f"**Question {self.current_question_idx + 1} of {len(self.current_questions)}**\n\n"
        q_display += f"📌 {q.question}"
        if q.context:
            q_display += f"\n\n_Context: {q.context}_"
        
        # Handle speaker ID questions
        is_speaker_q = q.type == QuestionType.SPEAKER_ID
        speaker_audio_update = gr.update(visible=False)
        
        if is_speaker_q and q.audio_snippet_b64:
            # Decode base64 audio for playback
            audio_data = base64.b64decode(q.audio_snippet_b64)
            speaker_audio_update = gr.update(
                visible=True,
                value=audio_data
            )
        
        progress = f"{self.current_question_idx} / {len(self.current_questions)} completed"
        
        return (
            q_display,
            "",  # clear answer input
            gr.update(visible=is_speaker_q, value=""),  # speaker name input
            speaker_audio_update,
            progress,
            self._format_speakers_list()
        )
    
    def _format_speakers_list(self) -> str:
        """Format the identified speakers list"""
        if not self.controller.qa_engine:
            return "_No speakers identified yet_"
        
        mappings = self.controller.qa_engine.get_speaker_mappings()
        if not mappings:
            return "_No speakers identified yet_"
        
        lines = []
        for speaker_id, name in mappings.items():
            lines.append(f"- **{name}** ({speaker_id})")
        
        return '\n'.join(lines)
    
    def _finalize_meeting(self):
        """Finalize meeting and generate summary"""
        try:
            result = self.controller.finalize_meeting()
            # Update notes display (would need to connect to outputs)
        except Exception as e:
            print(f"Error finalizing: {e}")
    
    def _export_meeting(self, format: str, title: str):
        """Export meeting notes in specified format"""
        if not hasattr(self.controller, 'current_summary') or not self.controller.current_summary:
            return None, "❌ No meeting to export. Process a meeting first."
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = title.replace(" ", "_") if title else f"meeting_{timestamp}"
            output_path = str(Path(MEETINGS_DIR) / filename)
            
            meeting_data = {
                "id": timestamp,
                "title": title or f"Meeting {timestamp}",
                "created_at": datetime.now().isoformat(),
                "audio_path": self.controller.current_recording_path,
                "transcript": self.controller.current_transcript,
                "summary": self.controller.current_summary,
                "speaker_names": self.controller.speaker_names,
                "qa_responses": self.controller.current_qa_responses
            }
            
            exported_path = self.controller.export_meeting(meeting_data, output_path, format)
            return exported_path, f"✅ Exported to: {exported_path}"
        except Exception as e:
            return None, f"❌ Export error: {str(e)}"
    
    def _save_to_history(self, title: str):
        """Save current meeting to history"""
        if not hasattr(self.controller, 'current_summary') or not self.controller.current_summary:
            return "❌ No meeting to save. Process a meeting first."
        
        try:
            from datetime import datetime
            meeting_data = {
                "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "title": title or f"Meeting {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "created_at": datetime.now().isoformat(),
                "audio_path": self.controller.current_recording_path,
                "transcript": self.controller.current_transcript,
                "summary": self.controller.current_summary,
                "speaker_names": self.controller.speaker_names,
                "qa_responses": self.controller.current_qa_responses,
                "metadata": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "meeting_type": self.controller.current_template
                }
            }
            
            meeting_id = self.controller.save_to_history(meeting_data, title)
            return f"✅ Saved to history with ID: {meeting_id}"
        except Exception as e:
            return f"❌ Error saving: {str(e)}"
    
    def _export_markdown(self):
        """Export meeting notes as Markdown"""
        if not hasattr(self.controller, 'current_meeting_result'):
            return None
        
        result = self.controller.current_meeting_result
        
        md_content = f"""# Meeting Notes

## Summary
{result.get('summary', {}).get('summary', 'No summary available')}

## Key Points
{result.get('summary', {}).get('key_points', 'No key points')}

## Action Items
"""
        for item in result.get('summary', {}).get('action_items', []):
            assignee = item.get('assignee', 'Unassigned')
            md_content += f"- [{assignee}] {item['description']}\n"
        
        md_content += "\n## Decisions\n"
        for decision in result.get('summary', {}).get('decisions', []):
            md_content += f"- {decision}\n"
        
        # Save to file
        output_path = Path(MEETINGS_DIR) / "export.md"
        output_path.write_text(md_content)
        
        return str(output_path)
    
    def _export_json(self):
        """Export meeting notes as JSON"""
        if not hasattr(self.controller, 'current_meeting_result'):
            return None
        
        output_path = Path(MEETINGS_DIR) / "export.json"
        with open(output_path, 'w') as f:
            json.dump(self.controller.current_meeting_result, f, indent=2, default=str)
        
        return str(output_path)
    
    def _load_history(self):
        """Load meeting history with statistics"""
        try:
            history = self.controller.get_meeting_history(limit=50)
            stats = self.controller.get_history_statistics()
            
            # Format for dataframe
            rows = []
            for m in history:
                duration = m.get('duration_seconds', 0)
                duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else "-"
                participants = ", ".join(m.get('participants', [])[:3])
                if len(m.get('participants', [])) > 3:
                    participants += "..."
                
                rows.append([
                    m.get('id', ''),
                    m.get('date', ''),
                    m.get('title', 'Untitled')[:40],
                    duration_str,
                    participants or "-",
                    m.get('meeting_type', 'general')
                ])
            
            # Format statistics
            stats_md = f"""
**Total Meetings:** {stats.get('total_meetings', 0)}
**Total Duration:** {stats.get('total_duration_hours', 0)} hours
**Unique Participants:** {stats.get('unique_participants', 0)}

**By Type:**
"""
            for mtype, count in stats.get('meetings_by_type', {}).items():
                stats_md += f"- {mtype}: {count}\n"
            
            return rows, stats_md
        except Exception as e:
            print(f"Error loading history: {e}")
            return [], f"Error: {str(e)}"
    
    def _search_history(self, query: str, date_from: str, date_to: str):
        """Search meeting history"""
        try:
            results = self.controller.search_history(
                query=query if query else None,
                date_from=date_from if date_from else None,
                date_to=date_to if date_to else None
            )
            
            rows = []
            for m in results:
                rows.append([
                    m.get('id', ''),
                    m.get('date', ''),
                    m.get('title', 'Untitled')[:40],
                    "-",  # Duration not in search results
                    ", ".join(m.get('participants', [])[:3]) or "-",
                    "-"
                ])
            
            return rows
        except Exception as e:
            print(f"Error searching history: {e}")
            return []
    
    def _load_selected_meeting(self, history_df):
        """Load selected meeting details"""
        if history_df is None or len(history_df) == 0:
            return "_No meeting selected_"
        
        try:
            # Get first selected row's ID
            selected = history_df
            if hasattr(selected, 'iloc'):
                meeting_id = selected.iloc[0, 0]  # First column is ID
            else:
                meeting_id = selected[0][0]
            
            meeting_data = self.controller.get_history_meeting(meeting_id)
            if not meeting_data:
                return f"_Meeting {meeting_id} not found_"
            
            # Format meeting details
            summary = meeting_data.get('summary', {})
            transcript = meeting_data.get('transcript', {})
            
            md = f"""
## {meeting_data.get('title', 'Meeting')}

**Date:** {meeting_data.get('created_at', 'Unknown')}

### Summary
{summary.get('summary', 'No summary available') if isinstance(summary, dict) else summary}

### Key Points
{summary.get('key_points', 'No key points') if isinstance(summary, dict) else ''}

### Action Items
"""
            action_items = summary.get('action_items', []) if isinstance(summary, dict) else []
            for item in action_items:
                if isinstance(item, dict):
                    md += f"- {item.get('description', item)}\n"
                else:
                    md += f"- {item}\n"
            
            return md
        except Exception as e:
            return f"_Error loading meeting: {str(e)}_"
    
    def _delete_selected_meeting(self, history_df):
        """Delete selected meeting from history"""
        if history_df is None or len(history_df) == 0:
            return history_df, "_No meeting selected_"
        
        try:
            if hasattr(history_df, 'iloc'):
                meeting_id = history_df.iloc[0, 0]
            else:
                meeting_id = history_df[0][0]
            
            self.controller.delete_from_history(meeting_id)
            return self._load_history()
        except Exception as e:
            return history_df, f"Error: {str(e)}"
    
    def _save_settings(self, whisper_model, ollama_model, ollama_host, qa_mode, sample_rate):
        """Save configuration settings"""
        try:
            from core.config import save_config
            
            self.config.whisper.model_size = whisper_model
            self.config.ollama.model_name = ollama_model
            self.config.ollama.host = ollama_host
            self.config.qa.mode = qa_mode
            self.config.audio.sample_rate = int(sample_rate)
            
            save_config(self.config)
            return "✅ Settings saved successfully!"
        except Exception as e:
            return f"❌ Error saving settings: {str(e)}"
    
    def _get_custom_css(self) -> str:
        """Custom CSS for the UI"""
        return """
        #status_bar {
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            text-align: center;
        }
        
        #summary_display {
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .gradio-container {
            max-width: 1200px !important;
        }
        """


def create_gradio_app(controller: MeetingMindController = None) -> gr.Blocks:
    """
    Factory function to create Gradio app
    
    Args:
        controller: Optional pre-configured controller
    
    Returns:
        Gradio Blocks app
    """
    ui = MeetingMindUI(controller)
    return ui.create_interface()


def launch_app(
    controller: MeetingMindController = None,
    share: bool = False,
    port: int = 7860
):
    """
    Launch the Gradio app
    
    Args:
        controller: Optional pre-configured controller
        share: Create public share link
        port: Port to run on
    """
    app = create_gradio_app(controller)
    app.launch(
        server_port=port,
        share=share,
        inbrowser=True
    )


if __name__ == "__main__":
    launch_app()
