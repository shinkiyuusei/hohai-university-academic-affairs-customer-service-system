
"""
教务领域知识图谱配置
"""
import os

# Neo4j数据库配置
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'neo4j123')
NEO4J_BROWSER_URL = os.getenv('NEO4J_BROWSER_URL', 'http://localhost:7474/browser/')

# 节点类型定义
NODE_TYPES = [
    'AcademicPolicy',      # 教务政策
    'Course',              # 课程
    'Student',             # 学生
    'Teacher',             # 教师
    'Major',               # 专业
    'Schedule',            # 课表
    'Requirement',         # 要求/规定
    'Procedure',           # 流程
    'Document',            # 文档
    'TimePoint'            # 时间点
]

# 关系类型定义
RELATIONSHIP_TYPES = [
    'APPLIES_TO',          # 政策适用于
    'REQUIRES',            # 课程要求
    'BELONGS_TO',          # 属于专业
    'TAUGHT_BY',           # 由教师教授
    'FOLLOWS',             # 遵循流程
    'MEETS_REQUIREMENT',   # 满足要求
    'SCHEDULED_AT',        # 安排在时间
    'RELATED_TO',          # 相关于
    'DOCUMENTED_IN',       # 记录于文档
    'PREREQUISITE_OF',     # 是...的先修课
    'EQUIVALENT_TO'        # 等价于
]

# 关系类型中文名称映射
RELATIONSHIP_NAMES = {
    'APPLIES_TO': '适用于',
    'REQUIRES': '要求',
    'BELONGS_TO': '属于',
    'TAUGHT_BY': '由...教授',
    'FOLLOWS': '遵循',
    'MEETS_REQUIREMENT': '满足要求',
    'SCHEDULED_AT': '安排在',
    'RELATED_TO': '相关于',
    'DOCUMENTED_IN': '记录于',
    'PREREQUISITE_OF': '是...的先修课',
    'EQUIVALENT_TO': '等价于'
}

# 节点类型中文名称映射
NODE_NAMES = {
    'AcademicPolicy': '教务政策',
    'Course': '课程',
    'Student': '学生',
    'Teacher': '教师',
    'Major': '专业',
    'Schedule': '课表',
    'Requirement': '要求规定',
    'Procedure': '流程',
    'Document': '文档',
    'TimePoint': '时间点'
}

# 节点类型颜色配置
NODE_COLORS = {
    'AcademicPolicy': '#ee6666',  # 红色 - 教务政策
    'Course': '#91cc75',          # 绿色 - 课程
    'Student': '#fc8452',         # 橙色 - 学生
    'Teacher': '#fac858',         # 黄色 - 教师
    'Major': '#5470c6',           # 蓝色 - 专业
    'Schedule': '#73c0de',        # 青色 - 课表
    'Requirement': '#ea7ccc',     # 粉色 - 要求
    'Procedure': '#3ba272',       # 深绿 - 流程
    'Document': '#9a60b4',        # 紫色 - 文档
    'TimePoint': '#ca8622'        # 棕色 - 时间点
}


# 节点类型属性定义（用于LLM提取指导）
# 所有节点统一使用 name（必须）和 description（可选）两个属性
# description 字段用于存储节点的详细描述信息，LLM 可以从中理解节点内容
NODE_PROPERTIES = {
    'AcademicPolicy': ['name', 'description'],
    'Course': ['name', 'description'],
    'Student': ['name', 'description'],
    'Teacher': ['name', 'description'],
    'Major': ['name', 'description'],
    'Schedule': ['name', 'description'],
    'Requirement': ['name', 'description'],
    'Procedure': ['name', 'description'],
    'Document': ['name', 'description'],
    'TimePoint': ['name', 'description']
}