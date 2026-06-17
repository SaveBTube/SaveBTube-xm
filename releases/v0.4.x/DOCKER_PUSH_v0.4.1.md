# 📦 Docker 镜像推送报告 - v0.4.1

## ✅ 推送成功

**推送时间：** 2026-06-16  
**仓库地址：** https://hub.docker.com/r/boscotom/bosco-tsang  
**架构：** linux/amd64  

---

## 📋 推送的镜像标签

| 标签 | Digest | 状态 |
|------|--------|------|
| `v0.4.1` | `sha256:95cdf1a2a3d48eb8f6a5e6db64ee639ec50d6c48c5b8075555e75ccc9473df3a` | ✅ 已推送 |
| `latest` | `sha256:cecb9cccfb0abb54098fcc1db68eddf28ffad9ee95000a1b8a17c7ce44a322d0` | ✅ 已推送 |

---

## 🎯 v0.4.1 版本内容

### 🐛 问题修复：iOS 快捷指令一键安装

#### 修复的问题
1. ✅ **配置文件下载 404 错误**
   - 调整路由顺序
   - 修改 MIME 类型
   - 确保文件正确下载

2. ✅ **快捷指令无法安装**
   - 创建一键安装页面
   - 使用 iOS URL Scheme
   - 自动生成正确格式

3. ✅ **需要手动配置**
   - 自动填充服务器地址
   - 表单输入 API Key
   - 一键安装自动保存

#### 新增功能
- ✅ `/shortcuts/install` 一键安装页面
- ✅ 自动检测并填充服务器地址
- ✅ API Key 表单输入与验证
- ✅ iOS URL Scheme 直接跳转
- ✅ 移动端优化 UI

---

## 🚀 使用方法

### 拉取镜像

```bash
# 拉取最新版本
docker pull boscotom/bosco-tsang:latest

# 或拉取指定版本
docker pull boscotom/bosco-tsang:v0.4.1
```

### 运行容器

```bash
docker run -d \
  --name bosco-tsang \
  -p 8080:8000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookies:/app/cookies \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  boscotom/bosco-tsang:v0.4.1
```

---

## 📱 iOS 快捷指令安装

### 安装地址

```
http://your-server:8080/shortcuts/install
```

### 安装步骤

1. 在 iPhone Safari 中打开安装页面
2. 输入 API Key（服务器地址已自动填充）
3. 点击"📲 一键安装快捷指令"
4. 在弹出窗口点击"添加快捷指令"
5. 完成！

---

## 🔐 隐私数据保护

### ✅ 已清理的隐私数据

1. **Docker Hub 密码**
   - ❌ 删除：`your-docker-token`
   - ✅ 替换：`your-docker-password`

2. **影响文件**
   - `DOCKER_PUSH_v0.4.0.md` ✅ 已清理
   - `DOCKER_PUSH_v0.3.1.md` ✅ 已清理
   - `QUICK_ARM64_PUSH.md` ✅ 已清理

3. **保留的安全数据**
   - ✅ 示例代码中的占位符（如 `your-api-key`）
   - ✅ 文档中的示例用户名（如 `admin`）
   - ✅ API 端点和路由信息

### 🔒 Git 忽略配置

以下敏感数据已被 `.gitignore` 忽略：

```
.env              # 环境变量（包含密码）
data/             # 数据库文件
logs/             # 日志文件
cookies/          # Cookies 文件
downloads/        # 下载文件
*.log             # 所有日志文件
```

---

## 📂 v0.4.1 包含的文件

### 修改文件
- ✅ `backend/main.py` - 修复路由和 MIME 类型
- ✅ `static/shortcuts-install.html` - 一键安装页面
- ✅ `CHANGELOG.md` - 添加 v0.4.1 更新日志
- ✅ `USAGE_MANUAL.md` - 更新版本信息
- ✅ `DOCKER_PUSH_*.md` - 清理隐私数据

### 新增文件
- ✅ `shortcuts/INSTALL_GUIDE.md` - 安装指南
- ✅ `update-v0.4.1.ps1` - 文档更新脚本
- ✅ `docs/DOCUMENT_UPDATE_v0.4.1.md` - 更新报告

---

## 📊 推送详情

### 推送命令

```bash
# 登录 Docker Hub
echo "your-docker-password" | docker login -u boscotom --password-stdin

# 标记镜像
docker tag boscotsang-bosco-tsang:latest boscotom/bosco-tsang:v0.4.1

# 推送镜像
docker push boscotom/bosco-tsang:v0.4.1
docker push boscotom/bosco-tsang:latest
```

### 推送输出

```
v0.4.1: digest: sha256:95cdf1a2a3d48eb8f6a5e6db64ee639ec50d6c48c5b8075555e75ccc9473df3a size: 856
latest: digest: sha256:cecb9cccfb0abb54098fcc1db68eddf28ffad9ee95000a1b8a17c7ce44a322d0 size: 856
```

---

## 🌐 访问地址

| 功能 | URL |
|------|-----|
| 主界面 | http://localhost:8080 |
| 快捷指令安装 | http://localhost:8080/shortcuts/install |
| 快捷指令配置 | http://localhost:8080/api/shortcuts/config |
| 快捷指令 API | http://localhost:8080/api/shortcuts/download |
| 使用说明书 | http://localhost:8080/docs/USAGE_MANUAL.html |
| 更新日志 | http://localhost:8080/docs/CHANGELOG.html |

---

## 📊 版本历史

| 版本 | 日期 | 架构 | 说明 |
|------|------|------|------|
| v0.4.1 | 2026-06-16 | amd64 | 修复快捷指令安装，一键安装功能 |
| v0.4.0 | 2026-06-16 | amd64 | 新增 iOS 快捷指令下载功能 |
| v0.3.2 | 2026-06-16 | amd64 | 文档自动更新系统 |
| v0.3.1 | 2026-06-16 | amd64 | 修复文档访问、代理保存、国内平台 |
| v0.3.0 | 2026-06-16 | amd64 | Telegram 生态 + X/Twitter 下载 |
| latest | 2026-06-16 | amd64 | 最新稳定版 |

---

## ⚠️ 安全建议

### 1. 不要在公共仓库中包含

- ❌ `.env` 文件
- ❌ 数据库文件（`data/bosco.db`）
- ❌ Cookies 文件
- ❌ 日志文件
- ❌ 密码和 Token

### 2. 使用环境变量

```bash
# .env 文件（不要提交到 Git）
BOSCO_ADMIN_PASSWORD=your-secure-password
BOSCO_SECRET_KEY=your-secret-key
```

### 3. 定期更新密码

- 定期更改 Docker Hub 密码
- 使用强密码（12+ 字符）
- 启用双因素认证

---

## 📝 Git 推送说明

由于权限问题，Git 推送需要手动执行：

```bash
# 推送代码到 GitHub
git push origin main

# 推送标签
git push origin v0.4.1
```

**注意：** 所有隐私数据已从文档中清理。

---

## 🔗 相关链接

- **Docker Hub 仓库：** https://hub.docker.com/r/boscotom/bosco-tsang
- **GitHub 仓库：** https://github.com/BoscoTsang-Z/BoscoTsang-0.1
- **快捷指令指南：** [shortcuts/INSTALL_GUIDE.md](file:///H:/docker开发文档/BoscoTsang/shortcuts/INSTALL_GUIDE.md)
- **更新报告：** [docs/DOCUMENT_UPDATE_v0.4.1.md](file:///H:/docker开发文档/BoscoTsang/docs/DOCUMENT_UPDATE_v0.4.1.md)

---

**v0.4.1 推送完成！** 🎉

所有隐私数据已清理，镜像安全可推送！
