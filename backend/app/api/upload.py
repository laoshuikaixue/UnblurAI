from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from app.models.models import UploadResponse, RefineRequest, RefineResponse
from app.services.zhipuai_service import ZhipuAIService
import time
import logging
import json
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化ZhipuAI服务
zhipuai_service = ZhipuAIService()

@router.post("/upload", response_model=UploadResponse)
async def upload_and_recognize(
    file: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None)
):
    """上传图片并识别文字"""
    start_time = time.time()
    
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
        
        # 调用ZhipuAI服务识别文字
        recognized_text = await zhipuai_service.recognize_text(
            image_bytes=file_content,
            custom_prompt=custom_prompt
        )
        
        processing_time = time.time() - start_time
        
        return UploadResponse(
            success=True,
            message="文字识别成功",
            recognized_text=recognized_text,
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload and recognition failed: {e}")
        processing_time = time.time() - start_time
        return UploadResponse(
            success=False,
            message=f"识别失败: {str(e)}",
            processing_time=round(processing_time, 2)
        )

@router.post("/upload-stream")
async def upload_and_recognize_stream(
    file: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None)
):
    """上传图片并流式识别文字"""
    
    async def generate_stream():
        start_time = time.time()
        
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'message': '开始处理图片...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
            
            # 验证文件类型
            if not file.content_type or not file.content_type.startswith('image/'):
                yield f"data: {json.dumps({'type': 'error', 'message': '只支持图片文件'}, ensure_ascii=False)}\n\n"
                return
            
            # 验证文件格式
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
            if file.content_type not in allowed_formats:
                yield f"data: {json.dumps({'type': 'error', 'message': '只支持 JPG、JPEG、PNG 格式的图片'}, ensure_ascii=False)}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '正在读取图片文件...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)
            
            # 读取文件内容
            file_content = await file.read()
            
            # 验证文件大小 (5MB)
            if len(file_content) > 5 * 1024 * 1024:
                yield f"data: {json.dumps({'type': 'error', 'message': '文件大小不能超过 5MB'}, ensure_ascii=False)}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '正在调用GLM-4.5V模型识别...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '模型正在分析图片内容...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '正在识别文字内容...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.3)
            
            # 调用ZhipuAI服务识别文字
            recognized_text = await zhipuai_service.recognize_text(
                image_bytes=file_content,
                custom_prompt=custom_prompt
            )
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '文字识别完成，正在处理结果...'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.2)
            
            processing_time = time.time() - start_time
            
            # 发送成功结果
            yield f"data: {json.dumps({
                'type': 'success',
                'message': '文字识别成功',
                'recognized_text': recognized_text,
                'processing_time': round(processing_time, 2)
            }, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"Stream upload and recognition failed: {e}")
            processing_time = time.time() - start_time
            yield f"data: {json.dumps({
                'type': 'error',
                'message': f'识别失败: {str(e)}',
                'processing_time': round(processing_time, 2)
            }, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.post("/refine", response_model=RefineResponse)
async def refine_text(request: RefineRequest):
    """使用自然语言指令微调识别结果"""
    start_time = time.time()
    
    try:
        # 调用ZhipuAI服务进行文字微调
        refined_text = await zhipuai_service.refine_text(
            original_text=request.original_text,
            refinement_instruction=request.refinement_instruction
        )
        
        processing_time = time.time() - start_time
        
        return RefineResponse(
            success=True,
            message="文字微调成功",
            refined_text=refined_text,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Text refinement failed: {e}")
        processing_time = time.time() - start_time
        return RefineResponse(
            success=False,
            message=f"微调失败: {str(e)}",
            processing_time=round(processing_time, 2)
        )