"""
FastAPI Web UI for Interview Analyzer
Supports text and audio input for self-introduction analysis
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from pathlib import Path

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

# Analyzer will be initialized on first request
analyzer = None

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = InterviewAnalyzer(model="gpt-4o")
    return analyzer


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main UI"""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return html_file.read_text()

    # Fallback inline HTML if static file doesn't exist
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interview Feedback System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
                border-bottom: 2px solid #eee;
            }
            .tab {
                padding: 12px 24px;
                background: none;
                border: none;
                cursor: pointer;
                font-size: 16px;
                color: #666;
                border-bottom: 3px solid transparent;
                transition: all 0.3s;
            }
            .tab.active {
                color: #667eea;
                border-bottom-color: #667eea;
                font-weight: 600;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            input[type="text"], select, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 15px;
                transition: border-color 0.3s;
            }
            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                min-height: 200px;
                resize: vertical;
                font-family: inherit;
            }
            .audio-controls {
                display: flex;
                gap: 10px;
                align-items: center;
                margin-top: 10px;
            }
            button {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: 500;
            }
            button:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .record-btn {
                background: #e74c3c;
            }
            .record-btn.recording {
                background: #c0392b;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            .stop-btn {
                background: #95a5a6;
            }
            #result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                display: none;
            }
            #result.show {
                display: block;
            }
            .loading {
                text-align: center;
                padding: 40px;
                display: none;
            }
            .loading.show {
                display: block;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                background: white;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #c33;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Interview Feedback System</h1>
            <p class="subtitle">Get AI-powered feedback on your self-introduction</p>

            <div class="tabs">
                <button class="tab active" onclick="switchTab('text')">📝 Text Input</button>
                <button class="tab" onclick="switchTab('audio')">🎤 Audio Input</button>
            </div>

            <!-- Text Input Tab -->
            <div id="text-tab" class="tab-content active">
                <form id="text-form">
                    <div class="form-group">
                        <label for="role">Job Role</label>
                        <input type="text" id="role" name="role" value="Software Engineer" required>
                    </div>

                    <div class="form-group">
                        <label for="yoe">Years of Experience (optional)</label>
                        <input type="number" id="yoe" name="yoe" min="0" max="50" placeholder="e.g., 3">
                    </div>

                    <div class="form-group">
                        <label for="introduction">Your Self-Introduction</label>
                        <textarea id="introduction" name="introduction"
                                  placeholder="Hi, I'm... I have X years of experience in..."
                                  required></textarea>
                    </div>

                    <button type="submit">Analyze Introduction</button>
                </form>
            </div>

            <!-- Audio Input Tab -->
            <div id="audio-tab" class="tab-content">
                <form id="audio-form">
                    <div class="form-group">
                        <label for="audio-role">Job Role</label>
                        <input type="text" id="audio-role" name="role" value="Software Engineer" required>
                    </div>

                    <div class="form-group">
                        <label for="audio-yoe">Years of Experience (optional)</label>
                        <input type="number" id="audio-yoe" name="yoe" min="0" max="50" placeholder="e.g., 3">
                    </div>

                    <div class="form-group">
                        <label>Record Your Introduction</label>
                        <div class="audio-controls">
                            <button type="button" id="record-btn" class="record-btn">🎤 Start Recording</button>
                            <button type="button" id="stop-btn" class="stop-btn" disabled>⏹ Stop</button>
                            <span id="timer">0:00</span>
                        </div>
                        <audio id="audio-preview" controls style="width: 100%; margin-top: 10px; display: none;"></audio>
                    </div>

                    <button type="submit" id="audio-submit" disabled>Analyze Audio</button>
                </form>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 20px;">Analyzing your introduction...</p>
            </div>

            <div id="result"></div>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let audioBlob;
            let recordingStartTime;
            let timerInterval;

            function switchTab(tab) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

                if (tab === 'text') {
                    document.querySelector('.tab:first-child').classList.add('active');
                    document.getElementById('text-tab').classList.add('active');
                } else {
                    document.querySelector('.tab:last-child').classList.add('active');
                    document.getElementById('audio-tab').classList.add('active');
                }
            }

            // Text form submission
            document.getElementById('text-form').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData();
                formData.append('introduction', document.getElementById('introduction').value);
                formData.append('role', document.getElementById('role').value);
                const yoe = document.getElementById('yoe').value;
                if (yoe) formData.append('yoe', yoe);

                await analyzeIntroduction(formData, '/analyze/text');
            });

            // Audio recording
            document.getElementById('record-btn').addEventListener('click', async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = () => {
                        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        const preview = document.getElementById('audio-preview');
                        preview.src = audioUrl;
                        preview.style.display = 'block';
                        document.getElementById('audio-submit').disabled = false;
                    };

                    mediaRecorder.start();
                    document.getElementById('record-btn').disabled = true;
                    document.getElementById('record-btn').classList.add('recording');
                    document.getElementById('stop-btn').disabled = false;

                    recordingStartTime = Date.now();
                    timerInterval = setInterval(updateTimer, 1000);
                } catch (err) {
                    alert('Error accessing microphone: ' + err.message);
                }
            });

            document.getElementById('stop-btn').addEventListener('click', () => {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                document.getElementById('record-btn').disabled = false;
                document.getElementById('record-btn').classList.remove('recording');
                document.getElementById('stop-btn').disabled = true;
                clearInterval(timerInterval);
            });

            function updateTimer() {
                const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                document.getElementById('timer').textContent =
                    `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }

            // Audio form submission
            document.getElementById('audio-form').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.wav');
                formData.append('role', document.getElementById('audio-role').value);
                const yoe = document.getElementById('audio-yoe').value;
                if (yoe) formData.append('yoe', yoe);

                await analyzeIntroduction(formData, '/analyze/audio');
            });

            async function analyzeIntroduction(formData, endpoint) {
                document.getElementById('loading').classList.add('show');
                document.getElementById('result').classList.remove('show');
                document.getElementById('result').innerHTML = '';

                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.detail || 'Analysis failed');
                    }

                    document.getElementById('result').innerHTML = `<pre>${data.feedback}</pre>`;
                    document.getElementById('result').classList.add('show');
                } catch (error) {
                    document.getElementById('result').innerHTML =
                        `<div class="error">Error: ${error.message}</div>`;
                    document.getElementById('result').classList.add('show');
                } finally {
                    document.getElementById('loading').classList.remove('show');
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/analyze/text")
async def analyze_text(
    introduction: str = Form(...),
    role: str = Form(...),
    company: str = Form(...),
    yoe: int = Form(...)
):
    """Analyze text introduction"""
    try:
        feedback = get_analyzer().analyze_introduction(
            introduction=introduction,
            role=role,
            company=company,
            yoe=yoe
        )
        return JSONResponse({"feedback": feedback, "input_type": "text"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/audio")
async def analyze_audio(
    audio: UploadFile = File(...),
    role: str = Form(...),
    company: str = Form(...),
    yoe: int = Form(...)
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
            company=company,
            yoe=yoe
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
