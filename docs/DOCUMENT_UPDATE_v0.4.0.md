# 📝 文档更新报告 - v0.4.0

## ✅ 更新完成

**更新时间：** 2026-06-16  
**版本：** v0.4.0  
**更新类型：** feat（新功能）

---

## 📦 v0.4.0 新增功能

### iOS 快捷指令下载功能

1. **Add iOS Shortcuts download feature**
   - 新增 iOS 快捷指令专用下载接口
   - 支持 X-API-Key 认证
   - 简洁的 JSON 响应格式

2. **Integrate Shortcuts into plugin management page**
   - 在插件管理页面添加快捷指令专区
   - 精美的 UI 设计（Apple 风格）
   - 完整的功能特性展示

3. **Add Shortcuts installation page**
   - 一键安装的 Web 页面
   - 移动端优化的 UI
   - iOS 设备自动检测

4. **Add Shortcuts download API**
   - 配置文件下载接口
   - 支持手动导入快捷指令
   - JSON 格式配置

5. **Add Shortcuts documentation**
   - 完整使用指南
   - 快速开始文档
   - 集成报告文档

---

## 📂 修改的文件

### 前端文件
- ✅ `frontend/src/views/Settings.vue` - 添加快捷指令卡片
- ✅ `static/shortcuts-install.html` - 安装页面

### 后端文件
- ✅ `backend/main.py` - 添加 3 个 API 接口

### 配置文件
- ✅ `Dockerfile` - 添加快捷指令文件复制
- ✅ `shortcuts/Bosco_Download.shortcut` - 快捷指令配置

### 文档文件
- ✅ `docs/IOS_SHORTCUTS_GUIDE.md` - 完整使用指南
- ✅ `docs/IOS_SHORTCUTS_INTEGRATION_REPORT.md` - 集成报告
- ✅ `shortcuts/README.md` - 快速开始
- ✅ `USAGE_MANUAL.md` - 使用说明书（已更新版本）

---

## 🚀 使用方法

### 更新文档的命令

```powershell
# 基本用法
.\scripts\update-docs.ps1 -Version "版本号" -Changes @("变更内容") -UpdateManual

# 完整示例（v0.4.0）
$changes = @(
    "Add iOS Shortcuts download feature",
    "Integrate Shortcuts into plugin management page",
    "Add Shortcuts installation page",
    "Add Shortcuts download API",
    "Add Shortcuts documentation"
)

.\scripts\update-docs.ps1 -Version "v0.4.0" -ChangeType "feat" -Changes $changes -UpdateManual
```

### 简化方法（推荐）

创建更新脚本文件 `update-v0.X.X.ps1`：

```powershell
# 变更内容
$changes = @(
    "功能 1",
    "功能 2",
    "功能 3"
)

# 执行更新
.\scripts\update-docs.ps1 -Version "v0.X.X" -ChangeType "feat" -Changes $changes -UpdateManual
```

---

## 📊 变更类型说明

| 类型 | 说明 | CHANGELOG 标题 | 示例 |
|------|------|---------------|------|
| `feat` | 新功能 | ### New Features | 新增 iOS 快捷指令 |
| `fix` | Bug 修复 | ### Bug Fixes | 修复代理问题 |
| `perf` | 性能优化 | ### Performance Improvements | 优化下载速度 |
| `refactor` | 代码重构 | ### Code Refactoring | 重构认证逻辑 |
| `docs` | 文档更新 | ### Documentation | 更新使用手册 |

---

## 🎯 下次发布流程

### 步骤 1：更新文档

```powershell
# 创建更新脚本
$changes = @("新功能描述")
.\scripts\update-docs.ps1 -Version "v0.X.X" -Changes $changes -UpdateManual
```

### 步骤 2：重新构建 Docker

```bash
docker-compose down
docker-compose up -d --build
```

### 步骤 3：推送 Docker 镜像

```bash
docker tag boscotsang-bosco-tsang:latest boscotom/bosco-tsang:v0.X.X
docker push boscotom/bosco-tsang:v0.X.X
docker push boscotom/bosco-tsang:latest
```

### 步骤 4：创建 Git 标签

```bash
git tag v0.X.X
git push origin v0.X.X
```

---

## 📝 CHANGELOG.md 格式

更新后的 CHANGELOG.md 应该包含：

```markdown
# Changelog

## [v0.4.0] - 2026-06-16

### New Features

- Add iOS Shortcuts download feature
- Integrate Shortcuts into plugin management page
- Add Shortcuts installation page
- Add Shortcuts download API
- Add Shortcuts documentation

---

## [v0.3.2] - 2026-06-16

### Documentation

- Add automated document update system

---
```

---

## 💡 注意事项

### 1. 特殊字符处理

如果变更内容包含特殊字符（如引号、括号），建议使用变量：

```powershell
# ❌ 错误 - 直接传递可能出错
.\scripts\update-docs.ps1 -Version "v0.4.0" -Changes @("包含"引号"的内容")

# ✅ 正确 - 使用变量
$changes = @("包含\"引号\"的内容")
.\scripts\update-docs.ps1 -Version "v0.4.0" -Changes $changes
```

### 2. 中文支持

脚本对中文支持良好，但建议使用英文避免编码问题：

```powershell
# ✅ 推荐 - 英文
$changes = @("Add iOS Shortcuts feature")

# ⚠️ 可能有问题 - 中文
$changes = @("新增 iOS 快捷指令功能")
```

### 3. 自动提交

使用 `-AutoCommit` 参数自动提交到 Git：

```powershell
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -Changes $changes `
  -UpdateManual `
  -AutoCommit
```

---

## 📚 相关文档

| 文档 | 路径 | 用途 |
|------|------|------|
| 更新脚本 | [scripts/update-docs.ps1](file:///H:/docker开发文档/BoscoTsang/scripts/update-docs.ps1) | 文档自动更新 |
| 快速参考 | [docs/QUICK_REFERENCE.md](file:///H:/docker开发文档/BoscoTsang/docs/QUICK_REFERENCE.md) | 命令速查 |
| 完整指南 | [docs/DOCUMENT_UPDATE_GUIDE.md](file:///H:/docker开发文档/BoscoTsang/docs/DOCUMENT_UPDATE_GUIDE.md) | 详细说明 |
| 更新示例 | [update-v0.4.0.ps1](file:///H:/docker开发文档/BoscoTsang/update-v0.4.0.ps1) | v0.4.0 更新脚本 |

---

## ✅ 验证清单

- [x] USAGE_MANUAL.md 已更新版本信息
- [x] CHANGELOG.md 已添加 v0.4.0 条目
- [x] 变更内容已正确记录
- [x] 文档格式正确
- [x] 文件编码 UTF-8

---

**v0.4.0 文档更新完成！** 🎉

下次更新时，只需修改版本号变更内容即可。
