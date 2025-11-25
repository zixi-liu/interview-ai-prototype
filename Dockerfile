FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY interview_analyzer.py .
COPY prompts.py .
COPY static/ ./static/

CMD ["python", "app.py"]
