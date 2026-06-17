# 📦 Docker 镜像推送报告

## ✅ 推送成功

**推送时间：** 2026-06-16 13:05  
**仓库地址：** https://hub.docker.com/r/boscotom/bosco-tsang  
**架构：** linux/amd64  

---

## 📋 推送的镜像标签

| 标签 | Digest | 大小 | 状态 |
|------|--------|------|------|
| `v0.3.1` | `sha256:3dc39df8a7f5fea0e907f6c6e8b5270663cc4640aeb6fcb17cce74958c0040e2` | ~850 MB | ✅ 已推送 |
| `latest` | `sha256:3dc39df8a7f5fea0e907f6c6e8b5270663cc4640aeb6fcb17cce74958c0040e2` | ~850 MB | ✅ 已推送 |

---

## 🎯 v0.3.1 版本内容

### 修复的问题

1. **✅ 帮助和更新按钮无法打开**
   - 添加模态框弹窗显示文档
   - 后端新增 `/docs/{doc_name}` API
   - Markdown 实时转 HTML

2. **✅ 代理开关无法保存状态**
   - 切换后立即保存到数据库
   - 刷新页面状态保持
   - 失败自动回滚

3. **✅ 断开代理后国内平台无法下载**
   - 重构代理逻辑
   - 关闭代理时完全清空
   - Bilibili 等平台强制禁用代理

### 技术改进

- 添加 `markdown` Python 库支持
- 优化代理配置逻辑
- 改进用户体验（模态框设计）
- 完善错误处理机制

---

## 🚀 使用方法

### 拉取镜像

```bash
# 拉取最新版本
docker pull boscotom/bosco-tsang:latest

# 或拉取指定版本
docker pull boscotom/bosco-tsang:v0.3.1
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
  boscotom/bosco-tsang:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  bosco-tsang:
    image: boscotom/bosco-tsang:v0.3.1
    container_name: bosco-tsang
    ports:
      - "8080:8000"
    volumes:
      - ./downloads:/app/downloads
      - ./cookies:/app/cookies
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

---

## 📊 推送详情

### 推送命令

```bash
# 登录 Docker Hub
echo "your-docker-password" | docker login -u boscotom --password-stdin

# 标记镜像
docker tag boscotsang-bosco-tsang:latest boscotom/bosco-tsang:v0.3.1
docker tag boscotsang-bosco-tsang:latest boscotom/bosco-tsang:latest

# 推送镜像
docker push boscotom/bosco-tsang:v0.3.1
docker push boscotom/bosco-tsang:latest
```

### 推送输出

```
v0.3.1: digest: sha256:3dc39df8a7f5fea0e907f6c6e8b5270663cc4640aeb6fcb17cce74958c0040e2 size: 856
latest: digest: sha256:3dc39df8a7f5fea0e907f6c6e8b5270663cc4640aeb6fcb17cce74958c0040e2 size: 856
```

### 层级信息

```
7f580a0b326b: Pushed (基础系统层)
afc5df9a7a66: Pushed (Python 依赖层)
f2b41d17a57a: Pushed (FFmpeg 层)
761b88a3de45: Pushed (后端代码层)
9fa096e2c9eb: Pushed (文档文件层)
f0ecb5b52fe7: Pushed (前端静态文件层)
4a6f3f8855f9: Pushed (配置层)
d513357a3801: Pushed (扩展插件层)
3c58578f3959: Pushed (数据目录层)
e55a54cc6a5a: Pushed (启动脚本层)
d0dc45a87190: Pushed (工作目录层)
```

---

## 🌐 验证推送

### 在线查看

访问 Docker Hub 查看推送的镜像：
- **仓库地址：** https://hub.docker.com/r/boscotom/bosco-tsang
- **标签列表：** https://hub.docker.com/r/boscotom/bosco-tsang/tags

### 命令行验证

```bash
# 查看远程标签
docker manifest inspect boscotom/bosco-tsang:v0.3.1

# 拉取并测试
docker pull boscotom/bosco-tsang:v0.3.1
docker run --rm boscotom/bosco-tsang:v0.3.1 python -c "import markdown; print('markdown OK')"
```

---

## ⚠️ 注意事项

### linux/arm64 架构

由于 Windows Docker Desktop 的 IPv6 网络限制，`linux/arm64` 架构未能推送。

**解决方案：**

1. **使用 GitHub Actions**（推荐）
   - 工作流文件已创建：`.github/workflows/docker-multiarch.yml`
   - 推送代码到 GitHub 后自动构建
   - 支持 amd64 + arm64 双架构

2. **在 Linux/Mac 服务器上构建**
   ```bash
   docker buildx build --platform linux/amd64,linux/arm64 \
     -t boscotom/bosco-tsang:v0.3.1 \
     --push .
   ```

3. **使用云服务器临时实例**
   - 创建 Ubuntu 云主机
   - 安装 Docker Buildx
   - 构建并推送多架构镜像

### 下次推送清单

- [ ] 推送 linux/arm64 架构
- [ ] 创建多架构 manifest
- [ ] 验证 arm64 设备上的运行

---

## 📝 版本历史

| 版本 | 日期 | 架构 | 说明 |
|------|------|------|------|
| v0.3.1 | 2026-06-16 | amd64 | 修复文档访问、代理保存、国内平台下载 |
| v0.3.0 | 2026-06-15 | amd64 | 初始版本 |
| latest | 2026-06-16 | amd64 | 最新稳定版 |

---

## 🔗 相关链接

- **Docker Hub 仓库：** https://hub.docker.com/r/boscotom/bosco-tsang
- **GitHub 仓库：** （待添加）
- **项目文档：** https://hub.docker.com/r/boscotom/bosco-tsang
- **问题反馈：** （待添加）

---

**推送完成！** 🎉

镜像已成功推送到 Docker Hub，用户可以随时拉取使用。
