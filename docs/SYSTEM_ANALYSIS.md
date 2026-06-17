# Bosco Tsang 系统分析报告

## 一、系统概述

**Bosco Tsang** 是一款基于 Web 的全平台多媒体内容下载管理系统，核心功能是支持从 YouTube、Bilibili、抖音、快手、小红书等 3000+ 平台下载视频、音频和图片内容。

### 1.1 系统定位
- **目标用户**: 需要批量下载视频/音频内容的企业或个人用户
- **应用场景**: 内容创作者素材收集、数据备份、离线观看等
- **部署方式**: 主要面向 NAS（群晖、极空间）、服务器等私有化部署

### 1.2 核心价值
| 维度 | 描述 |
|------|------|
| 🎯 **便捷性** | Web 界面操作，无需命令行 |
| 🌐 **全面性** | 3000+ 平台支持 |
| 🔒 **安全性** | 本地部署，数据自主控制 |
| ⚡ **高效性** | 支持批量下载、订阅自动更新 |
| 📊 **可观测性** | 完整的数据统计和日志系统 |

---

## 二、技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户端                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Web UI    │  │    CLI      │  │   API       │      │
│  │  (Vue 3)    │  │  (Python)   │  │  (REST)     │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
└─────────┼───────────────┼───────────────┼──────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                    ┌─────▼─────┐
                    │  FastAPI  │
                    │   Backend │
                    └─────┬─────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  SQLite   │   │  yt-dlp  │   │  FFmpeg   │
    │  Database │   │ Download │   │  Convert  │
    └───────────┘   └───────────┘   └───────────┘
```

### 2.2 技术栈详解

#### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | ^3.5 | 核心框架，组合式 API |
| **Vue Router** | ^4.5 | 页面路由管理 |
| **Chart.js** | ^4.4 | 数据可视化图表 |
| **vue-chartjs** | ^5.3 | Vue 3 图表封装 |
| **Axios** | ^1.7 | HTTP 请求库 |
| **Vite** | ^8.0 | 构建工具 |

#### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10 | 运行环境 |
| **FastAPI** | latest | Web 框架 |
| **uvicorn** | latest | ASGI 服务器 |
| **yt-dlp** | latest | 视频下载引擎 |
| **SQLAlchemy** | - | ORM（可选） |
| **SQLite** | 3 | 关系数据库 |

#### 基础设施
| 技术 | 用途 |
|------|------|
| **Docker** | 容器化部署 |
| **Docker Compose** | 多容器编排 |
| **FFmpeg** | 音视频格式转换 |

### 2.3 核心模块设计

#### 认证模块
```
┌─────────────────────────────────────────┐
│              认证流程                     │
├─────────────────────────────────────────┤
│  1. 用户登录 POST /api/admin/login       │
│  2. 验证用户名密码                       │
│  3. 生成 JWT Token                      │
│  4. 后续请求携带 Token                   │
│  5. 中间件验证 Token                     │
└─────────────────────────────────────────┘
```

#### 下载模块
```
┌─────────────────────────────────────────┐
│              下载流程                     │
├─────────────────────────────────────────┤
│  1. 接收 URL 和质量参数                  │
│  2. 平台检测（YouTube/Bilibili等）       │
│  3. 自动匹配 Cookies 文件                │
│  4. 创建下载任务（数据库记录）            │
│  5. 异步执行下载（Threading）            │
│  6. 实时推送进度（轮询）                  │
│  7. 完成通知 + 统计更新                  │
└─────────────────────────────────────────┘
```

---

## 三、功能模块分析

### 3.1 模块清单

| 模块 | 功能 | 优先级 |
|------|------|--------|
| 🔐 **用户认证** | 登录、注册、Token 管理 | P0 |
| ⬇️ **下载管理** | 创建下载任务、实时进度 | P0 |
| 📜 **历史记录** | 下载历史、筛选、删除 | P1 |
| 📡 **订阅管理** | 频道订阅、自动更新 | P1 |
| 📊 **仪表盘** | 数据统计、趋势图表 | P1 |
| 📋 **运行日志** | 系统日志、错误追踪 | P2 |
| 💻 **系统监控** | CPU/内存/磁盘监控 | P2 |
| ⚙️ **设置中心** | 账户、用户、API密钥管理 | P1 |

### 3.2 数据库设计

#### 用户表 (users)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT DEFAULT 'user',
    avatar TEXT,
    created_at TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
```

#### 下载任务表 (download_tasks)
```sql
CREATE TABLE download_tasks (
    id INTEGER PRIMARY KEY,
    task_id TEXT UNIQUE,
    url TEXT,
    title TEXT,
    platform TEXT,
    resource_type TEXT,
    resolution TEXT,
    file_size INTEGER,
    status TEXT,
    progress REAL,
    speed TEXT,
    error_message TEXT,
    user_id INTEGER,
    created_at TIMESTAMP,
    finished_at TIMESTAMP
);
```

#### 下载历史表 (download_history)
```sql
CREATE TABLE download_history (
    id INTEGER PRIMARY KEY,
    task_id TEXT,
    url TEXT,
    title TEXT,
    platform TEXT,
    resource_type TEXT,
    resolution TEXT,
    file_size INTEGER,
    status TEXT,
    user_id INTEGER,
    created_at TIMESTAMP,
    finished_at TIMESTAMP
);
```

#### 订阅表 (subscriptions)
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    sub_id TEXT UNIQUE,
    channel_name TEXT,
    channel_url TEXT,
    platform TEXT,
    poll_interval INTEGER,
    last_check TIMESTAMP,
    status TEXT,
    total_downloads INTEGER,
    user_id INTEGER
);
```

#### API密钥表 (api_keys)
```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    key_id TEXT UNIQUE,
    key_hash TEXT,
    key_prefix TEXT,
    note TEXT,
    status TEXT,
    user_id INTEGER,
    created_at TIMESTAMP,
    last_used TIMESTAMP
);
```

---

## 四、API 接口设计

### 4.1 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login` | 用户登录 |
| POST | `/api/admin/register` | 用户注册 |
| GET | `/api/admin/me` | 获取当前用户 |
| POST | `/api/admin/password` | 修改密码 |

### 4.2 下载接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/download` | 创建下载任务 |
| GET | `/api/progress/{task_id}` | 获取下载进度 |
| GET | `/api/downloads` | 列出下载任务 |
| DELETE | `/api/tasks/{task_id}` | 删除任务 |

### 4.3 历史接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/history` | 下载历史列表 |
| DELETE | `/api/history` | 删除历史记录 |
| DELETE | `/api/history/all` | 清空所有历史 |

### 4.4 文件接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/files` | 列出文件 |
| GET | `/api/files/{filename}` | 下载文件 |
| DELETE | `/api/files/{filename}` | 删除文件 |
| POST | `/api/files/rename` | 重命名文件 |

### 4.5 订阅接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/subscriptions` | 订阅列表 |
| POST | `/api/subscriptions` | 添加订阅 |
| PUT | `/api/subscriptions/{sub_id}` | 更新订阅 |
| DELETE | `/api/subscriptions/{sub_id}` | 删除订阅 |

### 4.6 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/statistics` | 获取统计数据 |
| GET | `/api/logs` | 获取运行日志 |

---

## 五、支持的平台列表

### 5.1 视频平台

| 平台 | 代码 | 备注 |
|------|------|------|
| YouTube | youtube.com | 支持 4K |
| Bilibili | bilibili.com | 支持番剧 |
| 抖音 | douyin.com | 支持主页下载 |
| 快手 | kuaishou.com | - |
| 小红书 | xiaohongshu.com | - |
| 微博 | weibo.com | - |
| Twitter/X | twitter.com | - |
| TikTok | tiktok.com | - |
| Instagram | instagram.com | - |
| 微信视频号 | channels.weixin | - |

### 5.2 音乐平台

| 平台 | 代码 | 备注 |
|------|------|------|
| 网易云音乐 | music.163.com | 支持 VIP |
| QQ音乐 | y.qq.com | - |
| Apple Music | apple.co | - |

### 5.3 其他平台

| 平台 | 代码 | 备注 |
|------|------|------|
| Telegram | t.me | 频道/群组 |
| 今日头条 | toutiao.com | - |

> 📝 yt-dlp 支持的平台总数超过 **3000+**，完整列表请参考 yt-dlp 官方文档。

---

## 六、安全性分析

### 6.1 认证机制
- ✅ Token 基于时间的动态令牌
- ✅ 密码使用 SHA256 哈希存储
- ✅ 邀请码机制控制注册
- ⚠️ 可选: 双因子认证 (2FA)

### 6.2 权限控制
- ✅ 角色区分: 管理员 / 普通用户
- ✅ API 密钥独立管理
- ✅ 可禁用/启用用户

### 6.3 数据安全
- ✅ 本地化部署，数据不外传
- ✅ Cookies 文件本地存储
- ⚠️ 建议配合 HTTPS 使用

---

## 七、性能优化建议

### 7.1 并发下载
- 当前: 单任务串行下载
- 建议: 使用 ThreadPoolExecutor 实现多任务并发

### 7.2 缓存策略
- 订阅检查结果缓存
- 平台信息缓存

### 7.3 数据库优化
- 定期清理历史记录
- 索引优化

### 7.4 前端优化
- 路由懒加载
- 组件按需引入

---

## 八、部署架构建议

### 8.1 最小部署
```
硬件: 1核 CPU, 1GB RAM
存储: 10GB+
用途: 个人使用，小规模下载
```

### 8.2 推荐部署
```
硬件: 2核 CPU, 4GB RAM
存储: 100GB+ (根据下载量)
用途: 家庭/团队共享
```

### 8.3 企业部署
```
硬件: 4核 CPU, 8GB RAM
存储: 500GB+ SSD
用途: 多用户，高并发
```

---

## 九、扩展功能规划

| 功能 | 状态 | 说明 |
|------|------|------|
| 🔄 断点续传 | 待开发 | 支持大文件断点续传 |
| 📱 移动端适配 | 待开发 | 响应式 UI |
| 🔔 通知推送 | 待开发 | 邮件/推送通知 |
| 📦 批量导入 | 待开发 | CSV/URL 列表导入 |
| ☁️ 云同步 | 待开发 | 多设备同步 |

---

*报告生成时间: 2026-06-14*
