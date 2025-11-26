"""
FastAPI Web UI for Interview Analyzer
Supports text and audio input for self-introduction analysis
"""

import os
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
from fastapi.staticfiles import (
    StaticFiles
)
from fastapi.middleware.cors import (
    CORSMiddleware
)
from jinja2 import (
    Environment, 
    FileSystemLoader
)

from interview_analyzer import InterviewAnalyzer

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
    global analyzer
    if analyzer is None:
        analyzer = InterviewAnalyzer(model="gpt-4o")
    return analyzer


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
        feedback = get_analyzer().analyze_introduction(
            introduction=introduction,
            role=role,
            company=company
        )
        return JSONResponse({"feedback": feedback, "input_type": "text"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/audio")
async def analyze_audio(
    audio: UploadFile = File(...),
    role: str = Form(...),
    company: str = Form(...)
):
    """Analyze audio introduction using GPT-4o audio input directly"""
    try:
        import base64
        from openai import OpenAI
        from litellm import completion
        from prompts import SYSTEM_MESSAGE_INTRODUCTION, get_introduction_prompt

        # Read audio content
        audio_content = await audio.read()

        # Always convert to WAV for GPT-4o audio compatibility
        # Mobile browsers use different formats: iOS=MP4/AAC, Android=WebM/Opus
        # GPT-4o audio supports: wav, mp3, flac, opus, pcm16
        from pydub import AudioSegment
        import io

        print(f"[Audio] Received format: {audio.content_type}, size: {len(audio_content)} bytes")

        # Save input audio to temp file
        input_suffix = ".audio"
        if audio.content_type:
            if "webm" in audio.content_type.lower():
                input_suffix = ".webm"
            elif "mp4" in audio.content_type.lower() or "m4a" in audio.content_type.lower():
                input_suffix = ".m4a"
            elif "mpeg" in audio.content_type.lower() or "mp3" in audio.content_type.lower():
                input_suffix = ".mp3"

        with tempfile.NamedTemporaryFile(delete=False, suffix=input_suffix) as temp_input:
            temp_input.write(audio_content)
            temp_input_path = temp_input.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            temp_output_path = temp_output.name

        try:
            # Convert any format to wav using pydub
            audio_segment = AudioSegment.from_file(temp_input_path)
            audio_segment.export(temp_output_path, format="wav")

            # Read converted audio
            with open(temp_output_path, "rb") as f:
                audio_content = f.read()

            audio_format = "wav"
            print(f"[Audio] Converted to wav, new size: {len(audio_content)} bytes")
        finally:
            # Cleanup
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_content).decode()

        # Get the text prompt from our prompt management system
        text_prompt = get_introduction_prompt(
            introduction="[Audio input - analyzing spoken content]",
            role=role,
            company=company
        )

        # Use OpenAI client directly for audio (LiteLLM doesn't support audio input format yet)
        client = OpenAI()

        # First get transcription using GPT-4o audio
        print(f"[Audio] Sending to GPT-4o audio, format: {audio_format}")
        transcription_response = client.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please transcribe the following audio exactly as spoken:"
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
            ]
        )

        transcription = transcription_response.choices[0].message.content

        # Now analyze using LiteLLM with the transcription
        analysis_response = completion(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE_INTRODUCTION
                },
                {
                    "role": "user",
                    "content": text_prompt.replace(
                        "[Audio input - analyzing spoken content]",
                        transcription
                    )
                }
            ],
            temperature=0.3
        )

        feedback = analysis_response.choices[0].message.content

        return JSONResponse({
            "feedback": feedback,
            "transcription": transcription,
            "input_type": "audio",
            "model": "gpt-4o-audio-preview (OpenAI) + gpt-4o (LiteLLM)"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
