# 📦 发布文档索引

## 📁 文档结构

```
releases/
├── README.md                    # 本文件（索引）
├── ORGANIZATION_REPORT.md       # 文档整理报告
├── DEPLOYMENT.md                # 部署指南
├── DOCKER_PUSH_REPORT.md        # 首次推送报告
├── ARM64_PUSH_GUIDE.md          # ARM64 架构推送指南
├── QUICK_ARM64_PUSH.md          # ARM64 快速推送指南
├── RELEASE_WORKFLOW.md          # 发布工作流程
├── LOCAL_TEST_PORTS.md          # 本地测试端口配置
├── update-v0.4.0.ps1            # v0.4.0 文档更新脚本
├── update-v0.4.1.ps1            # v0.4.1 文档更新脚本
├── v0.3.x/                      # v0.3.x 版本文档
│   ├── DOCKER_PUSH_v0.3.1.md    # v0.3.1 推送报告
│   ├── DEPLOYMENT_COMPLETE.md   # 部署完成报告
│   ├── FIXES_REPORT.md          # 问题修复报告
│   └── VERIFICATION_GUIDE.md    # 验证指南
└── v0.4.x/                      # v0.4.x 版本文档
    ├── DOCKER_PUSH_v0.4.0.md    # v0.4.0 推送报告
    ├── DOCKER_PUSH_v0.4.1.md    # v0.4.1 推送报告
    ├── DOCKER_PUSH_v0.4.2.md    # v0.4.2 推送报告
    ├── DOCKER_PUSH_v0.4.3.md    # v0.4.3 推送报告
    └── DOCKER_PUSH_v0.4.4.md    # v0.4.4 推送报告
```

---

## 📋 版本历史

### v0.4.x 系列

| 版本 | 日期 | 推送报告 | 说明 |
|------|------|---------|------|
| v0.4.4 | 2026-06-16 | [推送报告](v0.4.x/DOCKER_PUSH_v0.4.4.md) | 修复 Telegram 设置保存授权问题 |
| v0.4.3 | 2026-06-16 | [推送报告](v0.4.x/DOCKER_PUSH_v0.4.3.md) | 调整快捷指令安装方式（手动配置） |
| v0.4.2 | 2026-06-16 | [推送报告](v0.4.x/DOCKER_PUSH_v0.4.2.md) | 快捷指令成品化 + 文档 Web 访问 |
| v0.4.1 | 2026-06-16 | [推送报告](v0.4.x/DOCKER_PUSH_v0.4.1.md) | 修复快捷指令安装问题 |
| v0.4.0 | 2026-06-16 | [推送报告](v0.4.x/DOCKER_PUSH_v0.4.0.md) | 新增 iOS 快捷指令下载功能 |

### v0.3.x 系列

| 版本 | 日期 | 推送报告 | 说明 |
|------|------|---------|------|
| v0.3.2 | 2026-06-16 | - | 文档自动更新系统 |
| v0.3.1 | 2026-06-16 | [推送报告](v0.3.x/DOCKER_PUSH_v0.3.1.md) | 修复文档访问、代理保存、国内平台 |
| v0.3.0 | 2026-06-16 | - | Telegram 生态 + X/Twitter 下载 |

---

## 📚 通用文档

### 部署相关

| 文档 | 路径 | 说明 |
|------|------|------|
| 部署指南 | [DEPLOYMENT.md](DEPLOYMENT.md) | 完整部署流程 |
| 部署完成报告 | [v0.3.x/DEPLOYMENT_COMPLETE.md](v0.3.x/DEPLOYMENT_COMPLETE.md) | 部署验证 |
| 本地测试端口 | [LOCAL_TEST_PORTS.md](LOCAL_TEST_PORTS.md) | 端口配置 |

### 推送相关

| 文档 | 路径 | 说明 |
|------|------|------|
| 首次推送报告 | [DOCKER_PUSH_REPORT.md](DOCKER_PUSH_REPORT.md) | 初始推送 |
| ARM64 推送指南 | [QUICK_ARM64_PUSH.md](QUICK_ARM64_PUSH.md) | 多架构构建 |

### 工具脚本

| 脚本 | 路径 | 说明 |
|------|------|------|
| v0.4.0 更新脚本 | [update-v0.4.0.ps1](update-v0.4.0.ps1) | 文档自动更新 |
| v0.4.1 更新脚本 | [update-v0.4.1.ps1](update-v0.4.1.ps1) | 文档自动更新 |

---

## 🔍 快速查找

### 按功能查找

#### iOS 快捷指令
- v0.4.0 - [推送报告](v0.4.x/DOCKER_PUSH_v0.4.0.md) - 新增功能
- v0.4.1 - [推送报告](v0.4.x/DOCKER_PUSH_v0.4.1.md) - 修复安装问题
- v0.4.2 - [推送报告](v0.4.x/DOCKER_PUSH_v0.4.2.md) - 成品化 + 文档
- v0.4.3 - [推送报告](v0.4.x/DOCKER_PUSH_v0.4.3.md) - 手动配置

#### Telegram
- v0.3.0 - Telegram 生态集成
- v0.4.4 - [推送报告](v0.4.x/DOCKER_PUSH_v0.4.4.md) - 修复设置保存

#### 文档系统
- v0.3.2 - 文档自动更新系统
- v0.4.2 - 文档 Web 访问

---

## 📊 统计信息

### 文档数量

| 类别 | 数量 |
|------|------|
| 推送报告 | 7 个 |
| 部署文档 | 2 个 |
| 更新脚本 | 2 个 |
| 其他文档 | 2 个 |
| **总计** | **13 个** |

### 版本分布

| 系列 | 版本数 | 时间跨度 |
|------|--------|---------|
| v0.4.x | 5 个 | 2026-06-16 |
| v0.3.x | 3 个 | 2026-06-16 |
| **总计** | **8 个** | **1 天** |

---

## 🎯 使用建议

### 查看最新版本
- 查看 [v0.4.x/DOCKER_PUSH_v0.4.4.md](v0.4.x/DOCKER_PUSH_v0.4.4.md)

### 了解部署流程
- 查看 [DEPLOYMENT.md](DEPLOYMENT.md)

### 本地测试
- 查看 [LOCAL_TEST_PORTS.md](LOCAL_TEST_PORTS.md)

### 文档更新
- 查看 `docs/DOCUMENT_UPDATE_GUIDE.md`

---

## 📝 维护说明

### 添加新版本

1. 在 `releases/v0.4.x/` 创建推送报告
2. 更新本索引文件的版本历史
3. 创建文档更新脚本（可选）

### 清理旧版本

定期清理过时的文档，保持文件夹整洁。

---

**最后更新：** 2026-06-16  
**维护者：** Bosco Tsang Team
