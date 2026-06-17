# Bosco Tsang 部署文档

## 目录
- [系统简介](#系统简介)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [群晖/极空间部署](#群晖极空间部署)
- [推送到自己的 Docker 仓库](#推送到自己的-docker-仓库)
- [常见问题](#常见问题)

---

## 系统简介

**Bosco Tsang** 是一款功能强大的全平台视频/音乐/图片下载系统，基于 yt-dlp 核心，支持 **3000+** 平台的一键下载。

### 技术栈
- **前端**: Vue 3 + Vite + Chart.js
- **后端**: Python FastAPI + SQLite
- **下载引擎**: yt-dlp + FFmpeg
- **容器化**: Docker + Docker Compose

---

## 功能特性

### 核心功能
| 功能 | 说明 |
|------|------|
| 🌐 **3000+平台支持** | YouTube, Bilibili, 抖音, 快手, 小红书, 微博等 |
| 📺 **视频下载** | 支持 4K/1080p/720p 等多种分辨率 |
| 🎵 **音频提取** | 支持 MP3/FLAC 等格式提取 |
| 🖼️ **图片下载** | 支持社交平台图片批量下载 |
| 📡 **订阅管理** | 自动监控频道更新并下载 |
| 📊 **数据统计** | 完整的下载统计和趋势分析 |
| 🔒 **用户管理** | 多用户支持，角色权限控制 |
| 🔑 **API密钥** | 支持 API 调用，集成第三方工具 |
| 💻 **CLI工具** | 命令行工具，支持脚本自动化 |

### 平台支持（部分）
- YouTube / YouTube Music
- Bilibili (B站)
- 抖音 / TikTok
- 快手
- 小红书
- 微博
- Twitter / X
- Instagram
- 网易云音乐
- QQ音乐
- Apple Music
- Telegram
- 今日头条
- 微信视频号

---

## 快速开始

### 环境要求
- Docker & Docker Compose
- 或 Python 3.10+
- FFmpeg

### 本地开发

```bash
# 克隆项目
git clone https://github.com/your-repo/bosco-tsang.git
cd bosco-tsang

# 安装后端依赖
pip install fastapi uvicorn yt-dlp psutil python-multipart

# 安装前端依赖
cd frontend
npm install

# 启动后端
cd ..
uvicorn backend.main:app --reload --port 8000

# 启动前端 (另一个终端)
cd frontend
npm run dev
```

访问 http://localhost:3000

默认账号: `admin` / `admin123`

---

## Docker 部署

### 1. 构建镜像

```bash
# 进入项目目录
cd bosco-tsang

# 构建镜像
docker build -t bosco-tsang:latest .

# 或使用 Docker Compose
docker-compose up -d
```

### 2. 配置目录权限

```bash
# 创建数据目录
mkdir -p downloads cookies logs data

# 设置权限
chmod 777 downloads cookies logs data
```

### 3. 启动服务

```bash
# 使用 Docker Compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 4. 访问系统

打开浏览器访问: **http://localhost:8080**

默认管理员账号:
- 用户名: `admin`
- 密码: `admin123`

---

## 群晖/极空间部署

### 方法一: Docker Compose (推荐)

#### 群晖 (Synology NAS)

1. **打开 Docker 套件**
   - 打开"控制面板" > "终端机和SNMP"
   - 启用 SSH 功能

2. **SSH 连接群晖**
   ```bash
   ssh admin@your-nas-ip
   ```

3. **创建项目目录**
   ```bash
   # 创建共享文件夹中的目录
   mkdir -p /volume1/docker/bosco-tsang/{downloads,cookies,logs,data}
   
   # 进入目录
   cd /volume1/docker/bosco-tsang
   ```

4. **上传项目文件**
   - 使用 File Station 或 SCP 上传项目文件到该目录

5. **启动容器**
   ```bash
   docker-compose up -d
   ```

6. **访问系统**
   - 打开浏览器访问: `http://your-nas-ip:8080`

#### 极空间 (ZSpace NAS)

1. **开启 SSH**
   - 设置 > 系统设置 > 终端 > 开启 SSH

2. **SSH 连接极空间**
   ```bash
   ssh root@your-nas-ip
   ```

3. **创建目录并上传**
   ```bash
   mkdir -p /mnt/data/bosco-tsang/{downloads,cookies,logs,data}
   ```

4. **修改 docker-compose.yml 中的端口**
   - 如果 8080 端口被占用，修改为其他端口如 `8090:8000`

5. **启动**
   ```bash
   docker-compose up -d
   ```

### 方法二: 手动 Docker 命令

```bash
# 拉取镜像 (如果已推送)
docker pull your-registry/bosco-tsang:latest

# 创建网络
docker network create bosco-net

# 运行容器
docker run -d \
  --name bosco-tsang \
  --restart unless-stopped \
  -p 8080:8000 \
  -v /path/to/downloads:/app/downloads \
  -v /path/to/cookies:/app/cookies \
  -v /path/to/logs:/app/logs \
  -v /path/to/data:/app/data \
  -e APP_BASE_DIR=/app \
  your-registry/bosco-tsang:latest
```

### 方法三: 极空间 Docker 图形界面

1. **打开 Docker 套件**
2. **镜像仓库** > **添加镜像**
3. **本地镜像** > **导入镜像** (上传 tar 包)
4. **容器管理** > **创建容器**
5. **基本设置**
   - 容器名称: `bosco-tsang`
   - 开机自启: ✅
6. **端口设置**
   - 本地端口: `8080`
   - 容器端口: `8000`
7. **存储设置**
   - 添加 4 个绑定:
     - `/volume1/docker/bosco-tsang/downloads` -> `/app/downloads`
     - `/volume1/docker/bosco-tsang/cookies` -> `/app/cookies`
     - `/volume1/docker/bosco-tsang/logs` -> `/app/logs`
     - `/volume1/docker/bosco-tsang/data` -> `/app/data`
8. **环境变量**
   - `APP_BASE_DIR` = `/app`
9. **创建并启动**

---

## 推送到自己的 Docker 仓库

### 准备工作

1. **注册 Docker Hub 账号**
   - 访问 https://hub.docker.com
   - 创建仓库，假设用户名是 `yourusername`，仓库名是 `bosco-tsang`

2. **登录 Docker Hub**
   ```bash
   docker login
   # 输入用户名和密码
   ```

### 推送步骤

#### 方法一: 直接构建并推送

```bash
# 进入项目目录
cd bosco-tsang

# 重命名镜像为你的仓库
docker build -t yourusername/bosco-tsang:latest .

# 推送到 Docker Hub
docker push yourusername/bosco-tsang:latest

# 推送特定版本
docker tag yourusername/bosco-tsang:latest yourusername/bosco-tsang:1.0.0
docker push yourusername/bosco-tsang:1.0.0
```

#### 方法二: 修改镜像名后推送

```bash
# 拉取原镜像 (如果有)
docker pull boscolab/bosco-tsang:latest

# 打标签
docker tag boscolab/bosco-tsang:latest yourusername/bosco-tsang:latest

# 推送
docker push yourusername/bosco-tsang:latest
```

#### 方法三: 使用 GitHub Actions 自动推送

创建 `.github/workflows/docker.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
          
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/bosco-tsang:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/bosco-tsang:${{ github.ref_name }}
```

### 推送到私有仓库

```bash
# 登录私有仓库
docker login your-private-registry.com

# 打标签
docker tag bosco-tsang:latest your-private-registry.com/bosco-tsang:latest

# 推送
docker push your-private-registry.com/bosco-tsang:latest
```

### 拉取和使用

```bash
# 拉取镜像
docker pull yourusername/bosco-tsang:latest

# 运行
docker run -d \
  --name bosco-tsang \
  -p 8080:8000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookies:/app/cookies \
  yourusername/bosco-tsang:latest
```

---

## 常见问题

### Q1: 下载失败，提示需要登录
**A:** 需要配置 Cookies 文件：
1. 安装浏览器扩展 "Get cookies.txt LOCALLY"
2. 登录目标平台账号
3. 导出 Netscape 格式的 Cookies
4. 将文件命名为对应平台（如 `youtube.txt`）放入 `cookies` 目录

### Q2: 视频清晰度不够
**A:** 
- 确保登录了平台账号（配置 Cookies）
- 可以指定质量：`best`/`1080p`/`720p`/`audio`

### Q3: 群晖/极空间拉取镜像慢
**A:** 配置 Docker 镜像加速：
- 群晖: 控制面板 > Docker > 勾选"启用注册表镜像"
- 或手动配置 `/etc/docker/daemon.json`

### Q4: 端口被占用
**A:** 修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8090:8000"  # 改为其他端口
```

### Q5: 如何备份数据
**A:** 备份以下目录：
- `downloads/` - 下载的文件
- `cookies/` - 登录凭证
- `data/` - 数据库和配置

---

## 目录结构

```
bosco-tsang/
├── backend/              # 后端代码
│   ├── main.py          # 主应用
│   └── admin/           # 管理模块
├── frontend/            # 前端代码
│   └── src/             # Vue 源码
├── cli/                 # 命令行工具
├── downloads/           # 下载目录 (需创建)
├── cookies/             # Cookies 目录 (需创建)
├── logs/                # 日志目录 (需创建)
├── data/                # 数据目录 (需创建)
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
└── README.md            # 文档
```

---

## 联系方式

- 问题反馈: GitHub Issues
- 功能建议: GitHub Discussions

---

*© 2026 Bosco Tsang. All rights reserved.*
