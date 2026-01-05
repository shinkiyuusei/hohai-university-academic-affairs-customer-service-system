
"""
图片理解模块
使用多模态大语言模型分析图片内容
"""
import base64
import json
import cv2
import numpy as np
from typing import Dict
from openai import OpenAI
from .config import VL_MODEL_CONFIGS, DEFAULT_VL_MODEL


class ImageUnderstanding:
    """图片理解分析器"""
    
    def __init__(self, model_name: str = DEFAULT_VL_MODEL):
        """
        初始化图片理解分析器
        
        Args:
            model_name: 模型名称，默认使用配置中的默认模型
        """
        self.model_name = model_name
        if model_name not in VL_MODEL_CONFIGS:
            raise ValueError(f"不支持的模型: {model_name}")
        
        self.config = VL_MODEL_CONFIGS[model_name]
        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['api_url']
        )
    
    def analyze_image(self, image: np.ndarray, prompt: str = None) -> Dict:
        """
        分析图片内容
        
        Args:
            image: numpy数组格式的图像
            prompt: 自定义提示词，如果为None则使用默认提示词
            
        Returns:
            Dict: 分析结果
        """
        try:
            # 图像预处理，提高颜色识别准确性
            processed_image = self._preprocess_image(image)
            
            # 将numpy数组转换为base64
            image_base64 = self._numpy_to_base64(processed_image)
            
            # 使用默认提示词或自定义提示词
            if prompt is None:
                prompt = "请详细描述这张图片的内容，包括主要对象、场景、动作等。"
            
            # 调用LLM分析
            analysis_result = self._analyze_with_llm(image_base64, prompt)
            
            return {
                'success': True,
                'result': analysis_result,
                'model': self.model_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': self.model_name
            }
    
    def _numpy_to_base64(self, image: np.ndarray) -> str:
        """将numpy数组转换为base64编码"""
        try:
            # 确保图像是BGR格式（OpenCV格式）
            if len(image.shape) == 3:
                # 转换为RGB格式
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # 提高图像质量，减少压缩损失
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 95]  # 提高JPEG质量
            _, buffer = cv2.imencode('.jpg', image_rgb, encode_params)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            return image_base64
            
        except Exception as e:
            raise Exception(f"图像编码失败: {str(e)}")
    
    def _analyze_with_llm(self, image_base64: str, prompt: str) -> str:
        """使用LLM分析图像"""
        try:
            # 构建图像URL
            img_base64_url = f"data:image/jpeg;base64,{image_base64}"
            
            # 调用多模态模型
            completion = self.client.chat.completions.create(
                model=self.config['model'],
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_base64_url}}
                    ]
                }]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LLM分析失败: {str(e)}")
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理，提高颜色识别准确性"""
        try:
            # 确保图像是彩色图像
            if len(image.shape) == 3:
                # 转换为RGB格式
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # 轻微增强对比度，提高颜色识别准确性
                lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                
                # 对L通道进行CLAHE（对比度限制自适应直方图均衡化）
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                l = clahe.apply(l)
                
                # 合并通道
                lab = cv2.merge([l, a, b])
                enhanced_image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
                
                return enhanced_image
            else:
                return image
                
        except Exception as e:
            # 如果预处理失败，返回原图像
            print(f"图像预处理失败: {str(e)}")
            return image


# 创建全局实例
image_understanding = ImageUnderstanding()
