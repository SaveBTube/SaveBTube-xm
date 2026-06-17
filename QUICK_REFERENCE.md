# Bosco Tsang - 快速参考指南

## 🚀 快速开始

### 启动服务
```bash
docker-compose up -d --build
```

### 访问系统
- **URL:** http://localhost:8080
- **默认账号:** admin / admin123

---

## 📋 常用命令

### Docker 管理
```bash
# 查看服务状态
docker ps

# 查看日志
docker logs -f bosco-tsang

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d --build
```

### 数据管理
```bash
# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz downloads/ data/ cookies/

# 清理测试数据（推送前）
./scripts/clean-before-push.sh        # Linux/Mac
.\scripts\clean-before-push.ps1       # Windows
```

### 版本管理
```bash
# 更新版本号
./scripts/update-version.sh           # Linux/Mac
.\scripts\update-version.ps1          # Windows

# Git 操作
git add .
git commit -m "描述"
git tag v0.3.0
git push origin main
git push origin v0.3.0
```

---

## 📁 目录结构

```
BoscoTsang/
├── scripts/                    # 工具脚本
│   ├── clean-before-push.sh   # 清理脚本 (Linux/Mac)
│   ├── clean-before-push.ps1  # 清理脚本 (Windows)
│   ├── update-version.sh      # 版本更新 (Linux/Mac)
│   └── update-version.ps1     # 版本更新 (Windows)
├── downloads/                  # 下载文件
├── cookies/                    # Cookies 文件
├── data/                       # 数据库
├── logs/                       # 日志文件
├── USAGE_MANUAL.md            # 使用说明书
├── CHANGELOG.md               # 更新日志
└── QUICK_REFERENCE.md         # 快速参考
```

---

## 🔧 配置指南

### Telegram Bot 配置

1. **创建 Bot**
   - 联系 @BotFather
   - 发送 `/newbot`
   - 获取 Token

2. **系统配置**
   - Settings → Telegram
   - 填写 Bot Token
   - 开启 Telegram 登录
   - 保存

3. **前端配置**
   - 编辑 `frontend/src/views/Login.vue`
   - 替换 `data-telegram-login` 为 Bot Username
   - 重新构建

### X/Twitter Cookies 配置

1. **获取 Cookies**
   - 安装 EditThisCookie 扩展
   - 登录 X/Twitter
   - 导出 Cookies

2. **系统配置**
   - Settings → X/Twitter
   - 粘贴 Cookies
   - 配置下载选项
   - 保存

---

## 🎯 功能速查

### 下载支持

| 平台 | 视频 | 音频 | 图片 | Cookies |
|------|------|------|------|---------|
| YouTube | ✅ | ✅ | ❌ | 可选 |
| Bilibili | ✅ | ✅ | ❌ | 不需要 |
| Twitter/X | ✅ | ❌ | ✅ | **必需** |
| Instagram | ❌ | ❌ | ✅ | 可选 |
| 抖音 | ✅ | ✅ | ❌ | 不需要 |
| Apple Music | ❌ | ✅ | ❌ | 可选 |

### Telegram Bot 命令

| 命令 | 功能 |
|------|------|
| `/start` | 开始使用 |
| `/help` | 查看帮助 |
| `/status` | 下载状态 |
| 发送链接 | 自动下载 |

---

## 🐛 故障排查

### 下载失败
```bash
# 查看日志
docker logs bosco-tsang --tail 50

# 检查 Cookies
ls -lh cookies/

# 检查磁盘空间
df -h
```

### 服务异常
```bash
# 重启服务
docker-compose restart

# 查看容器状态
docker ps -a

# 清理并重建
docker-compose down
docker-compose up -d --build
```

### 端口冲突
```bash
# 修改端口
# 编辑 docker-compose.yml
ports:
  - "8888:8000"  # 改为 8888

# 重启
docker-compose down
docker-compose up -d
```

---

## 📚 文档链接

- [使用说明书](USAGE_MANUAL.md) - 详细使用指南
- [更新日志](CHANGELOG.md) - 版本变更记录
- [快速参考](QUICK_REFERENCE.md) - 本文档

---

## ⚠️ 推送前检查清单

- [ ] 运行清理脚本
- [ ] 检查 .env 文件
- [ ] 更新 CHANGELOG.md
- [ ] 更新版本号
- [ ] 测试通过
- [ ] Git status 检查

### 一键清理
```bash
# Linux/Mac
./scripts/clean-before-push.sh

# Windows
.\scripts\clean-before-push.ps1
```

---

## 📞 获取帮助

- 📖 查看 [使用说明书](USAGE_MANUAL.md)
- 🐛 提交 Issue
- 💬 联系开发团队

---

**版本:** v0.3.0  
**更新:** 2026-06-16
