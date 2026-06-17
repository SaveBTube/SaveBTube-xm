# Bosco Tsang v1.0.0 使用说明书

> 全平台视频/音乐/图片下载系统 · 改善版

---

## 目录

1. [快速开始](#快速开始)
2. [功能说明](#功能说明)
3. [Bot 配置](#bot-配置)
4. [API 接口](#api-接口)
5. [常见问题](#常见问题)

---

## 快速开始

### 一键部署

```bash
# 克隆
git clone -b dev-improve https://github.com/SaveBTube/SaveBTube-xm.git
cd SaveBTube-xm

# 启动
docker compose up -d --build

# 访问
open http://localhost:8080
```

**默认账号：** `admin` / `admin123`

> ⚠️ 首次登录后请立即修改密码！

### 包含 QQ Bot

```bash
docker compose --profile qq up -d --build
```

---

## 功能说明

### 📥 下载功能

**支持平台：** YouTube、Bilibili、抖音、快手、小红书、微博、Twitter/X、Instagram、TikTok、QQ音乐、网易云、Apple Music、Telegram 等 3000+ 平台

**使用方式：**

1. **Web 控制台** — 在 Dashboard 输入链接，选择画质
2. **浏览器扩展** — 一键下载当前页面（需安装插件）
3. **iOS 快捷指令** — 访问 `/shortcuts` 安装
4. **Bot 下载** — 在 Telegram/QQ/微信发链接

**画质选项：**

| 选项 | 说明 |
|------|------|
| best | 最佳画质 |
| 1080p | 1080P |
| 720p | 720P |
| audio | 最佳音频 |
| mp3 | 转换为 MP3 |
| m4a | 转换为 M4A |

### 📁 文件管理

- 浏览所有下载文件
- 在线播放（支持 AV1/HEVC 自动转码）
- 下载到本地
- 重命名、删除、批量操作

### 📊 监控与统计

- CPU / 内存 / 磁盘 / 网络实时监控
- 下载统计（按平台、用户、日期）
- 运行日志查看

### 👥 用户系统

- 管理员 / 普通用户角色
- 邀请码注册
- API Key 管理
- 头像上传

### 📡 订阅管理

- 添加频道/播客链接
- 自动监控新内容
- 自动下载

---

## Bot 配置

### Telegram Bot

**步骤：**

1. 在 Telegram 找 @BotFather，发送 `/newbot` 创建 Bot
2. 获取 Bot Token
3. 进入 Web 控制台 → 设置 → 平台设置 → Telegram
4. 填入 Bot Token
5. 开启「Telegram 登录」和「下载功能」

**Webhook 模式（推荐用于生产环境）：**

在设置中填入 `Telegram Webhook URL`：
```
https://your-domain.com/api/admin/telegram/webhook
```

系统会自动切换到 Webhook 模式，无需轮询。

**Bot 命令：**

| 命令 | 功能 |
|------|------|
| `/start` | 欢迎信息 |
| `/help` | 帮助 |
| `/dl <链接> [画质]` | 下载 |
| `/list` | 任务列表 |
| `/history` | 历史记录 |
| `/stats` | 统计 |
| `/status` | 系统状态 |
| `/bind <用户名> <密码>` | 绑定账户 |

**Inline Keyboard：** 发送链接后，Bot 会弹出画质选择按钮。

### QQ 机器人

**前置要求：** 部署 OneBot v11 协议实现（Lagrange / NapCat）

**Docker 方式（推荐）：**

```bash
# 启动（包含 QQ Bot）
docker compose --profile qq up -d

# 查看登录二维码
docker compose --profile qq logs -f qq-bot

# 编辑配置
vim qq-bot-data/appsettings.json
```

**配置 Webhook：**

在 OneBot 配置中设置 HTTP POST 上报地址：
```
http://your-server:8080/api/bot/qq/webhook
```

在 Web 控制台 → 设置 → 平台设置 → QQ 机器人，填入：
```
OneBot HTTP API 地址: http://localhost:3000
```
（Docker 内使用容器名：`http://bosco-qq-bot:8080`）

**功能：**
- 群聊 + 私聊
- 发送链接自动下载
- 下载完成通知
- 绑定系统账户

### 微信 ClawBot

**前置要求：** 部署 OpenClaw/ClawBot

**配置步骤：**

1. 在 Web 控制台 → 设置 → 平台设置 → 微信 ClawBot
2. 填入 ClawBot 回调 URL
3. 在 ClawBot 中设置消息转发地址：
```
http://your-server:8080/api/bot/wechat/webhook
```

---

## API 接口

### 认证

所有需要认证的接口支持以下方式：
- `Authorization: Bearer <JWT_TOKEN>`
- `X-API-Key: <API_KEY>`
- `?token=<JWT_TOKEN>`

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/login` | POST | 登录 |
| `/api/download` | POST | 发起下载 |
| `/api/downloads` | GET | 任务列表 |
| `/api/progress/{id}` | GET | 下载进度 |
| `/api/files` | GET | 文件列表 |
| `/api/files/stream/{path}` | GET | 流式播放 |
| `/api/history` | GET | 历史记录 |
| `/api/statistics` | GET | 统计数据 |
| `/api/settings` | GET/POST | 系统设置 |

### Bot 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/bot/qq/webhook` | POST | QQ 消息接收 |
| `/api/bot/wechat/webhook` | POST | 微信消息接收 |
| `/api/bot/status` | GET | Bot 状态 |
| `/api/admin/telegram/webhook` | POST | Telegram Webhook |

### WebSocket

```
ws://host:port/ws?token=JWT_TOKEN
```

消息格式：
```json
{
  "type": "download_progress",
  "task_id": "xxx",
  "data": {
    "status": "downloading",
    "percent": 45.2,
    "speed": "1.5 MB/s",
    "eta": "00:30"
  }
}
```

---

## 常见问题

**Q: 下载失败？**
A: 检查：
1. 日志（设置 → 日志）
2. Cookie 是否过期
3. 代理是否正常
4. 平台是否限制

**Q: Bot 收不到消息？**
A: 检查：
1. Bot Token 是否正确
2. Webhook URL 是否可访问
3. 查看 `/api/bot/status`

**Q: iOS 快捷指令安装失败？**
A: 设置 → 快捷指令 → 开启「允许不受信任的快捷指令」

**Q: 如何更新？**
```bash
git pull origin dev-improve
docker compose up -d --build
```

**Q: 如何备份？**
```bash
tar -czf backup.tar.gz downloads/ cookies/ data/ logs/
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_BASE_DIR` | `/app` | 应用根目录 |
| `HTTP_PROXY` | 空 | HTTP 代理 |
| `HTTPS_PROXY` | 空 | HTTPS 代理 |
| `TZ` | `Asia/Shanghai` | 时区 |

---

## 持久化目录

| 目录 | 说明 |
|------|------|
| `downloads/` | 下载文件 |
| `cookies/` | Cookies |
| `data/` | 数据库 |
| `logs/` | 日志 |
| `qq-bot-data/` | QQ Bot 数据（可选） |

---

Bosco Tsang v1.0.0 · MIT License
