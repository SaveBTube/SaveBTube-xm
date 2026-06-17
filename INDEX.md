# 📚 Bosco Tsang 文档导航

欢迎使用 Bosco Tsang 全平台视频/音乐/图片下载系统！

本文档索引帮助您快速找到所需的文档和资源。

---

## 🚀 快速开始

### 新用户
1. 📘 [**使用说明书**](USAGE_MANUAL.md) - 从这里开始！
   - 系统简介
   - 快速部署指南
   - 功能使用说明
   - 常见问题解答

2. ⚡ [**快速参考**](QUICK_REFERENCE.md) - 常用命令速查
   - Docker 命令
   - 功能速查表
   - 故障排查

3. 📋 [**功能清单**](FEATURES.md) - 了解所有功能
   - 10 大功能模块
   - 支持的平台
   - 技术栈说明

### 部署系统
- 🚀 [**部署指南**](DEPLOYMENT.md) - 3 种部署方式
  - 从源码构建
  - 预构建镜像
  - Docker Compose

---

## 🔄 版本管理

### 查看更新
- 📝 [**更新日志**](CHANGELOG.md) - 版本变更记录
  - v0.1.0 → v0.3.0
  - 新增功能
  - Bug 修复
  - 优化改进

### 发布新版本
- 🔄 [**版本更新工作流**](RELEASE_WORKFLOW.md) - 完整的发布流程
  - 清理敏感信息
  - 更新版本号
  - 提交并推送
  - 构建 Docker 镜像

---

## 📖 技术文档

### 架构设计
- 🏗️ [**系统架构分析**](docs/SYSTEM_ANALYSIS.md) - 系统设计文档

### 使用教程
- 📚 [**使用教程**](docs/USAGE.md) - 基础使用说明

### 项目说明
- 📘 [**README**](README.md) - 项目简介

---

## 🛠️ 工具和脚本

### 清理脚本
| 平台 | 脚本 | 说明 |
|------|------|------|
| Windows | [`scripts/clean-before-push.ps1`](scripts/clean-before-push.ps1) | 推送前清理 |
| Linux/Mac | [`scripts/clean-before-push.sh`](scripts/clean-before-push.sh) | 推送前清理 |

### 版本更新脚本
| 平台 | 脚本 | 说明 |
|------|------|------|
| Windows | [`scripts/update-version.ps1`](scripts/update-version.ps1) | 版本号更新 |
| Linux/Mac | [`scripts/update-version.sh`](scripts/update-version.sh) | 版本号更新 |

---

## 📊 文档统计

| 文档 | 大小 | 说明 |
|------|------|------|
| [USAGE_MANUAL.md](USAGE_MANUAL.md) | 10.5 KB | 使用说明书 |
| [RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md) | 8.8 KB | 版本更新工作流 |
| [SUMMARY.md](SUMMARY.md) | 8.7 KB | 工作总结 |
| [FEATURES.md](FEATURES.md) | 8.3 KB | 功能清单 |
| [CHANGELOG.md](CHANGELOG.md) | 7.8 KB | 更新日志 |
| [README.md](README.md) | 7.5 KB | 项目简介 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 4.8 KB | 部署指南 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 4.2 KB | 快速参考 |

**总计：** 约 60 KB，8 个文档文件

---

## 🎯 按场景查找文档

### 场景 1：第一次使用
👉 阅读顺序：
1. [README.md](README.md) - 了解项目
2. [USAGE_MANUAL.md](USAGE_MANUAL.md) - 学习使用
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 常用命令

### 场景 2：部署到服务器
👉 阅读顺序：
1. [DEPLOYMENT.md](DEPLOYMENT.md) - 部署方式
2. [USAGE_MANUAL.md](USAGE_MANUAL.md) - 配置说明
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 运维命令

### 场景 3：发布新版本
👉 阅读顺序：
1. [RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md) - 完整流程
2. [CHANGELOG.md](CHANGELOG.md) - 编写规范
3. [DEPLOYMENT.md](DEPLOYMENT.md) - 发布检查清单

### 场景 4：遇到问题
👉 查找位置：
1. [USAGE_MANUAL.md](USAGE_MANUAL.md) - 常见问题章节
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 故障排查章节
3. [RELEASE_WORKFLOW.md](RELEASE_WORKFLOW.md) - 常见问题章节

### 场景 5：了解功能
👉 阅读顺序：
1. [FEATURES.md](FEATURES.md) - 功能清单
2. [USAGE_MANUAL.md](USAGE_MANUAL.md) - 使用说明
3. [CHANGELOG.md](CHANGELOG.md) - 更新历史

---

## 📱 在线访问

### Web 界面
- **管理后台：** `http://localhost:8080`
- **使用说明书：** 页头 "📖 帮助" 按钮
- **更新日志：** 页头 "📝 更新" 按钮

### 文档位置
所有文档都位于项目根目录，可以直接在 Git 仓库中查看。

---

## 🔗 外部链接

- **yt-dlp 文档：** https://github.com/yt-dlp/yt-dlp
- **FastAPI 文档：** https://fastapi.tiangolo.com/
- **Vue 3 文档：** https://vuejs.org/
- **Docker 文档：** https://docs.docker.com/

---

## 📞 获取帮助

- 📖 查看文档 - 大部分问题都可以在文档中找到答案
- 🐛 提交 Issue - 遇到 Bug 请提交 Issue
- 💬 联系团队 - 需要帮助请联系开发团队

---

## 📝 文档维护

### 更新文档
当添加新功能或修改现有功能时，请同步更新相关文档：

1. **更新 CHANGELOG.md** - 记录变更
2. **更新 USAGE_MANUAL.md** - 更新使用说明
3. **更新 FEATURES.md** - 更新功能清单
4. **更新 README.md** - 更新项目简介

### 文档规范
- 使用 Markdown 格式
- 遵循语义化版本
- 保持文档同步更新
- 使用清晰的标题和结构

---

**最后更新：** 2026-06-16  
**版本：** v0.3.0  
**维护团队：** Bosco Tsang 开发团队
