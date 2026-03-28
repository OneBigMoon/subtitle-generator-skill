# 字幕生成器 / 字幕打轴工具 (Subtitle Generator)

基于音频和口播稿进行**字幕打轴**，生成带时间戳的 SRT 字幕文件的 API 服务。

## 核心功能

1. **音频转录**: 使用 OpenAI Whisper 从音频提取词级时间戳
2. **字符级时间戳**: 将词级时间戳转换为字符级时间戳
3. **智能分段**: 对口播稿进行智能分段（10-15字为一段，标点为分隔）
4. **精准对齐**: 将分段后的口播稿与字符级时间戳对齐
5. **SRT 输出**: 生成标准的 SRT 字幕文件

## 特点

- ✅ **REST API 服务** - 标准 HTTP 接口，易于集成
- ✅ **完全本地运行** - 无需外部 API Key
- ✅ **支持多种 Whisper 模型** - tiny, base, small, medium, large
- ✅ **智能中文处理** - 针对中文口播稿优化分段和对齐
- ✅ **Docker 支持** - 容器化部署，开箱即用
- ✅ **Skill 集成** - 支持作为 Trae Skill 使用

---

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 使用 Docker Compose 一键启动
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

服务启动后访问：
- API 服务: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 方式二：本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 API 服务
python api_server.py

# 或使用 uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

---

## API 接口文档

### 生成字幕

**POST** `/generate`

**请求方式**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| audio | file | ✅ | 音频文件 (MP3/WAV等) |
| script | string | ✅ | 口播稿文本内容 |
| model | string | ❌ | Whisper 模型 (tiny/base/small/medium/large)，默认 base |
| format | string | ❌ | 返回格式：`json`(返回JSON) 或 `file`(下载SRT文件)，默认 json |

#### 示例 1：返回 JSON 格式

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@audio.mp3" \
  -F "script=大家好，欢迎来到我的频道。" \
  -F "model=base" \
  -F "format=json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "字幕生成成功",
  "srt_content": "1\n00:00:00,000 --> 00:00:02,500\n大家好，\n\n2\n00:00:02,500 --> 00:00:05,000\n欢迎来到我的频道。\n\n"
}
```

#### 示例 2：直接下载 SRT 文件

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@audio.mp3" \
  -F "script=大家好，欢迎来到我的频道。" \
  -F "format=file" \
  -o audio.srt
```

**响应**: 直接返回 SRT 文件下载，文件名为 `{音频文件名}.srt`

### 3. 获取支持的模型列表

**GET** `/models`

**响应示例**:
```json
{
  "models": [
    {"name": "tiny", "description": "最快，准确率一般", "memory": "~1GB"},
    {"name": "base", "description": "快速，准确率良好", "memory": "~1GB"},
    {"name": "small", "description": "中等速度，准确率较好", "memory": "~2GB"},
    {"name": "medium", "description": "较慢，准确率好", "memory": "~5GB"},
    {"name": "large", "description": "最慢，准确率最好", "memory": "~10GB"}
  ],
  "default": "base"
}
```

### 4. 健康检查

**GET** `/health`

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Python 调用示例

### 返回 JSON 格式

```python
import requests

url = "http://localhost:8000/generate"

with open("audio.mp3", "rb") as audio_file:
    files = {"audio": audio_file}
    data = {
        "script": "大家好，欢迎来到我的频道。",
        "model": "base",
        "format": "json"
    }
    response = requests.post(url, files=files, data=data)

result = response.json()
if result["success"]:
    print(result["srt_content"])
else:
    print(f"错误: {result['message']}")
```

### 直接下载文件

```python
import requests

url = "http://localhost:8000/generate"

with open("audio.mp3", "rb") as audio_file:
    files = {"audio": audio_file}
    data = {
        "script": "大家好，欢迎来到我的频道。",
        "model": "base",
        "format": "file"
    }
    response = requests.post(url, files=files, data=data)

with open("output.srt", "wb") as f:
    f.write(response.content)
print("字幕已保存到 output.srt")
```

---

## 目录结构

```
subtitle-generator-skill/
├── api_server.py          # API 服务入口
├── subtitle_generator.py  # 字幕生成核心逻辑
├── Dockerfile             # Docker 镜像构建文件
├── docker-compose.yml     # Docker Compose 配置
├── requirements.txt       # Python 依赖
├── skill.json             # Skill 配置文件
├── example_script.txt     # 示例口播稿
├── input/                 # 输入文件目录（可选）
│   ├── audio.mp3          # 音频文件
│   └── script.txt         # 口播稿文件
└── output/                # 输出文件目录（可选）
    └── subtitle.srt       # 生成的字幕文件
```

### 目录说明

| 目录 | 说明 | 使用场景 |
|------|------|----------|
| `input/` | 输入文件存放目录 | 可选，用于存放音频和口播稿文件，方便 Docker 挂载使用 |
| `output/` | 输出文件存放目录 | 可选，用于存放生成的字幕文件 |

> **注意**: 通过 API 上传的文件会自动处理，无需放入 input 目录。input/output 目录主要用于批量处理或文件持久化场景。

---

## Whisper 模型选择

| 模型 | 速度 | 准确率 | 内存需求 | 适用场景 |
|------|------|--------|----------|----------|
| tiny | 最快 | 一般 | ~1GB | 快速预览、实时字幕 |
| base | 快 | 良好 | ~1GB | 日常使用（推荐） |
| small | 中等 | 较好 | ~2GB | 需要较高准确率 |
| medium | 慢 | 好 | ~5GB | 专业字幕制作 |
| large | 最慢 | 最好 | ~10GB | 最高精度要求 |

---

## 常见问题 (FAQ)

### 1. 首次运行很慢？

**原因**: 首次运行时会自动下载 Whisper 模型文件（约 70MB - 3GB，取决于模型大小）。

**解决**: 耐心等待下载完成，模型会缓存到本地，后续运行会很快。

### 2. 内存不足错误？

**原因**: Whisper 模型需要较多内存，尤其是 large 模型。

**解决**: 
- 使用更小的模型（如 base 或 small）
- 增加系统内存或 Docker 内存限制

### 3. 字幕时间对不上？

**原因**: 口播稿与音频内容不匹配，或音频质量较差。

**解决**:
- 确保口播稿与音频内容一致
- 使用更大的 Whisper 模型
- 提高音频质量（减少背景噪音）

### 4. 中文识别效果差？

**原因**: Whisper 对中文的识别依赖模型大小。

**解决**:
- 使用 medium 或 large 模型
- 确保音频清晰，语速适中

### 5. Docker 容器启动失败？

**原因**: 可能是端口被占用或内存不足。

**解决**:
```bash
# 检查端口占用
lsof -i :8000

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 改为其他端口
```

### 6. 如何查看 API 文档？

启动服务后访问 http://localhost:8000/docs 查看交互式 API 文档（Swagger UI）。

### 7. 支持哪些音频格式？

支持所有 FFmpeg 支持的格式，包括：
- MP3, WAV, M4A, FLAC, OGG, AAC 等

---

## 工作原理

1. **音频转录**: 使用 Whisper 模型转录音频，获取词级时间戳
2. **字符级时间戳**: 将词级时间戳细分为字符级时间戳
3. **口播稿分段**: 根据标点符号和字数限制（10-15字）将口播稿分段
4. **对齐匹配**: 使用序列匹配算法将分段后的口播稿与字符级时间戳对齐
5. **生成 SRT**: 按照 SRT 格式输出字幕文件

---

## License

MIT License
