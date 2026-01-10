# 部署指南

本指南详细说明如何使用Docker将项目与Neo4j一起打包部署到云端。

## 前提条件

- Docker已安装并运行
- Docker Compose已安装
- 云服务器或本地服务器
- 基本的Docker命令知识

## 项目结构

```
hohai-university-academic-affairs-customer-service-system/
├── data/                # 数据存储目录
├── web-flask/           # 后端Python代码
├── web-vue/             # 前端Vue代码
├── Dockerfile           # Docker构建文件
├── docker-compose.yml   # Docker Compose配置文件
├── nginx.conf           # Nginx配置文件
└── DEPLOYMENT_GUIDE.md  # 部署指南
```

## 配置说明

### 1. 环境变量配置

项目的关键环境变量已在`docker-compose.yml`中配置：

- `NEO4J_URI`: Neo4j数据库连接地址
- `NEO4J_USER`: Neo4j用户名
- `NEO4J_PASSWORD`: Neo4j密码
- `FLASK_APP`: Flask应用入口
- `FLASK_ENV`: Flask运行环境
- `FLASK_SERVICE_HOST`: Flask服务主机
- `FLASK_SERVICE_PORT`: Flask服务端口
- `DB_PATH`: SQLite数据库路径
- `FLASK_TEMP_DIR`: 临时文件目录
- `FILE_STORE_PATH`: 文件存储路径

### 2. 端口配置

默认端口映射：

- `80`: Nginx HTTP端口
- `443`: Nginx HTTPS端口
- `5000`: Flask应用端口
- `7474`: Neo4j浏览器界面端口
- `7687`: Neo4j Bolt协议端口

## 部署步骤

### 步骤1: 克隆项目（如果尚未克隆）

```bash
git clone <项目仓库地址>
cd hohai-university-academic-affairs-customer-service-system
```

### 步骤2: 准备SSL证书（可选，用于HTTPS）

如果需要HTTPS访问，在项目根目录创建`ssl`目录并放入证书文件：

```bash
mkdir -p ssl
# 将证书文件放入ssl目录
# ssl/fullchain.pem
# ssl/privkey.pem
```

### 步骤3: 构建和启动服务

在项目根目录执行以下命令：

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### 步骤4: 验证部署

部署完成后，可以通过以下方式验证：

1. **前端界面**: `http://服务器IP` 或 `https://服务器IP`
2. **Flask API**: `http://服务器IP:5000`
3. **Neo4j浏览器**: `http://服务器IP:7474/browser/`

### 步骤5: 初始化数据（首次部署）

首次部署后，需要初始化Neo4j数据库：

1. 访问Neo4j浏览器 `http://服务器IP:7474/browser/`
2. 使用用户名 `neo4j` 和密码 `secure_neo4j_password` 登录
3. 运行必要的初始化脚本（如果有）

## 管理命令

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f neo4j
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入Neo4j容器
docker-compose exec neo4j bash
```

## 数据持久化

项目使用以下卷进行数据持久化：

- `./data`: 应用数据目录
- `./web-flask/file_store`: 文件存储目录
- `neo4j_data`: Neo4j数据目录
- `neo4j_logs`: Neo4j日志目录

## 性能优化建议

1. **内存配置**: 根据服务器配置调整Neo4j内存设置
2. **存储优化**: 使用SSD存储提高I/O性能
3. **网络优化**: 配置合适的网络设置
4. **监控**: 部署监控工具监控服务状态

## 常见问题排查

### 1. 服务启动失败

检查服务日志：
```bash
docker-compose logs -f
```

### 2. Neo4j连接失败

- 确保Neo4j服务正常运行
- 检查环境变量配置
- 验证网络连接

### 3. 前端页面无法访问

- 检查Nginx服务状态
- 验证前端构建是否成功
- 检查端口映射是否正确

### 4. 数据库初始化问题

- 检查Neo4j认证配置
- 验证初始化脚本是否正确执行

## 云端部署建议

### 阿里云ECS部署

1. 创建ECS实例，选择Ubuntu 20.04或CentOS 7+
2. 安装Docker和Docker Compose
3. 克隆项目到服务器
4. 按照上述步骤部署

### 腾讯云CVM部署

1. 创建CVM实例，选择合适的配置
2. 安装Docker环境
3. 部署项目

### 华为云ECS部署

1. 创建ECS实例
2. 配置安全组规则，开放必要端口
3. 部署项目

## 扩展建议

1. **负载均衡**: 对于高流量场景，可配置负载均衡
2. **多节点部署**: 考虑使用Neo4j集群提高可靠性
3. **CI/CD集成**: 配置自动化部署流程
4. **监控告警**: 集成监控系统，及时发现问题

## 联系信息

如果遇到部署问题，请参考相关文档或联系技术支持。