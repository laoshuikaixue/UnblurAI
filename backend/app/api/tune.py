from fastapi import APIRouter, Form, HTTPException
from zhipuai import ZhipuAI
import os
from typing import Optional

router = APIRouter()

# 初始化ZhipuAI客户端
client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))

@router.post("/tune")
async def tune_text(
    text: str = Form(..., description="需要微调的文字内容"),
    instruction: str = Form(..., description="微调指令")
):
    """
    文字微调接口
    根据用户指令对识别出的文字进行优化调整
    """
    try:
        # 检查API密钥
        if not os.getenv("ZHIPUAI_API_KEY"):
            raise HTTPException(status_code=500, detail="ZHIPUAI_API_KEY未配置")
        
        # 构建微调提示词
        prompt = f"""请根据以下指令对文字内容进行优化调整：

指令：{instruction}

原始文字内容：
{text}

请直接输出优化后的文字内容，不要添加任何解释或说明。"""
        
        # 调用GLM-4.5V进行文字微调
        response = client.chat.completions.create(
            model="glm-4.5v",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 提取微调后的文字
        tuned_text = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "tuned_text": tuned_text,
            "original_instruction": instruction
        }
        
    except Exception as e:
        print(f"文字微调失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文字微调失败: {str(e)}")