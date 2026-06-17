"""文件管理路由"""
import os
import re
import urllib.parse
import mimetypes
import asyncio
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, HTTPException, Header, Request, Query
from fastapi.responses import FileResponse, Response, StreamingResponse

from backend.admin.auth import require_auth, get_token_info
from backend.services.platform_service import format_size

router = APIRouter(tags=["文件管理"])

BASE_DIR = Path(os.getenv("APP_BASE_DIR", "/app"))
DOWNLOAD_DIR = BASE_DIR / "downloads"


def safe_download_path(filename: str) -> Path:
    """返回下载目录内的安全路径"""
    candidate = (DOWNLOAD_DIR / filename).resolve()
    if DOWNLOAD_DIR.resolve() not in candidate.parents and candidate != DOWNLOAD_DIR.resolve():
        raise HTTPException(status_code=400, detail="非法文件路径")
    return candidate


@router.get("/api/files")
@require_auth
async def list_files(authorization: str = Header(None)):
    """列出已下载文件"""
    files = []
    if DOWNLOAD_DIR.exists():
        for f in DOWNLOAD_DIR.rglob('*'):
            if f.is_file() and not f.name.startswith('.'):
                stat = f.stat()
                files.append({
                    "name": f.relative_to(DOWNLOAD_DIR).as_posix(),
                    "size": stat.st_size,
                    "size_formatted": format_size(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    return {"files": sorted(files, key=lambda x: x["modified"], reverse=True)}


@router.get("/api/files/stream/{filename:path}")
@require_auth
async def stream_file(filename: str, request: Request, authorization: str = Header(None), token: str = Query(None)):
    """流式播放文件，支持 Range 请求"""
    file_path = safe_download_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    mime_type, _ = mimetypes.guess_type(str(file_path))
    media_type = mime_type or "application/octet-stream"

    # 视频转码检查
    if media_type.startswith('video/'):
        import subprocess
        try:
            probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_entries', 'stream=codec_name',
                        '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path)]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=5)
            codec = result.stdout.strip()
            if codec in ['av1', 'vp9', 'hevc', 'h265']:
                return await _stream_transcoded(file_path)
        except Exception:
            pass

    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")

    if range_header:
        range_match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            with open(file_path, "rb") as f:
                f.seek(start)
                content = f.read(end - start + 1)
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(content)),
                "Content-Type": media_type,
            }
            return Response(content=content, status_code=206, headers=headers)

    return FileResponse(path=file_path, media_type=media_type,
                       headers={"Accept-Ranges": "bytes", "Content-Length": str(file_size)})


async def _stream_transcoded(file_path: Path):
    """实时转码 AV1/HEVC → H.264"""
    ffmpeg_cmd = [
        'ffmpeg', '-i', str(file_path),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-movflags', 'frag_keyframe+empty_moov',
        '-f', 'mp4', 'pipe:1'
    ]
    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    return StreamingResponse(process.stdout, media_type="video/mp4",
                           headers={"Accept-Ranges": "none", "Cache-Control": "no-cache"})


@router.get("/api/files/{filename:path}")
@require_auth
async def download_file(filename: str, authorization: str = Header(None), token: str = Query(None)):
    """下载文件到本地"""
    file_path = safe_download_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    encoded_filename = urllib.parse.quote(file_path.name)
    return FileResponse(path=file_path, media_type="application/octet-stream",
                       filename=file_path.name,
                       headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"})


@router.delete("/api/files/{filename:path}")
@require_auth
async def delete_file(filename: str, authorization: str = Header(None)):
    """删除文件"""
    file_path = safe_download_path(filename)
    if file_path.exists():
        file_path.unlink()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="文件不存在")


@router.post("/api/files/rename")
@require_auth
async def rename_file(req: dict, authorization: str = Header(None)):
    """重命名文件"""
    old_path = safe_download_path(req.get('old_name', ''))
    ext = old_path.suffix
    new_path = old_path.with_name(req.get('new_name', '') + ext)
    if old_path.exists():
        old_path.rename(new_path)
        return {"status": "success", "new_name": req.get('new_name', '') + ext}
    raise HTTPException(status_code=404, detail="文件不存在")
