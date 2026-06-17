# Bosco Tsang 使用说明书

## 📖 目录

- [系统简介](#系统简介)
- [快速开始](#快速开始)
- [Docker 部署指南](#docker-部署指南)
- [功能使用说明](#功能使用说明)
- [平台配置指南](#平台配置指南)
- [常见问题](#常见问题)
- [技术支持](#技术支持)

---

## 系统简介

**Bosco Tsang** 是一个全平台视频/音乐/图片下载系统，支持 3000+ 平台的资源下载。

### 核心功能

- 🎬 **视频下载** - YouTube、Bilibili、抖音、Twitter 等
- 🎵 **音乐下载** - Apple Music、Spotify、网易云音乐、QQ音乐等
- 📷 **图片下载** - Instagram、微博、Twitter 等
- 📡 **订阅管理** - 自动监控频道更新
- 🔐 **Telegram 登录** - 使用 Telegram 账号登录系统
- 🤖 **Telegram Bot** - 通过 Telegram Bot 远程下载
- 🌐 **Web 界面** - 美观的管理后台
- 📱 **浏览器插件** - 快速下载当前页面资源

---

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 内存
- 50GB+ 磁盘空间

### 一键部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd BoscoTsang

# 2. 启动服务
docker-compose up -d --build

# 3. 访问系统
# 浏览器打开: http://localhost:8080
# 默认账号: admin / admin123
```

---

## Docker 部署指南

### 方式一：从源码构建（推荐）

**适用场景：** 开发环境、需要自定义配置

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

### 方式二：使用预构建镜像

**适用场景：** 生产环境、快速部署

```bash
# 拉取最新镜像
docker pull boscotom/bosco-tsang:latest

# 运行容器
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

### 方式三：使用 docker-compose（生产推荐）

**docker-compose.yml 配置：**

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
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; s = socket.socket(); result = s.connect_ex(('localhost', 8000)); s.close(); exit(0 if result == 0 else 1)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**启动命令：**

```bash
docker-compose up -d
```

### 目录结构

```
BoscoTsang/
├── downloads/          # 下载文件存储
│   ├── youtube/       # YouTube 下载
│   ├── bilibili/      # B站下载
│   ├── x/            # Twitter 下载
│   └── ...
├── cookies/           # Cookies 文件
│   ├── x.txt         # Twitter Cookies
│   ├── youtube.txt   # YouTube Cookies
│   └── ...
├── data/             # 数据库文件
│   └── bosco.db
├── logs/             # 运行日志
│   └── app_2026-06-16.log
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### 常用命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f bosco-tsang

# 进入容器
docker exec -it bosco-tsang /bin/bash

# 更新镜像
docker-compose pull
docker-compose up -d --build

# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz downloads/ data/ cookies/

# 清理无用镜像
docker image prune -a
```

---

## 功能使用说明

### 1. 视频下载

#### Web 界面下载

1. 登录系统
2. 进入 **下载** 页面
3. 粘贴视频链接
4. 选择下载质量
5. 点击 **开始下载**

**支持的平台：**
- YouTube: `https://youtube.com/watch?v=...`
- Bilibili: `https://bilibili.com/video/...`
- 抖音: `https://douyin.com/video/...`
- Twitter: `https://x.com/user/status/...`
- 以及 3000+ 其他平台

#### Telegram Bot 下载

1. 在 Telegram 中找到您的 Bot
2. 发送 `/start` 开始
3. 直接发送视频链接
4. Bot 自动下载并通知您

**支持的命令：**
- `/start` - 开始使用
- `/help` - 查看帮助
- `/status` - 查看下载状态

### 2. 音乐下载

**步骤：**
1. 复制音乐链接
2. 粘贴到下载框
3. 选择格式（MP3/M4A）
4. 开始下载

**支持的平台：**
- Apple Music
- Spotify
- 网易云音乐
- QQ音乐
- SoundCloud

### 3. 图片下载

**步骤：**
1. 复制图片页面链接
2. 粘贴到下载框
3. 系统自动识别并下载所有图片

**支持的平台：**
- Instagram
- 微博
- Twitter/X
- Pinterest

### 4. 订阅管理

**创建订阅：**
1. 进入 **订阅** 页面
2. 点击 **添加订阅**
3. 输入频道链接
4. 设置检查间隔
5. 保存订阅

**功能：**
- 自动监控更新
- 自动下载新内容
- 可暂停/恢复订阅
- 查看订阅统计

### 5. 文件管理

**功能：**
- 📁 浏览下载的文件
- ▶️ 在线播放视频
- ⬇️ 下载文件到本地
- ✏️ 重命名文件
- 🗑️ 删除文件
- 📊 查看文件信息

### 6. Telegram 登录

#### 配置步骤

1. **创建 Telegram Bot**
   - 联系 [@BotFather](https://t.me/BotFather)
   - 发送 `/newbot`
   - 获取 Bot Token

2. **系统配置**
   - 进入 **设置** → **Telegram**
   - 填写 Bot Token
   - 开启 **启用 Telegram 登录**
   - 开启 **允许下载功能**
   - 保存设置

3. **前端配置**
   - 编辑 `frontend/src/views/Login.vue`
   - 替换 `data-telegram-login` 为您的 Bot Username
   - 重新构建前端

4. **使用登录**
   - 访问登录页面
   - 点击 **使用 Telegram 登录**
   - 授权登录
   - 首次使用需绑定系统账号

### 7. X/Twitter 下载

#### 获取 Cookies

**方法一：浏览器扩展（推荐）**

1. 安装 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
2. 登录 X/Twitter
3. 点击扩展图标
4. 导出 Cookies
5. 复制全部内容

**方法二：开发者工具**

1. 按 F12 打开开发者工具
2. Application → Cookies
3. 复制所需 Cookies

#### 配置系统

1. 进入 **设置** → **X/Twitter**
2. 粘贴 Cookies
3. 配置下载选项：
   - ✅ 下载视频
   - ✅ 下载图片
   - ✅ 最高画质
   - 选择质量
4. 保存设置

#### 下载内容

- 视频推文
- GIF 动画
- 图片推文
- 长推文（Thread）

---

## 平台配置指南

### YouTube

**Cookies 配置（可选）：**
- 下载会员专享视频需要 Cookies
- 避免频率限制

**推荐设置：**
- 质量：1080p 或最佳
- 格式：MP4

### Bilibili

**特殊说明：**
- 系统已自动处理 B站防盗链
- 无需额外配置

**推荐设置：**
- 质量：1080p
- 需要大会员才能下载高画质

### X/Twitter

**必须配置：**
- Cookies 是必需的
- 否则无法下载私密内容

**推荐设置：**
- 开启视频下载
- 开启图片下载
- 最高画质

### Telegram

**Bot Token 获取：**
1. 联系 @BotFather
2. 创建新 Bot
3. 复制 Token

**用户 ID 获取：**
1. 联系 @userinfobot
2. 发送任意消息
3. 获取您的 ID

---

## 常见问题

### Q1: 下载失败怎么办？

**检查项：**
1. 链接是否正确
2. Cookies 是否有效
3. 磁盘空间是否充足
4. 网络连接是否正常

**解决方法：**
- 更新 Cookies
- 检查日志：`docker logs bosco-tsang`
- 重试下载

### Q2: 视频无法在线播放？

**可能原因：**
- 浏览器不支持视频编码（如 AV1）
- 系统会自动转码为 H.264

**解决方法：**
- 等待转码完成
- 下载后使用本地播放器

### Q3: Telegram Bot 无响应？

**检查项：**
1. Bot Token 是否正确
2. Telegram 登录功能是否启用
3. 用户 ID 是否在允许列表中
4. 网络连接是否正常

**解决方法：**
- 重新配置 Bot Token
- 检查系统日志
- 重启服务

### Q4: 如何更新系统？

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose down
docker-compose up -d --build

# 或使用预构建镜像
docker-compose pull
docker-compose up -d
```

### Q5: 如何备份数据？

```bash
# 备份所有数据
tar -czf backup-$(date +%Y%m%d).tar.gz \
  downloads/ \
  data/ \
  cookies/ \
  logs/

# 恢复数据
tar -xzf backup-20260616.tar.gz
```

### Q6: 如何修改端口？

编辑 `docker-compose.yml`：

```yaml
ports:
  - "8888:8000"  # 改为 8888 端口
```

然后重启：

```bash
docker-compose down
docker-compose up -d
```

---

## 技术支持

### 获取帮助

- 📖 查看 [更新日志](CHANGELOG.md)
- 🐛 提交 Issue
- 💬 联系开发团队

### 系统日志

```bash
# 查看实时日志
docker logs -f bosco-tsang

# 查看应用日志
docker exec bosco-tsang tail -f /app/logs/app_$(date +%Y-%m-%d).log

# 导出日志
docker cp bosco-tsang:/app/logs/ ./logs-backup/
```

### 性能优化

**建议配置：**
- 内存：8GB+
- CPU：4 核心+
- 磁盘：SSD
- 网络：稳定宽带

**优化建议：**
- 定期清理旧文件
- 限制并发下载数
- 使用代理加速（如需要）

---

## 附录

### A. 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `APP_BASE_DIR` | 应用根目录 | `/app` |
| `DOWNLOAD_DIR` | 下载目录 | `/app/downloads` |
| `COOKIES_DIR` | Cookies 目录 | `/app/cookies` |
| `LOGS_DIR` | 日志目录 | `/app/logs` |
| `TZ` | 时区 | `Asia/Shanghai` |

### B. 端口说明

- **8000** - 容器内服务端口
- **8080** - 宿主机映射端口（可修改）

### C. 默认账号

- **用户名：** admin
- **密码：** admin123

**⚠️ 重要：** 首次登录后请立即修改密码！

### D. 支持的平台（部分）

- YouTube
- Bilibili
- 抖音
- 快手
- Twitter/X
- Instagram
- 微博
- 小红书
- Apple Music
- Spotify
- 网易云音乐
- QQ音乐
- TikTok
- ... 以及 3000+ 其他平台

---

**版本：** v0.3.0  
**更新日期：** 2026-06-16  
**文档维护：** Bosco Tsang 开发团队
