
"""
文本分析模块
使用大语言模型处理文本内容
"""
import json
from typing import Dict
from openai import OpenAI
from .config import MODEL_CONFIGS, DEFAULT_MODEL


class TextAnalysis:
    """文本分析器"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        初始化文本分析器
        
        Args:
            model_name: 模型名称，默认使用配置中的默认模型
        """
        self.model_name = model_name
        if model_name not in MODEL_CONFIGS:
            raise ValueError(f"不支持的模型: {model_name}")
        
        self.config = MODEL_CONFIGS[model_name]
        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['api_url']
        )
    
    def send_message(self, message: str, system_prompt: str = None) -> Dict:
        """
        发送消息并获取回复
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词，如果为None则使用默认提示词
            
        Returns:
            Dict: 分析结果
        """
        try:
            # 使用默认提示词或自定义提示词
            if system_prompt is None:
                system_prompt = "你是一个有用的河海大学校务AI助手，请根据用户的问题提供准确、有帮助的回答。"
            
            # 调用LLM处理
            response = self._send_with_llm(message, system_prompt)
            
            return {
                'success': True,
                'result': response,
                'model': self.model_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': self.model_name
            }
    
    def _send_with_llm(self, message: str, system_prompt: str) -> str:
        """使用LLM发送消息"""
        try:
            # 调用文本模型
            completion = self.client.chat.completions.create(
                model=self.config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            # 尝试使用本地备选方案
            try:
                import re
                import logging
                
                # 设置日志记录器
                logger = logging.getLogger(__name__)
                logger.info(f"LLM调用失败，使用本地备选方案: {str(e)}")
                logger.debug(f"system_prompt: {system_prompt}")
                logger.debug(f"message: {message}")
                
                # 根据system_prompt判断任务类型
                if "意图识别" in system_prompt or "只输出YES或NO" in system_prompt:
                    # 意图识别任务
                    return self._local_intent_recognition(message)
                elif "标题生成" in system_prompt:
                    # 标题生成任务
                    return self._local_title_generation(message)
                else:
                    # 答案生成任务
                    return self._local_answer_generation(message)
            except Exception as local_e:
                # 如果本地生成也失败，记录错误但不抛出异常
                logger.error(f"本地生成失败: {str(local_e)}")
                # 根据任务类型返回默认值
                if "意图识别" in system_prompt or "只输出YES或NO" in system_prompt:
                    return "YES"  # 默认需要RAG检索
                elif "标题生成" in system_prompt:
                    return "未命名会话"
                else:
                    return "抱歉，当前服务暂时不可用，请稍后重试。"
    
    def _local_intent_recognition(self, message: str) -> str:
        """本地意图识别"""
        # 提取用户问题
        user_question = self._extract_user_question(message)
        if not user_question:
            return "NO"
        
        # 定义需要RAG检索的关键词
        rag_keywords = [
            "课程", "专业", "学期", "培养方案", "选课", "学分", "教务",
            "考试", "成绩", "转专业", "补修", "毕业", "学位", "奖学金",
            "政策", "流程", "要求", "安排", "查询", "检索", "知识"
        ]
        
        # 检查问题中是否包含需要RAG检索的关键词
        user_question_lower = user_question.lower()
        for keyword in rag_keywords:
            if keyword in user_question_lower:
                return "YES"
        
        # 定义不需要RAG检索的关键词
        no_rag_keywords = [
            "你好", "嗨", "哈喽", "再见", "谢谢", "感谢", "拜拜",
            "你是谁", "你叫什么", "你能做什么", "介绍一下", "功能", "帮助"
        ]
        
        # 检查问题中是否包含不需要RAG检索的关键词
        for keyword in no_rag_keywords:
            if keyword in user_question_lower:
                return "NO"
        
        # 默认返回YES，确保即使没有匹配到特定关键词，也会进行RAG检索
        return "YES"
    
    def _local_title_generation(self, message: str) -> str:
        """本地标题生成"""
        # 提取用户问题
        user_question = self._extract_user_question(message)
        if not user_question:
            return "会话咨询"
        
        # 优化标题生成，确保8-15字，且更准确
        if len(user_question) > 15:
            # 尝试提取核心问题，支持更多标点符号
            core_match = re.search(r'([^，。！？；：]+)[，。！？；：]', user_question)
            if core_match and 8 <= len(core_match.group(1)) <= 15:
                return core_match.group(1)
            # 如果没有找到合适的核心问题，截取前15字
            return user_question[:15]
        elif len(user_question) < 8:
            # 如果问题太短，尝试补充更合适的后缀
            suffixes = ["相关咨询", "相关问题", "相关信息"]
            for suffix in suffixes:
                if len(user_question + suffix) <= 15:
                    return user_question + suffix
            return user_question[:15]
        return user_question
    
    def _local_answer_generation(self, message: str) -> str:
        """本地答案生成"""
        # 提取用户问题
        user_question = self._extract_user_question(message)
        if not user_question:
            return "抱歉，我无法理解您的问题，请重新提问。"
        
        # 简单的答案生成逻辑
        user_question_lower = user_question.lower()
        
        # 问候语回复
        if any(greeting in user_question_lower for greeting in ["你好", "嗨", "哈喽"]):
            return "你好！我是河海大学校务AI助手，请问有什么可以帮助您的？"
        
        # 感谢回复
        if any(thanks in user_question_lower for thanks in ["谢谢", "感谢"]):
            return "不客气！如果您还有其他问题，随时可以问我。"
        
        # 再见回复
        if any(goodbye in user_question_lower for goodbye in ["再见", "拜拜"]):
            return "再见！欢迎下次咨询。"
        
        # 自我介绍回复
        if any(intro in user_question_lower for intro in ["你是谁", "你叫什么", "介绍一下"]):
            return "我是河海大学校务AI助手，专门为您提供教务相关的咨询服务。"
        
        # 默认回复
        return "抱歉，当前服务暂时不可用，请稍后重试。您可以尝试查询河海大学官网获取相关信息。"
    
    def _extract_user_question(self, message: str) -> str:
        """提取用户问题"""
        # 优化正则表达式，支持更多对话格式和Windows换行符
        patterns = [
            # 意图识别格式：用户问题：...（匹配到换行或结束）
            r'用户问题：\s*(.*?)\s*(?:\r?\n|$)',
            # 主要格式：用户: ... AI: 或 用户: ... 助手:
            r'用户:\s*(.*?)\s*(?:AI|助手):',
            # 任务描述格式：对话内容：用户: ... AI: 或 对话内容：用户: ... 助手:
            r'对话内容：\s*用户:\s*(.*?)\s*(?:AI|助手):',
            # 简单格式：只有用户问题
            r'用户:\s*(.*?)\s*$'
        ]
        
        user_question = None
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                user_question = match.group(1).strip()
                break
        
        # 如果没有匹配到，直接使用message作为用户问题
        if not user_question:
            user_question = message.strip()
        
        return user_question


# 创建全局实例
text_analysis = TextAnalysis()
