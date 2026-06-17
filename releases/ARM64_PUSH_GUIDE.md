# 🐳 推送 linux/arm64 架构镜像指南

## ⚠️ 当前问题

在 Windows Docker Desktop 环境下，尝试构建和推送 `linux/arm64` 架构镜像时遇到了 **IPv6 网络连接问题**：

```
ERROR: failed to solve: failed to fetch oauth token: 
Post "https://auth.docker.io/token": 
dial tcp [2a03:2880:f131:83:face:b00c:0:25de]:443: 
connectex: A connection attempt failed because the connected party 
did not properly respond after a period of time
```

**原因：** 
- Docker Hub 的 arm64 镜像需要使用 IPv6 连接
- Windows Docker Desktop 在某些网络环境下无法正确连接 IPv6 地址
- 这是 Windows 平台的已知限制

---

## ✅ 解决方案

### 方案 1：使用 GitHub Actions（推荐 ⭐⭐⭐⭐⭐）

这是最简单、最可靠的方式，完全自动化且不受本地网络限制。

#### 步骤：

**1. 创建 GitHub Actions 工作流文件**

在项目根目录创建 `.github/workflows/docker-multiarch.yml`：

```yaml
name: Docker Multi-Arch Build and Push

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to build (e.g., v0.3.0)'
        required: true
        default: 'v0.3.0'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3
        with:
          platforms: 'arm64'
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push multi-arch
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          provenance: false
          tags: |
            boscotom/bosco-tsang:latest
            boscotom/bosco-tsang:${{ github.event.inputs.version || github.ref_name }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**2. 设置 GitHub Secrets**

在 GitHub 仓库中设置：
- `Settings` → `Secrets and variables` → `Actions`
- 添加 `DOCKER_USERNAME`: `boscotom`
- 添加 `DOCKER_PASSWORD`: `your-docker-token`

**3. 触发构建**

方式一：推送标签
```bash
git tag v0.3.0
git push origin v0.3.0
```

方式二：手动触发
- 进入 GitHub 仓库 → `Actions` → `Docker Multi-Arch Build and Push`
- 点击 `Run workflow`
- 输入版本号 `v0.3.0`
- 点击 `Run workflow`

**优点：**
- ✅ 完全自动化
- ✅ 不受本地网络限制
- ✅ 支持真正的多架构构建
- ✅ 构建缓存，速度快
- ✅ 可重复触发

---

### 方案 2：使用 Linux/Mac 服务器（推荐 ⭐⭐⭐⭐）

如果您有 Linux 或 Mac 服务器/虚拟机：

#### 步骤：

**1. 在服务器上安装 Docker**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 或者使用官方脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**2. 克隆项目**

```bash
git clone <your-repo-url>
cd BoscoTsang
```

**3. 构建并推送多架构镜像**

```bash
docker login -u boscotom -p your-docker-token

# 构建并推送
docker buildx build --platform linux/amd64,linux/arm64 \
  -t boscotom/bosco-tsang:latest \
  -t boscotom/bosco-tsang:v0.3.0 \
  --push \
  --provenance=false \
  .
```

**4. 验证**

```bash
docker manifest inspect boscotom/bosco-tsang:latest
```

应该看到两个架构：
```json
{
  "manifests": [
    {
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    },
    {
      "platform": {
        "architecture": "arm64",
        "os": "linux"
      }
    }
  ]
}
```

---

### 方案 3：使用云服务器临时实例（推荐 ⭐⭐⭐）

使用 AWS EC2、Google Cloud、阿里云等的免费实例：

#### AWS EC2 示例：

**1. 启动 EC2 实例**

- 选择 Ubuntu 22.04
- 实例类型：t2.medium 或更高
- 存储：50GB

**2. SSH 连接并安装 Docker**

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
exit

# 重新连接
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**3. 克隆并构建**

```bash
git clone <your-repo-url>
cd BoscoTsang

docker login -u boscotom -p your-docker-token

docker buildx build --platform linux/amd64,linux/arm64 \
  -t boscotom/bosco-tsang:latest \
  -t boscotom/bosco-tsang:v0.3.0 \
  --push .
```

**4. 终止实例**

构建完成后终止实例以避免费用。

---

### 方案 4：在 Windows 上使用 WSL2 Linux（可能有效 ⭐⭐）

#### 步骤：

**1. 启用 WSL2**

```powershell
# PowerShell 管理员
wsl --install
wsl --set-default-version 2
```

**2. 安装 Ubuntu**

从 Microsoft Store 安装 Ubuntu 22.04

**3. 在 WSL2 中安装 Docker**

```bash
# 在 WSL2 Ubuntu 中
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**4. 构建并推送**

```bash
cd /mnt/h/docker开发文档/BoscoTsang

sudo docker login -u boscotom -p your-docker-token

sudo docker buildx build --platform linux/amd64,linux/arm64 \
  -t boscotom/bosco-tsang:latest \
  -t boscotom/bosco-tsang:v0.3.0 \
  --push \
  --provenance=false \
  .
```

**注意：** WSL2 的网络环境与 Windows Docker Desktop 不同，可能可以绕过 IPv6 问题。

---

### 方案 5：使用在线构建服务（推荐 ⭐⭐⭐）

#### 选项 1：Docker Hub 自动构建

1. 将代码推送到 GitHub
2. 在 Docker Hub 创建自动构建
3. 配置构建规则
4. Docker Hub 会自动构建多架构镜像

#### 选项 2：GitHub Container Registry (GHCR)

```yaml
# .github/workflows/docker-ghcr.yml
name: Docker GHCR Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

---

## 📊 方案对比

| 方案 | 难度 | 成本 | 速度 | 推荐度 |
|------|------|------|------|--------|
| GitHub Actions | ⭐ | 免费（2000分钟/月） | 快 | ⭐⭐⭐⭐⭐ |
| Linux/Mac 服务器 | ⭐⭐ | 需要服务器 | 快 | ⭐⭐⭐⭐ |
| 云服务器临时实例 | ⭐⭐ | 按量付费 | 快 | ⭐⭐⭐ |
| WSL2 Linux | ⭐⭐⭐ | 免费 | 中 | ⭐⭐ |
| Docker Hub 自动构建 | ⭐ | 免费 | 慢 | ⭐⭐⭐ |

---

## 🎯 快速开始（推荐 GitHub Actions）

**1 分钟设置：**

```bash
# 1. 创建工作流目录
mkdir -p .github/workflows

# 2. 创建文件 .github/workflows/docker-multiarch.yml
# （复制上面的配置）

# 3. 提交到 GitHub
git add .github/workflows/docker-multiarch.yml
git commit -m "ci: 添加多架构 Docker 构建工作流"
git push origin main

# 4. 在 GitHub 设置 Secrets
# DOCKER_USERNAME = boscotom
# DOCKER_PASSWORD = your-docker-token

# 5. 推送标签触发构建
git tag v0.3.0
git push origin v0.3.0
```

构建会自动进行，约 10-15 分钟完成。

---

## ✅ 验证多架构镜像

构建完成后验证：

```bash
# 拉取镜像
docker pull boscotom/bosco-tsang:latest

# 查看镜像信息
docker manifest inspect boscotom/bosco-tsang:latest

# 应该看到 amd64 和 arm64 两个架构
```

在不同平台测试：

```bash
# x86_64 服务器
docker run --rm boscotom/bosco-tsang:latest python -c "import platform; print(platform.machine())"
# 输出: x86_64

# ARM 服务器（如 AWS Graviton、树莓派）
docker run --rm boscotom/bosco-tsang:latest python -c "import platform; print(platform.machine())"
# 输出: aarch64
```

---

## 📝 当前状态

- ✅ **linux/amd64** - 已推送（latest, v0.3.0）
- ⏳ **linux/arm64** - 待推送（需要使用上述方案之一）

---

## 📞 需要帮助？

- 查看 [GitHub Actions 文档](https://docs.github.com/en/actions)
- 查看 [Docker Buildx 文档](https://docs.docker.com/build/buildx/)
- 查看 [多架构构建指南](https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/)

---

**更新时间：** 2026-06-16  
**版本：** v0.3.0  
**维护团队：** Bosco Tsang 开发团队
