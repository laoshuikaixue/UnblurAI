from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from app.models.models import UploadResponse
from app.services.zhipuai_service import ZhipuAIService
import time
import logging
import json
from typing import Optional, AsyncGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化ZhipuAI服务
zhipuai_service = ZhipuAIService()

async def stream_recognition_progress(
    file_content: bytes,
    custom_prompt: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """流式返回识别进度"""
    try:
        # 发送开始信号
        yield f"data: {json.dumps({'type': 'start', 'message': '开始处理图片...'}, ensure_ascii=False)}\n\n"
        
        # 验证文件
        yield f"data: {json.dumps({'type': 'progress', 'message': '验证图片格式和大小...'}, ensure_ascii=False)}\n\n"
        if not zhipuai_service.validate_image(file_content):
            yield f"data: {json.dumps({'type': 'error', 'message': '图片格式或大小不符合要求'}, ensure_ascii=False)}\n\n"
            return
        
        # 转换base64
        yield f"data: {json.dumps({'type': 'progress', 'message': '准备图片数据...'}, ensure_ascii=False)}\n\n"
        
        # 调用API
        yield f"data: {json.dumps({'type': 'progress', 'message': '正在调用GLM-4.5V进行文字识别...'}, ensure_ascii=False)}\n\n"
        
        start_time = time.time()
        recognized_text = await zhipuai_service.recognize_text(
            image_bytes=file_content,
            custom_prompt=custom_prompt
        )
        processing_time = time.time() - start_time
        
        # 发送成功结果
        result = {
            'type': 'success',
            'message': '识别完成',
            'data': {
                'recognized_text': recognized_text,
                'processing_time': round(processing_time, 2)
            }
        }
        yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
        
        # 发送结束信号
        yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        logger.error(f"Stream recognition failed: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'识别失败: {str(e)}'}, ensure_ascii=False)}\n\n"

@router.post("/upload-stream")
async def upload_and_recognize_stream(
    file: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None)
):
    """流式上传图片并识别文字"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图片文件")
        
        # 验证文件格式
        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
        if file.content_type not in allowed_formats:
            raise HTTPException(status_code=400, detail="只支持 JPG、JPEG、PNG 格式的图片")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 验证文件大小 (5MB)
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")
        
        logger.info(f"开始流式识别，文件大小: {len(file_content)} bytes")
        
        # 返回流式响应
        return StreamingResponse(
            stream_recognition_progress(file_content, custom_prompt),
            media_type="text/plain; charset=utf-8",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")