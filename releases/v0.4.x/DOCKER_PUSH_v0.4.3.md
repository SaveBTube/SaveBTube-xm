# 📦 Docker 镜像推送报告 - v0.4.3

## ✅ 推送成功

**推送时间：** 2026-06-16  
**版本：** v0.4.3  
**仓库：** https://hub.docker.com/r/boscotom/bosco-tsang  

---

## 🎯 v0.4.3 修复内容

### iOS 快捷指令安装方式调整

**问题：** iOS 不支持导入未签名的快捷指令文件

**解决方案：** 改为手动配置方式

- ✅ 提供详细的配置说明
- ✅ 一键复制配置信息
- ✅ 清晰的 5 步安装指南
- ✅ 自动填充服务器地址

---

## 📱 新的安装流程

```
1. 访问安装页面
   http://your-server:8080/shortcuts/install
        ↓
2. 填写服务器地址和 API Key
        ↓
3. 点击"获取快捷指令"
        ↓
4. 配置自动复制到剪贴板
        ↓
5. 按照提示创建快捷指令
   （只需操作一次）
        ↓
6. 完成！
```

---

## 📋 推送的镜像标签

| 标签 | Digest | 状态 |
|------|--------|------|
| `v0.4.3` | `sha256:0a13dc6d52f6d462cc593c20c37b87c4ab532aaa9ca0658e1a04b5f99687a535` | ✅ 已推送 |
| `latest` | `sha256:cecb9cccfb0abb54098fcc1db68eddf28ffad9ee95000a1b8a17c7ce44a322d0` | ✅ 已推送 |

---

## 🚀 使用方法

```bash
# 拉取镜像
docker pull boscotom/bosco-tsang:latest

# 运行容器
docker run -d \
  --name bosco-tsang \
  -p 8080:8000 \
  -v ./downloads:/app/downloads \
  -v ./cookies:/app/cookies \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  boscotom/bosco-tsang:v0.4.3
```

---

## 🌐 访问地址

| 功能 | URL |
|------|-----|
| 快捷指令安装 | http://localhost:8080/shortcuts/install |
| 快捷指令下载 | http://localhost:8080/shortcuts/download |
| 使用指南 | http://localhost:8080/docs/IOS_SHORTCUTS_GUIDE.html |
| 主界面 | http://localhost:8080 |

---

## 📊 版本历史

| 版本 | 说明 |
|------|------|
| v0.4.3 | 调整快捷指令安装方式（手动配置） |
| v0.4.2 | 快捷指令成品化 + 文档 Web 访问 |
| v0.4.1 | 修复快捷指令安装问题 |
| v0.4.0 | 新增 iOS 快捷指令功能 |
| latest | 最新稳定版 |

---

**v0.4.3 推送完成！** 🎉
