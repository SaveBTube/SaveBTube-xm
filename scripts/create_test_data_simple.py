"""创建测试数据（简单版本，无 emoji）"""
import sqlite3
import os
from datetime import datetime
import random

db_path = "data/bosco.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查是否已有数据
cursor.execute("SELECT COUNT(*) FROM download_tasks")
if cursor.fetchone()[0] > 0:
    print("[!] 数据库中已有数据，跳过测试数据创建")
    conn.close()
    exit(0)

print("[*] 创建测试数据...")

# 获取 admin 用户 ID
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
user_row = cursor.fetchone()
if not user_row:
    print("[X] 未找到 admin 用户")
    conn.close()
    exit(1)
user_id = user_row[0]

# 创建测试下载任务
test_tasks = [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Rick Astley - Never Gonna Give You Up", "youtube", "video", "1080p", 1024*1024*50),
    ("https://www.bilibili.com/video/BV1xx411c7mD", "测试视频标题", "bilibili", "video", "720p", 1024*1024*30),
    ("https://music.163.com/song?id=123456", "测试音乐", "netease", "audio", "320kbps", 1024*1024*10),
]

for i, (url, title, platform, res_type, resolution, file_size) in enumerate(test_tasks):
    task_id = f"test_task_{i+1}"
    status = random.choice(["completed", "pending", "downloading"])
    progress = 100.0 if status == "completed" else random.uniform(0, 80)
    
    cursor.execute("""
        INSERT INTO download_tasks 
        (task_id, url, title, platform, resource_type, resolution, file_size, status, progress, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_id, url, title, platform, res_type, resolution, file_size, status, progress, user_id, datetime.now()))
    
    # 同时创建下载历史
    cursor.execute("""
        INSERT INTO download_history
        (task_id, url, title, platform, resource_type, resolution, file_size, status, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_id, url, title, platform, res_type, resolution, file_size, status, user_id, datetime.now()))

# 创建测试订阅
test_subscriptions = [
    ("UC_x5XG1OV2P6uZZ5FSM9Ttw", "Google Developers", "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw", "youtube", 3600),
    ("BV1234567890", "测试B站UP主", "https://space.bilibili.com/123456", "bilibili", 7200),
]

for i, (channel_id, channel_name, channel_url, platform, poll_interval) in enumerate(test_subscriptions):
    sub_id = f"test_sub_{i+1}"
    cursor.execute("""
        INSERT INTO subscriptions
        (sub_id, channel_name, channel_url, platform, poll_interval, status, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
    """, (sub_id, channel_name, channel_url, platform, poll_interval, user_id, datetime.now()))

conn.commit()
conn.close()

print("[+] 测试数据创建成功！")
print(f"    - 下载任务: {len(test_tasks)} 条")
print(f"    - 下载历史: {len(test_tasks)} 条")
print(f"    - 订阅: {len(test_subscriptions)} 条")
print("")
print("[*] 现在可以刷新前端页面查看数据")
