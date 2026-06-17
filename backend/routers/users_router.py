"""用户管理路由"""
from fastapi import APIRouter, HTTPException, Header, Request

from backend.models.schemas import PasswordChangeRequest, UserUpdateRequest, UserCreateRequest
from backend.admin.auth import require_auth, require_admin, get_token_info
from backend.admin.db import (
    get_user_by_id, get_all_users, create_user, update_user, delete_user,
    change_password, update_avatar
)

router = APIRouter(prefix="/api/admin", tags=["用户管理"])


@router.get("/me")
@require_auth
async def get_current_user(authorization: str = Header(None)):
    """获取当前用户信息"""
    token_info = get_token_info(authorization)
    user = get_user_by_id(token_info["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/password")
@require_auth
async def change_user_password(req: PasswordChangeRequest, authorization: str = Header(None)):
    """修改密码"""
    token_info = get_token_info(authorization)
    if change_password(token_info["user_id"], req.old_password, req.new_password):
        return {"status": "success", "message": "密码修改成功"}
    raise HTTPException(status_code=400, detail="当前密码错误")


@router.post("/avatar")
@require_auth
async def upload_avatar(request: Request, authorization: str = Header(None)):
    """上传头像"""
    token_info = get_token_info(authorization)
    try:
        form = await request.form()
        avatar_file = form.get("avatar")
        if avatar_file:
            try:
                content = await avatar_file.read()
            except Exception:
                content = avatar_file.file.read() if hasattr(avatar_file, 'file') else None
            if not content:
                raise HTTPException(status_code=400, detail="头像文件读取失败")
            mime_type = getattr(avatar_file, 'content_type', 'image/png') or 'image/png'
            if mime_type not in ('image/png', 'image/jpeg'):
                raise HTTPException(status_code=400, detail="只支持 JPG/PNG 格式")
            import base64
            avatar_base64 = base64.b64encode(content).decode('utf-8')
            avatar_data = f"data:{mime_type};base64,{avatar_base64}"
            update_avatar(token_info["user_id"], avatar_data)
            return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=400, detail="未提供头像数据")


@router.get("/users")
@require_admin
async def list_users(authorization: str = Header(None)):
    """获取用户列表"""
    return {"users": get_all_users()}


@router.post("/users")
@require_admin
async def create_user_admin(req: UserCreateRequest, authorization: str = Header(None)):
    """管理员创建用户"""
    if create_user(req.username, req.password, role=req.role, is_active=req.is_active, invite_code=None):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="创建用户失败")


@router.put("/users/{user_id}")
@require_admin
async def update_user_info(user_id: int, req: UserUpdateRequest, authorization: str = Header(None)):
    """更新用户"""
    if update_user(user_id, req.role, req.is_active):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="更新失败")


@router.delete("/users/{user_id}")
@require_admin
async def delete_user_info(user_id: int, authorization: str = Header(None)):
    """删除用户"""
    if user_id == 1:
        raise HTTPException(status_code=403, detail="禁止删除默认管理员")
    if delete_user(user_id):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="删除失败")
