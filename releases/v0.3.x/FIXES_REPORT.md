# 🔧 问题修复报告

## 修复的三个问题

### ✅ 问题 1：帮助和更新按钮无法打开

**问题描述：**
- 点击页头的"📖 帮助"和"📝 更新"按钮无法打开文档
- 在极空间等 NAS 设备上无法访问 root 目录中的 Markdown 文件

**修复方案：**
1. 将外部链接改为模态框弹窗显示
2. 后端新增 `/docs/{doc_name}` API 端点
3. 使用 `markdown` 库将 Markdown 转换为 HTML
4. 通过 iframe 在模态框中展示格式化后的文档

**修改的文件：**
- `frontend/src/views/Layout.vue`
  - 将 `<a>` 标签改为 `<button>`
  - 添加 `showHelpModal` 和 `showChangelogModal` 状态
  - 添加模态框组件
  - 添加模态框样式

- `backend/main.py`
  - 新增 `serve_document()` 路由
  - 支持 Markdown 转 HTML
  - 提供完整的 HTML 页面（包含样式）

- `Dockerfile`
  - 添加 `markdown` Python 库依赖

**访问方式：**
- 点击页头 "📖 帮助" → 弹出使用说明书
- 点击页头 "📝 更新" → 弹出更新日志
- 文档在 Docker 容器内部提供，无需访问宿主机文件系统

---

### ✅ 问题 2：代理开关无法保存状态

**问题描述：**
- 点击关闭代理后，刷新页面代理仍然显示为开启状态
- `toggleProxy()` 函数只修改了前端状态，未保存到后端

**修复方案：**
修改 `toggleProxy()` 函数，使其在切换状态后立即调用 API 保存到数据库：

```javascript
async function toggleProxy() {
  settingsForm.value.proxy_enabled = !settingsForm.value.proxy_enabled
  // 立即保存代理开关状态
  try {
    await settingsApi.save({
      proxy_enabled: settingsForm.value.proxy_enabled,
      http_proxy: settingsForm.value.http_proxy,
      https_proxy: settingsForm.value.https_proxy
    })
  } catch (error) {
    // 如果保存失败，恢复原状态
    settingsForm.value.proxy_enabled = !settingsForm.value.proxy_enabled
    alert('保存失败: ' + error.message)
  }
}
```

**修改的文件：**
- `frontend/src/views/Settings.vue`
  - 将 `toggleProxy()` 改为 `async` 函数
  - 添加保存逻辑
  - 添加失败回滚机制

---

### ✅ 问题 3：断开代理后国内平台（如哔哩哔哩）无法下载

**问题描述：**
- 关闭代理后，Bilibili 等国内平台仍然尝试使用代理
- 环境变量中的代理设置可能仍然生效
- 导致下载失败或超时

**根本原因：**
原代码逻辑：
```python
proxy = (https_proxy or http_proxy) if proxy_enabled else ''
```
当 `proxy_enabled = False` 时，虽然 `proxy` 为空字符串，但如果环境变量中有代理设置，yt-dlp 可能仍会使用。

**修复方案：**

1. **重构代理逻辑** - 明确区分启用/禁用状态：
```python
# 如果代理未启用，完全清除代理设置
if not proxy_enabled:
    http_proxy = ''
    https_proxy = ''
else:
    # 代理启用时，从设置或环境变量读取
    http_proxy = get_setting('http_proxy') or ...
    https_proxy = get_setting('https_proxy') or ...
    
    # 自动模式：国内网站不使用代理
    if proxy_cfg['mode'] == 'auto':
        if is_local_address(hostname, ...):
            http_proxy = ''
            https_proxy = ''
```

2. **显式设置空代理** - 确保 yt-dlp 不使用任何代理：
```python
# 只有当代理非空时才设置
if proxy:
    ydl_opts['proxy'] = proxy
elif 'proxy' not in ydl_opts:
    # 确保未设置代理
    ydl_opts['proxy'] = ''
```

3. **Bilibili 特殊处理** - 国内平台强制禁用代理：
```python
if platform == 'bilibili':
    # ... 其他配置 ...
    # Bilibili 强制不使用代理（如果代理为空）
    if not proxy:
        ydl_opts['proxy'] = ''
```

**修改的文件：**
- `backend/main.py`
  - 重构 `run_download()` 函数中的代理逻辑（第 733-759 行）
  - 添加 Bilibili 代理强制禁用（第 838-840 行）
  - 确保空代理显式设置（第 847-850 行）

---

## 🚀 部署步骤

### 1. 重新构建 Docker 镜像

```bash
# 停止当前服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

### 2. 验证修复

#### 验证问题 1（文档访问）：
1. 访问 `http://localhost:8080`
2. 点击页头 "📖 帮助" 按钮
3. 应该弹出使用说明书模态框
4. 点击 "📝 更新" 按钮
5. 应该弹出更新日志模态框

#### 验证问题 2（代理保存）：
1. 进入 设置 → 代理与网络
2. 点击代理开关（关闭代理）
3. 刷新页面
4. 代理开关应该保持关闭状态

#### 验证问题 3（国内平台下载）：
1. 确保代理已关闭
2. 尝试下载 Bilibili 视频
3. 应该能够正常下载
4. 检查日志确认未使用代理

---

## 📊 技术细节

### 模态框实现

**前端组件结构：**
```vue
<div v-if="showHelpModal" class="modal-overlay" @click.self="showHelpModal = false">
  <div class="modal-card help-modal">
    <div class="modal-header">
      <h3>📖 使用说明书</h3>
      <button @click="showHelpModal = false">✕</button>
    </div>
    <div class="modal-body">
      <iframe src="/docs/USAGE_MANUAL.html" class="modal-iframe"></iframe>
    </div>
  </div>
</div>
```

**后端 API：**
```python
@app.get("/docs/{doc_name}")
async def serve_document(doc_name: str):
    """提供文档内容（Markdown 转 HTML）"""
    import markdown
    from fastapi.responses import HTMLResponse
    
    # 读取 Markdown 文件
    doc_path = BASE_DIR / actual_file
    with open(doc_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 转换为 HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
    
    # 返回完整的 HTML 页面
    return HTMLResponse(content=full_html)
```

### 代理逻辑优化

**优化前：**
```python
proxy_cfg = get_proxy_config(APP_CONFIG)
proxy_enabled = get_setting('proxy_enabled', '0') == '1'
if proxy_cfg['mode'] == 'none':
    proxy_enabled = False

http_proxy = get_setting('http_proxy') or proxy_cfg['http'] or os.getenv('HTTP_PROXY')
https_proxy = get_setting('https_proxy') or proxy_cfg['https'] or os.getenv('HTTPS_PROXY')
proxy = (https_proxy or http_proxy) if proxy_enabled else ''
```

**优化后：**
```python
proxy_enabled = get_setting('proxy_enabled', '0') == '1'
proxy_cfg = get_proxy_config(APP_CONFIG)

# 如果代理未启用，完全清除代理设置
if not proxy_enabled:
    http_proxy = ''
    https_proxy = ''
else:
    # 代理启用时，从设置或环境变量读取
    http_proxy = get_setting('http_proxy') or proxy_cfg['http'] or os.getenv('HTTP_PROXY') or ''
    https_proxy = get_setting('https_proxy') or proxy_cfg['https'] or os.getenv('HTTPS_PROXY') or http_proxy or ''
    
    # 自动模式：国内网站不使用代理
    if proxy_cfg['mode'] == 'auto' and (http_proxy or https_proxy):
        hostname = urllib.parse.urlparse(url).hostname or ''
        if is_local_address(hostname, proxy_cfg['bypass_cidrs']):
            http_proxy = ''
            https_proxy = ''

proxy = https_proxy or http_proxy
```

---

## 🎯 后续优化建议

1. **文档缓存** - 可以将转换后的 HTML 缓存，避免每次请求都转换
2. **代理测试** - 添加代理可用性测试功能
3. **自动检测** - 自动检测国内/国外平台，智能选择是否使用代理
4. **代理白名单** - 允许用户自定义不使用代理的域名列表

---

## 📝 相关文件清单

### 修改的文件
- ✅ `frontend/src/views/Layout.vue` - 添加模态框
- ✅ `frontend/src/views/Settings.vue` - 修复代理保存
- ✅ `backend/main.py` - 添加文档 API、修复代理逻辑
- ✅ `Dockerfile` - 添加 markdown 依赖

### 需要重新构建
- Docker 镜像需要重新构建以应用所有更改

---

**修复完成时间：** 2026-06-16  
**版本：** v0.3.1 (待发布)  
**维护团队：** Bosco Tsang 开发团队
