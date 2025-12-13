FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY utils.py .
COPY interview_analyzer.py .
COPY prompts.py .
# Only copy necessary policy files (not training data)
COPY policy/__init__.py ./policy/
COPY policy/stop_policy.py ./policy/
COPY policy/stop_policy_model.pkl ./policy/
COPY static/ ./static/
COPY templates/ ./templates/

CMD ["python", "app.py"]
