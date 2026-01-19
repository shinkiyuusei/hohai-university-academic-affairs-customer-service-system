# 第一阶段：构建前端
FROM node:20-alpine as frontend-builder

# 使用清华源加速 Alpine 软件包安装
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

WORKDIR /app/web-vue

# 复制前端依赖文件
COPY web-vue/package*.json ./
COPY web-vue/.npmrc ./

# 安装前端依赖
RUN npm install

# 复制前端源码
COPY web-vue ./

# 构建前端
RUN npm run build

# 第二阶段：构建后端（必须用 slim 避免编译 opencv）
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置国内镜像源加速 apt 安装
RUN if [ -f /etc/apt/sources.list ]; then \
        sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
        sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list; \
    fi && \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources; \
    fi

# 安装系统运行依赖 (libgl1 是 opencv 必须的)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python 镜像源加速 pip
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 复制依赖并安装
COPY web-flask/requirements.txt ./web-flask/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./web-flask/requirements.txt

# 复制后端源码
COPY web-flask ./web-flask

# 从第一阶段复制前端构建结果
COPY --from=frontend-builder /app/web-vue/dist ./web-flask/static

# 目录权限
RUN mkdir -p /app/data ./web-flask/file_store ./web-flask/temp && \
    chmod -R 755 /app

# --- 关键配置：解决 ModuleNotFoundError 和路径问题 ---
ENV PYTHONPATH=/app/web-flask
ENV FLASK_APP=web-flask/app.py
ENV FLASK_ENV=production
ENV FLASK_SERVICE_HOST=0.0.0.0
ENV FLASK_SERVICE_PORT=5000

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
