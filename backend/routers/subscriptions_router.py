"""订阅管理路由"""
import uuid
from fastapi import APIRouter, HTTPException, Header, Body
from typing import Optional

from backend.models.schemas import SubscribeRequest
from backend.admin.auth import require_auth, get_token_info
from backend.admin.db import create_subscription, get_subscriptions, get_subscription, update_subscription, delete_subscription

router = APIRouter(tags=["订阅"])


@router.get("/api/subscriptions")
@require_auth
async def list_subscriptions(authorization: str = Header(None), platform: str = None, status: str = None):
    """获取订阅列表"""
    token_info = get_token_info(authorization)
    subs = get_subscriptions(user_id=token_info["user_id"], platform=platform, status=status)
    return {"subscriptions": subs, "count": len(subs)}


@router.post("/api/subscriptions")
@require_auth
async def add_subscription(req: SubscribeRequest, authorization: str = Header(None)):
    """添加订阅"""
    token_info = get_token_info(authorization)
    sub_id = str(uuid.uuid4())
    create_subscription(sub_id=sub_id, channel_url=req.url, platform=req.platform,
                       channel_name=req.channel_name, poll_interval=req.poll_interval,
                       user_id=token_info["user_id"])
    return {"status": "success", "sub_id": sub_id}


@router.put("/api/subscriptions/{sub_id}")
@require_auth
async def update_sub(sub_id: str, status: Optional[str] = Body(None), authorization: str = Header(None)):
    """更新订阅状态"""
    token_info = get_token_info(authorization)
    if status not in {'active', 'paused'}:
        raise HTTPException(status_code=400, detail="无效的订阅状态")
    sub = get_subscription(sub_id, user_id=token_info["user_id"])
    if not sub:
        raise HTTPException(status_code=404, detail="订阅不存在")
    update_subscription(sub_id, status=status)
    return {"status": "success"}


@router.delete("/api/subscriptions/{sub_id}")
@require_auth
async def remove_subscription(sub_id: str, authorization: str = Header(None)):
    """删除订阅"""
    token_info = get_token_info(authorization)
    sub = get_subscription(sub_id, user_id=token_info["user_id"])
    if not sub:
        raise HTTPException(status_code=404, detail="订阅不存在")
    delete_subscription(sub_id)
    return {"status": "success"}
