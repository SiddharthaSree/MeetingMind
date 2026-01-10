# Contributing to MeetingMind

First off, thank you for considering contributing to MeetingMind! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to:
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.10+
- FFmpeg installed
- Ollama installed and running
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MeetingMind.git
   cd MeetingMind
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/MeetingMind.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### 3. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

### 4. Verify Setup

```bash
# Start Ollama
ollama serve

# In another terminal, run the app
python app.py
```

## Making Changes

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/speaker-diarization`)
- `bugfix/` - Bug fixes (e.g., `bugfix/audio-upload-error`)
- `docs/` - Documentation changes (e.g., `docs/api-reference`)
- `refactor/` - Code refactoring (e.g., `refactor/transcriber-module`)

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
```

### Making Commits

Follow conventional commit messages:

```
type(scope): short description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(transcriber): add speaker diarization support
fix(ui): resolve audio upload timeout issue
docs(readme): update installation instructions
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test your changes** thoroughly:
   ```bash
   python -m pytest tests/  # If tests exist
   python app.py  # Manual testing
   ```

3. **Check code style**:
   ```bash
   pip install black flake8
   black .
   flake8 .
   ```

4. **Update documentation** if needed

### Submitting PR

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create Pull Request on GitHub

3. Fill out the PR template:
   - **Description**: What does this PR do?
   - **Related Issue**: Link any related issues
   - **Testing**: How was this tested?
   - **Screenshots**: If UI changes

### PR Review Process

- All PRs require at least one review
- CI checks must pass
- Keep PRs focused and small when possible
- Respond to feedback promptly

## Style Guidelines

### Python Style

We follow PEP 8 with some modifications:

```python
# Good
class TranscriberService:
    """Service class for audio transcription."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize transcriber.
        
        Args:
            model_name: Whisper model to use
        """
        self.model_name = model_name
    
    def transcribe(self, audio_path: str) -> dict:
        """Transcribe audio file to text."""
        pass
```

**Key Points:**
- Use type hints
- Write docstrings for all public methods
- Maximum line length: 100 characters
- Use meaningful variable names
- Add comments for complex logic

### Documentation Style

- Use Markdown for all documentation
- Include code examples
- Keep language clear and concise
- Update docs with code changes

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Update to latest version
3. Verify prerequisites are installed

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.10.5]
- Whisper model: [e.g., base]
- Ollama model: [e.g., llama3.2]

**Additional context**
Any other relevant information.
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features.

**Additional context**
Any other context, mockups, or examples.
```

### Feature Ideas Welcome

- Speaker identification/diarization
- Multiple language support
- Export to different formats (PDF, DOCX)
- Meeting templates
- Integration with calendar apps
- Real-time transcription
- Custom summarization prompts

## Development Areas

### Current Priorities

1. **Stability** - Bug fixes and error handling
2. **Performance** - Faster processing
3. **UX** - Better user interface
4. **Features** - New capabilities

### Good First Issues

Look for issues labeled `good-first-issue` for beginner-friendly tasks.

## Questions?

- Open a GitHub Discussion
- Check existing documentation
- Review closed issues

---

Thank you for contributing to MeetingMind! 🙏
