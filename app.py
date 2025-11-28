"""
FastAPI Web UI for Interview Analyzer
Supports text and audio input for self-introduction analysis
"""

import asyncio
import os
import json
from pathlib import Path

from fastapi import (
    FastAPI, 
    File, 
    UploadFile, 
    Form, 
    HTTPException, 
    Request
)
from fastapi.responses import (
    HTMLResponse, 
    JSONResponse,
    StreamingResponse
)
from fastapi.middleware.cors import (
    CORSMiddleware
)
from jinja2 import (
    Environment, 
    FileSystemLoader
)

from interview_analyzer import InterviewAnalyzer, AUDIO_TARGET_FORMAT
from utils import AudioConverter

# Constants
DEFAULT_MODEL = "gpt-4o"
DEFAULT_PORT = 8000


app = FastAPI(title="Interview Feedback System", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
jinja_env = Environment(loader=FileSystemLoader("templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main UI"""
    # Check if static/index.html exists (preferred)
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return html_file.read_text()
    
    # Fallback to template
    template = jinja_env.get_template("index.html")
    return HTMLResponse(content=template.render())


@app.post("/analyze/text")
async def analyze_text(
    introduction: str = Form(...),
    role: str = Form(...),
    company: str = Form(...)
):
    """Analyze text introduction"""
    try:
        feedback = await InterviewAnalyzer(model=DEFAULT_MODEL).analyze_introduction(
            introduction=introduction,
            role=role,
            company=company
        )
        return JSONResponse({
            "feedback": feedback,
            "input_type": "text"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/audio")
async def analyze_audio(
    audio: UploadFile = File(...),
    role: str = Form(...),
    company: str = Form(...)
):
    """
    Analyze audio introduction using GPT-4o audio input directly.
    
    Mobile browsers use different formats: iOS=MP4/AAC, Android=WebM/Opus
    GPT-4o audio supports: wav, mp3, flac, opus, pcm16
    """
    try:
        # Read audio content
        audio_content = await audio.read()
        print(f"[Audio] Received format: {audio.content_type}, size: {len(audio_content)} bytes")

        # Convert to WAV format for GPT-4o audio compatibility
        wav_content = await AudioConverter.convert_to_wav(audio_content, audio.content_type or "")
        print(f"[Audio] Converted to wav, new size: {len(wav_content)} bytes")

        # Analyze audio directly using gpt-4o-audio-preview (supports text+audio input)
        # Execute analysis and transcription concurrently for better performance
        analyzer = InterviewAnalyzer(model=DEFAULT_MODEL)
        print(f"[Audio] Sending to {analyzer.audio_model} for direct analysis, format: {AUDIO_TARGET_FORMAT}")
        feedback, transcription = await asyncio.gather(
            analyzer.analyze_audio(wav_content, AUDIO_TARGET_FORMAT, role, company),
            analyzer.transcribe_audio(wav_content, AUDIO_TARGET_FORMAT)
        )

        return JSONResponse({
            "feedback": feedback,
            "transcription": transcription,
            "input_type": "audio",
            "model": f"{analyzer.audio_model} (LiteLLM)"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/audio/stream")
async def analyze_audio_stream(
    audio: UploadFile = File(...),
    role: str = Form(...),
    company: str = Form(...)
):
    """
    Analyze audio introduction using GPT-4o audio input with streaming response.
    
    Returns Server-Sent Events (SSE) stream of analysis feedback.
    Mobile browsers use different formats: iOS=MP4/AAC, Android=WebM/Opus
    GPT-4o audio supports: wav, mp3, flac, opus, pcm16
    """
    try:
        # Read audio content
        audio_content = await audio.read()
        print(f"[Audio Stream] Received format: {audio.content_type}, size: {len(audio_content)} bytes")

        # Convert to WAV format for GPT-4o audio compatibility
        wav_content = await AudioConverter.convert_to_wav(audio_content, audio.content_type or "")
        print(f"[Audio Stream] Converted to wav, new size: {len(wav_content)} bytes")

        # Create async generator for streaming response
        async def generate_stream():
            try:
                analyzer = InterviewAnalyzer(model=DEFAULT_MODEL)
                print(f"[Audio Stream] Sending to {analyzer.audio_model} for streaming analysis, format: {AUDIO_TARGET_FORMAT}")
                result = analyzer.analyze_audio(wav_content, AUDIO_TARGET_FORMAT, role, company, stream=True)
                async for chunk in result:
                    # Format as Server-Sent Events (SSE)
                    # SSE format: "data: <content>\n\n"
                    yield f"data: {chunk}\n\n"
                # Send completion signal
                yield "data: [DONE]\n\n"
            except Exception as e:
                # Send error as SSE event
                error_data = json.dumps({"error": str(e)})
                yield f"data: {error_data}\n\n"
                raise

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable buffering in nginx
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", DEFAULT_PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)
