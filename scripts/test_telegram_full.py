#!/usr/bin/env python
"""完整的 Telegram Bot 测试"""

import sqlite3
import httpx

# 从数据库读取完整 Token
conn = sqlite3.connect('/app/data/bosco.db')
cursor = conn.cursor()
cursor.execute("SELECT value FROM settings WHERE key='telegram_bot_token'")
result = cursor.fetchone()
conn.close()

if not result or not result[0]:
    print("❌ 错误: Bot Token 未配置")
    exit(1)

BOT_TOKEN = result[0]

print("=" * 60)
print("Telegram Bot 完整测试")
print("=" * 60)
print(f"\n✓ Bot Token: {BOT_TOKEN[:20]}...({len(BOT_TOKEN)} 字符)")

# 测试 1: getMe
print("\n" + "-" * 60)
print("测试 1: 获取 Bot 信息 (getMe)")
print("-" * 60)

try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    client = httpx.Client(timeout=10.0)
    response = client.get(url)
    
    print(f"HTTP 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print("✅ 连接成功！")
            bot = data['result']
            print(f"  Bot ID: {bot['id']}")
            print(f"  名称: {bot['first_name']}")
            print(f"  用户名: @{bot.get('username', 'N/A')}")
        else:
            print(f"❌ API 错误: {data.get('description')}")
    elif response.status_code == 401:
        print("❌ Token 无效或已过期")
        print("   请检查 Bot Token 是否完整")
    else:
        print(f"⚠️  未知状态码: {response.status_code}")
        
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")

# 测试 2: getUpdates
print("\n" + "-" * 60)
print("测试 2: 获取更新 (getUpdates)")
print("-" * 60)

try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'offset': 0, 'timeout': 5}
    response = client.get(url, params=params)
    
    print(f"HTTP 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            updates = data.get('result', [])
            print(f"✅ 成功！获取到 {len(updates)} 条更新")
        else:
            print(f"❌ API 错误: {data.get('description')}")
    elif response.status_code == 401:
        print("❌ Token 无效")
    else:
        print(f"⚠️  状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
        
except httpx.TimeoutException:
    print("⚠️  请求超时（正常，可能没有新消息）")
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")

# 测试 3: 网络连通性
print("\n" + "-" * 60)
print("测试 3: 网络连通性")
print("-" * 60)

try:
    response = client.get("https://api.telegram.org", timeout=5.0)
    print(f"✅ Telegram API 可访问 (状态码: {response.status_code})")
except Exception as e:
    print(f"❌ 无法访问: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
