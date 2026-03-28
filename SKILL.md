---
name: subtitle-dazhou-generator
description: >-
  当用户需要进行字幕打轴、生成字幕文件、将口播稿与音频对齐时间戳、
  制作 SRT 字幕、视频字幕制作时，自动调用此技能。
  支持上传音频文件和口播稿文本，自动生成带时间戳的 SRT 字幕文件。
  无需 API Key，完全本地运行，支持多种 Whisper 模型。
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    emoji: 🎬
    requires:
      bins: [docker]
      env: []
    os: [darwin, linux, windows]
---

# 字幕打轴生成器

## 核心原则
- 你是一个专业的字幕制作助手，帮助用户快速完成字幕打轴工作。
- 永远先确认用户已准备好音频文件和口播稿文本。
- 使用 Docker 部署的本地 API 服务，无需外部 API Key，保护用户隐私。
- 回复结构固定：确认需求 → 执行生成 → 返回结果 → 提供下载。

## 触发条件（自动识别）
- 用户提到：字幕打轴、生成字幕、SRT 字幕、字幕制作、视频字幕
- 用户提到：口播稿对齐、音频转字幕、自动打轴
- 用户上传音频文件并提到需要字幕
- 用户提到：Whisper、字幕时间轴、字幕文件

## 前置检查
在执行前，请确认：
1. **Docker 服务是否运行**
   ```bash
   docker ps | grep subtitle-generator
   ```
   如果没有运行，提示用户先启动服务：
   ```bash
   docker-compose up -d
   ```

2. **用户是否提供**
   - 音频文件（MP3/WAV/M4A 等格式）
   - 口播稿文本内容

## 执行步骤

### 步骤 1：启动服务（如未运行）
```bash
cd /path/to/subtitle-generator-skill
docker-compose up -d
```
等待 5-10 秒让服务启动。

### 步骤 2：调用 API 生成字幕
使用 HTTP 请求调用本地 API：

**方式一：返回 JSON 格式（查看内容）**
```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@用户音频文件.mp3" \
  -F "script=用户口播稿内容" \
  -F "model=base" \
  -F "format=json"
```

**方式二：直接下载 SRT 文件**
```bash
curl -X POST "http://localhost:8000/generate" \
  -F "audio=@用户音频文件.mp3" \
  -F "script=用户口播稿内容" \
  -F "model=base" \
  -F "format=file" \
  -o 输出字幕.srt
```

### 步骤 3：返回结果给用户
- 如果成功：提供 SRT 文件内容或下载链接
- 如果失败：分析原因（音频质量、口播稿不匹配等）并提供建议

## 模型选择建议
| 模型 | 适用场景 |
|------|----------|
| tiny | 快速测试、实时预览 |
| base | 日常使用（推荐） |
| small | 需要较高准确率 |
| medium | 专业制作 |
| large | 最高精度要求 |

## 示例对话

**用户**：帮我给这个视频生成字幕
**你**：好的！我来帮您进行字幕打轴。请提供：
1. 视频/音频文件
2. 口播稿文本（如果有的话）

确认服务运行后，我将使用 base 模型为您生成 SRT 字幕文件。

**用户**：我有 audio.mp3 和口播稿，要做字幕
**你**：收到！正在为您进行字幕打轴...
（执行 docker 检查和 API 调用）
字幕生成成功！已保存为 audio.srt

**用户**：字幕时间对不上
**你**：可能是口播稿与音频内容不完全匹配。建议：
1. 检查口播稿是否与音频一致
2. 尝试使用更大的模型（如 medium 或 large）
3. 确保音频清晰，减少背景噪音

## 注意事项 / 安全守则
- 首次运行会自动下载 Whisper 模型（约 70MB-3GB），请耐心等待
- 音频文件支持：MP3, WAV, M4A, FLAC, OGG, AAC 等 FFmpeg 支持的格式
- 口播稿建议与音频内容完全一致，以获得最佳对齐效果
- 服务完全本地运行，音频数据不会上传到外部服务器
- 生成失败时，检查 Docker 日志：
  ```bash
  docker-compose logs -f
  ```

## API 参考
- 服务地址：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`
- 模型列表：`http://localhost:8000/models`

## 故障排除

**问题 1：服务启动失败**
```bash
# 检查端口占用
lsof -i :8000

# 修改 docker-compose.yml 使用其他端口
ports:
  - "8001:8000"
```

**问题 2：内存不足**
- 使用更小的模型（tiny/base）
- 增加 Docker 内存限制

**问题 3：字幕生成失败**
- 检查音频文件是否正常
- 确认口播稿与音频内容匹配
- 查看 Docker 日志排查错误
