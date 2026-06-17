"""
数据库管理模块
支持 SQLite 数据库存储用户、历史、订阅、API密钥等数据
"""

import os
import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
from passlib.context import CryptContext

# bcrypt 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(os.getenv("APP_BASE_DIR", Path(__file__).resolve().parents[2]))
DB_PATH = BASE_DIR / "data" / "bosco.db"

def get_db_path() -> Path:
    """获取数据库路径"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表结构"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # 下载任务表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS download_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            platform TEXT,
            resource_type TEXT,
            resolution TEXT,
            file_size INTEGER,
            status TEXT DEFAULT 'pending',
            progress REAL DEFAULT 0,
            speed TEXT,
            error_message TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            finished_at TIMESTAMP,
            file_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 下载历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS download_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            platform TEXT,
            resource_type TEXT,
            resolution TEXT,
            file_size INTEGER,
            status TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 订阅表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sub_id TEXT UNIQUE NOT NULL,
            channel_name TEXT,
            channel_url TEXT,
            platform TEXT,
            poll_interval INTEGER DEFAULT 3600,
            last_check TIMESTAMP,
            status TEXT DEFAULT 'active',
            total_downloads INTEGER DEFAULT 0,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # API密钥表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_id TEXT UNIQUE NOT NULL,
            key_hash TEXT NOT NULL,
            key_prefix TEXT NOT NULL,
            note TEXT,
            status TEXT DEFAULT 'active',
            scopes TEXT DEFAULT '["read", "write"]',
            expires_at TIMESTAMP,
            rate_limit INTEGER DEFAULT 60,
            usage_count INTEGER DEFAULT 0,
            last_used TIMESTAMP,
            last_used_ip TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 邀请码表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invite_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            used_by INTEGER,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (used_by) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)
    
    # 统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            total_downloads INTEGER DEFAULT 0,
            video_count INTEGER DEFAULT 0,
            audio_count INTEGER DEFAULT 0,
            image_count INTEGER DEFAULT 0,
            total_size INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0
        )
    """)
    
    # 系统设置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Telegram 用户绑定表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE NOT NULL,
            telegram_username TEXT,
            telegram_first_name TEXT,
            telegram_last_name TEXT,
            user_id INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 创建默认管理员账户（bcrypt 哈希）
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        password_hash = pwd_context.hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", password_hash, "admin")
        )
        # 创建默认邀请码
        cursor.execute(
            "INSERT INTO invite_codes (code, created_by) VALUES (?, ?)",
            ("BOSCO2026", 1)
        )
    
    # 数据库迁移：为 api_keys 表添加新字段
    cursor.execute("PRAGMA table_info(api_keys)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'scopes' not in columns:
        cursor.execute("ALTER TABLE api_keys ADD COLUMN scopes TEXT DEFAULT '[\"read\", \"write\"]'")
    if 'expires_at' not in columns:
        cursor.execute("ALTER TABLE api_keys ADD COLUMN expires_at TIMESTAMP")
    if 'rate_limit' not in columns:
        cursor.execute("ALTER TABLE api_keys ADD COLUMN rate_limit INTEGER DEFAULT 60")
    if 'usage_count' not in columns:
        cursor.execute("ALTER TABLE api_keys ADD COLUMN usage_count INTEGER DEFAULT 0")
    if 'last_used_ip' not in columns:
        cursor.execute("ALTER TABLE api_keys ADD COLUMN last_used_ip TEXT")
    
    conn.commit()
    conn.close()

# ==================== 用户管理 ====================

def create_user(username: str, password: str, role: str = "user", is_active: int = 1, invite_code: str = None) -> bool:
    """创建新用户（bcrypt 哈希）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查邀请码
        if invite_code:
            cursor.execute("SELECT id FROM invite_codes WHERE code = ? AND used_by IS NULL", (invite_code,))
            if not cursor.fetchone():
                return False
        
        password_hash = pwd_context.hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, is_active)
        )
        user_id = cursor.lastrowid
        
        # 标记邀请码已使用
        if invite_code:
            cursor.execute(
                "UPDATE invite_codes SET used_by = ?, used_at = CURRENT_TIMESTAMP WHERE code = ?",
                (user_id, invite_code)
            )
        
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> Optional[Dict]:
    """验证用户登录（支持 bcrypt 新哈希 + SHA-256 旧哈希自动迁移）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 先取出用户记录
    cursor.execute(
        "SELECT id, username, password_hash, role, avatar FROM users WHERE username = ? AND is_active = 1",
        (username,)
    )
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return None
    
    stored_hash = user['password_hash']
    password_valid = False
    
    # 优先用 bcrypt 验证
    if stored_hash.startswith('$2'):
        password_valid = pwd_context.verify(password, stored_hash)
    else:
        # 旧 SHA-256 哈希，兼容验证
        old_hash = hashlib.sha256(password.encode()).hexdigest()
        if old_hash == stored_hash:
            password_valid = True
            # 自动迁移到 bcrypt
            new_hash = pwd_context.hash(password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user['id']))
            conn.commit()
    
    if not password_valid:
        conn.close()
        return None
    
    cursor.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
        (user['id'],)
    )
    conn.commit()
    
    conn.close()
    return {'id': user['id'], 'username': user['username'], 'role': user['role'], 'avatar': user.get('avatar')}

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """根据ID获取用户信息"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role, avatar, created_at, last_login, is_active FROM users WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users() -> List[Dict]:
    """获取所有用户列表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, role, avatar, created_at, last_login, is_active,
               (SELECT COUNT(*) FROM download_history WHERE user_id = users.id) as download_count
        FROM users ORDER BY created_at DESC
    """)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def update_user(user_id: int, role: str = None, is_active: int = None) -> bool:
    """更新用户信息"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if role is not None:
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        if is_active is not None:
            cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """删除用户"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        if cursor.rowcount == 0:
            conn.close()
            return False
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

def change_password(user_id: int, old_password: str, new_password: str) -> bool:
    """修改密码（bcrypt）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    stored_hash = row['password_hash']
    # 验证旧密码（兼容 SHA-256）
    if stored_hash.startswith('$2'):
        if not pwd_context.verify(old_password, stored_hash):
            conn.close()
            return False
    else:
        if hashlib.sha256(old_password.encode()).hexdigest() != stored_hash:
            conn.close()
            return False
    
    new_hash = pwd_context.hash(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return True

def update_avatar(user_id: int, avatar_data: str) -> bool:
    """更新用户头像"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar_data, user_id))
    conn.commit()
    conn.close()
    return True

# ==================== 下载任务管理 ====================

def create_download_task(task_id: str, url: str, user_id: int, platform: str = None, 
                        resource_type: str = "video", title: str = None) -> int:
    """创建下载任务"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO download_tasks (task_id, url, platform, resource_type, title, user_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (task_id, url, platform, resource_type, title, user_id))
    task_db_id = cursor.lastrowid
    
    # 同时创建历史记录
    cursor.execute("""
        INSERT INTO download_history (task_id, url, platform, resource_type, title, user_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (task_id, url, platform, resource_type, title, user_id))
    
    conn.commit()
    conn.close()
    return task_db_id

def get_download_task(task_id: str) -> Optional[Dict]:
    """获取单个下载任务记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM download_tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_download_task(task_id: str, **kwargs) -> bool:
    """更新下载任务"""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['status', 'progress', 'speed', 'title', 'platform', 'resource_type', 'resolution', 
                      'file_size', 'error_message', 'file_path', 'started_at', 'finished_at']
    
    updates = []
    values = []
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)
    
    if updates:
        values.append(task_id)
        cursor.execute(f"UPDATE download_tasks SET {', '.join(updates)} WHERE task_id = ?", values)
        
        # 同步更新历史表
        for key, value in kwargs.items():
            if key in ['status', 'title', 'platform', 'resource_type', 'resolution', 'file_size']:
                cursor.execute(f"UPDATE download_history SET {key} = ? WHERE task_id = ?", (value, task_id))
        
        conn.commit()
    
    conn.close()
    return True

def get_download_tasks(user_id: int = None, status: str = None, platform: str = None,
                       resource_type: str = None, search: str = None, limit: int = 100, offset: int = 0) -> List[Dict]:
    """获取下载任务列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM download_tasks WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if resource_type:
        query += " AND resource_type = ?"
        params.append(resource_type)
    if search:
        query += " AND (title LIKE ? OR url LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

def delete_download_task(task_id: str) -> bool:
    """删除下载任务记录（任务表 + 历史表）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM download_tasks WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM download_history WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()
    return True


def rename_download_task(task_id: str, title: str) -> bool:
    """重命名下载任务标题"""
    task = get_download_task(task_id)
    if not task:
        return False

    file_path = task.get('file_path')
    if file_path:
        old_path = Path(file_path)
        if old_path.exists():
            new_path = old_path.with_name(title + old_path.suffix)
            old_path.rename(new_path)
            task['file_path'] = str(new_path)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE download_tasks SET title = ?, file_path = ? WHERE task_id = ?", (title, task.get('file_path'), task_id))
    cursor.execute("UPDATE download_history SET title = ? WHERE task_id = ?", (title, task_id))
    conn.commit()
    conn.close()
    return True


def get_download_history(user_id: int = None, status: str = None, platform: str = None,
                        resource_type: str = None, search: str = None, 
                        limit: int = 100, offset: int = 0) -> List[Dict]:
    """获取下载历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM download_history WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if resource_type:
        query += " AND resource_type = ?"
        params.append(resource_type)
    if search:
        query += " AND (title LIKE ? OR url LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history

def delete_history(history_ids: List[int]) -> bool:
    """删除历史记录"""
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ','.join(['?'] * len(history_ids))
    cursor.execute(f"DELETE FROM download_history WHERE id IN ({placeholders})", history_ids)
    conn.commit()
    conn.close()
    return True

def clear_all_history(user_id: int = None) -> bool:
    """清空所有历史"""
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("DELETE FROM download_history WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("DELETE FROM download_history")
    conn.commit()
    conn.close()
    return True

# ==================== 订阅管理 ====================

def create_subscription(sub_id: str, channel_url: str, platform: str, 
                       channel_name: str = None, poll_interval: int = 3600, user_id: int = None) -> int:
    """创建订阅"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subscriptions (sub_id, channel_url, platform, channel_name, poll_interval, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sub_id, channel_url, platform, channel_name, poll_interval, user_id))
    sub_db_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sub_db_id

def get_subscriptions(user_id: int = None, platform: str = None, status: str = None) -> List[Dict]:
    """获取订阅列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM subscriptions WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    subs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return subs


def get_subscription(sub_id: str, user_id: int = None) -> Optional[Dict]:
    """根据订阅 ID 获取订阅"""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM subscriptions WHERE sub_id = ?"
    params = [sub_id]
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(user_id)
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_subscription(sub_id: str, **kwargs) -> bool:
    """更新订阅"""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['status', 'last_check', 'total_downloads', 'poll_interval']
    updates = []
    values = []
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)
    
    if updates:
        values.append(sub_id)
        cursor.execute(f"UPDATE subscriptions SET {', '.join(updates)} WHERE sub_id = ?", values)
        conn.commit()
    
    conn.close()
    return True

def delete_subscription(sub_id: str) -> bool:
    """删除订阅"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE sub_id = ?", (sub_id,))
    conn.commit()
    conn.close()
    return True

# ==================== 系统设置 ====================

def get_setting(key: str, default: str = None) -> Optional[str]:
    """读取设置项"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key: str, value: str) -> bool:
    """写入设置项"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    conn.commit()
    conn.close()
    return True

# ==================== API密钥管理 ====================

def create_api_key(note: str = None, user_id: int = None, 
                   scopes: list = None, expires_in_days: int = None, 
                   rate_limit: int = 60) -> tuple:
    """创建API密钥，返回(prefix, full_key)
    
    Args:
        note: 备注说明
        user_id: 所属用户ID
        scopes: 权限范围列表，如 ["read", "write", "admin"]
        expires_in_days: 多少天后过期，None表示永不过期
        rate_limit: 每分钟请求限制，默认60
    """
    key_id = secrets.token_hex(16)
    full_key = f"bts_{key_id}_{secrets.token_hex(24)}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    key_prefix = full_key[:20] + "..."
    
    # 计算过期时间
    expires_at = None
    if expires_in_days:
        expires_at = (datetime.now() + timedelta(days=expires_in_days)).strftime("%Y-%m-%d %H:%M:%S")
    
    # 权限范围
    if scopes is None:
        scopes = ["read", "write"]
    scopes_json = json.dumps(scopes)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_keys (key_id, key_hash, key_prefix, note, status, scopes, 
                            expires_at, rate_limit, user_id)
        VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)
    """, (key_id, key_hash, key_prefix, note, scopes_json, expires_at, rate_limit, user_id))
    conn.commit()
    conn.close()
    
    return key_prefix, full_key

def verify_api_key(full_key: str, client_ip: str = None) -> Optional[Dict]:
    """验证API密钥
    
    Args:
        full_key: API密钥完整字符串
        client_ip: 客户端IP地址
        
    Returns:
        验证成功返回密钥信息字典，失败返回None
    """
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT api_keys.*, users.username, users.role 
        FROM api_keys 
        LEFT JOIN users ON api_keys.user_id = users.id
        WHERE api_keys.key_hash = ? AND api_keys.status = 'active'
    """, (key_hash,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    key = dict(row)
    
    # 检查是否过期
    if key.get('expires_at'):
        expires_at = datetime.strptime(key['expires_at'], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_at:
            conn.close()
            return None
    
    # 检查速率限制
    if key.get('last_used'):
        last_used = datetime.strptime(key['last_used'], "%Y-%m-%d %H:%M:%S")
        minutes_passed = (datetime.now() - last_used).total_seconds() / 60
        if minutes_passed < 1 and key.get('usage_count', 0) >= key.get('rate_limit', 60):
            conn.close()
            return None
    
    # 更新使用统计
    cursor.execute("""
        UPDATE api_keys 
        SET last_used = CURRENT_TIMESTAMP,
            usage_count = usage_count + 1,
            last_used_ip = ?
        WHERE key_id = ?
    """, (client_ip, key['key_id']))
    conn.commit()
    conn.close()
    
    # 解析 scopes
    if key.get('scopes'):
        try:
            key['scopes'] = json.loads(key['scopes'])
        except:
            key['scopes'] = ["read", "write"]
    
    return key

def get_api_keys(user_id: int = None, status: str = None) -> List[Dict]:
    """获取API密钥列表
    
    Args:
        user_id: 用户ID筛选
        status: 状态筛选 (active/disabled)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """SELECT id, key_id, key_prefix, note, status, scopes, 
                       expires_at, rate_limit, usage_count, 
                       created_at, last_used, last_used_ip
                FROM api_keys WHERE 1=1"""
    params = []
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    keys = []
    for row in cursor.fetchall():
        key = dict(row)
        # 解析 scopes
        if key.get('scopes'):
            try:
                key['scopes'] = json.loads(key['scopes'])
            except:
                key['scopes'] = ["read", "write"]
        keys.append(key)
    
    conn.close()
    return keys

def update_api_key(key_id: str, **kwargs) -> bool:
    """更新API密钥信息
    
    Args:
        key_id: 密钥ID
        kwargs: 可更新的字段 (note, scopes, expires_at, rate_limit, status)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['note', 'scopes', 'expires_at', 'rate_limit', 'status']
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            if key == 'scopes' and isinstance(value, list):
                value = json.dumps(value)
            updates.append(f"{key} = ?")
            values.append(value)
    
    if updates:
        values.append(key_id)
        cursor.execute(f"UPDATE api_keys SET {', '.join(updates)} WHERE key_id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def get_api_key_by_id(key_id: str) -> Optional[Dict]:
    """根据ID获取API密钥详情"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, key_id, key_prefix, note, status, scopes, 
               expires_at, rate_limit, usage_count,
               created_at, last_used, last_used_ip, user_id
        FROM api_keys WHERE key_id = ?
    """, (key_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        key = dict(row)
        if key.get('scopes'):
            try:
                key['scopes'] = json.loads(key['scopes'])
            except:
                key['scopes'] = ["read", "write"]
        return key
    return None

def update_api_key_status(key_id: str, status: str) -> bool:
    """更新API密钥状态"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE api_keys SET status = ? WHERE key_id = ?", (status, key_id))
    conn.commit()
    conn.close()
    return True

def delete_api_key(key_id: str) -> bool:
    """删除API密钥"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_keys WHERE key_id = ?", (key_id,))
    conn.commit()
    conn.close()
    return True

# ==================== 统计功能 ====================

def update_daily_stats(date: str = None, **kwargs):
    """更新每日统计"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查当天记录是否存在
    cursor.execute("SELECT id FROM statistics WHERE date = ?", (date,))
    exists = cursor.fetchone()
    
    if exists:
        updates = []
        values = []
        for key, value in kwargs.items():
            updates.append(f"{key} = {key} + ?")
            values.append(value)
        if updates:
            values.append(date)
            cursor.execute(f"UPDATE statistics SET {', '.join(updates)} WHERE date = ?", values)
    else:
        cursor.execute("""
            INSERT INTO statistics (date, total_downloads, video_count, audio_count, image_count, total_size, success_count, fail_count)
            VALUES (?, 0, 0, 0, 0, 0, 0, 0)
        """, (date,))
        updates = []
        values = [date]
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            values.append(value)
        if updates:
            cursor.execute(f"UPDATE statistics SET {', '.join(updates)} WHERE date = ?", values)
    
    conn.commit()
    conn.close()

def get_statistics(days: int = 30) -> Dict:
    """获取统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 总览统计
    cursor.execute("""
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as fail_count,
            SUM(CASE WHEN status = 'downloading' THEN 1 ELSE 0 END) as downloading_count,
            SUM(file_size) as total_size,
            SUM(CASE WHEN resource_type = 'video' THEN 1 ELSE 0 END) as video_count,
            SUM(CASE WHEN resource_type = 'audio' THEN 1 ELSE 0 END) as audio_count,
            SUM(CASE WHEN resource_type = 'image' THEN 1 ELSE 0 END) as image_count
        FROM download_history
    """)
    overview = dict(cursor.fetchone())
    
    # 今日统计
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT * FROM statistics WHERE date = ?
    """, (today,))
    today_stats = cursor.fetchone()
    
    # 近N天趋势
    cursor.execute("""
        SELECT date, total_downloads, success_count, fail_count, total_size
        FROM statistics 
        ORDER BY date DESC LIMIT ?
    """, (days,))
    trend = [dict(row) for row in cursor.fetchall()]
    
    # 平台分布
    cursor.execute("""
        SELECT platform, COUNT(*) as count 
        FROM download_history 
        WHERE platform IS NOT NULL
        GROUP BY platform 
        ORDER BY count DESC
    """)
    platform_dist = [dict(row) for row in cursor.fetchall()]
    
    # 用户下载排行
    cursor.execute("""
        SELECT u.username, COUNT(*) as download_count
        FROM download_history dh
        JOIN users u ON dh.user_id = u.id
        GROUP BY u.username
        ORDER BY download_count DESC
        LIMIT 10
    """)
    user_ranking = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "overview": overview,
        "today": dict(today_stats) if today_stats else {},
        "trend": trend,
        "platform_dist": platform_dist,
        "user_ranking": user_ranking
    }

# ==================== 邀请码管理 ====================

def get_invite_codes() -> List[Dict]:
    """获取邀请码列表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ic.*, u.username as created_by_username
        FROM invite_codes ic
        LEFT JOIN users u ON ic.created_by = u.id
        ORDER BY ic.created_at DESC
    """)
    codes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return codes

def create_invite_code(created_by: int = 1) -> str:
    """创建邀请码"""
    code = secrets.token_hex(4).upper()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invite_codes (code, created_by) VALUES (?, ?)", (code, created_by))
    conn.commit()
    conn.close()
    return code

# ==================== Telegram 用户管理 ====================

def get_telegram_user(telegram_id: str) -> Optional[Dict]:
    """根据 Telegram ID 获取用户"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tu.*, u.username, u.role, u.avatar, u.is_active as user_is_active
        FROM telegram_users tu
        LEFT JOIN users u ON tu.user_id = u.id
        WHERE tu.telegram_id = ? AND tu.is_active = 1
    """, (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_telegram_user(telegram_id: str, telegram_username: str = None, 
                        telegram_first_name: str = None, telegram_last_name: str = None,
                        user_id: int = None) -> bool:
    """创建 Telegram 用户绑定"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO telegram_users (telegram_id, telegram_username, telegram_first_name, telegram_last_name, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, telegram_username, telegram_first_name, telegram_last_name, user_id))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

def update_telegram_user(telegram_id: str, **kwargs) -> bool:
    """更新 Telegram 用户信息"""
    conn = get_connection()
    cursor = conn.cursor()
    allowed_fields = ['telegram_username', 'telegram_first_name', 'telegram_last_name', 'user_id', 'is_active']
    updates = []
    values = []
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)
    if updates:
        values.append(telegram_id)
        cursor.execute(f"UPDATE telegram_users SET {', '.join(updates)} WHERE telegram_id = ?", values)
        conn.commit()
    conn.close()
    return True

def link_telegram_to_user(telegram_id: str, user_id: int) -> bool:
    """将 Telegram 账号绑定到系统用户"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 检查是否已存在
        cursor.execute("SELECT id FROM telegram_users WHERE telegram_id = ?", (telegram_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE telegram_users SET user_id = ?, last_login = CURRENT_TIMESTAMP 
                WHERE telegram_id = ?
            """, (user_id, telegram_id))
        else:
            cursor.execute("""
                INSERT INTO telegram_users (telegram_id, user_id, last_login)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (telegram_id, user_id))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()
