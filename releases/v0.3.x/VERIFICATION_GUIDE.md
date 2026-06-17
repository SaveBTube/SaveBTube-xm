# ✅ 修复验证指南

## 🎉 部署状态

**服务状态：** ✅ 运行中（Healthy）  
**端口映射：** 8080 -> 8000  
**构建时间：** 2026-06-16 13:00  
**镜像 ID：** b93daf31f121

---

## 📋 验证清单

请按以下步骤验证三个问题的修复：

### ✅ 1. 验证帮助和更新按钮

**测试步骤：**

1. 打开浏览器访问：`http://localhost:8080`
2. 登录系统（admin / admin123）
3. 查看页头右上角

**预期结果：**

- ✅ 看到 "📖 帮助" 按钮
- ✅ 看到 "📝 更新" 按钮
- ✅ 点击 "📖 帮助" 弹出使用说明书模态框
- ✅ 点击 "📝 更新" 弹出更新日志模态框
- ✅ 模态框内容正常显示（Markdown 已转换为 HTML）
- ✅ 点击模态框外部或 ✕ 按钮可关闭

**截图位置：**
- 帮助按钮：页头右上角，语言切换左侧
- 更新按钮：帮助按钮左侧

**如果失败：**
```bash
# 检查日志
docker logs bosco-tsang | grep "docs"

# 检查文档是否存在
docker exec bosco-tsang ls -la /app/USAGE_MANUAL.md
docker exec bosco-tsang ls -la /app/CHANGELOG.md

# 测试 API
curl http://localhost:8080/docs/USAGE_MANUAL.html
```

---

### ✅ 2. 验证代理开关保存

**测试步骤：**

1. 进入 **设置** → **代理与网络**
2. 查看当前代理状态
3. 点击代理开关（如果开启则关闭，如果关闭则开启）
4. 等待提示 "✅ 代理配置已保存"
5. **刷新页面**（F5 或 Ctrl+R）
6. 再次进入设置页面

**预期结果：**

- ✅ 点击开关后立即显示保存提示
- ✅ 刷新页面后代理状态保持不变
- ✅ 开关状态与数据库同步

**如果失败：**
```bash
# 检查数据库中的代理设置
docker exec bosco-tsang python -c "
from backend.admin.db import get_setting
print('proxy_enabled:', get_setting('proxy_enabled', '0'))
print('http_proxy:', get_setting('http_proxy', ''))
print('https_proxy:', get_setting('https_proxy', ''))
"

# 检查浏览器控制台错误
# F12 → Console → 查看是否有 API 错误
```

---

### ✅ 3. 验证国内平台下载（关闭代理后）

**测试步骤：**

1. 进入 **设置** → **代理与网络**
2. **关闭代理**（确保开关为关闭状态）
3. 保存设置（如果未自动保存）
4. 进入 **下载** 页面
5. 粘贴 Bilibili 视频链接，例如：
   ```
   https://www.bilibili.com/video/BV1GJ411x7h7
   ```
6. 选择画质（如 1080p）
7. 点击 **开始下载**
8. 观察下载进度

**预期结果：**

- ✅ 下载任务成功创建
- ✅ 下载进度正常显示
- ✅ 下载成功完成
- ✅ 日志中显示未使用代理

**验证日志：**
```bash
# 查看下载日志
docker logs bosco-tsang | grep -A 5 "bilibili"

# 应该看到类似输出：
# [INFO] 用户 admin 发起下载: https://www.bilibili.com/video/...
# REQUEST POST /api/download
# RESPONSE POST /api/download -> 200
```

**如果失败：**
```bash
# 检查代理设置
docker exec bosco-tsang python -c "
from backend.admin.db import get_setting
print('代理启用:', get_setting('proxy_enabled', '0'))
"

# 手动测试下载
docker exec bosco-tsang python -c "
from backend.main import run_download
import uuid
task_id = str(uuid.uuid4())
# 这将测试 Bilibili 下载
"

# 查看完整日志
docker logs bosco-tsang --tail 100
```

---

## 🔍 高级验证

### 验证文档 API

```bash
# 测试使用说明书 API
curl http://localhost:8080/docs/USAGE_MANUAL.html | head -20

# 测试更新日志 API
curl http://localhost:8080/docs/CHANGELOG.html | head -20

# 应该返回 HTML 内容，包含 <html>、<head>、<body> 标签
```

### 验证代理逻辑

```bash
# 进入容器
docker exec -it bosco-tsang /bin/bash

# 测试代理关闭时的逻辑
python -c "
from backend.admin.db import get_setting, set_setting

# 关闭代理
set_setting('proxy_enabled', '0')
print('代理已关闭')

# 模拟下载逻辑
proxy_enabled = get_setting('proxy_enabled', '0') == '1'
print(f'proxy_enabled: {proxy_enabled}')

if not proxy_enabled:
    print('✅ 代理未启用，http_proxy 和 https_proxy 将为空')
else:
    print('❌ 代理仍然启用')
"

# 测试代理开启时的逻辑
python -c "
from backend.admin.db import get_setting, set_setting

# 开启代理（测试用）
set_setting('proxy_enabled', '1')
set_setting('http_proxy', 'http://127.0.0.1:7890')
set_setting('https_proxy', 'http://127.0.0.1:7890')

proxy_enabled = get_setting('proxy_enabled', '0') == '1'
http_proxy = get_setting('http_proxy', '')
https_proxy = get_setting('https_proxy', '')

print(f'proxy_enabled: {proxy_enabled}')
print(f'http_proxy: {http_proxy}')
print(f'https_proxy: {https_proxy}')

# 恢复关闭状态
set_setting('proxy_enabled', '0')
print('✅ 代理已恢复关闭状态')
"
```

---

## 📊 测试用例

| 测试项 | 操作 | 预期结果 | 状态 |
|--------|------|----------|------|
| 帮助按钮 | 点击 "📖 帮助" | 弹出模态框显示使用说明书 | ⏳ 待测试 |
| 更新按钮 | 点击 "📝 更新" | 弹出模态框显示更新日志 | ⏳ 待测试 |
| 模态框关闭 | 点击外部或 ✕ | 模态框关闭 | ⏳ 待测试 |
| 代理开关 | 点击开关 | 状态切换并保存 | ⏳ 待测试 |
| 代理持久化 | 刷新页面 | 代理状态保持不变 | ⏳ 待测试 |
| B站下载（无代理） | 下载 Bilibili 视频 | 下载成功 | ⏳ 待测试 |
| B站下载（有代理） | 开启代理后下载 | 使用代理下载 | ⏳ 待测试 |

---

## 🐛 故障排查

### 问题：模态框无法显示内容

**可能原因：**
1. markdown 库未安装
2. 文档文件不存在
3. API 路由未正确配置

**解决方案：**
```bash
# 检查 markdown 库
docker exec bosco-tsang python -c "import markdown; print(markdown.__version__)"

# 检查文档文件
docker exec bosco-tsang ls -la /app/*.md

# 检查 API 路由
docker logs bosco-tsang | grep "docs"
```

### 问题：代理开关仍然无法保存

**可能原因：**
1. 前端代码未更新
2. API 调用失败
3. 数据库连接问题

**解决方案：**
```bash
# 强制重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 检查前端代码
docker exec bosco-tsang cat /app/static/assets/*.js | grep -o "toggleProxy" | head -1

# 检查数据库
docker exec bosco-tsang python -c "
import sqlite3
conn = sqlite3.connect('/app/data/bosco.db')
cursor = conn.cursor()
cursor.execute(\"SELECT key, value FROM settings WHERE key='proxy_enabled'\")
print(cursor.fetchall())
conn.close()
"
```

### 问题：B站下载仍然失败

**可能原因：**
1. 代理未完全关闭
2. 环境变量中有代理设置
3. B站需要 Cookies

**解决方案：**
```bash
# 确认代理关闭
docker exec bosco-tsang python -c "
from backend.admin.db import get_setting
print('代理启用:', get_setting('proxy_enabled', '0'))
print('HTTP代理:', get_setting('http_proxy', ''))
print('HTTPS代理:', get_setting('https_proxy', ''))
"

# 检查环境变量
docker exec bosco-tsang env | grep -i proxy

# 尝试添加 B站 Cookies
# 导出 cookies.txt 并放入 ./cookies/bilibili.txt
```

---

## 📝 完成标记

测试完成后，请在对应位置打勾：

- [ ] 帮助按钮正常工作
- [ ] 更新按钮正常工作
- [ ] 代理开关可以保存
- [ ] 刷新页面代理状态保持
- [ ] 关闭代理后 B站可以下载
- [ ] 所有功能验证通过

---

## 🎯 下一步

验证通过后：

1. **更新版本号**（可选）
   ```bash
   .\scripts\update-version.ps1  # Windows
   ```

2. **提交代码**
   ```bash
   git add .
   git commit -m "fix: 修复文档访问、代理保存和国内平台下载问题"
   ```

3. **推送 Docker 镜像**（可选）
   ```bash
   docker push boscotom/bosco-tsang:latest
   ```

---

**验证时间：** 2026-06-16  
**版本：** v0.3.1  
**服务地址：** http://localhost:8080
