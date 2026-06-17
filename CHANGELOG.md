# 更新日志

本文件记录所有重要变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [v1.0.0-improve] - 2026-06-17

### 🔒 安全加固
- **密码哈希**: SHA-256 → bcrypt，支持旧密码自动迁移
- **Token**: 内存存储 → JWT（HS256，72 小时过期）
- **CORS**: 通配符 `*` → 配置文件白名单
- **限流**: 登录 10次/分、注册 5次/分、下载 30次/分

### 🏗️ 架构重构
- `main.py` 从 1911 行精简到 ~200 行
- 新增 `backend/routers/` 目录（7 个路由文件）
- 新增 `backend/services/` 目录（3 个服务文件）
- 新增 `backend/models/` 目录（Pydantic 模型）

### ✨ 新功能
- **统一 Bot 网关**: 所有机器人共享命令和逻辑
- **QQ 机器人**: OneBot v11 协议适配器（Lagrange/NapCat）
- **微信 ClawBot**: Webhook 双向消息集成
- **iOS 快捷指令**: `/shortcuts` 安装引导页
- **Telegram Inline Keyboard**: 支持画质选择按钮

### 🐳 Docker
- 新增 QQ Bot Lagrange 可选服务（`--profile qq`）
- 多容器编排优化

### 📦 前端
- 设置页新增 QQ 机器人配置标签页
- 设置页新增微信 ClawBot 配置标签页
- Bot 状态显示

---

## [v0.3.0] - 2026-06-16

### ✨ 新功能
- Telegram Widget 登录
- Telegram Bot 下载
- X/Twitter 专属下载器
- 浏览器扩展快速下载
- iOS 快捷指令集成

---

## [v0.2.0] - 2026-06-10

### ✨ 新功能
- 浏览器扩展
- 订阅管理
- API Key 管理

---

## [v0.1.0] - 2026-06-01

### ✨ 首次发布
- 核心下载功能（yt-dlp）
- Web 管理界面
- 用户管理
- Docker 部署
