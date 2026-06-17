# 🐳 Docker 镜像推送报告

## 推送信息

**推送时间：** 2026-06-16  
**Docker Hub 账号：** boscotom  
**镜像名称：** boscotom/bosco-tsang

---

## ✅ 成功推送的标签

| 标签 | 架构 | 大小 | 状态 | Digest |
|------|------|------|------|--------|
| `latest` | linux/amd64 | 303 MB | ✅ 已推送 | `sha256:6cf2fb335f23a8d01ef079164f9821f31bd1aa17a47d68a38a9e3dd8b8f00f49` |
| `v0.3.0` | linux/amd64 | 303 MB | ✅ 已推送 | `sha256:6cf2fb335f23a8d01ef079164f9821f31bd1aa17a47d68a38a9e3dd8b8f00f49` |

---

## 📦 镜像信息

### 基础镜像
- **前端构建：** node:20-slim
- **后端运行：** python:3.10-slim

### 包含组件
- ✅ FastAPI 后端服务
- ✅ Vue 3 前端（已构建为静态文件）
- ✅ yt-dlp 下载引擎
- ✅ FFmpeg 视频处理工具
- ✅ httpx 异步 HTTP 客户端
- ✅ 浏览器扩展插件

### 暴露端口
- **8000** - 内部服务端口

### 数据卷
- `/app/downloads` - 下载文件
- `/app/cookies` - Cookies 文件
- `/app/data` - 数据库
- `/app/logs` - 日志文件

---

## 🏗️ 构建详情

### 构建命令
```bash
# 构建并推送（多架构 - 由于网络问题仅推送了 amd64）
docker buildx build --platform linux/amd64 -t boscotom/bosco-tsang:latest -t boscotom/bosco-tsang:v0.3.0 --push --provenance=false .
```

### 推送命令
```bash
# 推送 latest 标签
docker push boscotom/bosco-tsang:latest

# 推送 v0.3.0 标签
docker push boscotom/bosco-tsang:v0.3.0
```

---

## ⚠️ 多架构构建说明

### 当前状态
- ✅ **linux/amd64** - 已成功推送
- ❌ **linux/arm64** - 由于网络问题未推送

### 网络问题
在尝试构建多架构镜像时遇到了 IPv6 连接问题：
```
failed to fetch oauth token: Post "https://auth.docker.io/token": 
dial tcp [2a03:2880:f131:83:face:b00c:0:25de]:443: 
connectex: A connection attempt failed because the connected party 
did not properly respond after a period of time
```

### 解决方案

#### 方案 1：在 Linux/Mac 服务器上构建（推荐）
```bash
# 在 Linux/Mac 服务器上执行
docker buildx build --platform linux/amd64,linux/arm64 \
  -t boscotom/bosco-tsang:latest \
  -t boscotom/bosco-tsang:v0.3.0 \
  --push .
```

#### 方案 2：使用 GitHub Actions
创建 `.github/workflows/docker.yml`：
```yaml
name: Docker Build and Push

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            boscotom/bosco-tsang:latest
            boscotom/bosco-tsang:${{ github.ref_name }}
```

#### 方案 3：使用云服务器
1. 在 AWS/GCP/Aliyun 创建一台 Linux 实例
2. 安装 Docker 和 Buildx
3. 克隆项目并执行多架构构建

---

## 📥 使用镜像

### 拉取镜像
```bash
# 拉取最新版本
docker pull boscotom/bosco-tsang:latest

# 拉取指定版本
docker pull boscotom/bosco-tsang:v0.3.0
```

### 运行容器
```bash
# 快速运行
docker run -d \
  --name bosco-tsang \
  -p 8080:8000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookies:/app/cookies \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e APP_BASE_DIR=/app \
  --restart unless-stopped \
  boscotom/bosco-tsang:latest
```

### 使用 Docker Compose
```yaml
version: '3.8'

services:
  bosco-tsang:
    image: boscotom/bosco-tsang:latest
    container_name: bosco-tsang
    ports:
      - "8080:8000"
    volumes:
      - ./downloads:/app/downloads
      - ./cookies:/app/cookies
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - APP_BASE_DIR=/app
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

启动命令：
```bash
docker-compose up -d
```

---

## 🔍 验证镜像

### 查看镜像信息
```bash
# 查看本地镜像
docker images | grep boscotom/bosco-tsang

# 查看镜像详情
docker inspect boscotom/bosco-tsang:latest

# 查看镜像架构
docker manifest inspect boscotom/bosco-tsang:latest
```

### 测试运行
```bash
# 运行容器
docker run -d --name test -p 8080:8000 boscotom/bosco-tsang:latest

# 检查健康状态
docker ps

# 查看日志
docker logs -f test

# 测试 API
curl http://localhost:8080/

# 清理测试容器
docker stop test
docker rm test
```

---

## 📊 镜像层级

```
boscotom/bosco-tsang:latest
├── base: python:3.10-slim
├── system: ffmpeg
├── python: fastapi, uvicorn, yt-dlp, psutil, httpx
├── backend: backend/, BoscoTsang.toml, extensions/
├── frontend: static/ (from node:20-slim build)
└── directories: downloads, cookies, logs, data
```

---

## 🔄 下次推送清单

推送新版本前请确认：

- [ ] 运行清理脚本清理敏感信息
  ```bash
  .\scripts\clean-before-push.ps1  # Windows
  ./scripts/clean-before-push.sh   # Linux/Mac
  ```

- [ ] 更新版本号
  ```bash
  .\scripts\update-version.ps1  # Windows
  ./scripts/update-version.sh   # Linux/Mac
  ```

- [ ] 更新 CHANGELOG.md

- [ ] 构建多架构镜像（在 Linux/Mac 服务器上）
  ```bash
  docker buildx build --platform linux/amd64,linux/arm64 \
    -t boscotom/bosco-tsang:latest \
    -t boscotom/bosco-tsang:v0.4.0 \
    --push .
  ```

- [ ] 验证推送
  ```bash
  docker manifest inspect boscotom/bosco-tsang:latest
  ```

---

## 📞 相关链接

- **Docker Hub:** https://hub.docker.com/r/boscotom/bosco-tsang
- **GitHub:** https://github.com/BoscoTsang/BoscoTsang
- **文档索引:** INDEX.md
- **使用说明书:** USAGE_MANUAL.md

---

**推送状态：** ✅ 成功（linux/amd64）  
**推送时间：** 2026-06-16  
**版本：** v0.3.0  
**维护团队：** Bosco Tsang 开发团队
