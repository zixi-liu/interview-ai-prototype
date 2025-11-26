"""
FastAPI Web UI for Interview Analyzer
Supports text and audio input for self-introduction analysis
"""

import asyncio
import os
import re
import base64
import tempfile
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
    JSONResponse
)
from fastapi.middleware.cors import (
    CORSMiddleware
)
from jinja2 import (
    Environment, 
    FileSystemLoader
)
from litellm import acompletion
from pydub import AudioSegment

from interview_analyzer import InterviewAnalyzer
from prompts import SYSTEM_MESSAGE_INTRODUCTION, get_introduction_prompt

# Constants
DEFAULT_MODEL = "gpt-4o"
AUDIO_MODEL = "gpt-4o-audio-preview"
AUDIO_TARGET_FORMAT = "wav"
DEFAULT_PORT = 8000
AUDIO_PLACEHOLDER = "[Audio input - analyzing spoken content]"
TRANSCRIPTION_PROMPT = "Please transcribe the following audio exactly as spoken:"


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

# Analyzer will be initialized on first request
analyzer = None

def get_analyzer():
    """Get or create the InterviewAnalyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = InterviewAnalyzer(model=DEFAULT_MODEL)
    return analyzer


def _get_audio_suffix(content_type: str) -> str:
    """Determine audio file suffix from content type"""
    # use regex to match the content type
    match = re.match(r"audio/([^;]+)", content_type)
    if match:
        return f".{match.group(1).lower()}"
    return ".audio"


def _convert_audio_to_wav_sync(audio_content: bytes, content_type: str) -> bytes:
    """
    Synchronous audio conversion (CPU-intensive, runs in thread pool)
    
    Args:
        audio_content: Raw audio bytes
        content_type: MIME type of the audio
        
    Returns:
        WAV format audio bytes
    """
    input_suffix = _get_audio_suffix(content_type)
    temp_input_path = None
    temp_output_path = None
    
    try:
        # Save input audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=input_suffix) as temp_input:
            temp_input.write(audio_content)
            temp_input_path = temp_input.name
        
        # Create output temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            temp_output_path = temp_output.name
        
        # Convert to WAV (CPU-intensive operation)
        audio_segment = AudioSegment.from_file(temp_input_path)
        audio_segment.export(temp_output_path, format=AUDIO_TARGET_FORMAT)
        
        # Read converted audio
        with open(temp_output_path, "rb") as f:
            return f.read()
    finally:
        # Cleanup temp files
        for path in [temp_input_path, temp_output_path]:
            if path and os.path.exists(path):
                os.unlink(path)


async def _convert_audio_to_wav(audio_content: bytes, content_type: str) -> bytes:
    """
    Convert audio content to WAV format asynchronously
    
    Args:
        audio_content: Raw audio bytes
        content_type: MIME type of the audio
        
    Returns:
        WAV format audio bytes
    """
    # Run CPU-intensive conversion in thread pool to avoid blocking event loop
    return await asyncio.to_thread(_convert_audio_to_wav_sync, audio_content, content_type)


async def _transcribe_audio(audio_content: bytes, audio_format: str) -> str:
    """
    Transcribe audio using GPT-4o audio model asynchronously via LiteLLM
    
    Args:
        audio_content: Audio bytes in WAV format
        audio_format: Audio format (should be "wav")
        
    Returns:
        Transcribed text
    """
    audio_b64 = base64.b64encode(audio_content).decode()
    
    response = await acompletion(
        model=AUDIO_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": TRANSCRIPTION_PROMPT
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": audio_format
                        }
                    }
                ]
            }
        ],
        modalities=["text"]
    )
    
    return response.choices[0].message.content


async def _analyze_transcription(transcription: str, role: str, company: str) -> str:
    """
    Analyze transcribed text using LiteLLM asynchronously
    
    Args:
        transcription: Transcribed text from audio
        role: Job role
        company: Company name
        
    Returns:
        Analysis feedback
    """
    text_prompt = get_introduction_prompt(
        introduction=AUDIO_PLACEHOLDER,
        role=role,
        company=company
    )
    
    # Replace placeholder with actual transcription
    text_prompt = text_prompt.replace(AUDIO_PLACEHOLDER, transcription)
    
    response = await acompletion(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE_INTRODUCTION
            },
            {
                "role": "user",
                "content": text_prompt
            }
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content


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
        feedback = await get_analyzer().analyze_introduction(
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
        wav_content = await _convert_audio_to_wav(audio_content, audio.content_type or "")
        print(f"[Audio] Converted to wav, new size: {len(wav_content)} bytes")

        # Transcribe audio
        print(f"[Audio] Sending to GPT-4o audio, format: {AUDIO_TARGET_FORMAT}")
        transcription = await _transcribe_audio(wav_content, AUDIO_TARGET_FORMAT)

        # Analyze transcription
        feedback = await _analyze_transcription(transcription, role, company)

        return JSONResponse({
            "feedback": feedback,
            "transcription": transcription,
            "input_type": "audio",
            "model": f"{AUDIO_MODEL} (LiteLLM) + {DEFAULT_MODEL} (LiteLLM)"
        })

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
