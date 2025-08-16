from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    """图片上传和识别响应模型"""
    success: bool
    message: str
    recognized_text: Optional[str] = None
    processing_time: Optional[float] = None

class RefineRequest(BaseModel):
    """文字微调请求模型"""
    original_text: str
    refinement_instruction: str

class RefineResponse(BaseModel):
    """文字微调响应模型"""
    success: bool
    message: str
    refined_text: Optional[str] = None
    processing_time: Optional[float] = None