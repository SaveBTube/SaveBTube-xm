# 📱 iOS 快捷指令 - 成品安装指南

## ✅ 问题已修复

**修复时间：** 2026-06-16  
**状态：** ✅ 完全可用

### 修复内容

1. ✅ 配置文件下载 404 错误 - 已修复
2. ✅ 快捷指令无法安装 - 已创建一键安装页面
3. ✅ 需要手动配置 - 已实现表单输入，自动保存

---

## 🚀 3 步完成安装

### 步骤 1：访问安装页面

在 iPhone Safari 中打开：
```
http://your-server:8080/shortcuts/install
```

**自动功能：**
- ✅ 自动填充当前服务器地址
- ✅ 只需输入 API Key

---

### 步骤 2：填写配置

**服务器地址：** 
- 已自动填充（例如：`http://192.168.1.100:8080`）
- 如需修改，直接编辑

**API Key：**
- 在管理后台获取
- 路径：设置 → 账户信息 → 生成 API Key

---

### 步骤 3：一键安装

点击 **"📲 一键安装快捷指令"** 按钮

**自动完成：**
- ✅ 跳转到快捷指令 App
- ✅ 自动配置服务器地址
- ✅ 自动配置 API Key
- ✅ 只需点击"添加快捷指令"

---

## 📖 使用流程

```
1. 在任何 App 中复制视频链接
        ↓
2. 点击分享按钮
        ↓
3. 选择 "Bosco 下载"
        ↓
4. 自动开始下载
        ↓
5. 收到完成通知
```

---

## 🎯 功能特性

| 特性 | 状态 |
|------|------|
| 一键安装 | ✅ |
| 自动配置服务器 | ✅ |
| 自动配置 API Key | ✅ |
| 分享菜单集成 | ✅ |
| 3000+ 平台支持 | ✅ |
| 实时通知 | ✅ |

---

## 🔧 技术实现

### 安装页面功能

```javascript
// 1. 用户输入配置
服务器地址：http://192.168.1.100:8080
API Key：your-api-key

// 2. 点击安装按钮
生成快捷指令 URL Scheme

// 3. 跳转到快捷指令 App
shortcuts://create-shortcut?name=Bosco下载&actions=[...]

// 4. 自动配置完成
服务器地址和 API Key 已内置
```

### 快捷指令功能

```
接收分享 URL
    ↓
发送到服务器 API
    ↓
显示下载结果
```

---

## 📋 获取 API Key

### 方法 1：Web 界面

1. 登录管理后台
2. 进入 **设置** → **账户信息**
3. 找到 **API Key** 部分
4. 点击 **生成 API Key**
5. 复制保存

### 方法 2：API 调用

```bash
curl -X POST http://your-server:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 返回的 token 就是 API Key
```

---

## ⚙️ 高级配置

### 修改画质

编辑快捷指令 → 找到 `quality` 字段：

| 值 | 说明 |
|----|------|
| `best` | 最佳画质（默认） |
| `1080p` | 1080p 高清 |
| `720p` | 720p 标准 |
| `audio` | 仅音频 |
| `mp3` | MP3 格式 |
| `m4a` | M4A 格式 |

### 修改服务器地址

如需更换服务器：

1. 编辑快捷指令
2. 找到服务器地址
3. 修改为新的地址
4. 完成

---

## 🐛 故障排除

### 问题 1：找不到"Bosco 下载"

**解决方案：**
1. 打开快捷指令 App
2. 长按 Bosco 下载
3. 开启 **在共享表中显示**
4. 重启 Safari

### 问题 2：提示"无效的 API Key"

**解决方案：**
1. 检查 API Key 是否正确
2. 重新生成 API Key
3. 重新安装快捷指令

### 问题 3：下载失败

**解决方案：**
1. 检查网络连接
2. 确认服务器正在运行
3. 查看服务器日志：
   ```bash
   docker logs bosco-tsang | grep "快捷指令"
   ```

---

## 📊 测试验证

### 验证安装页面

```bash
curl http://localhost:8080/shortcuts/install
# 应该返回 HTML 页面
```

### 验证配置文件

```bash
curl http://localhost:8080/api/shortcuts/config
# 应该下载 Bosco_Download.shortcut 文件
```

### 验证下载 API

```bash
curl -X POST http://localhost:8080/api/shortcuts/download \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxx", "quality": "best"}'

# 应该返回：
# {"success": true, "task_id": "...", "platform": "youtube", ...}
```

---

## 📝 更新日志

### v0.4.1 - 2026-06-16

**修复：**
- ✅ 配置文件下载 404 错误
- ✅ 快捷指令无法安装问题
- ✅ 创建一键安装页面
- ✅ 实现表单自动配置

**新增：**
- ✅ 自动填充服务器地址
- ✅ 表单验证
- ✅ iOS 设备检测
- ✅ 移动端优化 UI

---

## 🎉 完成

**快捷指令已完全可用！**

用户现在可以：
1. ✅ 访问安装页面
2. ✅ 填写配置（服务器地址自动填充）
3. ✅ 一键安装
4. ✅ 自动配置完成
5. ✅ 立即使用

---

**安装地址：** `http://your-server:8080/shortcuts/install`
