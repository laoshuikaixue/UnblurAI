import os
import base64
import httpx
from zai import ZhipuAiClient
from PIL import Image
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ZhipuAIService:
    def __init__(self):
        self.api_key = os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable is required")
        
        self.client = ZhipuAiClient(api_key=self.api_key)
    
    def image_to_base64(self, image_bytes: bytes) -> str:
        """将图片字节转换为base64编码"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def validate_image(self, image_bytes: bytes) -> bool:
        """验证图片格式和大小"""
        try:
            image = Image.open(BytesIO(image_bytes))
            # 检查图片格式
            if image.format.lower() not in ['jpeg', 'jpg', 'png']:
                return False
            # 检查图片大小 (5MB限制)
            if len(image_bytes) > 5 * 1024 * 1024:
                return False
            return True
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def clean_response_text(self, text: str) -> str:
        """清理GLM-4.5V返回结果中的特殊标记"""
        if not text:
            return text
        
        # 移除 <|begin_of_box|> 和 <|end_of_box|> 标记
        cleaned_text = text.replace('<|begin_of_box|>', '').replace('<|end_of_box|>', '')
        
        # 清理多余的空行和空格
        lines = cleaned_text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        return '\n'.join(cleaned_lines)
    
    async def recognize_text(self, image_bytes: bytes, custom_prompt: Optional[str] = None) -> str:
        """使用GLM-4.5V识别图片中的文字"""
        try:
            logger.info(f"开始文字识别，图片大小: {len(image_bytes)} bytes")
            
            # 验证图片
            if not self.validate_image(image_bytes):
                raise ValueError("Invalid image format or size")
            
            # 转换为base64
            image_base64 = self.image_to_base64(image_bytes)
            
            # 构建优化的默认提示词（简体中文）
            default_prompt = """请仔细识别这张图片中的所有文字内容，特别注意以下要求：
1. 识别所有可见的文字，包括模糊、不清晰或部分遮挡的文字
2. 尽可能准确地还原文字的原始内容和含义
3. 保持原有的文本格式、段落结构和排版布局
4. 对于模糊或不确定的文字，请根据上下文进行合理推测
5. 使用简体中文输出结果
6. 如果图片中包含英文或其他语言，请保持原语言不变
7. 按照从上到下、从左到右的顺序输出文字内容

请直接输出识别到的文字内容，不需要添加额外的说明或解释。"""
            
            # 使用自定义提示词或默认提示词
            prompt = custom_prompt if custom_prompt else default_prompt
            logger.info(f"使用提示词: {prompt[:100]}...")
            
            # 调用GLM-4.5V API
            logger.info("调用GLM-4.5V API进行文字识别")
            response = self.client.chat.completions.create(
                model="glm-4.5v",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                thinking={
                    "type": "enabled"
                }
            )
            
            # 提取识别结果
            if response.choices and len(response.choices) > 0:
                raw_text = response.choices[0].message.content
                logger.info(f"GLM-4.5V API返回原始结果长度: {len(raw_text) if raw_text else 0}")
                
                # 清理特殊标记
                cleaned_text = self.clean_response_text(raw_text)
                logger.info(f"清理后结果长度: {len(cleaned_text)}")
                
                return cleaned_text
            else:
                raise ValueError("No response from GLM-4.5V API")
                
        except Exception as e:
            logger.error(f"Text recognition failed: {e}")
            raise e
    
    async def refine_text(self, original_text: str, refinement_instruction: str) -> str:
        """使用自然语言指令微调识别结果"""
        try:
            logger.info(f"开始文字微调，原始文字长度: {len(original_text)}")
            logger.info(f"微调指令: {refinement_instruction}")
            
            prompt = f"""请根据以下指令对文字内容进行微调：

原始文字内容：
{original_text}

微调指令：
{refinement_instruction}

请输出微调后的文字内容："""
            
            logger.info("调用GLM-4.5V API进行文字微调")
            response = self.client.chat.completions.create(
                model="glm-4.5v",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                thinking={
                    "type": "enabled"
                }
            )
            
            if response.choices and len(response.choices) > 0:
                raw_text = response.choices[0].message.content
                logger.info(f"GLM-4.5V API返回微调结果长度: {len(raw_text) if raw_text else 0}")
                
                # 清理特殊标记
                cleaned_text = self.clean_response_text(raw_text)
                logger.info(f"微调清理后结果长度: {len(cleaned_text)}")
                
                return cleaned_text
            else:
                raise ValueError("No response from GLM-4 API")
                
        except Exception as e:
            logger.error(f"Text refinement failed: {e}")
            raise e