# 🎬 字幕生成器 / 字幕打轴工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://github.com/OpenClaw)

> 🎯 **基于音频和口播稿进行字幕打轴，生成带时间戳的 SRT 字幕文件**

[English](README_EN.md) | [中文](#)

---

## ✨ 功能特性

- 🎙️ **音频转录** - 使用 OpenAI Whisper 从音频提取词级时间戳
- ⏱️ **字符级时间戳** - 将词级时间戳转换为字符级时间戳
- 📝 **智能分段** - 对口播稿进行智能分段（10-15字为一段，标点为分隔）
- 🎯 **精准对齐** - 将分段后的口播稿与字符级时间戳对齐
- 📄 **SRT 输出** - 生成标准的 SRT 字幕文件

### 🚀 特点

- ✅ **REST API 服务** - 标准 HTTP 接口，易于集成
- ✅ **完全本地运行** - 无需外部 API Key，保护隐私
- ✅ **支持多种 Whisper 模型** - tiny, base, small, medium, large
- ✅ **智能中文处理** - 针对中文口播稿优化分段和对齐
- ✅ **Docker 支持** - 容器化部署，开箱即用
- ✅ **OpenClaw Skill** - 支持作为龙虾智能体技能使用
- ✅ **双格式输出** - JSON 响应或直接下载 SRT 文件

---

## 📖 目录

- [快速开始](#-快速开始)
- [安装部署](#-安装部署)
- [API 文档](#-api-文档)
- [使用示例](#-使用示例)
- [系统架构](#-系统架构)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [更新日志](CHANGELOG.md)

---

## 🚀 快速开始

### 方式一：Docker Hub 一键部署（最简单，推荐）

无需克隆仓库，直接使用预构建的多平台镜像：

```bash
# 创建 docker-compose.yml 文件
curl -o docker-compose.yml https://raw.githubusercontent.com/OneBigMoon/subtitle-generator-skill/main/docker-compose.yml

# 创建输入输出目录
mkdir -p input output

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

或者使用纯 Docker 命令：

```bash
# 创建目录
mkdir -p subtitle-generator/input subtitle-generator/output
cd subtitle-generator

# 直接运行容器（无需 docker-compose）
docker run -d \
  --name subtitle-generator \
  -p 8000:8000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --restart unless-stopped \
  onebigmoon/subtitle-generator:latest
```

**支持的架构**: `linux/amd64` (x86_64), `linux/arm64` (ARM64/Apple Silicon)

服务启动后访问：
- 🌐 API 服务: http://localhost:8000
- 📚 API 文档: http://localhost:8000/docs
- 🏥 健康检查: http://localhost:8000/health

### 方式二：Docker 本地构建部署

```bash
# 克隆仓库
git clone https://github.com/OneBigMoon/subtitle-generator-skill.git
cd subtitle-generator-skill

# 使用 Docker Compose 一键启动
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 方式三：本地运行

```bash
# 克隆仓库
git clone https://github.com/OneBigMoon/subtitle-generator-skill.git
cd subtitle-generator-skill

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动 API 服务
python api_server.py

# 或使用 uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### 方式四：OpenClaw (龙虾) Skill 安装

```bash
# 克隆到 OpenClaw skills 目录
git clone https://github.com/OneBigMoon/subtitle-generator-skill.git \
  ~/.openclaw/skills/subtitle-dazhou-generator

# 重启 OpenClaw 或刷新技能
reload skills
```

---

## 📦 安装部署

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核以上 |
| 内存 | 2GB | 4GB 以上 |
| 磁盘 | 5GB | 10GB 以上 |
| Docker | 20.10+ | 最新版 |

### Docker Compose 配置说明

`docker-compose.yml` 提供了丰富的配置选项，您可以根据需要调整：

#### 1. 端口映射（常用）

```yaml
ports:
  - "8000:8000"    # 默认端口
  # - "8080:8000"  # 如果 8000 被占用，改为 8080
  # - "3000:8000"  # 或其他任意端口
```

#### 2. 镜像来源

```yaml
# 选项1: 使用 Docker Hub 预构建镜像（推荐，支持多平台）
image: onebigmoon/subtitle-generator:latest

# 选项2: 本地构建（适合二次开发）
# build: .
# image: subtitle-generator:latest
```

#### 3. 内存限制（根据模型选择）

```yaml
deploy:
  resources:
    limits:
      memory: 4G    # 限制最大内存
    reservations:
      memory: 2G    # 预留内存
```

**内存配置建议：**
| 模型 | 建议内存限制 |
|------|-------------|
| tiny/base | 2GB |
| small | 4GB |
| medium | 8GB |
| large | 12GB+ |

#### 4. 环境变量

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - TZ=Asia/Shanghai              # 设置时区
  - HF_ENDPOINT=https://hf-mirror.com  # 国内镜像加速
```

#### 5. 数据卷挂载

```yaml
volumes:
  - ./input:/app/input      # 音频文件输入目录
  - ./output:/app/output    # 字幕文件输出目录
```

### Docker 命令行部署

```bash
# 使用 Docker Hub 镜像（无需构建）
docker run -d \
  --name subtitle-generator \
  -p 8000:8000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --restart unless-stopped \
  onebigmoon/subtitle-generator:latest

# 查看日志
docker logs -f subtitle-generator

# 停止服务
docker stop subtitle-generator

# 删除容器
docker rm subtitle-generator
```

### 本地构建部署

```bash
# 克隆仓库后构建
docker build -t subtitle-generator:latest .

# 运行本地构建的镜像
docker run -d \
  --name subtitle-generator \
  -p 8000:8000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --restart unless-stopped \
  subtitle-generator:latest
```

---

## 📡 API 文档

### 端点概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/health` | GET | 健康检查 |
| `/generate` | POST | 生成字幕 |
| `/models` | GET | 获取支持的模型列表 |
| `/docs` | GET | Swagger API 文档 |

### 生成字幕

**POST** `/generate`

**请求方式**: `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| audio | file | ✅ | 音频文件 (MP3/WAV/M4A/FLAC/OGG/AAC等) |
| script | string | 条件 | 口播稿文本内容（与 script_file 二选一） |
| script_file | file | 条件 | 口播稿文件 .txt（与 script 二选一） |
| model | string | ❌ | Whisper 模型，默认 base |
| output_format | string | ❌ | 返回格式：`json` / `file` / `path`，默认 json |
| output_path | string | 条件 | 当 output_format=path 时必填，指定输出路径 |

#### 示例 1：音频 + 口播稿文本，返回 JSON

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@audio.mp3" \
  -F "script=大家好，欢迎来到我的频道。今天我们要讲的是..." \
  -F "model=base" \
  -F "output_format=json"
```

**响应示例**:
```json
{
  "success": true,
  "message": "字幕生成成功",
  "srt_content": "1\n00:00:00,000 --> 00:00:02,500\n大家好，\n\n2\n00:00:02,500 --> 00:00:05,000\n欢迎来到我的频道。\n\n...",
  "output_path": null
}
```

#### 示例 2：音频 + 口播稿文件，返回 JSON

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@audio.mp3" \
  -F "script_file=@script.txt" \
  -F "model=base" \
  -F "output_format=json"
```

#### 示例 3：直接下载 SRT 文件

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@audio.mp3" \
  -F "script_file=@script.txt" \
  -F "output_format=file" \
  -o output.srt
```

#### 示例 4：保存到指定路径（服务器端）

```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@audio.mp3" \
  -F "script_file=@script.txt" \
  -F "output_format=path" \
  -F "output_path=/app/output/my_subtitle.srt"
```

**响应示例**:
```json
{
  "success": true,
  "message": "字幕已保存到: /app/output/my_subtitle.srt",
  "srt_content": null,
  "output_path": "/app/output/my_subtitle.srt"
}
```

### 获取支持的模型列表

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

### 健康检查

**GET** `/health`

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 💡 使用示例

### Python 调用

#### 方式 1：音频 + 口播稿文本，返回 JSON

```python
import requests

url = "http://localhost:8000/generate"

with open("audio.mp3", "rb") as audio_file:
    files = {"audio": audio_file}
    data = {
        "script": "大家好，欢迎来到我的频道。今天我们要讲的是字幕打轴技术...",
        "model": "base",
        "output_format": "json"
    }
    response = requests.post(url, files=files, data=data)

result = response.json()
if result["success"]:
    print("✅ 字幕生成成功！")
    print(result["srt_content"])
    # 保存到文件
    with open("output.srt", "w", encoding="utf-8") as f:
        f.write(result["srt_content"])
else:
    print(f"❌ 错误: {result['message']}")
```

#### 方式 2：音频 + 口播稿文件，返回 JSON

```python
import requests

url = "http://localhost:8000/generate"

with open("audio.mp3", "rb") as audio_file, \
     open("script.txt", "rb") as script_file:
    files = {
        "audio": audio_file,
        "script_file": script_file
    }
    data = {
        "model": "base",
        "output_format": "json"
    }
    response = requests.post(url, files=files, data=data)

result = response.json()
if result["success"]:
    print("✅ 字幕生成成功！")
    with open("output.srt", "w", encoding="utf-8") as f:
        f.write(result["srt_content"])
```

#### 方式 3：直接下载 SRT 文件

```python
import requests

url = "http://localhost:8000/generate"

with open("audio.mp3", "rb") as audio_file, \
     open("script.txt", "rb") as script_file:
    files = {
        "audio": audio_file,
        "script_file": script_file
    }
    data = {
        "model": "base",
        "output_format": "file"
    }
    response = requests.post(url, files=files, data=data)

# 直接保存下载的文件
with open("output.srt", "wb") as f:
    f.write(response.content)
print("✅ 字幕已保存到 output.srt")
```

#### 方式 4：保存到服务器指定路径

```python
import requests

url = "http://localhost:8000/generate"

with open("audio.mp3", "rb") as audio_file, \
     open("script.txt", "rb") as script_file:
    files = {
        "audio": audio_file,
        "script_file": script_file
    }
    data = {
        "model": "base",
        "output_format": "path",
        "output_path": "/app/output/my_video_subtitle.srt"
    }
    response = requests.post(url, files=files, data=data)

result = response.json()
if result["success"]:
    print(f"✅ 字幕已保存到: {result['output_path']}")
else:
    print(f"❌ 错误: {result['message']}")
```

### JavaScript/Node.js 调用

#### 方式 1：音频 + 口播稿文本，返回 JSON

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('audio', fs.createReadStream('audio.mp3'));
form.append('script', '大家好，欢迎来到我的频道。今天我们要讲的是字幕打轴技术...');
form.append('model', 'base');
form.append('output_format', 'json');

axios.post('http://localhost:8000/generate', form, {
  headers: form.getHeaders()
}).then(response => {
  const result = response.data;
  if (result.success) {
    console.log('✅ 字幕生成成功！');
    fs.writeFileSync('output.srt', result.srt_content, 'utf-8');
  } else {
    console.error('❌ 错误:', result.message);
  }
}).catch(error => {
  console.error('❌ 请求失败:', error.message);
});
```

#### 方式 2：音频 + 口播稿文件，直接下载

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('audio', fs.createReadStream('audio.mp3'));
form.append('script_file', fs.createReadStream('script.txt'));
form.append('model', 'base');
form.append('output_format', 'file');

axios.post('http://localhost:8000/generate', form, {
  headers: form.getHeaders(),
  responseType: 'stream'
}).then(response => {
  const writer = fs.createWriteStream('output.srt');
  response.data.pipe(writer);
  writer.on('finish', () => {
    console.log('✅ 字幕已保存到 output.srt');
  });
}).catch(error => {
  console.error('❌ 错误:', error.message);
});
```

#### 方式 3：保存到服务器指定路径

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('audio', fs.createReadStream('audio.mp3'));
form.append('script_file', fs.createReadStream('script.txt'));
form.append('model', 'base');
form.append('output_format', 'path');
form.append('output_path', '/app/output/my_video_subtitle.srt');

axios.post('http://localhost:8000/generate', form, {
  headers: form.getHeaders()
}).then(response => {
  const result = response.data;
  if (result.success) {
    console.log('✅ 字幕已保存到:', result.output_path);
  } else {
    console.error('❌ 错误:', result.message);
  }
}).catch(error => {
  console.error('❌ 请求失败:', error.message);
});
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Web UI    │  │   API 调用   │  │   OpenClaw Skill   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI 服务层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  /generate  │  │   /models   │  │      /health        │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
└─────────┼────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────┐
│                   字幕生成核心逻辑                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 音频转录    │  │ 口播稿分段   │  │   时间戳对齐        │  │
│  │ (Whisper)   │  │ (智能分段)   │  │   (SequenceMatcher) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 工作流程

1. **📤 接收请求** - FastAPI 接收音频文件和口播稿
2. **🎙️ 音频转录** - Whisper 模型提取词级时间戳
3. **⏱️ 字符级时间戳** - 将词级时间戳细分为字符级
4. **📝 口播稿分段** - 根据标点和字数限制智能分段
5. **🎯 对齐匹配** - 使用序列匹配算法对齐文本和时间戳
6. **📄 生成 SRT** - 输出标准 SRT 格式字幕文件

---

## 🎛️ Whisper 模型选择

| 模型 | 速度 | 准确率 | 内存需求 | 适用场景 |
|------|------|--------|----------|----------|
| tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | 快速测试、实时预览 |
| base | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1GB | 日常使用（推荐） |
| small | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2GB | 需要较高准确率 |
| medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | 专业字幕制作 |
| large | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | 最高精度要求 |

---

## 📁 目录结构

```
subtitle-generator-skill/
├── 📄 api_server.py              # API 服务入口 (FastAPI)
├── 📄 subtitle_generator.py      # 字幕生成核心逻辑
├── 📄 Dockerfile                 # Docker 镜像构建
├── 📄 docker-compose.yml         # Docker Compose 配置
├── 📄 requirements.txt           # Python 依赖
├── 📄 skill.json                 # Trae Skill 配置
├── 📄 SKILL.md                   # OpenClaw Skill 配置
├── 📄 example_script.txt         # 示例口播稿
├── 📄 LICENSE                    # MIT 许可证
├── 📄 CHANGELOG.md               # 更新日志
├── 📄 CONTRIBUTING.md            # 贡献指南
├── 📁 input/                     # 输入文件目录（可选）
│   └── .gitkeep
└── 📁 output/                    # 输出文件目录（可选）
    └── .gitkeep
```

---

## ❓ 常见问题

### 1. 首次运行很慢？

**原因**: 首次运行时会自动下载 Whisper 模型文件（约 70MB - 3GB）。

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

### 6. 支持哪些音频格式？

支持所有 FFmpeg 支持的格式：
- MP3, WAV, M4A, FLAC, OGG, AAC, WMA, OPUS 等

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 快速开始

```bash
# Fork 并克隆仓库
git clone https://github.com/您的用户名/subtitle-generator-skill.git
cd subtitle-generator-skill

# 创建分支
git checkout -b feature/您的功能

# 提交更改
git commit -m "feat: 添加新功能"

# 推送并创建 PR
git push origin feature/您的功能
```

---

## 📜 许可证

[MIT License](LICENSE) © 2025 onebigmoon

---

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [OpenClaw](https://github.com/OpenClaw) - 开源 AI 智能体平台

---

## 📮 联系我们

- 📧 问题反馈: [GitHub Issues](https://github.com/OneBigMoon/subtitle-generator-skill/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/OneBigMoon/subtitle-generator-skill/discussions)
- ⭐ 如果这个项目对您有帮助，请给我们一个 Star！

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/OneBigMoon">onebigmoon</a>
</p>
