"""认证路由"""
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.models.schemas import LoginRequest, RegisterRequest
from backend.admin.db import verify_user, create_user
from backend.admin.auth import generate_token

router = APIRouter(prefix="/api/admin", tags=["认证"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login")
@limiter.limit("10/minute")
async def admin_login(request: Request, req: LoginRequest):
    """用户登录"""
    user = verify_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="账户名或密码错误")

    token = generate_token(user["username"], user["id"], user["role"])
    return {
        "status": "success",
        "token": token,
        "username": user["username"],
        "role": user["role"],
        "avatar": user.get("avatar")
    }


@router.post("/register")
@limiter.limit("5/minute")
async def admin_register(request: Request, req: RegisterRequest):
    """用户注册"""
    if create_user(req.username, req.password, invite_code=req.invite_code):
        return {"status": "success", "message": "注册成功，请登录"}
    raise HTTPException(status_code=400, detail="注册失败，请检查邀请码是否有效")
