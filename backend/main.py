from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from app.api.upload import router as upload_router
from app.api.health import router as health_router
from app.api.tune import router as tune_router
from app.api.stream import router as stream_router

# 创建FastAPI应用实例
app = FastAPI(
    title="UnblurAI API",
    description="文字去模糊识别系统 API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vue开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(tune_router, prefix="/api")
app.include_router(stream_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "UnblurAI API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="warning")