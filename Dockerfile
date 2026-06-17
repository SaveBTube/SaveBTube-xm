# ===========================================
# Bosco Tsang Dockerfile
# 全平台视频/音乐/图片下载系统
# ===========================================

# 阶段1: 构建前端
FROM node:20-slim AS frontend-builder
WORKDIR /frontend

# 复制前端代码
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制并构建前端
COPY frontend/ ./
RUN npm run build

# 阶段2: 构建后端
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
# 安装 Python 依赖（yt-dlp 指定最新版）
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    "yt-dlp>=2025.6.1" \
    psutil \
    python-multipart \
    tomli \
    httpx \
    markdown \
    passlib[bcrypt] \
    PyJWT \
    slowapi

# 复制后端代码
COPY backend/ ./backend/

# 复制配置文件
COPY BoscoTsang.toml ./

# 复制文档文件
COPY USAGE_MANUAL.md ./
COPY CHANGELOG.md ./

# 复制 docs 目录
COPY docs/ ./docs/

# 复制快捷指令安装页面
COPY static/ ./static/

# 复制快捷指令配置文件
COPY shortcuts/ ./shortcuts/

# 复制浏览器扩展插件
COPY extensions/ ./extensions/

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /frontend/dist /app/static

# 创建数据目录
RUN mkdir -p /app/downloads /app/cookies /app/logs /app/data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
