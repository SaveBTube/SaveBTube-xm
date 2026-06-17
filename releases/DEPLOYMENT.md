# 🚀 Bosco Tsang 部署与发布指南

## 📦 Docker 部署方式

### 方式一：从源码构建（开发环境）

```bash
# 1. 克隆项目
git clone <repository-url>
cd BoscoTsang

# 2. 构建并启动
docker-compose up -d --build

# 3. 查看日志
docker-compose logs -f
```

### 方式二：使用预构建镜像（生产环境）

```bash
# 拉取最新镜像
docker pull boscotom/bosco-tsang:latest

# 运行容器
docker run -d \
  --name bosco-tsang \
  -p 8080:8000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookies:/app/cookies \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e APP_BASE_DIR=/app \
  -e TZ=Asia/Shanghai \
  --restart unless-stopped \
  boscotom/bosco-tsang:latest
```

### 方式三：Docker Compose（推荐）

```bash
# 创建 docker-compose.yml
# (参考项目根目录的 docker-compose.yml)

# 启动服务
docker-compose up -d

# 更新服务
docker-compose pull
docker-compose up -d --build
```

---

## 🔄 版本发布流程

### 1. 推送前清理

**⚠️ 重要：必须先清理敏感信息！**

```bash
# Linux/Mac
./scripts/clean-before-push.sh

# Windows PowerShell
.\scripts\clean-before-push.ps1
```

**清理内容：**
- ✅ Cookies 文件内容
- ✅ 日志文件内容
- ✅ 测试下载文件
- ✅ 临时文件
- ✅ Python/Node 缓存

### 2. 更新版本号

```bash
# Linux/Mac
./scripts/update-version.sh

# Windows PowerShell
.\scripts\update-version.ps1
```

**版本号规则（语义化版本）：**
- **主版本号 (MAJOR)** - 破坏性变更
- **次版本号 (MINOR)** - 新功能
- **修订号 (PATCH)** - Bug 修复

### 3. 更新 CHANGELOG.md

在 `CHANGELOG.md` 中添加新版本变更内容：

```markdown
## [v0.3.1] - 2026-06-16

### ✨ 新增功能
- 功能描述

### 🐛 错误修复
- 修复描述

### 🔧 功能优化
- 优化描述
```

### 4. 提交并推送

```bash
# 检查变更
git status

# 添加文件
git add .

# 提交
git commit -m "chore: 版本更新至 v0.3.1"

# 打标签
git tag v0.3.1

# 推送代码和标签
git push origin main
git push origin v0.3.1
```

### 5. 构建并发布 Docker 镜像

```bash
# 构建镜像
docker build -t boscotom/bosco-tsang:v0.3.1 .
docker tag boscotom/bosco-tsang:v0.3.1 boscotom/bosco-tsang:latest

# 推送镜像
docker push boscotom/bosco-tsang:v0.3.1
docker push boscotom/bosco-tsang:latest
```

---

## 📋 发布检查清单

- [ ] **代码审查**
  - [ ] 所有功能测试通过
  - [ ] 无已知 Bug
  - [ ] 代码风格检查通过

- [ ] **敏感信息清理**
  - [ ] 运行清理脚本
  - [ ] 检查 .env 文件
  - [ ] 确认 .gitignore 生效
  - [ ] Git status 无敏感文件

- [ ] **文档更新**
  - [ ] 更新 CHANGELOG.md
  - [ ] 更新 USAGE_MANUAL.md（如需要）
  - [ ] 更新版本号

- [ ] **构建测试**
  - [ ] Docker 构建成功
  - [ ] 服务启动正常
  - [ ] 核心功能测试通过

- [ ] **推送发布**
  - [ ] Git 提交
  - [ ] 打标签
  - [ ] 推送代码
  - [ ] 推送 Docker 镜像

---

## 🛡️ 安全注意事项

### 绝对不能提交的内容

❌ **Cookies 文件**
- `cookies/*.txt`
- 包含真实账号的认证信息

❌ **测试日志**
- `logs/*.log`
- 包含下载记录和敏感信息

❌ **测试下载内容**
- `downloads/*/*`
- 可能包含版权内容

❌ **环境变量**
- `.env` 文件
- 包含密码和密钥

❌ **数据库文件**
- `data/bosco.db`
- 包含用户数据

### 已配置的 .gitignore

```gitignore
downloads/
cookies/
data/
logs/
.env
*.log
__pycache__/
*.pyc
node_modules/
```

---

## 📚 相关文档

- [使用说明书](USAGE_MANUAL.md) - 详细功能说明
- [更新日志](CHANGELOG.md) - 版本变更记录
- [快速参考](QUICK_REFERENCE.md) - 常用命令

---

## 🐛 故障排查

### 构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### 推送被拒绝

```bash
# 检查大文件
git rev-list --objects --all | grep "$(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -10 | awk '{print$1}')"

# 从历史中移除大文件
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch PATH-TO-YOUR-FILE-FULL-PATH' --prune-empty --tag-name-filter cat -- --all
```

### 版本冲突

```bash
# 查看当前版本
grep version=" backend/main.py

# 手动更新版本号
# 编辑 backend/main.py
# 编辑 frontend/package.json
# 编辑 CHANGELOG.md
```

---

## 📞 支持

- 📖 [使用说明书](USAGE_MANUAL.md)
- 🐛 提交 Issue
- 💬 联系开发团队

---

**最后更新:** 2026-06-16  
**版本:** v0.3.0
