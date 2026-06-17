# 📦 Bosco Tsang 版本更新工作流

本文档说明如何正确地更新版本、清理敏感信息并推送新版本。

---

## 🔄 完整更新流程

### 第 1 步：清理敏感信息

**⚠️ 推送前必须执行！防止敏感数据泄露！**

#### Windows PowerShell
```powershell
.\scripts\clean-before-push.ps1
```

#### Linux/Mac
```bash
chmod +x scripts/clean-before-push.sh
./scripts/clean-before-push.sh
```

**清理内容：**
- ✅ Cookies 文件内容（`cookies/*.txt`）
- ✅ 日志文件内容（`logs/*.log`）
- ✅ 测试下载文件（`downloads/*/*`）
- ✅ 临时文件（`/tmp/xtwitter_cookies.txt`）
- ✅ Python 缓存（`__pycache__/`）
- ✅ Node.js 缓存（`node_modules/.cache/`）

**清理脚本输出示例：**
```
🧹 开始清理敏感信息...
========================================

📁 清除 Cookies 文件内容...
  ✓ 清除: cookies/x.txt
  ✓ 清除: cookies/youtube.txt

📝 清除日志文件内容...
  ✓ 清除: logs/app_2026-06-16.log

🗑️ 清除测试下载内容...
  ✓ 清除: downloads/youtube/*
  ✓ 清除: downloads/x/*

🧽 清除临时文件...
  ✓ 清除: /tmp/xtwitter_cookies.txt

🧹 清除缓存文件...
  ✓ 清除: __pycache__/
  ✓ 清除: node_modules/.cache/

========================================
✅ 清理完成！
========================================

📋 已清理的项目:
  - Cookies 文件内容
  - 日志文件内容
  - 测试下载内容
  - 临时文件
  - 缓存文件

⚠️ 重要提醒:
  1. 检查 .env 文件是否包含敏感信息
  2. 确认 .gitignore 配置正确
  3. 运行 git status 检查是否有遗漏

🚀 可以安全地推送代码了！
```

---

### 第 2 步：更新版本号

#### Windows PowerShell
```powershell
.\scripts\update-version.ps1
```

#### Linux/Mac
```bash
chmod +x scripts/update-version.sh
./scripts/update-version.sh
```

**版本号规则（语义化版本）：**

| 更新类型 | 版本号变化 | 适用场景 | 示例 |
|---------|-----------|---------|------|
| **修订号 (PATCH)** | 1.0.0 → 1.0.1 | Bug 修复、小优化 | `0.3.0 → 0.3.1` |
| **次版本号 (MINOR)** | 1.0.0 → 1.1.0 | 新功能、向下兼容 | `0.3.0 → 0.4.0` |
| **主版本号 (MAJOR)** | 1.0.0 → 2.0.0 | 破坏性变更 | `0.3.0 → 1.0.0` |

**更新脚本输出示例：**
```
========================================
📦 版本号更新工具
========================================

当前版本: v0.3.0

请选择更新类型:
1. 修订号 (PATCH) - Bug 修复
2. 次版本号 (MINOR) - 新功能
3. 主版本号 (MAJOR) - 破坏性变更

输入选项 (1/2/3): 2

========================================
📝 更新版本: v0.3.0 → v0.4.0
========================================

📄 更新 backend/main.py...
  ✓ 版本号已更新: version="0.4.0"

📄 更新 frontend/package.json...
  ✓ 版本号已更新: "version": "0.4.0"

📄 更新 CHANGELOG.md...
  ✓ 已添加新版本记录: ## [v0.4.0]

✅ 版本更新完成！
========================================
```

---

### 第 3 步：更新 CHANGELOG.md

在 `CHANGELOG.md` 的 `[未发布]` 部分添加新版本的变更内容：

```markdown
## [未发布]

### ✨ 新增功能
- 新功能描述 1
- 新功能描述 2

### 🔧 功能优化
- 优化描述 1

### 🐛 错误修复
- 修复描述 1

### 📝 文档更新
- 文档更新描述
```

**更新类型标识：**
- ✨ **新增功能** - 新功能或重大改进
- 🔧 **功能优化** - 现有功能的优化
- 🐛 **错误修复** - Bug 修复
- 📝 **文档更新** - 文档相关变更
- 🔐 **安全增强** - 安全性相关变更
- 📦 **依赖更新** - 依赖库变更
- ⚠️ **破坏性变更** - 不兼容的变更

---

### 第 4 步：提交并推送

```bash
# 1. 检查变更
git status

# 2. 查看差异
git diff

# 3. 添加文件
git add .

# 4. 提交（使用规范的提交信息）
git commit -m "chore: 版本更新至 v0.4.0

- 清理敏感信息
- 更新版本号
- 更新 CHANGELOG.md"

# 5. 打标签
git tag -a v0.4.0 -m "Release v0.4.0"

# 6. 推送代码和标签
git push origin main
git push origin v0.4.0
```

**提交信息规范：**
```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
perf: 性能优化
test: 测试相关
chore: 构建/工具相关
```

---

### 第 5 步：构建并发布 Docker 镜像（可选）

```bash
# 1. 构建镜像
docker build -t boscotom/bosco-tsang:v0.4.0 .

# 2. 标记 latest
docker tag boscotom/bosco-tsang:v0.4.0 boscotom/bosco-tsang:latest

# 3. 推送镜像
docker push boscotom/bosco-tsang:v0.4.0
docker push boscotom/bosco-tsang:latest
```

---

## 🛡️ 敏感信息防护

### 绝对不能提交的内容

| 类型 | 路径 | 原因 |
|------|------|------|
| ❌ **Cookies 文件** | `cookies/*.txt` | 包含账号认证信息 |
| ❌ **日志文件** | `logs/*.log` | 包含下载记录和敏感信息 |
| ❌ **测试下载** | `downloads/*/*` | 可能包含版权内容 |
| ❌ **环境变量** | `.env` | 包含密码和密钥 |
| ❌ **数据库文件** | `data/bosco.db` | 包含用户数据 |
| ❌ **临时文件** | `/tmp/*.txt` | 可能包含临时 Cookies |

### .gitignore 配置

项目已配置 `.gitignore` 过滤敏感文件：

```gitignore
# Bosco Tsang
.DS_Store
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.log
.env
downloads/
cookies/
data/
logs/
node_modules/
.vscode/
.idea/
*.swp
*.swo
```

**验证 .gitignore 是否生效：**
```bash
# 检查是否有敏感文件被跟踪
git ls-files | grep -E "(cookies|downloads|logs|data|\.env)"

# 如果有输出，说明这些文件已被跟踪，需要移除
git rm -r --cached cookies/ downloads/ logs/ data/
git commit -m "chore: 从 Git 跟踪中移除敏感文件"
```

---

## 📋 发布检查清单

每次发布新版本前，逐项检查：

### 代码质量
- [ ] 所有功能测试通过
- [ ] 无已知 Bug
- [ ] 代码风格检查通过
- [ ] 性能测试通过

### 敏感信息清理
- [ ] ✅ 运行清理脚本
- [ ] ✅ 检查 `.env` 文件
- [ ] ✅ 确认 `.gitignore` 生效
- [ ] ✅ `git status` 无敏感文件

### 文档更新
- [ ] ✅ 更新 `CHANGELOG.md`
- [ ] ✅ 更新 `USAGE_MANUAL.md`（如需要）
- [ ] ✅ 版本号已更新

### 构建测试
- [ ] ✅ Docker 构建成功
- [ ] ✅ 服务启动正常
- [ ] ✅ 核心功能测试通过
- [ ] ✅ 健康检查通过

### 推送发布
- [ ] ✅ Git 提交
- [ ] ✅ 打标签
- [ ] ✅ 推送代码
- [ ] ✅ 推送 Docker 镜像（如需要）

---

## 🐛 常见问题

### Q1: 清理脚本执行失败？

**Windows PowerShell:**
```powershell
# 检查执行策略
Get-ExecutionPolicy

# 如果 Restricted，临时允许执行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 然后执行脚本
.\scripts\clean-before-push.ps1
```

**Linux/Mac:**
```bash
# 添加执行权限
chmod +x scripts/clean-before-push.sh

# 执行
./scripts/clean-before-push.sh
```

### Q2: 版本更新脚本找不到文件？

**检查文件路径：**
```bash
# 确认文件存在
ls backend/main.py
ls frontend/package.json
ls CHANGELOG.md
```

**手动更新版本号：**
```bash
# backend/main.py
# 找到: version="0.3.0"
# 改为: version="0.4.0"

# frontend/package.json
# 找到: "version": "0.3.0"
# 改为: "version": "0.4.0"

# CHANGELOG.md
# 在顶部添加新版本记录
```

### Q3: Git 推送被拒绝（大文件）？

```bash
# 检查大文件
git rev-list --objects --all | \
  grep "$(git verify-pack -v .git/objects/pack/*.idx | \
  sort -k 3 -n | tail -10 | awk '{print$1}')"

# 从历史中移除大文件
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch PATH-TO-FILE' \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（谨慎使用）
git push origin main --force
```

### Q4: Docker 构建失败？

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建（不使用缓存）
docker-compose build --no-cache

# 查看构建日志
docker-compose up --build 2>&1 | tee build.log
```

---

## 📚 相关文档

- [使用说明书](USAGE_MANUAL.md) - 详细功能说明和配置指南
- [更新日志](CHANGELOG.md) - 版本变更记录
- [部署指南](DEPLOYMENT.md) - Docker 部署方式
- [快速参考](QUICK_REFERENCE.md) - 常用命令速查

---

## 📞 技术支持

- 📖 查看 [使用说明书](USAGE_MANUAL.md)
- 🐛 提交 Issue
- 💬 联系开发团队

---

**最后更新:** 2026-06-16  
**版本:** v0.3.0  
**文档维护:** Bosco Tsang 开发团队
