# 🌐 本地测试端口配置

## 📊 当前端口映射

| 容器端口 | 主机端口 | 协议 | 状态 |
|---------|---------|------|------|
| 8000 | 8080 | TCP | ✅ 运行中 |

---

## 🔗 访问地址

### 主入口
```
http://localhost:8080
http://127.0.0.1:8080
```

### 局域网访问
```
http://<你的IP地址>:8080
```

查看本机 IP：
```bash
# Windows
ipconfig | findstr IPv4

# 或使用
hostname -I  # Linux/Mac
```

---

## 📱 功能访问地址

### 核心功能

| 功能 | 地址 | 说明 |
|------|------|------|
| **管理后台** | http://localhost:8080 | 主界面 |
| **登录页面** | http://localhost:8080/login | 管理员登录 |
| **API 文档** | http://localhost:8080/docs | Swagger UI |
| **健康检查** | http://localhost:8080/ | 服务状态 |

### 快捷指令相关

| 功能 | 地址 | 说明 |
|------|------|------|
| **快捷指令下载** | http://localhost:8080/shortcuts/download | 下载页面 |
| **快捷指令安装** | http://localhost:8080/shortcuts/install | 安装配置 |
| **快捷指令文件** | http://localhost:8080/api/shortcuts/download-file | .shortcut 文件 |
| **快捷指令 API** | http://localhost:8080/api/shortcuts/download | 下载接口 |
| **使用指南** | http://localhost:8080/docs/IOS_SHORTCUTS_GUIDE.html | Web 文档 |

### 文档中心

| 功能 | 地址 | 说明 |
|------|------|------|
| **使用说明书** | http://localhost:8080/docs/USAGE_MANUAL.html | 完整使用说明 |
| **更新日志** | http://localhost:8080/docs/CHANGELOG.html | 版本历史 |
| **快速参考** | http://localhost:8080/docs/QUICK_REFERENCE.html | 命令速查 |

---

## 🔧 修改端口

### 方法 1：修改 docker-compose.yml

编辑 `docker-compose.yml`：

```yaml
services:
  bosco-tsang:
    ports:
      - "8080:8000"  # 修改这里的 8080 为你想要的端口
```

例如改为 3000 端口：
```yaml
    ports:
      - "3000:8000"
```

然后重启：
```bash
docker-compose down
docker-compose up -d
```

### 方法 2：使用 docker run

```bash
docker run -d \
  --name bosco-tsang \
  -p 3000:8000 \  # 修改这里的端口
  -v ./downloads:/app/downloads \
  -v ./cookies:/app/cookies \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  boscotom/bosco-tsang:latest
```

---

## 🧪 本地测试命令

### 1. 测试服务是否运行

```bash
curl http://localhost:8080/
# 应该返回服务信息
```

### 2. 测试登录

```bash
curl -X POST http://localhost:8080/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 3. 测试获取设置

```bash
curl http://localhost:8080/api/settings \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 测试快捷指令下载页面

```bash
curl http://localhost:8080/shortcuts/download
# 应该返回 HTML 页面
```

### 5. 测试文档访问

```bash
curl http://localhost:8080/docs/USAGE_MANUAL.html
# 应该返回 HTML 格式的文档
```

---

## 📊 端口占用检查

### Windows

```powershell
# 检查 8080 端口是否被占用
netstat -ano | findstr :8080

# 或使用 PowerShell
Get-NetTCPConnection -LocalPort 8080
```

### Linux/Mac

```bash
# 检查端口占用
lsof -i :8080
# 或
netstat -tuln | grep 8080
```

---

## 🔥 常用端口推荐

| 端口 | 用途 | 推荐场景 |
|------|------|---------|
| **8080** | 默认端口 | 开发测试 ✅ |
| **3000** | 替代端口 | 避免冲突 |
| **5000** | 备用端口 | 多实例测试 |
| **8000** | 内部端口 | 容器内部 |
| **80** | HTTP 标准 | 生产环境 |
| **443** | HTTPS 标准 | 生产环境（SSL） |

---

## 🌍 外部访问配置

### 1. 防火墙设置

**Windows：**
```powershell
# 允许 8080 端口
New-NetFirewallRule -DisplayName "Bosco Tsang" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

**Linux：**
```bash
# UFW
sudo ufw allow 8080/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### 2. 路由器端口转发

如果要从外网访问：
1. 登录路由器管理界面
2. 找到"端口转发"或"虚拟服务器"
3. 添加规则：
   - 外部端口：8080
   - 内部 IP：你的电脑 IP
   - 内部端口：8080
   - 协议：TCP

---

## 🔐 安全建议

### 开发环境
- ✅ 使用 localhost 访问
- ✅ 关闭外部访问
- ✅ 使用默认密码测试

### 生产环境
- ✅ 修改默认密码
- ✅ 使用 HTTPS
- ✅ 配置防火墙
- ✅ 限制 IP 访问
- ✅ 定期更新

---

## 📝 测试清单

### 基础测试
- [ ] 访问 http://localhost:8080
- [ ] 登录管理后台
- [ ] 查看仪表板

### 功能测试
- [ ] 测试下载功能
- [ ] 测试快捷指令
- [ ] 测试文件管理
- [ ] 测试设置保存

### API 测试
- [ ] 测试登录接口
- [ ] 测试设置接口
- [ ] 测试下载接口
- [ ] 测试文档访问

---

## 🎯 快速开始

### 1. 启动服务

```bash
cd "H:\docker开发文档\BoscoTsang"
docker-compose up -d
```

### 2. 访问网站

打开浏览器访问：
```
http://localhost:8080
```

### 3. 登录系统

```
用户名：admin
密码：admin123
```

### 4. 开始使用

- 📥 下载视频/音频/图片
- 📱 安装快捷指令
- 📖 查看使用文档
- ⚙️ 配置系统设置

---

## 🐛 故障排除

### 问题 1：端口被占用

**错误：** `port 8080 is already allocated`

**解决：**
```bash
# 方法 1：停止占用端口的程序
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# 方法 2：更换端口
# 修改 docker-compose.yml 中的端口映射
```

### 问题 2：无法访问

**检查：**
1. 服务是否运行：`docker ps`
2. 端口是否正确：`docker port bosco-tsang`
3. 防火墙是否放行

### 问题 3：服务启动失败

**查看日志：**
```bash
docker logs bosco-tsang
```

---

## 📞 获取帮助

- **项目文档：** http://localhost:8080/docs/USAGE_MANUAL.html
- **API 文档：** http://localhost:8080/docs
- **GitHub：** https://github.com/BoscoTsang-Z/BoscoTsang-0.1
- **Docker Hub：** https://hub.docker.com/r/boscotom/bosco-tsang

---

**本地测试端口配置完成！** 🎉

访问 http://localhost:8080 开始使用！
