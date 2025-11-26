FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY interview_analyzer.py .
COPY prompts.py .
COPY static/ ./static/
COPY templates/ ./templates/

CMD ["python", "app.py"]
