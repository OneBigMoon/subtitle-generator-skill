#!/usr/bin/env python3
"""
字幕打轴 / 字幕生成器 API 服务 - 基于 FastAPI

提供 REST API 接口，支持：
- 音频文件上传
- 口播稿文件或文本上传
- 字幕打轴（自动对齐时间戳）
- SRT 字幕生成
- 多种 Whisper 模型选择
- 灵活选择返回格式：JSON 内容 / 文件下载 / 保存到指定路径
"""

import os
import tempfile
import shutil
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, Response, FileResponse
from pydantic import BaseModel

from subtitle_generator import generate_srt_from_audio

app = FastAPI(
    title="字幕打轴 / 字幕生成器 API",
    description="基于音频和口播稿进行字幕打轴，生成带时间戳的 SRT 字幕文件",
    version="1.0.0"
)


class SubtitleResponse(BaseModel):
    """字幕生成响应模型"""
    success: bool
    message: str
    srt_content: Optional[str] = None
    output_path: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    version: str


class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    description: str
    memory: str


class ModelsResponse(BaseModel):
    """模型列表响应"""
    models: list[ModelInfo]
    default: str


@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 服务状态"""
    return HealthResponse(status="running", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/generate")
async def generate_subtitle(
    audio: UploadFile = File(..., description="音频文件 (MP3/WAV/M4A等)"),
    script: Optional[str] = Form(default=None, description="口播稿文本内容（与 script_file 二选一）"),
    script_file: Optional[UploadFile] = File(default=None, description="口播稿文件（txt格式，与 script 二选一）"),
    model: str = Form(default="base", description="Whisper 模型 (tiny/base/small/medium/large)"),
    output_format: str = Form(default="json", description="返回格式: json / file / path"),
    output_path: Optional[str] = Form(default=None, description="当 output_format=path 时，指定输出文件路径")
):
    """
    生成字幕接口
    
    **参数说明：**
    - **audio**: 音频文件 (MP3, WAV, M4A, FLAC, OGG, AAC 等格式)
    - **script**: 口播稿文本内容（直接输入文本）
    - **script_file**: 口播稿文件（.txt 格式，与 script 二选一）
    - **model**: Whisper 模型大小，可选 tiny/base/small/medium/large，默认 base
    - **output_format**: 返回格式
        - `json`: 返回 JSON 格式响应（包含 srt_content 字段）
        - `file`: 直接返回 SRT 文件下载
        - `path`: 保存到指定路径，返回文件路径
    - **output_path**: 当 output_format=path 时，指定输出文件路径（如 /app/output/subtitle.srt）
    
    **使用示例：**
    
    1. **上传音频 + 口播稿文本，返回 JSON：**
    ```bash
    curl -X POST "http://localhost:8000/generate" \
      -F "audio=@audio.mp3" \
      -F "script=大家好，欢迎来到我的频道。" \
      -F "output_format=json"
    ```
    
    2. **上传音频 + 口播稿文件，返回 JSON：**
    ```bash
    curl -X POST "http://localhost:8000/generate" \
      -F "audio=@audio.mp3" \
      -F "script_file=@script.txt" \
      -F "output_format=json"
    ```
    
    3. **上传音频 + 口播稿，直接下载文件：**
    ```bash
    curl -X POST "http://localhost:8000/generate" \
      -F "audio=@audio.mp3" \
      -F "script_file=@script.txt" \
      -F "output_format=file" \
      -o output.srt
    ```
    
    4. **上传音频 + 口播稿，保存到指定路径：**
    ```bash
    curl -X POST "http://localhost:8000/generate" \
      -F "audio=@audio.mp3" \
      -F "script_file=@script.txt" \
      -F "output_format=path" \
      -F "output_path=/app/output/my_subtitle.srt"
    ```
    """
    # 验证模型参数
    valid_models = ["tiny", "base", "small", "medium", "large"]
    if model not in valid_models:
        raise HTTPException(
            status_code=400,
            detail=f"无效的模型参数，可选值: {', '.join(valid_models)}"
        )
    
    # 验证输出格式参数
    valid_formats = ["json", "file", "path"]
    if output_format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"无效的格式参数，可选值: {', '.join(valid_formats)}"
        )
    
    # 验证必须提供口播稿（文本或文件二选一）
    if not script and not script_file:
        raise HTTPException(
            status_code=400, 
            detail="必须提供口播稿：使用 script 参数上传文本，或使用 script_file 参数上传文件"
        )
    
    # 如果 output_format=path，必须提供 output_path
    if output_format == "path" and not output_path:
        raise HTTPException(
            status_code=400,
            detail="当 output_format=path 时，必须提供 output_path 参数指定输出文件路径"
        )
    
    temp_audio_path = None
    temp_script_path = None
    
    try:
        # 保存音频文件到临时位置
        audio_ext = os.path.splitext(audio.filename)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=audio_ext) as temp_audio:
            audio_content = await audio.read()
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name
        
        # 获取口播稿内容
        script_text = None
        if script:
            # 直接使用提供的文本
            script_text = script
        elif script_file:
            # 从口播稿文件读取
            script_content = await script_file.read()
            try:
                script_text = script_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    script_text = script_content.decode('gbk')
                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="口播稿文件编码错误，请使用 UTF-8 或 GBK 编码的文本文件"
                    )
        
        if not script_text or not script_text.strip():
            raise HTTPException(status_code=400, detail="口播稿内容不能为空")
        
        # 生成字幕
        srt_content = generate_srt_from_audio(
            audio_path=temp_audio_path,
            script_text=script_text,
            model_size=model,
            output_path=None
        )
        
        if not srt_content:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "字幕生成失败，请检查音频文件和口播稿是否匹配",
                    "srt_content": None,
                    "output_path": None
                }
            )
        
        # 根据 output_format 返回不同格式
        if output_format == "json":
            # 返回 JSON 格式
            return SubtitleResponse(
                success=True,
                message="字幕生成成功",
                srt_content=srt_content,
                output_path=None
            )
        
        elif output_format == "file":
            # 直接返回文件下载
            audio_basename = os.path.splitext(audio.filename)[0] if audio.filename else "subtitle"
            filename = f"{audio_basename}.srt"
            return Response(
                content=srt_content.encode('utf-8'),
                media_type="application/x-subrip",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        
        elif output_format == "path":
            # 保存到指定路径
            try:
                # 确保目标目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                # 写入文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                
                return SubtitleResponse(
                    success=True,
                    message=f"字幕已保存到: {output_path}",
                    srt_content=None,
                    output_path=output_path
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"保存文件失败: {str(e)}"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    """获取支持的模型列表"""
    return ModelsResponse(
        models=[
            ModelInfo(name="tiny", description="最快，准确率一般", memory="~1GB"),
            ModelInfo(name="base", description="快速，准确率良好", memory="~1GB"),
            ModelInfo(name="small", description="中等速度，准确率较好", memory="~2GB"),
            ModelInfo(name="medium", description="较慢，准确率好", memory="~5GB"),
            ModelInfo(name="large", description="最慢，准确率最好", memory="~10GB")
        ],
        default="base"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
