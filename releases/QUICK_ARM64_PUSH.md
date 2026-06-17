# 🚀 快速推送 arm64 镜像指南

## 📋 当前状态

- ✅ **linux/amd64** - 已推送到 Docker Hub
- ⏳ **linux/arm64** - 需要通过 GitHub Actions 推送

---

## 🎯 最简单的方法：GitHub Actions（5 分钟完成）

我已经为您创建好了 GitHub Actions 工作流文件，只需要按照以下步骤操作：

### 步骤 1：提交代码到 GitHub

```bash
# 添加所有文件
git add .

# 提交
git commit -m "ci: 添加多架构 Docker 构建工作流"

# 推送到 GitHub
git push origin main

# 推送标签（这会触发自动构建）
git tag v0.3.0
git push origin v0.3.0
```

### 步骤 2：设置 GitHub Secrets

1. 打开您的 GitHub 仓库
2. 进入 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`

添加以下两个 Secret：

| Secret 名称 | 值 |
|------------|-----|
| `DOCKER_USERNAME` | `boscotom` |
| `DOCKER_PASSWORD` | `your-docker-password` |

### 步骤 3：等待构建完成

推送标签后，GitHub Actions 会自动开始构建：

1. 进入仓库的 `Actions` 标签页
2. 点击 `Docker Multi-Arch Build and Push` 工作流
3. 等待约 10-15 分钟
4. 构建完成后，arm64 镜像会自动推送到 Docker Hub

### 步骤 4：验证

构建完成后验证：

```bash
# 查看镜像信息
docker manifest inspect boscotom/bosco-tsang:latest
```

您应该看到两个架构：
- ✅ linux/amd64
- ✅ linux/arm64

---

## 📝 手动触发构建（可选）

如果您不想推送标签，也可以手动触发：

1. 进入 GitHub 仓库
2. 点击 `Actions` → `Docker Multi-Arch Build and Push`
3. 点击 `Run workflow` 按钮
4. 输入版本号：`v0.3.0`
5. 点击 `Run workflow`

---

## 📊 构建过程

GitHub Actions 会执行以下步骤：

1. ✅ 检出代码
2. ✅ 设置 QEMU（模拟 arm64）
3. ✅ 设置 Docker Buildx
4. ✅ 登录 Docker Hub
5. ✅ 构建 linux/amd64 镜像
6. ✅ 构建 linux/arm64 镜像
7. ✅ 创建多架构 manifest
8. ✅ 推送到 Docker Hub
9. ✅ 验证 manifest

---

## 💡 优势

使用 GitHub Actions 的优势：

- ✅ **不受网络限制** - 在 GitHub 服务器上构建，无 IPv6 问题
- ✅ **完全自动化** - 推送标签即触发构建
- ✅ **真正的多架构** - 使用 QEMU 模拟构建 arm64
- ✅ **构建缓存** - 后续构建更快
- ✅ **免费使用** - 每月 2000 分钟免费额度
- ✅ **可重复触发** - 随时可以重新构建

---

## 📁 已创建的文件

我已经为您创建了以下文件：

| 文件 | 说明 |
|------|------|
| `.github/workflows/docker-multiarch.yml` | GitHub Actions 工作流配置 |
| `ARM64_PUSH_GUIDE.md` | 详细的 arm64 推送指南（5 种方案） |
| `DOCKER_PUSH_REPORT.md` | Docker 推送报告 |

---

## 🆘 遇到问题？

### 问题 1：GitHub Actions 未触发

**解决方案：**
- 检查标签是否正确推送：`git tag -l`
- 检查 GitHub Actions 是否启用
- 检查工作流文件语法

### 问题 2：构建失败

**解决方案：**
- 查看 Actions 日志
- 确认 Docker Hub 凭据正确
- 确认 Dockerfile 无误

### 问题 3：Secret 未设置

**解决方案：**
- 进入 `Settings` → `Secrets and variables` → `Actions`
- 确保 `DOCKER_USERNAME` 和 `DOCKER_PASSWORD` 已设置
- 注意 Secret 名称必须完全匹配（区分大小写）

---

## 🎉 完成后

构建成功后，您就可以在任何平台使用镜像：

### x86_64 服务器
```bash
docker pull boscotom/bosco-tsang:latest
docker run -d -p 8080:8000 boscotom/bosco-tsang:latest
```

### ARM 服务器（树莓派、AWS Graviton 等）
```bash
docker pull boscotom/bosco-tsang:latest
docker run -d -p 8080:8000 boscotom/bosco-tsang:latest
```

### Apple Silicon Mac（M1/M2/M3）
```bash
docker pull boscotom/bosco-tsang:latest
docker run -d -p 8080:8000 boscotom/bosco-tsang:latest
```

Docker 会自动选择正确的架构！

---

**下一步：** 提交代码到 GitHub 并设置 Secrets，然后推送标签触发构建！

**更新时间：** 2026-06-16  
**版本：** v0.3.0
