# Bosco Tsang v1.0.0 改善版

> 全平台视频/音乐/图片下载系统 · 集成 Telegram/QQ/微信 Bot

## ✨ 新增功能（v1.0.0 改善版）

### 🔒 安全加固
- **bcrypt 密码哈希** — 替代不安全的 SHA-256，自动迁移旧密码
- **JWT Token** — 替代内存 Token，72 小时过期，重启不丢失登录态
- **CORS 白名单** — 替代 `*` 通配符，从配置文件读取
- **API 限流** — 登录 10次/分、注册 5次/分、下载 30次/分

### 🏗️ 架构重构
- **路由分离** — `main.py` 从 1911 行精简到 ~200 行
- **分层架构** — `routers/` + `services/` + `models/`
- **模块化** — 每个功能独立文件，易于维护和扩展

```
backend/
├── main.py              # 入口（路由注册 + 中间件）
├── routers/             # API 路由
│   ├── auth_router.py       # 登录/注册
│   ├── download_router.py   # 下载任务
│   ├── files_router.py      # 文件管理
│   ├── users_router.py      # 用户管理
│   ├── subscriptions_router.py  # 订阅
│   ├── settings_router.py   # 设置/统计/API Key
│   ├── telegram_router.py   # Telegram 登录/绑定
│   └── bot_router.py        # Bot Webhook 路由
├── services/            # 业务逻辑
│   ├── download_service.py  # 下载引擎
│   ├── platform_service.py  # 平台检测/Cookies
│   └── bot_gateway.py       # 统一 Bot 网关
├── models/              # 数据模型
│   └── schemas.py           # Pydantic 模型
└── admin/               # 核心模块
    ├── auth.py              # JWT 认证
    ├── db.py                # SQLite 数据库
    ├── telegram_bot.py      # Telegram Bot
    ├── qq_bot.py            # QQ Bot (OneBot)
    ├── wechat_bot.py        # 微信 ClawBot
    └── twitter_downloader.py # Twitter 下载
```

### 🤖 统一 Bot 网关
所有机器人共享同一套命令和逻辑：

| 命令 | 功能 |
|------|------|
| `/dl <链接> [画质]` | 下载视频/音频 |
| `/list` | 查看下载任务 |
| `/history` | 下载历史 |
| `/stats` | 下载统计 |
| `/status` | 系统状态 |
| `/bind <用户名> <密码>` | 绑定系统账户 |

**支持平台：**
- ✅ Telegram — Inline Keyboard + Widget 登录
- ✅ QQ — OneBot v11 协议（Lagrange / NapCat）
- ✅ 微信 — ClawBot Webhook 模式

### 📱 Telegram Bot
- 发送链接自动下载
- Inline Keyboard 选择画质
- 下载进度实时通知
- 群组支持
- `/start` `/help` 命令

### 🐧 QQ 机器人
- 基于 OneBot v11 协议
- 支持 Lagrange / NapCat / go-cqhttp
- 群聊 + 私聊
- 自动识别链接并下载

### 💬 微信 ClawBot
- Webhook 双向消息
- 下载完成自动回复
- 通过 OpenClaw 集成

### 📦 iOS 快捷指令
- `/shortcuts` 安装引导页
- 自动检测 iOS 环境
- URL Scheme 一键安装
- 首次使用引导开启权限

---

## 🚀 快速部署

### 方式一：Docker Compose（推荐）

```bash
# 克隆改善版
git clone -b dev-improve https://github.com/SaveBTube/SaveBTube-xm.git
cd SaveBTube-xm

# 启动主服务
docker compose up -d --build

# 访问
# Web 控制台: http://localhost:8080
# 默认账号: admin / admin123
```

### 方式二：包含 QQ Bot

```bash
# 启动主服务 + QQ Bot
docker compose --profile qq up -d --build

# QQ Bot 配置
# 1. 编辑 qq-bot-data/appsettings.json（首次启动后生成）
# 2. 填入 QQ 账号信息
# 3. 设置上报地址: http://bosco-tsang:8000/api/bot/qq/webhook
# 4. 重启: docker compose --profile qq restart qq-bot
```

---

## ⚙️ 配置指南

### Telegram Bot 配置

1. 找 @BotFather 创建 Bot，获取 Token
2. 进入 Web 控制台 → 设置 → 平台设置 → Telegram
3. 填入 Bot Token
4. 开启「Telegram 登录」和「下载功能」
5. （可选）填入允许的用户 ID

### QQ 机器人配置

1. 部署 Lagrange（Docker 自带或独立部署）
2. 登录 QQ 账号
3. 设置 HTTP POST 上报地址: `http://your-server:8080/api/bot/qq/webhook`
4. 在 Web 控制台 → 设置 → 平台设置 → QQ 机器人
5. 填入 OneBot HTTP API 地址（如 `http://localhost:3000`）

### 微信 ClawBot 配置

1. 部署 OpenClaw/ClawBot
2. 在 Web 控制台 → 设置 → 平台设置 → 微信 ClawBot
3. 填入 ClawBot 回调 URL
4. 在 ClawBot 中设置消息转发地址: `http://your-server:8080/api/bot/wechat/webhook`

### 代理配置

在设置 → 网络代理中配置：
- **关闭** — 不使用代理
- **全局** — 所有请求走代理
- **自动** — 国内站点直连，国外走代理

---

## 🔌 API 接口

### 认证
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/admin/login` | POST | 登录（返回 JWT） |
| `/api/admin/register` | POST | 注册 |

### 下载
| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/download` | POST | ✅ | 发起下载 |
| `/api/quick-download` | POST | ✅ | 快速下载（浏览器扩展） |
| `/api/shortcuts/download` | POST | API Key | iOS 快捷指令 |
| `/api/progress/{id}` | GET | ✅ | 下载进度 |
| `/api/downloads` | GET | ✅ | 任务列表 |

### 文件
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/files` | GET | 文件列表 |
| `/api/files/stream/{path}` | GET | 流式播放（支持 Range） |
| `/api/files/{path}` | GET | 下载文件 |

### Bot 网关
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/bot/qq/webhook` | POST | QQ 消息接收 |
| `/api/bot/wechat/webhook` | POST | 微信消息接收 |
| `/api/bot/status` | GET | Bot 状态 |

### 设置
| 端点 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/settings` | GET | Admin | 读取设置 |
| `/api/settings` | POST | Admin | 保存设置 |
| `/api/settings/test-proxy` | POST | Admin | 测试代理 |

---

## 🛡️ 安全说明

- 密码使用 **bcrypt** 哈希存储（带 salt）
- Token 使用 **JWT** 签名（HS256，72 小时过期）
- CORS 从配置读取白名单
- API 接口有速率限制
- 文件路径经过安全校验（防止目录遍历）

---

## 📋 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_BASE_DIR` | `/app` | 应用根目录 |
| `HTTP_PROXY` | 空 | HTTP 代理 |
| `HTTPS_PROXY` | 空 | HTTPS 代理 |
| `TZ` | `Asia/Shanghai` | 时区 |

---

## 📂 持久化目录

| 本地目录 | 容器路径 | 说明 |
|----------|----------|------|
| `./downloads` | `/app/downloads` | 下载文件 |
| `./cookies` | `/app/cookies` | Cookies 文件 |
| `./data` | `/app/data` | SQLite 数据库 |
| `./logs` | `/app/logs` | 运行日志 |
| `./qq-bot-data` | `/app/data` | QQ Bot 数据（可选） |

---

## 🧰 CLI 命令

```bash
python3 cli/bosco.py login -u admin -p admin123
python3 cli/bosco.py whoami
python3 cli/bosco.py url "https://youtube.com/watch?v=xxx"
python3 cli/bosco.py his
python3 cli/bosco.py mon
```

---

## 🍪 Cookies 配置

部分平台需要 Cookie 才能下载高清内容：

1. 使用浏览器插件导出 `cookies.txt`（Netscape 格式）
2. 命名为平台名：`youtube.txt`、`bilibili.txt`、`x.txt`
3. 放入 `cookies/` 目录

---

## ❓ 常见问题

**Q: 下载失败怎么办？**
A: 检查日志（设置 → 日志），常见原因：Cookie 过期、代理不通、平台限制。

**Q: QQ Bot 无法连接？**
A: 确认 Lagrange 已启动，检查 API 地址是否正确，查看 `/api/bot/status`。

**Q: iOS 快捷指令安装提示不受信任？**
A: 前往 设置 → 快捷指令 → 开启「允许不受信任的快捷指令」。

**Q: 如何更新版本？**
A: `git pull && docker compose up -d --build`

---

## 📄 License

MIT License
