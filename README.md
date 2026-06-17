# Bosco Tsang

🚀 **Bosco Tsang - 全平台视频 / 音乐 / 图片下载系统**

> 集成前端 Vue3 管理面板、FastAPI 后端服务、yt-dlp 下载引擎的完整下载平台。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Telegram](https://img.shields.io/badge/Telegram-Login-blue)
![Twitter](https://img.shields.io/badge/Twitter-Download-black)

## 📌 项目简介

Bosco Tsang 是一个基于 Docker 的全能内容下载系统，支持多平台抓取、订阅管理、代理配置、用户权限、API Key 与下载统计。

## ✨ 核心功能

### 下载功能
- ✅ 多平台下载：YouTube、Bilibili、抖音、快手、Instagram、QQ音乐、网易云音乐、Apple Music、Twitter/X、微信视频号等
- ✅ 视频 / 音频 / 图片下载与提取
- ✅ 下载任务管理与进度查看
- ✅ 订阅管理：自动监控频道更新并自动下载
- ✅ 浏览器扩展：快速下载当前页面资源

### Telegram 生态集成 🆕
- ✅ **Telegram 账号登录** - 使用 Telegram Widget 一键登录
- ✅ **Telegram Bot 下载** - 通过 Bot 远程发送链接即可下载
- ✅ **实时进度推送** - 下载进度实时通知
- ✅ **用户权限控制** - 可配置允许的用户 ID

### X/Twitter 专属下载 🆕
- ✅ **Cookies 配置** - 支持 Netscape HTTP Cookie 格式
- ✅ **视频下载** - 自动下载推文中的视频和 GIF
- ✅ **图片下载** - 支持多图片推文、原始尺寸下载
- ✅ **画质控制** - 360p-1080p 多档可选

### 用户与系统管理
- ✅ 用户管理：管理员面板支持用户新增、编辑、启停、删除
- ✅ 邀请码注册：新用户支持邀请码激活注册
- ✅ API Key 管理：生成、启用/禁用、删除 API Key
- ✅ 代理设置：Web 控制台可配置 HTTP/HTTPS 代理
- ✅ 下载历史与统计分析
- ✅ 日志查看与诊断
- ✅ 命令行工具：支持登录、下载、历史查询、订阅管理、统计查看
- ✅ Docker Compose 一键部署

## 🧱 项目结构

```
BoscoTsang-0.1/
├── backend/              # FastAPI 后端服务
│   ├── main.py          # 后端应用入口
│   └── admin/           # 管理模块与数据持久化逻辑
├── frontend/            # Vue 3 前端源码
│   └── src/             # 单页应用源代码
├── cli/                 # 命令行客户端脚本
├── cookies/             # 浏览器 Cookie 存放目录
├── data/                # SQLite 数据库与持久化数据
├── downloads/           # 下载文件输出目录
├── docs/                # 文档说明
├── Dockerfile           # Docker 镜像构建文件
├── docker-compose.yml   # Docker Compose 部署配置
└── README.md            # 项目说明文档
```

## 🚀 快速部署（推荐）

### 1. 克隆仓库

```bash
git clone https://github.com/BoscoTsang-Z/BoscoTsang-0.1.git
cd BoscoTsang-0.1
```

### 2. 启动容器

```bash
docker-compose up -d --build
```

### 3. 访问应用

- Web 管理界面：`http://localhost:8080`

### 4. 默认管理员账号

- 用户名：`admin`
- 密码：`admin123`

> 初始化后请尽快修改默认管理员密码。

## 🐳 Docker Compose 部署说明

`docker-compose.yml` 已经配置：

- 通过本地 `Dockerfile` 构建镜像
- 将前端静态资源打包到容器 `/app/static`
- 持久化目录映射到宿主机
- 端口映射 `8080:8000`
- 支持代理环境变量配置
- 启用 `restart: unless-stopped`
- 包含简单健康检查

## 📂 持久化目录说明

| 本地目录 | 容器路径 | 说明 |
|----------|----------|------|
| `./downloads` | `/app/downloads` | 下载文件输出目录 |
| `./cookies` | `/app/cookies` | Cookie 输入目录 |
| `./data` | `/app/data` | SQLite 数据库和应用数据 |
| `./logs` | `/app/logs` | 日志文件 |

## ⚙️ 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_BASE_DIR` | `/app` | 应用根目录 |
| `HTTP_PROXY` | 空 | 可选 HTTP 代理地址 |
| `HTTPS_PROXY` | 空 | 可选 HTTPS 代理地址 |

> 如果需要下载通过代理访问，请在 `docker-compose.yml` 或环境中设置 `HTTP_PROXY` / `HTTPS_PROXY`。

## 💻 Web 控制台功能

- `Dashboard`：总览与下载入口
- `Downloads`：下载任务列表与控制
- `History`：下载历史记录与结果查看
- `Subscriptions`：订阅管理与自动下载
- `Settings`：代理设置、平台配置、用户管理、API Key、邀请码管理
- `Logs`：运行日志查看

## 🧰 命令行工具使用

CLI 脚本位于 `cli/bosco.py`，支持常用操作：

```bash
python3 cli/bosco.py login -u admin -p admin123
python3 cli/bosco.py whoami
python3 cli/bosco.py url "https://youtube.com/watch?v=xxx"
python3 cli/bosco.py his
python3 cli/bosco.py mon
```

## 🍪 Cookies 配置

部分平台需要 Cookie 才能下载高清内容：

1. 使用浏览器插件导出 `cookies.txt`
2. 将文件命名为对应平台，例如 `youtube.txt`、`bilibili.txt`
3. 复制到项目根目录 `cookies/` 下

## 🌐 支持平台

主要支持：

- YouTube / YouTube Music
- Bilibili
- 抖音 / TikTok
- 快手
- 小红书
- 微博
- Twitter / X
- Instagram
- QQ音乐
- 网易云音乐
- Apple Music
- Telegram
- 微信视频号

> 系统基于 `yt-dlp`，还可支持更多平台，详情请参考 `yt-dlp` 官方文档。

## 📖 文档链接

### 快速开始
- 📘 [使用说明书](USAGE_MANUAL.md) - 详细功能说明和配置指南
- 🚀 [部署指南](DEPLOYMENT.md) - Docker 部署方式和发布流程
- ⚡ [快速参考](QUICK_REFERENCE.md) - 常用命令速查表

### 版本管理
- 📝 [更新日志](CHANGELOG.md) - 版本变更记录
- 🔄 [版本更新工作流](RELEASE_WORKFLOW.md) - 如何更新版本并推送

### 技术文档
- 🏗️ [系统架构分析](docs/SYSTEM_ANALYSIS.md) - 系统架构设计
- 📚 [使用教程](docs/USAGE.md) - 基础使用说明

## 🔒 安全建议

1. 启动后修改默认管理员密码
2. 建议配合 HTTPS / 反向代理使用
3. 定期备份 `data/`, `cookies/`, `downloads/`, `logs/`
4. 仅在可信网络环境中部署

## 🌐 快速下载浏览器扩展

项目提供一个简单的 Chrome / Edge 浏览器扩展示例，支持通过 API Key 直接将页面链接发送到后台下载队列。

### 1. 生成 API Key

- 登录系统后台 → `Settings` → `访问密钥` → `创建`。
- 记录生成的完整密钥。

### 2. 安装扩展

1. 打开 Chrome/Edge 扩展程序页面。
2. 启用“开发者模式”。
3. 选择“加载已解压的扩展程序”，然后选择 `extensions/quick-download/` 目录。

### 3. 使用扩展

- 在扩展弹窗中填写服务器地址，例如 `http://localhost:8080`
- 填入 API Key
- 扩展会自动读取当前标签页 URL，也可手动输入下载链接
- 选择下载质量，点击“快速下载`

> 扩展会调用 `/api/quick-download` 接口，将任务直接加入后台下载队列。

### 4. 右键快速下载

扩展还支持页面和链接右键菜单：

- 右键页面空白处选择“Bosco Tsang 快速下载当前页面”
- 右键链接选择“Bosco Tsang 快速下载链接”

扩展会自动将链接写入弹窗并打开快速下载界面。

## 🤝 贡献

欢迎提交 Issue、Bug 报告和 Pull Request。

## 📄 License

MIT License
