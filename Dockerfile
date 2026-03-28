FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖和构建工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    curl \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip setuptools wheel

# 安装 PyTorch (CPU 版本)
RUN pip install --no-cache-dir torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# 安装 whisper 依赖
RUN pip install --no-cache-dir more-itertools tiktoken

# 从 GitHub 安装 openai-whisper (避免构建问题)
RUN pip install --no-cache-dir git+https://github.com/openai/whisper.git@v20240930

# 安装 API 依赖
RUN pip install --no-cache-dir fastapi uvicorn python-multipart pydantic

# 复制应用代码
COPY subtitle_generator.py .
COPY api_server.py .

# 创建输入输出目录
RUN mkdir -p /app/input /app/output

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
