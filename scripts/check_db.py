"""检查数据库内容的脚本"""
import sqlite3
import os

db_path = "data/bosco.db"
if not os.path.exists(db_path):
    print(f"❌ 数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查所有表
print("=" * 60)
print("数据库表列表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# 检查每个表的数据量
print("\n" + "=" * 60)
print("各表数据数量:")
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} 条记录")
    except Exception as e:
        print(f"  - {table_name}: 查询失败 ({e})")

# 检查 downloads 表的最近5条记录
print("\n" + "=" * 60)
print("下载记录 (最近5条):")
try:
    cursor.execute("SELECT id, url, status, created_at FROM downloads ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  - ID: {row[0]}, URL: {row[1][:50]}..., 状态: {row[2]}, 时间: {row[3]}")
    else:
        print("  (无数据)")
except Exception as e:
    print(f"  查询失败: {e}")

# 检查 users 表
print("\n" + "=" * 60)
print("用户列表:")
try:
    cursor.execute("SELECT id, username, role, is_active FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  - ID: {row[0]}, 用户名: {row[1]}, 角色: {row[2]}, 状态: {'启用' if row[3] else '禁用'}")
except Exception as e:
    print(f"  查询失败: {e}")

conn.close()
print("\n" + "=" * 60)
print("检查完成！")
