"""
下载服务 - yt-dlp 下载逻辑
"""
import os
import re
import uuid
import urllib.parse
import yt_dlp
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from threading import Thread

from backend.admin.db import (
    create_download_task, update_download_task,
    update_daily_stats, get_setting
)
from backend.config import get_proxy_config, is_local_address, load_config
from backend.services.platform_service import detect_platform, get_cookies_file, get_platform_folder

BASE_DIR = Path(os.getenv("APP_BASE_DIR", "/app"))
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 全局下载进度存储
DOWNLOAD_PROGRESS: Dict = {}

# 加载配置
try:
    APP_CONFIG = load_config(BASE_DIR)
except Exception:
    APP_CONFIG = {}


def ytdl_progress_hook(d: Dict, task_id: str):
    """yt-dlp 进度回调"""
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0%')
        percent_clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str).strip().replace('%', '')
        try:
            percent = float(percent_clean)
        except:
            percent = 0

        speed_str = d.get('_speed_str', '0 B/s')
        speed = re.sub(r'\x1b\[[0-9;]*m', '', speed_str).strip()

        eta_str = d.get('_eta_str', '00:00')
        eta = re.sub(r'\x1b\[[0-9;]*m', '', eta_str).strip()

        filename = os.path.basename(d.get('filename', ''))

        DOWNLOAD_PROGRESS[task_id] = {
            "status": "downloading",
            "percent": percent,
            "speed": speed,
            "eta": eta,
            "filename": filename
        }

        update_download_task(task_id, progress=percent, speed=speed, status="downloading")
        
        # WebSocket 推送
        try:
            from backend.services.ws_manager import ws_manager
            task = get_download_task(task_id)
            if task and task.get('user_id'):
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    ws_manager.notify_download_progress(task_id, task['user_id'], {
                        "status": "downloading",
                        "percent": percent,
                        "speed": speed,
                        "eta": eta,
                        "filename": filename
                    }),
                    asyncio.get_event_loop()
                )
        except Exception:
            pass

    elif d['status'] == 'finished':
        filename = d.get('filename', '')
        file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
        resolution = 'audio' if d.get('format_id', '').startswith('audio') else None

        DOWNLOAD_PROGRESS[task_id] = {
            "status": "completed",
            "percent": 100,
            "speed": "0 B/s",
            "eta": "00:00",
            "filename": os.path.basename(filename)
        }

        update_download_task(
            task_id,
            status="completed",
            progress=100,
            file_size=file_size,
            file_path=filename,
            resolution=resolution,
            finished_at=datetime.now().isoformat()
        )

        today = datetime.now().strftime("%Y-%m-%d")
        update_daily_stats(today, total_downloads=1, success_count=1, total_size=file_size)
        
        # WebSocket 推送完成
        try:
            from backend.services.ws_manager import ws_manager
            task = get_download_task(task_id)
            if task and task.get('user_id'):
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    ws_manager.notify_download_progress(task_id, task['user_id'], {
                        "status": "completed",
                        "percent": 100,
                        "filename": os.path.basename(filename)
                    }),
                    asyncio.get_event_loop()
                )
        except Exception:
            pass


def _build_ydl_opts(task_id: str, url: str, quality: str, cookies_file: Optional[str] = None) -> Dict:
    """构建 yt-dlp 配置"""
    platform = detect_platform(url)
    folder = DOWNLOAD_DIR / get_platform_folder(platform)
    folder.mkdir(parents=True, exist_ok=True)

    # 代理配置
    proxy_enabled = get_setting('proxy_enabled', '0') == '1'
    proxy_cfg = get_proxy_config(APP_CONFIG)

    if not proxy_enabled:
        http_proxy = ''
        https_proxy = ''
    else:
        http_proxy = get_setting('http_proxy') or proxy_cfg['http'] or os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY') or ''
        https_proxy = get_setting('https_proxy') or proxy_cfg['https'] or os.getenv('HTTPS_PROXY') or http_proxy or ''

        if proxy_cfg['mode'] == 'auto' and (http_proxy or https_proxy):
            hostname = urllib.parse.urlparse(url).hostname or ''
            if is_local_address(hostname, proxy_cfg['bypass_cidrs']):
                http_proxy = ''
                https_proxy = ''

    proxy = https_proxy or http_proxy

    ydl_opts = {
        'outtmpl': str(folder / '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: ytdl_progress_hook(d, task_id)],
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
    }

    # 质量格式
    if quality == "audio":
        ydl_opts['format'] = 'bestaudio/best'
    elif quality == "mp3":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
    elif quality == "m4a":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}]
    elif quality == "1080p":
        ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio/best/best'
        ydl_opts['merge_output_format'] = 'mp4'
    elif quality == "720p":
        ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio/best/best'
        ydl_opts['merge_output_format'] = 'mp4'
    elif quality == "mp4":
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio/best/best'
        ydl_opts['merge_output_format'] = 'mp4'
    elif quality == "webm":
        ydl_opts['format'] = 'bestvideo[ext=webm]+bestaudio/best/best'
        ydl_opts['merge_output_format'] = 'webm'
    elif quality in ("image", "jpg", "png"):
        ydl_opts['format'] = 'best'
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio/best/best'
        ydl_opts['merge_output_format'] = 'mp4'

    # Cookies
    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    # Bilibili 特殊处理
    if platform == 'bilibili':
        ydl_opts['extractor_args'] = {'bilibili': {'ssr': ['yes']}}
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/video/' + url.split('/')[-1].split('?')[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        if not proxy:
            ydl_opts['proxy'] = ''

    if proxy:
        ydl_opts['proxy'] = proxy
    elif 'proxy' not in ydl_opts:
        ydl_opts['proxy'] = ''

    return ydl_opts


def run_download(task_id: str, url: str, quality: str, cookies_file: str = None):
    """执行下载（在线程中运行）"""
    platform = detect_platform(url)
    ydl_opts = _build_ydl_opts(task_id, url, quality, cookies_file)

    def _extract_and_update(ydl_local, do_download=True):
        info_local = ydl_local.extract_info(url, download=do_download)
        title = info_local.get('title', 'Unknown')
        resource_type = 'audio' if info_local.get('acodec') or info_local.get('ext') in ('mp3', 'm4a', 'wav') else 'video'
        if info_local.get('_type') == 'playlist':
            resource_type = 'video'
        resolution = None
        formats = info_local.get('formats', []) if isinstance(info_local, dict) else []
        video_formats = [f for f in formats if f.get('vcodec') not in (None, 'none') and f.get('height')]
        if video_formats:
            resolution = f"{max(f['height'] for f in video_formats)}p"
        update_download_task(task_id, title=title, platform=platform, resource_type=resource_type, resolution=resolution)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            _extract_and_update(ydl, do_download=True)
    except Exception as e:
        # 回退策略
        try:
            probe_opts = dict(ydl_opts)
            probe_opts.update({'quiet': True, 'no_warnings': True, 'skip_download': True})
            with yt_dlp.YoutubeDL(probe_opts) as ydl_probe:
                info_probe = ydl_probe.extract_info(url, download=False)

            available_formats = info_probe.get('formats', []) if isinstance(info_probe, dict) else []
            fallback_errors = []
            fallback_formats = ['bestvideo[ext=mp4]+bestaudio/best/best', 'bestvideo+bestaudio/best', 'best[ext=mp4]/best', 'best']
            attempted = False

            for fmt in fallback_formats:
                try:
                    attempt_opts = dict(ydl_opts)
                    attempt_opts['format'] = fmt
                    if fmt != 'bestaudio/best':
                        attempt_opts['merge_output_format'] = 'mp4'
                    with yt_dlp.YoutubeDL(attempt_opts) as ydl_retry:
                        _extract_and_update(ydl_retry, do_download=True)
                    attempted = True
                    break
                except Exception as ee:
                    fallback_errors.append(f"{fmt}: {str(ee)}")

            if not attempted and available_formats:
                sorted_formats = sorted(available_formats, key=lambda f: (int(f.get('height') or 0), int(f.get('tbr') or 0)), reverse=True)
                for fmt_info in sorted_formats:
                    fmt_id = fmt_info.get('format_id')
                    if not fmt_id:
                        continue
                    try:
                        attempt_opts = dict(ydl_opts)
                        attempt_opts['format'] = fmt_id
                        if 'video' in (fmt_info.get('format') or ''):
                            attempt_opts['merge_output_format'] = 'mp4'
                        with yt_dlp.YoutubeDL(attempt_opts) as ydl_retry2:
                            _extract_and_update(ydl_retry2, do_download=True)
                        attempted = True
                        break
                    except Exception as ee:
                        fallback_errors.append(f"{fmt_id}: {str(ee)}")

            if not attempted:
                err_msg = f"下载失败: {str(e)}; 回退: {fallback_errors}"
                DOWNLOAD_PROGRESS[task_id] = {"status": "failed", "error": err_msg}
                update_download_task(task_id, status="failed", error_message=err_msg)
                today = datetime.now().strftime("%Y-%m-%d")
                update_daily_stats(today, total_downloads=1, fail_count=1)
                
                # WebSocket 推送失败
                try:
                    from backend.services.ws_manager import ws_manager
                    task = get_download_task(task_id)
                    if task and task.get('user_id'):
                        import asyncio
                        asyncio.run_coroutine_threadsafe(
                            ws_manager.notify_download_progress(task_id, task['user_id'], {
                                "status": "failed",
                                "error": err_msg[:200]
                            }),
                            asyncio.get_event_loop()
                        )
                except Exception:
                    pass
        except Exception as probe_exc:
            err_msg = f"下载失败: {str(e)}; 探测失败: {str(probe_exc)}"
            DOWNLOAD_PROGRESS[task_id] = {"status": "failed", "error": err_msg}
            update_download_task(task_id, status="failed", error_message=err_msg)
            today = datetime.now().strftime("%Y-%m-%d")
            update_daily_stats(today, total_downloads=1, fail_count=1)


def start_download_task(url: str, quality: str, user_id: int) -> Dict:
    """创建并启动下载任务，返回任务信息"""
    import re as _re
    url_match = _re.search(r'(https?://[^\s]+)', url)
    if not url_match:
        return {"error": "未识别到有效的网址链接"}

    clean_url = url_match.group(1).strip()
    platform = detect_platform(clean_url)
    task_id = str(uuid.uuid4())

    create_download_task(task_id, clean_url, user_id, platform=platform)
    cookies_file = get_cookies_file(platform)

    Thread(target=run_download, args=(task_id, clean_url, quality, cookies_file)).start()

    return {"status": "started", "task_id": task_id, "platform": platform}
