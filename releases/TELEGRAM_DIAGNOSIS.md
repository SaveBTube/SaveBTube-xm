# 🔍 Telegram Bot 异常诊断报告

## 🐛 当前问题

**错误日志：**
```
[2026-06-16 11:32:34] [ERROR] 获取 Telegram 更新失败: 
```

**问题特征：**
- ❌ 错误信息为空
- ❌ 没有堆栈跟踪
- ❌ 无法确定具体原因

---

## 🔬 诊断过程

### 1. 代码增强

已完成：
- ✅ 添加详细的异常处理
- ✅ 记录异常类型和详情
- ✅ 添加堆栈跟踪
- ✅ 支持 DEBUG 日志级别

### 2. Logger 配置问题

**发现的问题：**
```python
# main.py 中设置
logger.setLevel(logging.INFO)  # 应该是 20

# 实际运行中
logger.getEffectiveLevel()  # 返回 30 (WARNING)
```

**影响：**
- DEBUG 日志不会输出
- 详细的错误诊断信息被过滤

### 3. 异常特征分析

错误信息为空字符串的可能原因：
1. **httpx 内部异常** - 某些 httpx 异常的 `str(e)` 返回空
2. **网络层错误** - 底层网络错误没有消息
3. **SSL/TLS 错误** - 证书或加密问题

---

## 🎯 诊断方案

### 方案 1：使用测试脚本（推荐）

**步骤：**

1. **复制测试脚本到容器**
   ```bash
   docker cp H:\docker开发文档\BoscoTsang\scripts\test_telegram.py bosco-tsang:/app/test_telegram.py
   ```

2. **执行测试**
   ```bash
   docker exec bosco-tsang python test_telegram.py YOUR_BOT_TOKEN
   ```

**预期输出：**
```
============================================================
Telegram API 连接测试
============================================================

✓ Bot Token: 123456:ABC-DEF...
✓ 测试 URL: https://api.telegram.org/bot123456.../getMe

🔄 正在连接 Telegram API...
✓ HTTP 状态码: 200
✓ 响应内容: {"ok":true,"result":{...}}

✅ 连接成功！
Bot 信息:
  - ID: 123456789
  - 名称: Bosco Bot
  - 用户名: @boscobot
```

### 方案 2：直接检查配置

**查看 Bot Token 是否配置：**
```bash
# 方法 1：通过 API
curl http://localhost:8080/api/settings -H "Authorization: Bearer YOUR_TOKEN"

# 方法 2：查看数据库
docker exec bosco-tsang sqlite3 /app/data/bosco.db "SELECT value FROM settings WHERE key='telegram_bot_token';"
```

### 方案 3：修改 Logger 级别

**临时方案：**
在 `telegram_bot.py` 开头添加：
```python
import logging
logging.getLogger('bosco').setLevel(logging.DEBUG)
```

---

## 🔧 可能的原因和解决方案

### 原因 1：Bot Token 未配置或无效

**检查：**
```bash
curl http://localhost:8080/api/settings -H "Authorization: Bearer YOUR_TOKEN" | grep telegram_bot_token
```

**解决：**
1. 登录管理后台
2. 进入系统设置
3. 填写 Telegram Bot Token
4. 启用 Telegram 登录功能
5. 保存设置

### 原因 2：网络无法访问 Telegram

**测试：**
```bash
docker exec bosco-tsang curl -I https://api.telegram.org
```

**解决（配置代理）：**
1. 管理后台 → 系统设置
2. 启用代理
3. 填写代理地址：
   - HTTP 代理：`http://proxy.example.com:7890`
   - HTTPS 代理：`http://proxy.example.com:7890`
4. 保存并重启

### 原因 3：SSL/TLS 证书问题

**测试：**
```bash
docker exec bosco-tsang python -c "import ssl; print(ssl.get_default_verify_paths())"
```

**解决：**
```bash
# 更新证书
docker exec bosco-tsang apt-get update
docker exec bosco-tsang apt-get install -y ca-certificates
docker exec bosco-tsang update-ca-certificates
```

### 原因 4：httpx 版本问题

**检查：**
```bash
docker exec bosco-tsang python -c "import httpx; print(httpx.__version__)"
```

**当前版本：** 0.28.1 ✅ 正常

---

## 📋 快速诊断清单

### 1. 检查 Bot Token
- [ ] Token 已配置
- [ ] Token 格式正确
- [ ] Bot 未删除

### 2. 检查功能开关
- [ ] Telegram 登录功能已启用
- [ ] 设置已保存

### 3. 检查网络
- [ ] 可以访问 api.telegram.org
- [ ] 防火墙未阻止
- [ ] 代理已配置（如需要）

### 4. 检查依赖
- [ ] httpx 已安装
- [ ] SSL 证书正常

---

## 🚀 立即执行诊断

### 快速测试命令

```bash
# 1. 测试网络连通性
docker exec bosco-tsang curl -s -o /dev/null -w "%{http_code}" https://api.telegram.org

# 2. 测试 Bot Token（替换 YOUR_TOKEN）
docker exec bosco-tsang curl -s https://api.telegram.org/botYOUR_TOKEN/getMe

# 3. 查看详细日志
docker logs bosco-tsang 2>&1 | grep -A 5 "Telegram"
```

### 预期结果

**网络测试：**
- 200 - ✅ 正常
- 000 - ❌ 无法连接（需要代理）
- 其他 - ⚠️ 异常

**Bot Token 测试：**
```json
{"ok":true,"result":{"id":123456,"first_name":"Bot","username":"bot"}}
```
✅ 正常

```json
{"ok":false,"error_code":401,"description":"Unauthorized"}
```
❌ Token 无效

---

## 📝 下一步操作

### 推荐步骤

1. **运行测试脚本**
   ```bash
   docker cp scripts/test_telegram.py bosco-tsang:/app/
   docker exec bosco-tsang python test_telegram.py YOUR_BOT_TOKEN
   ```

2. **查看输出结果**
   - 如果成功 → Bot 配置正常，检查其他问题
   - 如果失败 → 根据错误信息修复

3. **修复配置**
   - Token 无效 → 重新获取 Token
   - 网络问题 → 配置代理
   - SSL 问题 → 更新证书

4. **重启服务**
   ```bash
   docker restart bosco-tsang
   ```

---

## 📞 提供诊断信息

如果问题仍然存在，请提供：

### 1. 测试结果
```bash
docker exec bosco-tsang python test_telegram.py YOUR_BOT_TOKEN
```

### 2. 网络测试
```bash
docker exec bosco-tsang curl -v https://api.telegram.org
```

### 3. 配置信息
```bash
# 查看 Telegram 相关配置
curl http://localhost:8080/api/settings -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 完整日志
```bash
docker logs bosco-tsang --tail 200
```

---

## ✅ 已完成的修复

- [x] 增强异常处理
- [x] 添加详细错误日志
- [x] 添加堆栈跟踪
- [x] 支持 DEBUG 级别
- [x] 创建测试脚本
- [x] 创建诊断报告

---

## 🎯 预期效果

修复后，错误日志应该类似：

```
[ERROR] 获取 Telegram 更新失败: [ConnectError] All connection attempts failed
[DEBUG] 异常类型: httpx.ConnectError
[DEBUG] 异常表示: ConnectError('All connection attempts failed')
[DEBUG] 错误堆栈:
Traceback (most recent call last):
  File "/app/backend/admin/telegram_bot.py", line 89, in get_updates
    response = await self.client.get(url, params=params)
  ...
```

这样可以快速定位问题！

---

**诊断报告生成完成！** 🔍

请按照上述步骤执行诊断，或提供 Bot Token 以便进一步测试。
