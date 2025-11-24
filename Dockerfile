FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY interview_analyzer.py .
COPY example_usage.py .
COPY prompts.py .

CMD ["python", "interview_analyzer.py"]
