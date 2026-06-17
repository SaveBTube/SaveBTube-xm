# 📱 iOS 快捷指令下载功能

## 🎯 功能简介

通过 iOS 快捷指令（Shortcuts），您可以在 iPhone/iPad 上实现：

- ✅ **分享菜单直接下载** - 在任何 App 中点击分享 → 选择"Bosco 下载"
- ✅ **自动识别链接** - 支持 YouTube、Bilibili、Twitter、Instagram 等 3000+ 平台
- ✅ **实时进度推送** - 下载完成后自动通知
- ✅ **多种画质选择** - 自动/1080p/720p/音频
- ✅ **安全可靠** - 使用 API Key 认证，无需登录

---

## 📋 前置要求

1. **iOS 13 或更高版本**
2. **已安装"快捷指令" App**（iOS 自带）
3. **Bosco Tsang 服务已部署**
4. **获取 API Key**（见下方）

---

## 🔑 获取 API Key

### 方法 1：通过 Web 界面

1. 登录 BOSCO TSANG 管理后台
2. 进入 **设置** → **账户信息**
3. 找到 **API Key** 部分
4. 点击 **生成 API Key**
5. 复制并保存（只显示一次）

### 方法 2：通过 API

```bash
curl -X POST http://your-server:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 返回的 token 就是 API Key
```

---

## 🚀 安装快捷指令

### 方法 1：一键安装（推荐）

1. 在 iPhone 上打开 Safari
2. 访问：`http://your-server:8080/shortcuts/install`
3. 点击 **安装快捷指令**
4. 在弹出窗口中点击 **添加快捷指令**
5. 完成！

### 方法 2：手动创建

#### 步骤 1：创建新快捷指令

1. 打开 **快捷指令** App
2. 点击右上角 **+** 号
3. 点击 **添加操作**

#### 步骤 2：配置快捷指令

添加以下操作：

**操作 1：获取分享的内容**
```
操作：接收共享内容
类型：URL
```

**操作 2：显示输入框（API Key）**
```
操作：显示提示
标题：输入 API Key
文本：（首次使用时输入）
```

**操作 3：获取变量（服务器地址）**
```
操作：设定变量
名称：ServerURL
值：http://your-server:8080
```

**操作 4：下载 URL**
```
操作：获取 URL 的内容
URL：[ServerURL]/api/shortcuts/download
方法：POST
请求体：{
  "url": [共享的URL],
  "quality": "best"
}
标头：{
  "X-API-Key": [API Key],
  "Content-Type": "application/json"
}
```

**操作 5：显示结果**
```
操作：显示通知
标题：下载任务已创建
内容：[响应消息]
```

#### 步骤 3：设置分享菜单

1. 点击快捷指令名称（顶部）
2. 选择 **重命名** → `Bosco 下载`
3. 选择图标和颜色（可选）
4. 点击 **完成**
5. 在快捷指令详情中，开启 **在共享表中显示**

---

## 📖 使用说明

### 场景 1：从 Safari 下载

1. 在 Safari 中打开视频页面（如 YouTube）
2. 点击 **分享按钮**（底部中间）
3. 向下滚动，找到 **Bosco 下载**
4. 点击后自动开始下载
5. 收到通知：下载完成

### 场景 2：从其他 App 下载

1. 在任何 App 中复制链接
2. 或点击分享按钮
3. 选择 **Bosco 下载**
4. 输入 API Key（首次）
5. 完成！

### 场景 3：从剪贴板下载

1. 复制视频链接
2. 打开 **快捷指令** App
3. 运行 **Bosco 下载**
4. 自动读取剪贴板链接

---

## ⚙️ 高级配置

### 修改默认画质

1. 打开 **快捷指令** App
2. 长按 **Bosco 下载** → **编辑**
3. 找到请求体中的 `quality` 字段
4. 修改为以下值之一：
   - `best` - 最佳画质（默认）
   - `1080p` - 1080p
   - `720p` - 720p
   - `audio` - 仅音频
   - `mp3` - MP3 格式
   - `m4a` - M4A 格式

### 修改服务器地址

1. 编辑快捷指令
2. 修改 `ServerURL` 变量
3. 格式：`http://your-server:8080` 或 `https://your-domain.com`

### 保存 API Key（免输入）

1. 编辑快捷指令
2. 将"显示提示"操作改为"设定变量"
3. 直接填入 API Key
4. ⚠️ 注意：这会明文保存在快捷指令中

---

## 🔧 故障排除

### 问题 1：找不到"Bosco 下载"选项

**解决方案：**
1. 打开快捷指令 App
2. 长按 Bosco 下载
3. 确保已开启 **在共享表中显示**
4. 重启 Safari

### 问题 2：提示"无效的 API Key"

**解决方案：**
1. 检查 API Key 是否正确
2. 重新生成 API Key
3. 确保 API Key 未过期

### 问题 3：下载失败

**解决方案：**
1. 检查网络连接
2. 确认服务器正在运行
3. 查看服务器日志：
   ```bash
   docker logs bosco-tsang | grep "快捷指令"
   ```

### 问题 4：不支持的平台

**解决方案：**
1. 检查平台是否在支持列表中
2. 更新 yt-dlp：
   ```bash
   docker exec bosco-tsang pip install --upgrade yt-dlp
   ```

---

## 📊 API 接口文档

### 快捷指令专用接口

**端点：** `POST /api/shortcuts/download`

**请求头：**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**请求体：**
```json
{
  "url": "https://www.youtube.com/watch?v=xxx",
  "quality": "best"
}
```

**响应：**
```json
{
  "success": true,
  "task_id": "uuid-here",
  "platform": "youtube",
  "message": "已添加到下载队列: youtube",
  "progress_url": "/api/progress/uuid-here"
}
```

**错误响应：**
```json
{
  "success": false,
  "detail": "无效的 API Key"
}
```

---

## 🎨 快捷指令截图

### 分享菜单
```
[分享按钮]
  ↓
[Bosco 下载] ← 在这里
  ↓
[快捷指令图标]
```

### 通知示例
```
✅ 下载任务已创建
已添加到下载队列: youtube
任务 ID: abc-123-def
```

---

## 💡 使用技巧

### 技巧 1：批量下载

1. 复制链接列表到备忘录
2. 创建快捷指令循环
3. 逐个发送到 Bosco

### 技巧 2：自动下载到 NAS

1. 配置下载目录为 NAS 挂载点
2. 快捷指令只负责发起任务
3. 文件自动保存到 NAS

### 技巧 3：配合自动化

使用 iOS 自动化：
- 当复制到剪贴板的是视频链接 → 自动运行 Bosco 下载
- 当连接到家中的 Wi-Fi → 自动检查下载队列

---

## 🔐 安全建议

1. **不要公开分享 API Key**
2. **定期更换 API Key**
3. **使用 HTTPS**（生产环境）
4. **限制 API Key 权限**（仅下载）
5. **监控异常使用**

---

## 📞 技术支持

如遇到问题：

1. 查看服务器日志
2. 检查 API Key 是否有效
3. 确认网络连接正常
4. 联系管理员

---

## 🚀 下一步

- [ ] 支持进度实时推送
- [ ] 支持下载完成通知
- [ ] 支持多服务器配置
- [ ] 支持画质选择菜单
- [ ] 支持批量下载

---

**快捷指令已就绪！** 🎉

现在您可以在 iPhone 上随时随地下载视频了！
