# Interview AI Prototype

AI-powered interview analyzer providing FAANG-standard feedback on self-introductions and behavioral questions. Supports text and audio input.

---

## 🚀 Quick Start

**3 steps to get started:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 3. Run the app
python app.py
```

Open `http://localhost:8000` in your browser.

---

## What It Does

- 📝 **Text Analysis**: Analyze self-introductions and behavioral question answers
- 🎤 **Audio Input**: Record or upload audio with automatic transcription
- 🤖 **AI Feedback**: FAANG-standard evaluation (Google, Amazon, Apple, Netflix, Meta)
- 🌐 **Web UI**: Modern, responsive interface

---

## Usage

### Web Interface

1. Go to `http://localhost:8000`
2. Choose **Text** or **Audio** input
3. Enter job role, company, and your introduction
4. Get instant AI feedback

### Programmatic Usage

```python
import asyncio
from interview_analyzer import InterviewAnalyzer

async def main():
    analyzer = InterviewAnalyzer()
    feedback = await analyzer.analyze_introduction(
        introduction="Hi, I'm John. I've been a software engineer for 5 years...",
        role="Software Engineer",
        company="Google"
    )
    print(feedback)

asyncio.run(main())
```

---

## API Endpoints

- `POST /analyze/text` - Analyze text input
- `POST /analyze/audio` - Analyze audio input (auto-transcribe)
- `GET /health` - Health check

See code for request/response formats.

---

## Deployment

### Docker

```bash
docker-compose up
```

### Railway

1. Connect GitHub repo to Railway
2. Set `OPENAI_API_KEY` environment variable
3. Deploy (auto-detects `railway.json`)

---

## Requirements

- Python 3.11+
- OpenAI API key
- FFmpeg (auto-installed in Docker)

---

## Supported Models

Any LiteLLM-supported model:
- OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4o-audio-preview`
- Anthropic: `claude-3-5-sonnet-20241022`
- Google: `gemini-1.5-pro`

Change model: `InterviewAnalyzer(model="claude-3-5-sonnet-20241022")`

---

## Evaluation Criteria

**Self-Introduction**: Clarity, Relevance, Technical Depth, Ownership, Motivation, Confidence

**Behavioral Questions**: STAR Method, Specificity, Impact, Leadership, Problem-Solving, Communication

---

## License

MIT
