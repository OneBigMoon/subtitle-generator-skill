FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（ffmpeg 用于音频处理）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip 并安装必要的构建工具
RUN pip install --upgrade pip setuptools wheel

# 先安装 PyTorch（CPU 版本）
RUN pip install --no-cache-dir torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# 安装 whisper 依赖
RUN pip install --no-cache-dir more-itertools tiktoken

# 安装 openai-whisper
RUN pip install --no-cache-dir --no-build-isolation openai-whisper==20240930

# 复制应用代码
COPY subtitle_generator.py .

# 创建输入输出目录
RUN mkdir -p /app/input /app/output

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 默认命令
ENTRYPOINT ["python", "subtitle_generator.py"]
CMD ["--help"]
