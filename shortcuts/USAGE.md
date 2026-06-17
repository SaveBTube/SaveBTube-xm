# 📱 iOS 快捷指令 - 下载使用指南

## ✅ 问题已修复

**修复时间：** 2026-06-16  
**状态：** ✅ 完全可用

### 修复内容

1. ✅ **快捷指令做成成品** - 用户点击下载即可直接使用
2. ✅ **文档可以查看** - 所有文档通过 Web 直接访问，无需进入 root
3. ✅ **添加 docs 目录到 Docker** - 确保所有文档都可访问

---

## 🚀 3 步完成安装

### 步骤 1：下载快捷指令

**访问下载页面：**
```
http://your-server:8080/shortcuts/download
```

**点击下载按钮：**
- 点击 "📲 下载快捷指令" 按钮
- 文件会自动下载到您的 iPhone

---

### 步骤 2：安装快捷指令

**在 iPhone 上操作：**

1. 点击下载的文件 `Bosco_Download.shortcut`
2. 在弹出窗口中点击 **"打开"**
3. 快捷指令 App 会自动打开
4. 点击 **"添加快捷指令"**
5. 安装完成！

---

### 步骤 3：配置快捷指令

**编辑快捷指令：**

1. 打开 **快捷指令** App
2. 找到 **"Bosco 下载"** 快捷指令
3. 长按或点击右上角 **"..."** 编辑
4. 找到 **"设定服务器地址"** 步骤
5. 修改为您的服务器地址：
   ```
   http://your-server:8080
   ```
   （例如：`http://192.168.1.100:8080`）

6. 找到 **"输入 API Key"** 步骤
7. 修改为您的 API Key（在管理后台获取）
8. 点击 **"完成"** 保存

---

## 📖 使用流程

```
1. 在任何 App 中复制视频链接
        ↓
2. 点击分享按钮
        ↓
3. 向下滚动，选择 "Bosco 下载"
        ↓
4. 自动开始下载
        ↓
5. 收到完成通知
```

---

## 🎯 功能特性

| 特性 | 状态 |
|------|------|
| 成品文件下载 | ✅ |
| 一键下载 | ✅ |
| 分享菜单集成 | ✅ |
| 3000+ 平台支持 | ✅ |
| 实时通知 | ✅ |
| Web 文档查看 | ✅ |

---

## 🌐 访问地址

### 快捷指令相关

| 功能 | URL | 说明 |
|------|-----|------|
| 下载页面 | http://localhost:8080/shortcuts/download | 下载快捷指令文件 |
| 快捷指令文件 | http://localhost:8080/api/shortcuts/download-file | 直接下载 .shortcut 文件 |
| 使用指南 | http://localhost:8080/docs/IOS_SHORTCUTS_GUIDE.html | 完整使用说明 |

### 其他文档

| 功能 | URL |
|------|-----|
| 使用说明书 | http://localhost:8080/docs/USAGE_MANUAL.html |
| 更新日志 | http://localhost:8080/docs/CHANGELOG.html |
| 快速参考 | http://localhost:8080/docs/QUICK_REFERENCE.html |
| API 文档 | http://localhost:8080/docs |

---

## 📋 获取 API Key

### 方法 1：Web 界面

1. 登录管理后台：`http://your-server:8080`
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
2. 找到 "设定服务器地址" 步骤
3. 修改为新的地址
4. 点击 "完成" 保存

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
3. 重新编辑快捷指令

### 问题 3：下载失败

**解决方案：**
1. 检查网络连接
2. 确认服务器正在运行
3. 检查服务器地址是否正确
4. 查看服务器日志：
   ```bash
   docker logs bosco-tsang | grep "快捷指令"
   ```

### 问题 4：文档无法查看

**现在已修复！** 所有文档都可以通过 Web 直接访问：
- ✅ 不需要进入 root
- ✅ 不需要访问文件系统
- ✅ 直接在浏览器中查看

---

## 📊 测试验证

### 验证下载页面

```bash
curl http://localhost:8080/shortcuts/download
# 应该返回 HTML 下载页面
```

### 验证文件下载

```bash
curl http://localhost:8080/api/shortcuts/download-file -o test.shortcut
# 应该成功下载 .shortcut 文件
```

### 验证文档访问

```bash
curl http://localhost:8080/docs/IOS_SHORTCUTS_GUIDE.html
# 应该返回 HTML 格式的文档
```

---

## 📝 更新日志

### v0.4.2 - 2026-06-16

**修复：**
- ✅ 快捷指令做成成品文件
- ✅ 用户下载即可直接使用
- ✅ 文档通过 Web 直接访问
- ✅ 添加 docs 目录到 Docker 容器
- ✅ 添加快捷指令下载页面

**新增：**
- ✅ `/shortcuts/download` 下载页面
- ✅ `/api/shortcuts/download-file` 文件下载
- ✅ 文档路由支持
- ✅ 完整的下载使用说明

---

## 🎉 完成

**快捷指令现在完全可用！**

用户可以：
1. ✅ 访问下载页面
2. ✅ 点击按钮下载成品文件
3. ✅ 直接安装到 iPhone
4. ✅ 编辑配置服务器地址和 API Key
5. ✅ 立即使用

**所有文档都可以在 Web 上查看，无需进入 root！**

---

**下载页面：** `http://your-server:8080/shortcuts/download`  
**使用指南：** `http://your-server:8080/docs/IOS_SHORTCUTS_GUIDE.html`
