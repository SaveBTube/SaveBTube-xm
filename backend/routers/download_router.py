"""下载路由"""
import re
import uuid
from fastapi import APIRouter, HTTPException, Header, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.models.schemas import DownloadRequest, QuickDownloadRequest, ShortcutsDownloadRequest, RenameTaskRequest
from backend.admin.auth import require_auth, get_token_info
from backend.admin.db import get_download_tasks, get_download_task, delete_download_task, rename_download_task
from backend.services.download_service import start_download_task, DOWNLOAD_PROGRESS
from backend.services.platform_service import detect_platform

router = APIRouter(tags=["下载"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/api/download")
@require_auth
@limiter.limit("30/minute")
async def download_video(request: Request, req: DownloadRequest, authorization: str = Header(None)):
    """发起下载任务"""
    token_info = get_token_info(authorization)
    result = start_download_task(req.url, req.quality, token_info["user_id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/api/quick-download")
@require_auth
async def quick_download(req: QuickDownloadRequest, request: Request, authorization: str = Header(None), x_api_key: str = Header(None)):
    """快速下载（浏览器扩展）"""
    raw_token = authorization or x_api_key
    if not raw_token:
        raw_token = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if not raw_token:
        raise HTTPException(status_code=401, detail="未授权")

    token_info = get_token_info(raw_token)
    if not token_info:
        raise HTTPException(status_code=401, detail="无效的认证凭据")

    result = start_download_task(req.url, req.quality, token_info["user_id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/api/shortcuts/download")
async def shortcuts_download(req: ShortcutsDownloadRequest, x_api_key: str = Header(None)):
    """iOS 快捷指令下载"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="未提供 API Key")

    token_info = get_token_info(x_api_key)
    if not token_info:
        raise HTTPException(status_code=401, detail="无效的 API Key")

    result = start_download_task(req.url, req.quality or "best", token_info["user_id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "task_id": result["task_id"],
        "platform": result["platform"],
        "message": f"已添加到下载队列: {result['platform']}",
        "progress_url": f"/api/progress/{result['task_id']}"
    }


@router.get("/api/progress/{task_id}")
@require_auth
async def get_progress(task_id: str, authorization: str = Header(None)):
    """获取下载进度"""
    return DOWNLOAD_PROGRESS.get(task_id, {"status": "unknown"})


@router.get("/api/downloads")
@require_auth
async def list_downloads(
    authorization: str = Header(None),
    status: str = None,
    platform: str = None,
    resource_type: str = None,
    search: str = None
):
    """获取下载任务列表"""
    token_info = get_token_info(authorization)
    tasks = get_download_tasks(
        user_id=token_info["user_id"],
        status=status, platform=platform,
        resource_type=resource_type, search=search
    )
    return {"tasks": tasks, "count": len(tasks)}


@router.delete("/api/tasks/{task_id}")
@require_auth
async def delete_task(task_id: str, authorization: str = Header(None)):
    """删除任务"""
    from pathlib import Path
    task = get_download_task(task_id)
    if task and task.get('file_path'):
        try:
            file_path = Path(task['file_path']).resolve()
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass
    if task_id in DOWNLOAD_PROGRESS:
        del DOWNLOAD_PROGRESS[task_id]
    delete_download_task(task_id)
    return {"status": "success"}


@router.post("/api/tasks/{task_id}/rename")
@require_auth
async def rename_task(task_id: str, req: RenameTaskRequest, authorization: str = Header(None)):
    """重命名任务"""
    new_title = (req.new_title or '').strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="新名称不能为空")
    rename_download_task(task_id, new_title)
    return {"status": "success", "task_id": task_id, "title": new_title}
