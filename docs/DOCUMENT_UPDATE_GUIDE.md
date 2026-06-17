# 📝 文档自动更新指南

## 🎯 概述

本系统提供自动化的文档更新流程，确保每次版本发布时，帮助文档和更新日志都能同步更新。

---

## 📋 自动化脚本

### 脚本位置

```
scripts/update-docs.ps1
```

### 功能特性

- ✅ 自动更新 CHANGELOG.md
- ✅ 自动更新 USAGE_MANUAL.md
- ✅ 自动更新 Dockerfile 版本标签
- ✅ 自动更新 docker-compose.yml 版本注释
- ✅ 支持自定义变更内容
- ✅ 可选自动 Git 提交

---

## 🚀 使用方法

### 基础用法

#### 1. 更新 CHANGELOG.md

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2" -UpdateChangelog
```

**示例：**
```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2" -UpdateChangelog `
  -ChangeType "feat" `
  -Changes @(
    "新增 TikTok 平台下载支持",
    "优化下载速度",
    "修复代理配置问题"
  )
```

#### 2. 更新 USAGE_MANUAL.md

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2" -UpdateManual
```

#### 3. 同时更新两个文档

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2"
```

#### 4. 带变更内容更新

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2" `
  -ChangeType "fix" `
  -Changes @(
    "修复帮助和更新按钮无法打开的问题",
    "修复代理开关无法保存状态的问题",
    "修复断开代理后国内平台无法下载的问题"
  ) `
  -AutoCommit
```

---

## 📖 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `-Version` | string | ✅ | - | 版本号（如 v0.3.2） |
| `-ReleaseDate` | string | ❌ | 今天 | 发布日期（yyyy-MM-dd） |
| `-UpdateManual` | switch | ❌ | false | 是否更新使用说明书 |
| `-UpdateChangelog` | switch | ❌ | false | 是否更新更新日志 |
| `-ChangeType` | string | ❌ | fix | 变更类型 |
| `-Changes` | string[] | ❌ | @() | 变更内容列表 |
| `-AutoCommit` | switch | ❌ | false | 是否自动提交到 Git |

### 变更类型

| 类型 | 说明 | CHANGELOG 标题 |
|------|------|---------------|
| `feat` | 新功能 | ### ✨ 新增功能 |
| `fix` | 问题修复 | ### 🐛 问题修复 |
| `perf` | 性能优化 | ### ⚡ 性能优化 |
| `refactor` | 代码重构 | ### ♻️ 代码重构 |
| `docs` | 文档更新 | ### 📝 文档更新 |

---

## 🎓 使用示例

### 示例 1：发布新版本（新功能）

```powershell
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -ChangeType "feat" `
  -Changes @(
    "新增 TikTok 平台下载支持",
    "新增批量下载功能",
    "新增下载队列管理",
    "优化用户权限系统"
  ) `
  -UpdateManual `
  -AutoCommit
```

**效果：**

CHANGELOG.md 会添加：
```markdown
## [v0.4.0] - 2026-06-16

### ✨ 新增功能

- 新增 TikTok 平台下载支持
- 新增批量下载功能
- 新增下载队列管理
- 优化用户权限系统

---
```

USAGE_MANUAL.md 会在"功能使用说明"后添加：
```markdown
#### v0.4.0 新功能

- 新增 TikTok 平台下载支持
- 新增批量下载功能
- 新增下载队列管理
- 优化用户权限系统
```

---

### 示例 2：修复 Bug

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.1" `
  -ChangeType "fix" `
  -Changes @(
    "修复帮助和更新按钮无法打开的问题",
    "修复代理开关无法保存状态的问题",
    "修复断开代理后国内平台无法下载的问题"
  )
```

---

### 示例 3：性能优化

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2" `
  -ChangeType "perf" `
  -Changes @(
    "优化视频转码速度",
    "减少内存占用",
    "提升并发下载性能"
  )
```

---

### 示例 4：自定义发布日期

```powershell
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -ReleaseDate "2026-07-01" `
  -ChangeType "feat" `
  -Changes @("新增功能...")
```

---

## 🔄 完整发布流程

### 步骤 1：更新文档

```powershell
# 更新 CHANGELOG.md 和 USAGE_MANUAL.md
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -ChangeType "feat" `
  -Changes @(
    "新增 TikTok 平台下载支持",
    "新增批量下载功能"
  ) `
  -UpdateManual `
  -AutoCommit
```

### 步骤 2：重新构建 Docker 镜像

```powershell
docker-compose down
docker-compose up -d --build
```

### 步骤 3：测试新功能

```powershell
# 访问 http://localhost:8080 测试
# 检查帮助文档是否更新
# 检查更新日志是否正确
```

### 步骤 4：推送 Docker 镜像

```powershell
# 标记镜像
docker tag boscotsang-bosco-tsang:latest boscotom/bosco-tsang:v0.4.0
docker tag boscotsang-bosco-tsang:latest boscotom/bosco-tsang:latest

# 推送镜像
docker push boscotom/bosco-tsang:v0.4.0
docker push boscotom/bosco-tsang:latest
```

### 步骤 5：创建 Git 标签

```powershell
git tag v0.4.0
git push origin v0.4.0
```

---

## 📊 文档结构

### CHANGELOG.md 结构

```markdown
# 更新日志 (CHANGELOG)

## [未发布]
### 计划中
- 未来功能...

---

## [v0.4.0] - 2026-06-16
### ✨ 新增功能
- 新功能 1
- 新功能 2

---

## [v0.3.1] - 2026-06-16
### 🐛 问题修复
- 修复 1
- 修复 2

---
```

### USAGE_MANUAL.md 结构

```markdown
# Bosco Tsang 使用说明书

## 系统简介
### 核心功能
### 当前版本
**v0.4.0** (2026-06-16)

## 快速开始

## 功能使用说明
#### v0.4.0 新功能
- 新功能 1
- 新功能 2

## 平台配置指南

## 常见问题

## 技术支持
```

---

## ⚙️ 高级用法

### 1. 从 Git 提交记录自动生成

```powershell
# 获取最近的提交
$Commits = git log --oneline --since="1 week ago" | ForEach-Object {
    $_ -replace "^[a-f0-9]+ ", ""
}

# 使用提交记录更新
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -Changes $Commits `
  -AutoCommit
```

### 2. 批量更新多个版本

```powershell
$Versions = @(
    @{ Version="v0.3.1"; Type="fix"; Changes=@("修复 1", "修复 2") },
    @{ Version="v0.3.2"; Type="perf"; Changes=@("优化 1") },
    @{ Version="v0.4.0"; Type="feat"; Changes=@("新功能 1") }
)

foreach ($v in $Versions) {
    .\scripts\update-docs.ps1 -Version $v.Version `
      -ChangeType $v.Type `
      -Changes $v.Changes
}
```

### 3. 检查文档是否已更新

```powershell
# 检查 CHANGELOG.md
Select-String -Path "CHANGELOG.md" -Pattern "v0.4.0"

# 检查 USAGE_MANUAL.md
Select-String -Path "USAGE_MANUAL.md" -Pattern "v0.4.0"
```

---

## 🐛 常见问题

### Q1: 脚本执行失败？

**A:** 检查 PowerShell 执行策略：
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Q2: CHANGELOG.md 格式错乱？

**A:** 确保文件使用 UTF-8 编码，且包含 `[未发布]` 部分。

### Q3: 如何撤销更新？

**A:** 使用 Git 回滚：
```powershell
git checkout HEAD -- CHANGELOG.md USAGE_MANUAL.md
```

### Q4: 如何自定义文档模板？

**A:** 修改 `scripts/update-docs.ps1` 中的模板字符串。

---

## 📝 最佳实践

### 1. 每次发布前更新文档

```powershell
# 发布前先更新文档
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -ChangeType "feat" `
  -Changes @("...") `
  -UpdateManual

# 然后构建和推送
docker-compose up -d --build
docker push boscotom/bosco-tsang:v0.4.0
```

### 2. 使用语义化版本

- **主版本号** (v1.0.0 → v2.0.0)：不兼容的 API 更改
- **次版本号** (v0.3.0 → v0.4.0)：向后兼容的新功能
- **修订号** (v0.3.0 → v0.3.1)：向后兼容的 Bug 修复

### 3. 保持 CHANGELOG 清晰

- 按时间倒序排列（最新版本在最上面）
- 使用统一的格式和图标
- 提供详细的变更说明

### 4. 同步更新多个文档

```powershell
# 同时更新所有文档
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -UpdateManual `
  -AutoCommit

# 重新构建（确保文档被打包到镜像中）
docker-compose up -d --build
```

---

## 🎯 快速参考

### 最常用命令

```powershell
# 发布新版本（推荐）
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -ChangeType "feat" `
  -Changes @("新功能描述") `
  -UpdateManual `
  -AutoCommit

# 仅更新 CHANGELOG
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -Changes @("变更描述")

# 查看帮助
Get-Help .\scripts\update-docs.ps1 -Detailed
```

---

## 🔗 相关文档

- [CHANGELOG.md](../CHANGELOG.md) - 更新日志
- [USAGE_MANUAL.md](../USAGE_MANUAL.md) - 使用说明书
- [DEPLOYMENT.md](../DEPLOYMENT.md) - 部署指南
- [DOCKER_PUSH_v0.3.1.md](../DOCKER_PUSH_v0.3.1.md) - Docker 推送报告

---

**文档自动更新系统已就绪！** 🚀

每次版本发布时，只需运行一行命令即可更新所有文档。
