import sqlite3

conn = sqlite3.connect('/app/data/bosco.db')
cursor = conn.cursor()

cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'telegram%' ORDER BY key")
rows = cursor.fetchall()

print("=" * 60)
print("Telegram 配置检查")
print("=" * 60)

for key, value in rows:
    if value:
        if 'token' in key.lower() or 'secret' in key.lower():
            display_value = value[:20] + '...' if len(value) > 20 else value
        else:
            display_value = value
        print(f"✓ {key}: {display_value}")
    else:
        print(f"✗ {key}: 未配置")

print("=" * 60)

conn.close()
