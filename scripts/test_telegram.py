#!/usr/bin/env python
"""Telegram Bot 连接测试脚本"""

import httpx
import sys

# 测试配置
BOT_TOKEN = "YOUR_BOT_TOKEN"  # 替换为实际的 Bot Token

def test_telegram_api():
    """测试 Telegram API 连接"""
    print("=" * 60)
    print("Telegram API 连接测试")
    print("=" * 60)
    
    # 检查 Bot Token
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("\n❌ 错误: 请先设置 BOT_TOKEN")
        print("使用方法:")
        print("  python test_telegram.py <your_bot_token>")
        sys.exit(1)
    
    print(f"\n✓ Bot Token: {BOT_TOKEN[:20]}...")
    
    # 测试 URL
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    print(f"✓ 测试 URL: {url}")
    
    # 发送请求
    print("\n🔄 正在连接 Telegram API...")
    try:
        client = httpx.Client(timeout=10.0)
        response = client.get(url)
        
        print(f"✓ HTTP 状态码: {response.status_code}")
        print(f"✓ 响应内容: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("\n✅ 连接成功！")
                print(f"Bot 信息:")
                print(f"  - ID: {data['result']['id']}")
                print(f"  - 名称: {data['result']['first_name']}")
                print(f"  - 用户名: @{data['result']['username']}")
            else:
                print(f"\n❌ API 返回错误: {data.get('description')}")
        elif response.status_code == 401:
            print("\n❌ Bot Token 无效或已过期")
        elif response.status_code == 404:
            print("\n❌ API 端点不存在")
        else:
            print(f"\n⚠️  未知状态码: {response.status_code}")
            
    except httpx.TimeoutException:
        print("\n❌ 请求超时")
        print("可能原因:")
        print("  1. 网络连接缓慢")
        print("  2. 需要配置代理")
    except httpx.ConnectError as e:
        print(f"\n❌ 连接失败: {e}")
        print("可能原因:")
        print("  1. 无法访问 Telegram API")
        print("  2. 需要配置代理")
        print("  3. 防火墙阻止")
    except Exception as e:
        print(f"\n❌ 未知错误: {type(e).__name__}")
        print(f"错误详情: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BOT_TOKEN = sys.argv[1]
    test_telegram_api()
