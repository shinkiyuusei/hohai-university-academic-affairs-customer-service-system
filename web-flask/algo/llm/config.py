
"""
LLM配置文件
"""

# 文字大语言模型
MODEL_CONFIGS = {
    'qwen-turbo': {
        'name': 'Qwen-Turbo',
        'api_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'api_key': 'sk-ab42c6c18b444527b57de22382f7ab63',
        'model': 'qwen-turbo'
    },
}

# 文字视觉多模态大语言模型
VL_MODEL_CONFIGS = {
    'qwen-vl-plus': {
        'name': 'Qwen-VL-Plus',
        'api_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'api_key': 'sk-f74271899f464d0faa481d97801bc553',
        'model': 'qwen-vl-plus'
    }
}
# 更新默认提示词
DEFAULT_SYSTEM_PROMPT = "你是一个有用的教务信息AI助手，请根据用户的问题提供准确、有帮助的教务信息回答。"

# 默认文字模型
DEFAULT_MODEL = 'qwen-turbo' 

# 默认多模态模型
DEFAULT_VL_MODEL = 'qwen-vl-plus' 