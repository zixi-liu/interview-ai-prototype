"""
FastAPI Web UI for Interview Analyzer
Supports text and audio input for self-introduction analysis
"""

import asyncio
import os
import re
import base64
import subprocess
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

from interview_analyzer import InterviewAnalyzer
from prompts import SystemMessage, get_introduction_prompt

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


def _get_ffmpeg_input_format(content_type: str) -> str:
    """Determine ffmpeg input format from content type"""
    # Map common MIME types to ffmpeg format names
    format_map = {
        "mpeg": "mp3",
        "mp4": "mp4",
        "webm": "webm",
        "ogg": "ogg",
        "opus": "opus",
        "flac": "flac",
        "wav": "wav",
        "aac": "aac",
        "m4a": "m4a",
    }
    
    # Extract format from content type (e.g., "audio/mpeg" -> "mpeg")
    match = re.match(r"audio/([^;]+)", content_type)
    if match:
        format_name = match.group(1).lower()
        return format_map.get(format_name, format_name)
    
    # Default to auto-detect
    return "auto"


def _convert_audio_to_wav_sync(audio_content: bytes, content_type: str) -> bytes:
    """
    Convert audio to WAV format directly in memory using ffmpeg (no temp files, no AudioSegment)
    
    Args:
        audio_content: Raw audio bytes
        content_type: MIME type of the audio
        
    Returns:
        WAV format audio bytes
    """
    input_format = _get_ffmpeg_input_format(content_type)
    
    # Build ffmpeg command to convert from stdin to stdout
    # -f: input format
    # -i pipe:0: read from stdin
    # -f wav: output format as WAV
    # -: output to stdout
    # -y: overwrite output file (not needed for stdout, but harmless)
    cmd = [
        "ffmpeg",
        "-f", input_format,
        "-i", "pipe:0",  # Read from stdin
        "-f", AUDIO_TARGET_FORMAT,  # Output format
        "-",  # Output to stdout
        "-y"  # Overwrite (for stdout this is harmless)
    ]
    
    try:
        # Run ffmpeg with audio content as stdin, capture stdout
        process = subprocess.run(
            cmd,
            input=audio_content,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return process.stdout
    except subprocess.CalledProcessError as e:
        # If format detection fails, try with auto-detect
        if input_format != "auto":
            cmd[2] = "auto"  # Change input format to auto-detect
            try:
                process = subprocess.run(
                    cmd,
                    input=audio_content,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                return process.stdout
            except subprocess.CalledProcessError:
                raise RuntimeError(f"Audio conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")
        else:
            raise RuntimeError(f"Audio conversion failed: {e.stderr.decode('utf-8', errors='ignore')}")


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
                "content": SystemMessage.INTRODUCTION
            },
            {
                "role": "user",
                "content": text_prompt
            }
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content


async def _analyze_audio(audio_content: bytes, audio_format: str, role: str, company: str) -> str:
    """
    Analyze audio directly using gpt-4o-audio-preview which supports text+audio mixed input.
    
    Args:
        audio_content: Audio bytes in WAV format
        audio_format: Audio format (should be "wav")
        role: Job role
        company: Company name
        
    Returns:
        Analysis feedback
    """
    audio_b64 = base64.b64encode(audio_content).decode()

    text_prompt = get_introduction_prompt(
        introduction=AUDIO_PLACEHOLDER,
        role=role,
        company=company
    )
    
    response = await acompletion(
        model=AUDIO_MODEL,  # Use gpt-4o-audio-preview which supports text+audio input
        messages=[
            {
                "role": "system",
                "content": SystemMessage.INTRODUCTION
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
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
        temperature=0.3,
        modalities=["text"]  # Request text output
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

        # Analyze audio directly using gpt-4o-audio-preview (supports text+audio input)
        print(f"[Audio] Sending to {AUDIO_MODEL} for direct analysis, format: {AUDIO_TARGET_FORMAT}")
        feedback = await _analyze_audio(wav_content, AUDIO_TARGET_FORMAT, role, company)

        # Optionally transcribe for display (can be done in parallel if needed)
        transcription = await _transcribe_audio(wav_content, AUDIO_TARGET_FORMAT)

        return JSONResponse({
            "feedback": feedback,
            "transcription": transcription,
            "input_type": "audio",
            "model": f"{AUDIO_MODEL} (LiteLLM)"
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
