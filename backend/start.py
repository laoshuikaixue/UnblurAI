#!/usr/bin/env python3
"""
UnblurAI Backend 启动脚本
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    """启动FastAPI应用"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting UnblurAI API server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Log Level: {log_level}")
    
    # 检查必要的环境变量
    if not os.getenv("ZHIPUAI_API_KEY"):
        print("Warning: ZHIPUAI_API_KEY not found in environment variables")
        print("Please set your ZhipuAI API key in .env file")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            log_level=log_level,
            reload=True  # 开发模式下启用热重载
        )
    except KeyboardInterrupt:
        print("\nShutting down UnblurAI API server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()