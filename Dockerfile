# 第一阶段：构建前端
FROM node:20-alpine as frontend-builder

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

# 第二阶段：构建后端
FROM python:3.9-alpine

WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    build-base \
    gfortran \
    openblas-dev \
    lapack-dev \
    libffi-dev \
    openssl-dev \
    zlib-dev \
    jpeg-dev \
    freetype-dev \
    libpng-dev \
    tiff-dev \
    lcms2-dev \
    libwebp-dev \
    harfbuzz-dev \
    fribidi-dev \
    tesseract-ocr \
    poppler-utils \
    curl

# 复制后端依赖文件
COPY web-flask/requirements.txt ./requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY web-flask ./web-flask

# 从第一阶段复制前端构建结果
COPY --from=frontend-builder /app/web-vue/dist ./web-flask/static

# 创建必要的目录
RUN mkdir -p ./web-flask/static \
    && mkdir -p ./data \
    && mkdir -p ./web-flask/file_store \
    && mkdir -p ./web-flask/temp \
    && chmod -R 755 ./web-flask

# 设置环境变量
ENV FLASK_APP=web-flask/app.py
ENV FLASK_ENV=production
ENV FLASK_SERVICE_HOST=0.0.0.0
ENV FLASK_SERVICE_PORT=5000

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]