#!/usr/bin/env python3
"""
字幕打轴 / 字幕生成器 API 服务 - 基于 FastAPI

提供 REST API 接口，支持：
- 音频文件上传
- 口播稿文本提交
- 字幕打轴（自动对齐时间戳）
- SRT 字幕生成
- 多种 Whisper 模型选择
- 可选返回 JSON 或文件下载
"""

import os
import tempfile
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse, Response
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
    audio: UploadFile = File(..., description="音频文件 (MP3/WAV等)"),
    script: str = Form(..., description="口播稿文本"),
    model: str = Form(default="base", description="Whisper 模型 (tiny/base/small/medium/large)"),
    format: str = Form(default="json", description="返回格式: json(返回JSON) 或 file(下载SRT文件)")
):
    """
    生成字幕接口
    
    - **audio**: 音频文件 (MP3, WAV 等格式)
    - **script**: 口播稿文本内容
    - **model**: Whisper 模型大小，可选 tiny/base/small/medium/large，默认 base
    - **format**: 返回格式
        - `json`: 返回 JSON 格式响应（包含 srt_content 字段）
        - `file`: 直接返回 SRT 文件下载
    """
    valid_models = ["tiny", "base", "small", "medium", "large"]
    if model not in valid_models:
        raise HTTPException(
            status_code=400,
            detail=f"无效的模型参数，可选值: {', '.join(valid_models)}"
        )
    
    valid_formats = ["json", "file"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"无效的格式参数，可选值: {', '.join(valid_formats)}"
        )
    
    if not script or not script.strip():
        raise HTTPException(status_code=400, detail="口播稿文本不能为空")
    
    temp_audio_path = None
    try:
        file_ext = os.path.splitext(audio.filename)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        srt_content = generate_srt_from_audio(
            audio_path=temp_audio_path,
            script_text=script,
            model_size=model,
            output_path=None
        )
        
        if not srt_content:
            if format == "json":
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": False,
                        "message": "字幕生成失败，请检查音频文件和口播稿是否匹配",
                        "srt_content": None
                    }
                )
            else:
                raise HTTPException(
                    status_code=422,
                    detail="字幕生成失败，请检查音频文件和口播稿是否匹配"
                )
        
        if format == "json":
            return SubtitleResponse(
                success=True,
                message="字幕生成成功",
                srt_content=srt_content
            )
        else:
            audio_basename = os.path.splitext(audio.filename)[0] if audio.filename else "subtitle"
            filename = f"{audio_basename}.srt"
            return Response(
                content=srt_content.encode('utf-8'),
                media_type="application/x-subrip",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
    finally:
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
