"""
认证模块 - JWT Token + API Key 管理
支持：Bearer Token / X-API-Key Header / ?token= 查询参数
"""

import time
import secrets
import jwt
from typing import Optional, Dict
from functools import wraps
from fastapi import HTTPException, Header, Query, Request
from backend.admin.db import verify_api_key

# JWT 配置
JWT_SECRET = secrets.token_hex(32)  # 启动时随机生成，重启后旧 token 失效
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 72  # Token 72 小时过期

def generate_token(username: str, user_id: int, role: str = "user") -> str:
    """生成 JWT 访问令牌"""
    payload = {
        "sub": username,
        "user_id": user_id,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRE_HOURS * 3600,
        "jti": secrets.token_hex(8)  # 唯一标识，防重放
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> Optional[Dict]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "username": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token(token: Optional[str]) -> bool:
    """验证令牌或 API Key"""
    if not token:
        return False
    
    token = str(token).strip()
    
    if token.lower().startswith('bearer '):
        token = token[7:].strip()
    
    # 先尝试 JWT 解码
    if _decode_token(token):
        return True
    
    # 再尝试 API Key
    return verify_api_key(token) is not None


def get_token_info(token: str) -> Optional[Dict]:
    """获取令牌或 API Key 的用户信息"""
    if not token:
        return None
    
    token = str(token).strip()
    
    if token.lower().startswith('bearer '):
        token = token[7:].strip()
    
    # 先尝试 JWT
    info = _decode_token(token)
    if info:
        return info
    
    # 再尝试 API Key
    api_key = verify_api_key(token)
    if api_key:
        return {
            "username": api_key.get("username"),
            "user_id": api_key.get("user_id"),
            "role": api_key.get("role"),
            "api_key_id": api_key.get("key_id")
        }
    return None


def invalidate_token(token: str) -> bool:
    """使令牌失效（JWT 无法真正吊销，这里仅做兼容接口）
    要真正吊销需要维护黑名单，这里简化处理"""
    return True


def _extract_token_from_request(request: Request = None, 
                                authorization: str = None,
                                x_api_key: str = None,
                                token: str = None) -> Optional[str]:
    """
    从多个来源提取认证令牌，优先级：
    1. request.headers['X-API-Key']
    2. authorization header（Bearer Token）
    3. x_api_key header
    4. token 查询参数
    """
    raw_token = None
    
    if request:
        headers = dict(request.headers)
        for key in headers:
            if key.lower() == 'x-api-key':
                raw_token = headers[key]
                break
    
    if not raw_token:
        if authorization:
            raw_token = authorization
        elif x_api_key:
            raw_token = x_api_key
        elif token:
            raw_token = token
    
    if raw_token:
        raw_token = str(raw_token).strip()
        if raw_token.lower().startswith('bearer '):
            raw_token = raw_token[7:].strip()
    
    return raw_token


def require_auth(func):
    """认证装饰器 - 支持 JWT Bearer Token / X-API-Key / ?token="""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        authorization = kwargs.get('authorization')
        x_api_key = kwargs.get('x_api_key')
        token = kwargs.get('token')
        
        if not request:
            from fastapi import Request as ReqCls
            for arg in args:
                if isinstance(arg, ReqCls):
                    request = arg
                    break
        
        raw_token = _extract_token_from_request(request, authorization, x_api_key, token)
        
        if not verify_token(raw_token):
            raise HTTPException(status_code=401, detail="未授权，请先登录")
        
        token_info = get_token_info(raw_token)
        if 'authorization' in kwargs:
            kwargs['authorization'] = raw_token
        
        return await func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """管理员权限装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        authorization = kwargs.get('authorization')
        x_api_key = kwargs.get('x_api_key')
        token = kwargs.get('token')
        
        if not request:
            from fastapi import Request as ReqCls
            for arg in args:
                if isinstance(arg, ReqCls):
                    request = arg
                    break
        
        raw_token = _extract_token_from_request(request, authorization, x_api_key, token)
        
        if not verify_token(raw_token):
            raise HTTPException(status_code=401, detail="未授权，请先登录")
        
        token_info = get_token_info(raw_token)
        if not token_info or token_info.get("role") != "admin":
            raise HTTPException(status_code=403, detail="需要管理员权限")
        
        return await func(*args, **kwargs)
    return wrapper
