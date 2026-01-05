
"""
文档处理器
使用text_analysis模块进行文档摘要生成
"""
from typing import Dict
from ..llm.text_analysis import text_analysis


class DocumentProcessor:
	"""文档处理器"""
	
	def __init__(self):
		"""初始化文档处理器"""
		pass
	
	def generate_summary(self, content: str, max_length: int = 200) -> Dict:
		"""
		生成文档摘要
		
		Args:
			content: 文档内容
			max_length: 摘要最大长度（默认200字）
			
		Returns:
			Dict: 生成结果
		"""
		try:
			# 构建摘要生成提示词
			prompt = f"""请为以下文档生成一个简洁的摘要，严格控制在{max_length}字以内，不要超过这个字数限制：

文档内容：
{content}

请生成摘要（不超过{max_length}字）："""
			
			system_prompt = f"你是一个专业的文档摘要生成助手。请严格按照字数限制生成摘要，绝对不能超过{max_length}字。摘要应该准确、简洁、完整地概括文档的核心内容。"
			
			# 调用text_analysis模块
			result = text_analysis.send_message(prompt, system_prompt)
			
			if result['success']:
				summary = result['result']
				return {
					'success': True,
					'summary': summary,
					'length': len(summary)
				}
			else:
				return {
					'success': False,
					'error': result['error']
				}
				
		except Exception as e:
			return {
				'success': False,
				'error': f'摘要生成失败: {str(e)}'
			}


# 创建全局实例
document_processor = DocumentProcessor()
