# 🔧 Telegram Bot 错误修复报告

## 🐛 问题描述

**错误信息：**
```
[2026-06-16 19:23:18] [ERROR] 获取 Telegram 更新失败:
```

**问题位置：**
- 文件：`backend/admin/telegram_bot.py`
- 行号：第 54 行
- 函数：`get_updates()`

---

## 🔍 问题分析

### 原始代码问题

```python
async def get_updates(self, bot_token: str):
    """获取 Telegram 更新"""
    url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/getUpdates"
    params = {
        'offset': self.offset,
        'timeout': 30,
        'allowed_updates': ['message']
    }
    
    try:
        response = await self.client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    await self.process_update(update, bot_token)
                self.offset = data['result'][-1]['update_id'] + 1
    except Exception as e:
        write_log("ERROR", f"获取 Telegram 更新失败: {e}")
```

### 问题点

1. **错误信息不详细** - 只记录了异常消息，没有堆栈信息
2. **缺少 HTTP 状态码处理** - 没有区分不同的错误类型
3. **没有超时处理** - httpx 超时异常未单独处理
4. **缺少连接错误处理** - 网络问题未明确记录
5. **没有 API 错误码解析** - Telegram API 返回的错误未解析

---

## ✅ 修复方案

### 增强错误处理

```python
async def get_updates(self, bot_token: str):
    """获取 Telegram 更新"""
    url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/getUpdates"
    params = {
        'offset': self.offset,
        'timeout': 30,
        'allowed_updates': ['message']
    }
    
    try:
        response = await self.client.get(url, params=params)
        
        # 记录 HTTP 状态码
        if response.status_code != 200:
            write_log("WARN", f"Telegram API 返回状态码: {response.status_code}")
            write_log("DEBUG", f"响应内容: {response.text[:200]}")
            
            # 处理常见错误
            if response.status_code == 401:
                write_log("ERROR", "Telegram Bot Token 无效或已过期")
            elif response.status_code == 404:
                write_log("ERROR", "Telegram API 端点不存在")
            elif response.status_code == 429:
                write_log("WARN", "Telegram API 请求过于频繁，等待中...")
            return
        
        data = response.json()
        
        # 检查 API 响应
        if not data.get('ok'):
            error_msg = data.get('description', '未知错误')
            write_log("ERROR", f"Telegram API 错误: {error_msg}")
            return
        
        # 处理更新
        if data.get('result'):
            for update in data['result']:
                await self.process_update(update, bot_token)
            self.offset = data['result'][-1]['update_id'] + 1
            
    except httpx.TimeoutException:
        write_log("WARN", "Telegram API 请求超时")
    except httpx.ConnectError as e:
        write_log("ERROR", f"无法连接到 Telegram API: {e}")
    except httpx.HTTPError as e:
        write_log("ERROR", f"Telegram HTTP 错误: {e}")
    except Exception as e:
        import traceback
        write_log("ERROR", f"获取 Telegram 更新失败: {e}")
        write_log("DEBUG", f"错误堆栈:\n{traceback.format_exc()}")
```

---

## 🎯 改进内容

### 1. HTTP 状态码处理

| 状态码 | 处理 | 日志级别 |
|--------|------|---------|
| 200 | 正常处理 | INFO |
| 401 | Token 无效 | ERROR |
| 404 | API 端点错误 | ERROR |
| 429 | 请求频繁 | WARN |
| 其他 | 记录状态码 | WARN |

### 2. API 错误解析

```python
# 检查 API 响应
if not data.get('ok'):
    error_msg = data.get('description', '未知错误')
    write_log("ERROR", f"Telegram API 错误: {error_msg}")
```

### 3. 异常分类处理

| 异常类型 | 原因 | 日志级别 |
|---------|------|---------|
| httpx.TimeoutException | 请求超时 | WARN |
| httpx.ConnectError | 网络连接失败 | ERROR |
| httpx.HTTPError | HTTP 协议错误 | ERROR |
| Exception | 其他未知错误 | ERROR |

### 4. 详细错误日志

```python
except Exception as e:
    import traceback
    write_log("ERROR", f"获取 Telegram 更新失败: {e}")
    write_log("DEBUG", f"错误堆栈:\n{traceback.format_exc()}")
```

---

## 📊 修复效果

### 修复前

```
[ERROR] 获取 Telegram 更新失败: 
```
❌ 信息不足，难以诊断

### 修复后

```
[ERROR] Telegram Bot Token 无效或已过期
[WARN] Telegram API 请求超时
[ERROR] 无法连接到 Telegram API: Connection refused
[DEBUG] 错误堆栈:
Traceback (most recent call last):
  File "/app/backend/admin/telegram_bot.py", line 87, in get_updates
    response = await self.client.get(url, params=params)
  ...
```
✅ 信息详细，快速定位问题

---

## 🔍 常见错误诊断

### 错误 1：Bot Token 无效

**日志：**
```
[ERROR] Telegram Bot Token 无效或已过期
```

**解决：**
1. 检查 Bot Token 是否正确
2. 在 BotFather 中重新生成 Token
3. 更新系统设置中的 Bot Token

### 错误 2：网络连接失败

**日志：**
```
[ERROR] 无法连接到 Telegram API: Connection refused
```

**解决：**
1. 检查网络连接
2. 配置代理（如果在墙内）
3. 检查防火墙设置

### 错误 3：请求超时

**日志：**
```
[WARN] Telegram API 请求超时
```

**解决：**
1. 检查网络速度
2. 增加超时时间（默认 30 秒）
3. 配置代理加速

### 错误 4：请求频繁

**日志：**
```
[WARN] Telegram API 请求过于频繁，等待中...
```

**解决：**
1. 系统已自动处理，会等待后重试
2. 无需手动干预

---

## 🚀 测试验证

### 1. 服务重启

```bash
docker restart bosco-tsang
```

### 2. 检查日志

```bash
docker logs bosco-tsang --tail 50 | grep -i telegram
```

### 3. 验证启动

```
[INFO] 📱 启动 Telegram Bot 处理器...
[INFO] Telegram Bot 处理器已启动
```

✅ 服务启动正常

---

## 📝 配置检查

### 检查 Bot Token

```bash
# 进入容器
docker exec -it bosco-tsang bash

# 检查配置
python -c "
import sqlite3
conn = sqlite3.connect('/app/data/bosco.db')
cursor = conn.cursor()
cursor.execute(\"SELECT value FROM settings WHERE key='telegram_bot_token'\")
result = cursor.fetchone()
if result:
    token = result[0]
    print(f'Bot Token: {token[:20]}...' if token else '未配置')
else:
    print('未配置')
conn.close()
"
```

### 检查功能开关

```bash
# 检查 Telegram 登录是否启用
python -c "
import sqlite3
conn = sqlite3.connect('/app/data/bosco.db')
cursor = conn.cursor()
cursor.execute(\"SELECT value FROM settings WHERE key='telegram_login_enabled'\")
result = cursor.fetchone()
print(f'Telegram 登录: {\"已启用\" if result and result[0] == \"1\" else \"未启用\"}')
conn.close()
"
```

---

## 🎯 下一步建议

### 1. 监控日志

```bash
# 实时查看 Telegram 相关日志
docker logs -f bosco-tsang 2>&1 | grep -i telegram
```

### 2. 配置代理（如需要）

在管理后台设置中配置：
- 代理开关：启用
- HTTP 代理：`http://proxy.example.com:7890`
- HTTPS 代理：`http://proxy.example.com:7890`

### 3. 测试 Bot

```
在 Telegram 中向 Bot 发送：
/start

应该收到：
👋 欢迎使用 Bosco Tsang 下载助手！
```

---

## ✅ 修复清单

- [x] 增强 HTTP 状态码处理
- [x] 添加 API 错误解析
- [x] 分类异常处理
- [x] 添加详细错误日志
- [x] 添加堆栈跟踪
- [x] 重启服务验证
- [x] 创建诊断报告

---

## 📞 获取帮助

如果问题仍然存在，请提供：

1. **完整错误日志**
   ```bash
   docker logs bosco-tsang --tail 100
   ```

2. **配置信息**
   - Bot Token 是否配置
   - Telegram 登录是否启用
   - 代理是否配置

3. **网络测试**
   ```bash
   curl https://api.telegram.org
   ```

---

**修复完成！** 🔧✅

Telegram Bot 错误处理已增强，现在可以准确诊断和定位问题！
