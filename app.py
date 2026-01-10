"""
MeetingMind - 100% Free, Offline Meeting Notes Tool
Main Gradio application with audio recording capability
"""
import gradio as gr
import os
from pathlib import Path
from datetime import datetime
from transcriber import Transcriber
from summarizer import Summarizer


# Initialize models globally (loaded once)
transcriber = None
summarizer = None


def initialize_models(whisper_model="base", ollama_model="llama3.2"):
    """Initialize Whisper and Ollama models"""
    global transcriber, summarizer
    
    try:
        if transcriber is None:
            transcriber = Transcriber(model_name=whisper_model)
        if summarizer is None:
            summarizer = Summarizer(model_name=ollama_model)
        return "✅ Models loaded successfully!"
    except Exception as e:
        return f"❌ Error loading models: {str(e)}"


def process_audio(audio_file, whisper_model="base", ollama_model="llama3.2"):
    """
    Process uploaded or recorded audio file
    
    Args:
        audio_file: Path to audio file or tuple (sample_rate, audio_data) from recorder
        whisper_model: Whisper model to use
        ollama_model: Ollama model to use
    
    Returns:
        tuple: (transcript, summary, key_points, action_items, status_message)
    """
    global transcriber, summarizer
    
    if audio_file is None:
        return "", "", "", "", "⚠️ Please upload or record an audio file first."
    
    try:
        # Initialize models if not already loaded
        if transcriber is None or summarizer is None:
            status = initialize_models(whisper_model, ollama_model)
            if "Error" in status:
                return "", "", "", "", status
        
        # Handle the audio file path
        audio_path = audio_file
        if isinstance(audio_file, tuple):
            # From recorder - save it first
            audio_path = "temp_recording.wav"
        
        # Step 1: Transcribe
        status_msg = "🎙️ Transcribing audio..."
        print(status_msg)
        
        result = transcriber.transcribe_audio(audio_path)
        transcript = result['text']
        
        if not transcript or transcript.strip() == "":
            return "", "", "", "", "⚠️ No speech detected in audio file."
        
        # Step 2: Summarize
        status_msg = "🤖 Generating summary and action items..."
        print(status_msg)
        
        summary_result = summarizer.summarize_transcript(transcript)
        
        # Format output
        full_summary = summary_result['summary']
        key_points = summary_result['key_points']
        action_items = summary_result['action_items']
        
        success_msg = "✅ Processing complete!"
        
        return transcript, full_summary, key_points, action_items, success_msg
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return "", "", "", "", error_msg


def save_to_file(transcript, summary, key_points, action_items):
    """Save the results to a text file"""
    if not transcript:
        return "⚠️ Nothing to save yet. Please process an audio file first."
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("meeting_outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"meeting_notes_{timestamp}.txt"
        
        # Write content
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MEETINGMIND - MEETING NOTES\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("TRANSCRIPT:\n")
            f.write("-" * 80 + "\n")
            f.write(transcript + "\n\n")
            
            f.write("SUMMARY:\n")
            f.write("-" * 80 + "\n")
            f.write(summary + "\n\n")
            
            f.write("KEY POINTS:\n")
            f.write("-" * 80 + "\n")
            f.write(key_points + "\n\n")
            
            f.write("ACTION ITEMS:\n")
            f.write("-" * 80 + "\n")
            f.write(action_items + "\n\n")
        
        return f"✅ Saved to: {filename}"
        
    except Exception as e:
        return f"❌ Error saving file: {str(e)}"


def create_ui():
    """Create the Gradio interface"""
    
    # Custom CSS for better styling
    custom_css = """
    .main-title {
        text-align: center;
        color: #2e7d32;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 14px;
        margin-bottom: 20px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="MeetingMind") as app:
        
        # Header
        gr.Markdown(
            """
            # 🧠 MeetingMind
            ### 100% Free, Offline Meeting Notes Tool
            Upload or record audio → Get transcripts, summaries & action items instantly!
            """,
            elem_classes="main-title"
        )
        
        gr.Markdown(
            "🔒 **Fully Private** - Everything runs locally on your machine. No data leaves your computer.",
            elem_classes="subtitle"
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                whisper_model = gr.Dropdown(
                    choices=["tiny", "base", "small", "medium", "large"],
                    value="base",
                    label="Whisper Model",
                    info="base = good speed/accuracy balance"
                )
                
                ollama_model = gr.Dropdown(
                    choices=["llama3.2", "llama3.1", "mistral", "llama2"],
                    value="llama3.2",
                    label="Ollama Model",
                    info="Make sure model is installed locally"
                )
                
                init_btn = gr.Button("🔄 Initialize Models", variant="secondary", size="sm")
                init_status = gr.Textbox(label="Status", interactive=False, show_label=False)
                
                init_btn.click(
                    fn=initialize_models,
                    inputs=[whisper_model, ollama_model],
                    outputs=init_status
                )
        
        gr.Markdown("---")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎤 Input Audio")
                
                # Tabs for upload vs record
                with gr.Tabs():
                    with gr.Tab("📁 Upload File"):
                        audio_upload = gr.Audio(
                            sources=["upload"],
                            type="filepath",
                            label="Upload Audio/Video File",
                            format="wav"
                        )
                        gr.Markdown("*Supports: mp3, wav, m4a, mp4, webm, and more*")
                    
                    with gr.Tab("🎙️ Record Audio"):
                        audio_record = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            label="Record Audio",
                            format="wav"
                        )
                        gr.Markdown("*Click to start recording, click again to stop*")
                
                process_btn = gr.Button("🚀 Process Audio", variant="primary", size="lg")
                status_box = gr.Textbox(label="Status", interactive=False)
        
        gr.Markdown("---")
        
        # Output section
        gr.Markdown("### 📄 Results")
        
        with gr.Tabs():
            with gr.Tab("📝 Transcript"):
                transcript_output = gr.Textbox(
                    label="Full Transcript",
                    lines=10,
                    max_lines=20,
                    show_copy_button=True
                )
            
            with gr.Tab("📊 Summary"):
                summary_output = gr.Textbox(
                    label="Meeting Summary",
                    lines=8,
                    max_lines=15,
                    show_copy_button=True
                )
            
            with gr.Tab("🔑 Key Points"):
                keypoints_output = gr.Textbox(
                    label="Key Discussion Points",
                    lines=8,
                    max_lines=15,
                    show_copy_button=True
                )
            
            with gr.Tab("✅ Action Items"):
                actions_output = gr.Textbox(
                    label="Action Items",
                    lines=8,
                    max_lines=15,
                    show_copy_button=True
                )
        
        # Save button
        with gr.Row():
            save_btn = gr.Button("💾 Save to File", variant="secondary")
            save_status = gr.Textbox(label="Save Status", interactive=False, show_label=False)
        
        # Define the processing logic for both upload and record
        def process_uploaded_audio(audio, whisper_m, ollama_m):
            return process_audio(audio, whisper_m, ollama_m)
        
        # Connect the process button to work with either upload or record
        # We'll use a combined input approach
        def get_audio_source(upload, record):
            """Return whichever audio source has content"""
            return upload if upload is not None else record
        
        process_btn.click(
            fn=lambda upload, record, whisper_m, ollama_m: process_audio(
                get_audio_source(upload, record), whisper_m, ollama_m
            ),
            inputs=[audio_upload, audio_record, whisper_model, ollama_model],
            outputs=[transcript_output, summary_output, keypoints_output, actions_output, status_box]
        )
        
        save_btn.click(
            fn=save_to_file,
            inputs=[transcript_output, summary_output, keypoints_output, actions_output],
            outputs=save_status
        )
        
        # Footer
        gr.Markdown(
            """
            ---
            **💡 Tips:**
            - First time? Click "Initialize Models" to load Whisper & Ollama
            - For faster processing, use "tiny" or "base" Whisper model
            - Make sure Ollama is running: `ollama serve` in terminal
            - All processing happens locally - completely private!
            """
        )
    
    return app


if __name__ == "__main__":
    print("=" * 80)
    print("🧠 MeetingMind - Starting application...")
    print("=" * 80)
    print("\n⚠️  IMPORTANT: Make sure Ollama is running!")
    print("   Run in terminal: ollama serve")
    print("   And pull a model: ollama pull llama3.2\n")
    print("=" * 80)
    
    app = create_ui()
    app.launch(
        share=False,
        inbrowser=True,
        server_name="127.0.0.1",
        server_port=7860
    )
