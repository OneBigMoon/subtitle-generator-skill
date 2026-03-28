FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir more-itertools tiktoken

RUN pip install --no-cache-dir --no-build-isolation openai-whisper==20240930

RUN pip install --no-cache-dir fastapi uvicorn python-multipart

COPY subtitle_generator.py .
COPY api_server.py .

RUN mkdir -p /app/input /app/output

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
