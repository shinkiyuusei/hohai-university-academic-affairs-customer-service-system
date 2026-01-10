# 河海大学校务智能问答系统

## 项目简介
河海大学校务智能问答系统是一个基于知识图谱和自然语言处理技术的智能问答平台，旨在帮助师生查询和了解校务相关的专业知识。系统采用前后端分离架构，结合了知识图谱技术、文本分析和向量检索等先进技术，为用户提供准确、高效的问答服务。

## 技术栈

### 后端
- **框架**: Flask
- **数据库**: SQLite、Neo4j（知识图谱）
- **向量检索**: FAISS
- **自然语言处理**: OpenAI API
- **其他**: JWT认证、CORS支持

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **图表**: ECharts
- **构建工具**: Vite

## 项目结构

```
hohai-university-academic-affairs-customer-service-system/
├── web-flask/              # 后端代码
│   ├── algo/              # 算法模块（自然语言处理、向量检索等）
│   │   ├── document/      # 文档处理相关算法
│   │   ├── knowledge_graph/ # 知识图谱相关算法
│   │   └── llm/           # 大语言模型相关算法
│   ├── clients/           # 客户端工具
│   ├── file_store/        # 文件存储
│   │   └── documents/     # 文档存储目录
│   ├── routes/            # API路由
│   ├── services/          # 业务逻辑服务
│   ├── utils/             # 工具函数
│   ├── weights/           # 模型权重文件
│   ├── app.py             # 应用入口
│   ├── config.py          # 配置文件
│   └── requirements.txt   # 依赖列表
├── web-vue/               # 前端代码
│   ├── public/            # 静态资源
│   ├── src/               # 源代码
│   │   ├── api/           # API接口
│   │   └── App.vue        # 主应用组件
│   ├── package.json       # 项目配置
│   └── vite.config.ts     # Vite配置
├── data/                  # 数据目录
├── DEPLOYMENT_GUIDE.md    # 部署指南
├── Dockerfile             # Docker配置文件
├── docker-compose.yml     # Docker Compose配置
├── nginx.conf             # Nginx配置
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明文档
```

## 功能特性

### 1. 校务知识图谱管理
- 校务知识图谱构建与可视化
- 实体与关系管理
- 图谱数据导入与导出

### 2. 文档管理
- 校务相关文档上传与解析
- 文档内容索引与检索
- 支持多种文档格式

### 3. 智能问答
- 基于知识图谱的精准问答
- 自然语言理解与处理
- 上下文感知对话

### 4. 学术信息服务
- 学术案例管理
- 学术信息查询
- 相关政策解读

### 5. 用户管理
- 多角色权限控制
- 用户信息管理
- 登录注册与身份验证

## 快速开始

### 环境要求

- **后端**: Python 3.8+
- **前端**: Node.js 16+

### 安装部署

#### 1. 后端部署

```bash
# 进入后端目录
cd web-flask

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

#### 2. 前端部署

```bash
# 进入前端目录
cd web-vue

# 安装依赖
npm install

# 开发环境运行
npm run dev

# 生产环境构建
npm run build
```

### 配置说明

#### 后端配置
编辑 `web-flask/config.py` 文件，配置数据库连接、API密钥等参数：

```python
# 数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'

# Neo4j配置
NEO4J_URI = 'bolt://localhost:7687'
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'password'

# OpenAI API配置
OPENAI_API_KEY = 'your_api_key'

# JWT密钥
SECRET_KEY = 'your_secret_key'
```

#### 前端配置
编辑 `web-vue/.env` 文件，配置API地址等参数：

```
VITE_API_BASE_URL=http://localhost:5000/api
```

## API文档

系统提供以下主要API接口：

### 问答接口
- `POST /api/qa/ask` - 提交问题获取答案
- `GET /api/qa/history` - 获取问答历史

### 知识图谱接口
- `GET /api/graph/nodes` - 获取图谱节点
- `GET /api/graph/relationships` - 获取图谱关系
- `POST /api/graph/query` - 执行图谱查询

### 文档接口
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents/list` - 获取文档列表
- `GET /api/documents/search` - 搜索文档内容

### 学术信息接口
- `GET /api/academic/cases` - 获取学术案例
- `GET /api/academic/info` - 获取学术信息
- `GET /api/academic/policies` - 获取学术政策

### 用户接口
- `POST /api/users/login` - 用户登录
- `POST /api/users/register` - 用户注册
- `GET /api/users/profile` - 获取用户信息

## 使用说明

1. **启动系统**：分别启动后端服务和前端应用
2. **用户登录**：使用已有账号登录或注册新账号
3. **知识查询**：在问答页面输入校务相关问题
4. **图谱浏览**：在知识图谱页面查看校务知识图谱
5. **文档管理**：上传和管理校务相关文档
6. **学术信息**：查询学术案例和相关政策

## 项目亮点

1. **知识图谱驱动**：基于Neo4j构建的知识图谱，实现精准的校务知识查询
2. **向量检索技术**：使用FAISS进行高效的向量相似性搜索
3. **自然语言处理**：结合OpenAI API实现智能问答
4. **前后端分离**：现代化的技术栈，便于维护和扩展
5. **学术信息服务**：专门针对校务场景的学术信息管理和查询功能

## 部署方式

### 本地部署
按照上述快速开始步骤进行部署

### Docker部署
使用项目提供的Docker配置文件进行容器化部署：

```bash
# 构建并启动容器
docker-compose up -d
```

## 开发者

- **后端开发**：Python + Flask
- **前端开发**：Vue 3 + TypeScript
- **算法开发**：自然语言处理、向量检索、知识图谱
