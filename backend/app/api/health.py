from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="UnblurAI API is running normally"
    )