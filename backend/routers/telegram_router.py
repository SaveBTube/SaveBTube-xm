"""Telegram 路由 - 登录/绑定/Bot 管理"""
import time
from fastapi import APIRouter, HTTPException

from backend.models.schemas import TelegramLoginRequest, TelegramBindRequest
from backend.admin.db import (
    get_setting, verify_user, get_telegram_user, create_telegram_user,
    link_telegram_to_user, update_telegram_user
)
from backend.admin.auth import generate_token

router = APIRouter(prefix="/api/admin/telegram", tags=["Telegram"])


def verify_telegram_auth(telegram_data: dict, bot_token: str) -> bool:
    """验证 Telegram Widget 数据的 HMAC-SHA256 签名"""
    import hashlib
    import hmac

    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(telegram_data.items()) if k != 'hash'
    )
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return computed_hash == telegram_data.get('hash', '')


@router.get("/login-url")
async def get_telegram_login_url():
    """获取 Telegram 登录 Widget URL"""
    telegram_bot_token = get_setting('telegram_bot_token', '')
    telegram_login_enabled = get_setting('telegram_login_enabled', '0')
    if not telegram_bot_token or telegram_login_enabled != '1':
        return {"enabled": False}
    return {"enabled": True, "bot_token": telegram_bot_token[:10] + "..."}


@router.post("/login")
async def telegram_login(req: TelegramLoginRequest):
    """Telegram Widget 登录"""
    telegram_bot_token = get_setting('telegram_bot_token', '')
    telegram_login_enabled = get_setting('telegram_login_enabled', '0')
    if not telegram_bot_token or telegram_login_enabled != '1':
        raise HTTPException(status_code=403, detail="Telegram 登录未启用")

    telegram_data = {
        'id': str(req.id), 'first_name': req.first_name,
        'last_name': req.last_name, 'username': req.username,
        'photo_url': req.photo_url, 'auth_date': str(req.auth_date),
        'hash': req.hash
    }

    if not verify_telegram_auth(telegram_data.copy(), telegram_bot_token):
        raise HTTPException(status_code=401, detail="Telegram 验证失败")

    if time.time() - req.auth_date > 300:
        raise HTTPException(status_code=401, detail="Telegram 验证已过期")

    telegram_id = str(req.id)
    tg_user = get_telegram_user(telegram_id)

    if tg_user:
        if not tg_user.get('user_is_active'):
            raise HTTPException(status_code=403, detail="账户已被禁用")
        token = generate_token(tg_user['username'], tg_user['user_id'], tg_user['role'])
        update_telegram_user(telegram_id, last_login=datetime.now().isoformat())
        return {
            "status": "success", "token": token,
            "username": tg_user['username'], "role": tg_user['role'],
            "avatar": tg_user.get('avatar'), "telegram_bound": True
        }
    else:
        return {
            "status": "need_binding", "telegram_id": telegram_id,
            "telegram_username": req.username,
            "telegram_first_name": req.first_name,
            "telegram_last_name": req.last_name
        }


@router.post("/bind")
async def telegram_bind_account(req: TelegramBindRequest):
    """绑定 Telegram 到系统账户"""
    telegram_bot_token = get_setting('telegram_bot_token', '')
    telegram_login_enabled = get_setting('telegram_login_enabled', '0')
    if not telegram_bot_token or telegram_login_enabled != '1':
        raise HTTPException(status_code=403, detail="Telegram 登录未启用")

    user = verify_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="账户名或密码错误")

    telegram_id = str(req.telegram_id)
    if link_telegram_to_user(telegram_id, user['id']):
        token = generate_token(user['username'], user['id'], user['role'])
        return {
            "status": "success", "token": token,
            "username": user['username'], "role": user['role'],
            "avatar": user.get('avatar'), "telegram_bound": True
        }
    else:
        raise HTTPException(status_code=400, detail="绑定失败")


# 补充 datetime import
from datetime import datetime
