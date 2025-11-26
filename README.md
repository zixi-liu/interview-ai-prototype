# Interview AI Prototype

An AI-powered interview analyzer with a web interface that provides FAANG-standard feedback on self-introductions and behavioral questions. Supports both text and audio input with real-time transcription.

## Features

- 🌐 **Web UI**: Modern, responsive web interface for easy interaction
- 📝 **Text Analysis**: Analyze self-introductions and BQ answers from text input
- 🎤 **Audio Input**: Record or upload audio files with automatic transcription
- 🤖 **AI-Powered**: Uses GPT-4o and LiteLLM for multi-provider LLM support
- 📊 **FAANG Standards**: Evaluates candidates using Google, Amazon, Apple, Netflix, and Meta hiring criteria
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- ☁️ **Cloud Ready**: Configured for Railway deployment

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up environment variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Run the web application

```bash
python app.py
```

The web interface will be available at `http://localhost:8000`

Alternatively, use uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Choose between **Text Input** or **Audio Input** tabs
3. Enter your job role and company
4. Provide your self-introduction (text or audio)
5. Get instant AI-powered feedback

### Programmatic Usage

#### Self-Introduction Analysis

```python
from interview_analyzer import InterviewAnalyzer

analyzer = InterviewAnalyzer()
feedback = analyzer.analyze_introduction(
    introduction="Hi, I'm John. I've been a software engineer for 5 years...",
    role="Software Engineer",
    company="Google"
)
print(feedback)
```

#### Behavioral Question Analysis

```python
from interview_analyzer import InterviewAnalyzer

analyzer = InterviewAnalyzer()
feedback = analyzer.analyze_bq_question(
    question="Tell me about your most challenging project.",
    answer="I worked on a project where we had to migrate...",
    role="Senior Software Engineer"
)
print(feedback)
```

## API Endpoints

### POST `/analyze/text`

Analyze a text self-introduction.

**Request:**
- `introduction` (form data): Self-introduction text
- `role` (form data): Job role
- `company` (form data): Target company name

**Response:**
```json
{
  "feedback": "Detailed analysis...",
  "input_type": "text"
}
```

### POST `/analyze/audio`

Analyze an audio self-introduction with automatic transcription.

**Request:**
- `audio` (file): Audio file (WAV, MP3, WebM, M4A)
- `role` (form data): Job role
- `company` (form data): Target company name

**Response:**
```json
{
  "feedback": "Detailed analysis...",
  "transcription": "Transcribed text...",
  "input_type": "audio",
  "model": "gpt-4o-audio-preview (OpenAI) + gpt-4o (LiteLLM)"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Supported Models

Any model supported by LiteLLM:
- **OpenAI**: `gpt-4o-mini`, `gpt-4o`, `gpt-4o-audio-preview`
- **Anthropic**: `claude-3-5-sonnet-20241022`
- **Google**: `gemini-1.5-pro`

To use a different model:

```python
analyzer = InterviewAnalyzer(model="claude-3-5-sonnet-20241022")
```

## Docker Deployment

### Build and run with Docker

```bash
docker build -t interview-analyzer .
docker run -p 8000:8000 --env-file .env interview-analyzer
```

### Using Docker Compose

```bash
docker-compose up
```

The application will be available at `http://localhost:8000`

## Railway Deployment

The project is configured for Railway deployment:

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the `railway.json` configuration
3. Set your `OPENAI_API_KEY` environment variable in Railway
4. Deploy!

## Project Structure

```
interview-ai-prototype/
├── app.py                    # FastAPI web application
├── interview_analyzer.py     # Core analyzer class
├── prompts.py                # Prompt templates for analysis
├── example_usage.py          # Example usage scripts
├── static/
│   └── index.html           # Web UI frontend
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── railway.json            # Railway deployment config
├── deploy.sh               # Deployment script
└── README.md               # This file
```

## Evaluation Criteria

The analyzer evaluates candidates using FAANG standards:

### Self-Introduction Checkpoints
- Clarity & Conciseness
- Relevance to Job
- Technical Depth Preview
- Ownership
- Motivation & Career Narrative
- Confidence & Professionalism

### Behavioral Question Checkpoints
- STAR Method Structure (Situation, Task, Action, Result)
- Specificity & Details
- Impact & Results
- Leadership & Ownership
- Problem-Solving & Decision Making
- Communication & Clarity

## Requirements

- Python 3.11+
- FFmpeg (for audio processing, installed automatically in Docker)
- OpenAI API key

## Dependencies

- `litellm>=1.0.0` - Multi-provider LLM support
- `fastapi>=0.104.0` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `openai>=1.0.0` - OpenAI client for audio transcription
- `pydub>=0.25.1` - Audio format conversion
- `python-dotenv>=1.0.0` - Environment variable management

## License

MIT
