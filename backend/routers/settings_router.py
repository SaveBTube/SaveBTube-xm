"""设置与统计路由"""
import socket
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, Header
from datetime import datetime
import os

from backend.admin.auth import require_auth, require_admin, get_token_info
from backend.admin.db import (
    get_invite_codes, create_invite_code,
    create_api_key, verify_api_key, get_api_keys, update_api_key_status,
    delete_api_key, update_api_key, get_api_key_by_id,
    get_statistics, get_setting, set_setting
)
from backend.models.schemas import ApiKeyRequest

router = APIRouter(tags=["设置与统计"])


# ==================== 邀请码 ====================

@router.get("/api/admin/invite-codes")
@require_admin
async def list_invite_codes(authorization: str = Header(None)):
    return {"codes": get_invite_codes()}


@router.post("/api/admin/invite-codes")
@require_admin
async def generate_invite_code(authorization: str = Header(None)):
    token_info = get_token_info(authorization)
    code = create_invite_code(token_info["user_id"])
    return {"code": code}


# ==================== API Key ====================

@router.get("/api/admin/api-keys")
@require_auth
async def list_api_keys(authorization: str = Header(None), status: str = None):
    token_info = get_token_info(authorization)
    return {"keys": get_api_keys(token_info["user_id"], status=status)}


@router.post("/api/admin/api-keys")
@require_auth
async def create_new_api_key(req: ApiKeyRequest, authorization: str = Header(None)):
    token_info = get_token_info(authorization)
    prefix, full_key = create_api_key(note=req.note, user_id=token_info["user_id"],
                                      scopes=req.scopes, expires_in_days=req.expires_in_days,
                                      rate_limit=req.rate_limit)
    return {"key_prefix": prefix, "full_key": full_key}


@router.put("/api/admin/api-keys/{key_id}/status")
@require_auth
async def toggle_api_key(key_id: str, status: str = "active", authorization: str = Header(None)):
    token_info = get_token_info(authorization)
    key = get_api_key_by_id(key_id)
    if not key or key["user_id"] != token_info["user_id"]:
        raise HTTPException(status_code=403, detail="无权限")
    if update_api_key_status(key_id, status):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="更新失败")


@router.put("/api/admin/api-keys/{key_id}")
@require_auth
async def update_api_key_settings(key_id: str, req: ApiKeyRequest, authorization: str = Header(None)):
    token_info = get_token_info(authorization)
    key = get_api_key_by_id(key_id)
    if not key or key["user_id"] != token_info["user_id"]:
        raise HTTPException(status_code=403, detail="无权限")
    update_data = {}
    if req.note is not None:
        update_data['note'] = req.note
    if req.scopes is not None:
        update_data['scopes'] = req.scopes
    if req.expires_in_days is not None:
        from datetime import timedelta
        expires_at = (datetime.now() + timedelta(days=req.expires_in_days)).strftime("%Y-%m-%d %H:%M:%S")
        update_data['expires_at'] = expires_at
    if req.rate_limit is not None:
        update_data['rate_limit'] = req.rate_limit
    if update_api_key(key_id, **update_data):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="更新失败")


@router.delete("/api/admin/api-keys/{key_id}")
@require_auth
async def remove_api_key(key_id: str, authorization: str = Header(None)):
    token_info = get_token_info(authorization)
    key = get_api_key_by_id(key_id)
    if not key or key["user_id"] != token_info["user_id"]:
        raise HTTPException(status_code=403, detail="无权限")
    if delete_api_key(key_id):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="删除失败")


# ==================== 系统设置 ====================

@router.get("/api/settings")
@require_admin
async def get_settings(authorization: str = Header(None)):
    return {
        "proxy_enabled": get_setting('proxy_enabled', '0') == '1',
        "http_proxy": get_setting('http_proxy', ''),
        "https_proxy": get_setting('https_proxy', ''),
        "telegram_bot_token": get_setting('telegram_bot_token', ''),
        "telegram_allowed_user_ids": get_setting('telegram_allowed_user_ids', ''),
        "telegram_api_id": get_setting('telegram_api_id', ''),
        "telegram_api_hash": get_setting('telegram_api_hash', ''),
        "telegram_session": get_setting('telegram_session', ''),
        "telegram_login_enabled": get_setting('telegram_login_enabled', '0') == '1',
        "telegram_login_download_enabled": get_setting('telegram_login_download_enabled', '0') == '1',
        "xtwitter_cookies": get_setting('xtwitter_cookies', ''),
        "xtwitter_download_video": get_setting('xtwitter_download_video', '1') == '1',
        "xtwitter_download_images": get_setting('xtwitter_download_images', '1') == '1',
        "xtwitter_best_quality": get_setting('xtwitter_best_quality', '1') == '1',
        "xtwitter_quality": get_setting('xtwitter_quality', 'best'),
        # QQ Bot
        "qq_bot_api_url": get_setting('qq_bot_api_url', ''),
        # 微信 ClawBot
        "wechat_clawbot_callback_url": get_setting('wechat_clawbot_callback_url', ''),
    }


@router.post("/api/settings")
@require_admin
async def save_settings(req: dict, authorization: str = Header(None)):
    """保存系统设置"""
    setting_keys = {
        'proxy_enabled': ('bool', 'proxy_enabled'),
        'http_proxy': ('str', 'http_proxy'),
        'https_proxy': ('str', 'https_proxy'),
        'telegram_bot_token': ('str', 'telegram_bot_token'),
        'telegram_allowed_user_ids': ('str', 'telegram_allowed_user_ids'),
        'telegram_api_id': ('str', 'telegram_api_id'),
        'telegram_api_hash': ('str', 'telegram_api_hash'),
        'telegram_session': ('str', 'telegram_session'),
        'telegram_login_enabled': ('bool', 'telegram_login_enabled'),
        'telegram_login_download_enabled': ('bool', 'telegram_login_download_enabled'),
        'xtwitter_cookies': ('str', 'xtwitter_cookies'),
        'xtwitter_download_video': ('bool', 'xtwitter_download_video'),
        'xtwitter_download_images': ('bool', 'xtwitter_download_images'),
        'xtwitter_best_quality': ('bool', 'xtwitter_best_quality'),
        'xtwitter_quality': ('str', 'xtwitter_quality'),
        # QQ Bot
        'qq_bot_api_url': ('str', 'qq_bot_api_url'),
        # 微信 ClawBot
        'wechat_clawbot_callback_url': ('str', 'wechat_clawbot_callback_url'),
    }
    for key, (typ, setting_key) in setting_keys.items():
        if key in req:
            if typ == 'bool':
                set_setting(setting_key, '1' if req[key] else '0')
            else:
                set_setting(setting_key, str(req[key] or ''))
    return {"status": "success"}


@router.post("/api/settings/test-proxy")
@require_admin
async def test_proxy_connection(req: dict, authorization: str = Header(None)):
    """测试代理连接"""
    proxy_url = req.get('proxy_url', '')
    if not proxy_url:
        raise HTTPException(status_code=400, detail="请提供代理地址")
    try:
        parsed = urlparse(proxy_url)
        host, port = parsed.hostname, parsed.port
        if not host or not port:
            return {"success": False, "detail": "代理地址格式不正确"}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return {"success": result == 0, "detail": f"成功连接到 {host}:{port}" if result == 0 else f"无法连接到 {host}:{port}"}
    except Exception as e:
        return {"success": False, "detail": f"测试失败: {str(e)}"}


# ==================== 统计 ====================

@router.get("/api/statistics")
@require_auth
async def get_stats(days: int = 30, authorization: str = Header(None)):
    """获取统计数据"""
    import psutil, time
    stats = get_statistics(days)
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        stats["system"] = {
            "cpu_percent": cpu_percent,
            "memory_total": memory.total, "memory_used": memory.used, "memory_percent": memory.percent,
            "disk_total": disk.total, "disk_used": disk.used, "disk_percent": disk.percent,
            "network_up_mb": 0, "network_down_mb": 0,
            "network_total_sent": net.bytes_sent, "network_total_recv": net.bytes_recv,
        }
    except Exception:
        pass
    return stats


# ==================== 日志 ====================

@router.get("/api/logs")
@require_auth
async def get_logs(authorization: str = Header(None), date: str = None, level: str = None, limit: int = 100):
    """获取应用日志"""
    from pathlib import Path
    LOGS_DIR = Path(os.getenv("APP_BASE_DIR", "/app")) / "logs"
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"app_{date}.log"
    logs = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f.readlines()[-limit:]:
                if level:
                    if level.upper() in line:
                        logs.append(line.strip())
                else:
                    logs.append(line.strip())
    return {"logs": logs, "date": date}
