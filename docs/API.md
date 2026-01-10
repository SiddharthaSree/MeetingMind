# MeetingMind API Reference

This document provides the API reference for MeetingMind's Python modules.

---

## Transcriber Module

**File:** `transcriber.py`

### Class: `Transcriber`

Handles audio transcription using OpenAI Whisper.

#### Constructor

```python
Transcriber(model_name: str = "base")
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `model_name` | str | "base" | Whisper model to use |

**Available Models:**
- `tiny` - Fastest, lowest accuracy
- `base` - Good balance (recommended)
- `small` - Better accuracy
- `medium` - High accuracy
- `large` - Best accuracy, slowest

**Example:**
```python
from transcriber import Transcriber

# Initialize with default model
transcriber = Transcriber()

# Initialize with specific model
transcriber = Transcriber(model_name="small")
```

---

#### Method: `transcribe_audio`

Transcribe an audio file to text.

```python
transcribe_audio(audio_path: str, language: str = None) -> dict
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `audio_path` | str | required | Path to the audio file |
| `language` | str | None | Language code (auto-detect if None) |

**Returns:**
```python
{
    'text': str,        # Full transcription text
    'segments': list,   # Timestamped segments
    'language': str     # Detected/specified language
}
```

**Supported Languages:**
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `zh` - Chinese
- And 90+ more (auto-detected)

**Example:**
```python
result = transcriber.transcribe_audio("meeting.mp3")
print(result['text'])

# With specific language
result = transcriber.transcribe_audio("meeting.mp3", language="en")
```

**Raises:**
- `FileNotFoundError` - If audio file doesn't exist

---

#### Method: `get_available_models`

Get list of available Whisper models.

```python
get_available_models() -> list
```

**Returns:**
```python
['tiny', 'base', 'small', 'medium', 'large']
```

---

### Function: `transcribe_file`

Convenience function for quick transcription without class initialization.

```python
transcribe_file(audio_path: str, model_name: str = "base", language: str = None) -> str
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `audio_path` | str | required | Path to audio file |
| `model_name` | str | "base" | Whisper model name |
| `language` | str | None | Language code |

**Returns:** `str` - Transcribed text

**Example:**
```python
from transcriber import transcribe_file

text = transcribe_file("meeting.mp3")
print(text)
```

---

## Summarizer Module

**File:** `summarizer.py`

### Class: `Summarizer`

Generates meeting summaries using Ollama (local LLM).

#### Constructor

```python
Summarizer(model_name: str = "llama3.2")
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `model_name` | str | "llama3.2" | Ollama model to use |

**Recommended Models:**
- `llama3.2` - Fast, good quality (3B)
- `llama3.1` - Better quality (8B)
- `mistral` - Good balance (7B)
- `llama2` - Reliable fallback (7B)

**Example:**
```python
from summarizer import Summarizer

summarizer = Summarizer()
summarizer = Summarizer(model_name="mistral")
```

---

#### Method: `summarize_transcript`

Generate a meeting summary with action items from transcript.

```python
summarize_transcript(transcript: str) -> dict
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `transcript` | str | required | The meeting transcript text |

**Returns:**
```python
{
    'summary': str,       # Concise meeting summary
    'key_points': str,    # Bullet-pointed key discussion points
    'action_items': str   # Extracted action items
}
```

**Example:**
```python
result = summarizer.summarize_transcript(transcript_text)

print("Summary:", result['summary'])
print("Key Points:", result['key_points'])
print("Actions:", result['action_items'])
```

---

#### Method: `check_ollama_status`

Check if Ollama is running and accessible.

```python
check_ollama_status() -> bool
```

**Returns:** `bool` - True if Ollama is accessible

**Example:**
```python
if summarizer.check_ollama_status():
    print("Ollama is running!")
else:
    print("Please start Ollama: ollama serve")
```

---

### Function: `summarize_text`

Convenience function for quick summarization.

```python
summarize_text(transcript: str, model_name: str = "llama3.2") -> dict
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `transcript` | str | required | Meeting transcript |
| `model_name` | str | "llama3.2" | Ollama model name |

**Returns:** Same as `summarize_transcript`

**Example:**
```python
from summarizer import summarize_text

result = summarize_text("Meeting discussion...")
```

---

## App Module

**File:** `app.py`

### Function: `initialize_models`

Initialize Whisper and Ollama models.

```python
initialize_models(whisper_model: str = "base", ollama_model: str = "llama3.2") -> str
```

**Returns:** Status message string

---

### Function: `process_audio`

Process uploaded or recorded audio file through full pipeline.

```python
process_audio(audio_file, whisper_model: str = "base", ollama_model: str = "llama3.2") -> tuple
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `audio_file` | str/tuple | Path to audio or recorder output |
| `whisper_model` | str | Whisper model name |
| `ollama_model` | str | Ollama model name |

**Returns:**
```python
(transcript, summary, key_points, action_items, status_message)
```

---

### Function: `save_to_file`

Save the results to a text file.

```python
save_to_file(transcript: str, summary: str, key_points: str, action_items: str) -> str
```

**Returns:** Status message with file path

---

### Function: `create_ui`

Create the Gradio interface.

```python
create_ui() -> gr.Blocks
```

**Returns:** Configured Gradio app

---

## Usage Examples

### Complete Pipeline

```python
from transcriber import Transcriber
from summarizer import Summarizer

# Initialize
transcriber = Transcriber(model_name="base")
summarizer = Summarizer(model_name="llama3.2")

# Transcribe
result = transcriber.transcribe_audio("meeting.mp3")
transcript = result['text']
print(f"Language: {result['language']}")

# Summarize
summary = summarizer.summarize_transcript(transcript)

# Output
print("=== TRANSCRIPT ===")
print(transcript)

print("\n=== SUMMARY ===")
print(summary['summary'])

print("\n=== KEY POINTS ===")
print(summary['key_points'])

print("\n=== ACTION ITEMS ===")
print(summary['action_items'])
```

### Quick One-Liner

```python
from transcriber import transcribe_file
from summarizer import summarize_text

text = transcribe_file("meeting.mp3")
result = summarize_text(text)
print(result['action_items'])
```

### Running the UI

```python
from app import create_ui

app = create_ui()
app.launch(share=False, inbrowser=True)
```

---

## Error Handling

```python
from transcriber import Transcriber
from summarizer import Summarizer

try:
    transcriber = Transcriber()
    result = transcriber.transcribe_audio("audio.mp3")
except FileNotFoundError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"Transcription error: {e}")

try:
    summarizer = Summarizer()
    if not summarizer.check_ollama_status():
        print("Start Ollama first: ollama serve")
    else:
        summary = summarizer.summarize_transcript(transcript)
except Exception as e:
    print(f"Summarization error: {e}")
```
