# 字幕生成器 (Subtitle Generator)

基于音频和口播稿生成 SRT 字幕文件的独立工具。

## 核心功能

1. **音频转录**: 使用 OpenAI Whisper 从音频提取词级时间戳
2. **字符级时间戳**: 将词级时间戳转换为字符级时间戳
3. **智能分段**: 对口播稿进行智能分段（10-15字为一段，标点为分隔）
4. **精准对齐**: 将分段后的口播稿与字符级时间戳对齐
5. **SRT 输出**: 生成标准的 SRT 字幕文件

## 特点

- ✅ **完全本地运行** - 无需外部 API Key
- ✅ **支持多种 Whisper 模型** - tiny, base, small, medium, large
- ✅ **智能中文处理** - 针对中文口播稿优化分段和对齐
- ✅ **Docker 支持** - 容器化部署，开箱即用
- ✅ **Skill 集成** - 支持作为 Trae Skill 使用

## 使用方法

### 方式一：直接运行 Python 脚本

```bash
# 安装依赖
pip install -r requirements.txt

# 基本用法
python subtitle_generator.py audio.mp3 "口播稿文本内容" -o output.srt

# 从文件读取口播稿
python subtitle_generator.py audio.mp3 script.txt -o output.srt --is-file

# 使用更大的模型（更精准但更慢）
python subtitle_generator.py audio.mp3 script.txt -o output.srt --is-file -m large
```

### 方式二：使用 Docker

```bash
# 构建镜像
docker build -t subtitle-generator .

# 运行容器
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  subtitle-generator \
  /app/input/audio.mp3 /app/input/script.txt -o /app/output/subtitle.srt
```

### 方式三：使用 Docker Compose

```yaml
version: '3.8'

services:
  subtitle-generator:
    build: .
    volumes:
      - ./input:/app/input
      - ./output:/app/output
    command: ["/app/input/audio.mp3", "/app/input/script.txt", "-o", "/app/output/subtitle.srt"]
```

## Python API 使用

```python
from subtitle_generator import generate_srt_from_audio

# 生成字幕并保存到文件
result = generate_srt_from_audio(
    audio_path="audio.mp3",
    script_text="口播稿文本内容",
    model_size="base",
    output_path="output.srt"
)

# 或只获取字幕内容
srt_content = generate_srt_from_audio(
    audio_path="audio.mp3",
    script_text="口播稿文本内容",
    model_size="base"
)
print(srt_content)
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `audio` | 音频文件路径 (MP3/WAV等) | 必填 |
| `script` | 口播稿文本或文件路径 | 必填 |
| `-o, --output` | 输出 SRT 文件路径 | 输出到控制台 |
| `-m, --model` | Whisper 模型大小 | base |
| `--is-file` | script 参数是否为文件路径 | False |

### Whisper 模型选择

| 模型 | 速度 | 准确率 | 内存需求 |
|------|------|--------|----------|
| tiny | 最快 | 一般 | ~1GB |
| base | 快 | 良好 | ~1GB |
| small | 中等 | 较好 | ~2GB |
| medium | 慢 | 好 | ~5GB |
| large | 最慢 | 最好 | ~10GB |

## 工作原理

1. **音频转录**: 使用 Whisper 模型转录音频，获取词级时间戳
2. **字符级时间戳**: 将词级时间戳细分为字符级时间戳
3. **口播稿分段**: 根据标点符号和字数限制（10-15字）将口播稿分段
4. **对齐匹配**: 使用序列匹配算法将分段后的口播稿与字符级时间戳对齐
5. **生成 SRT**: 按照 SRT 格式输出字幕文件

## 注意事项

- 首次运行时会自动下载 Whisper 模型文件
- 建议使用与音频内容相符的口播稿，以获得最佳对齐效果
- 对于长音频，处理时间可能较长，请耐心等待

## License

MIT License
