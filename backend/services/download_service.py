"""
下载服务 - yt-dlp 下载逻辑
修复 YouTube / 快手 / 全平台下载
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
    create_download_task, update_download_task, get_download_task,
    update_daily_stats, get_setting
)
from backend.config import get_proxy_config, is_local_address, load_config
from backend.services.platform_service import detect_platform, get_cookies_file, get_platform_folder

BASE_DIR = Path(os.getenv("APP_BASE_DIR", "/app"))
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

DOWNLOAD_PROGRESS: Dict = {}

try:
    APP_CONFIG = load_config(BASE_DIR)
except Exception:
    APP_CONFIG = {}

# 通用 UA（Chrome 最新）
COMMON_UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/131.0.0.0 Safari/537.36'
)


def ytdl_progress_hook(d: Dict, task_id: str):
    """yt-dlp 进度回调"""
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0%')
        percent_clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str).strip().replace('%', '')
        try:
            percent = float(percent_clean)
        except Exception:
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
        _ws_notify(task_id, {"status": "downloading", "percent": percent, "speed": speed, "eta": eta, "filename": filename})

    elif d['status'] == 'finished':
        filename = d.get('filename', '')
        file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
        resolution = 'audio' if d.get('format_id', '').startswith('audio') else None

        DOWNLOAD_PROGRESS[task_id] = {
            "status": "completed", "percent": 100,
            "speed": "0 B/s", "eta": "00:00",
            "filename": os.path.basename(filename)
        }
        update_download_task(
            task_id, status="completed", progress=100,
            file_size=file_size, file_path=filename,
            resolution=resolution, finished_at=datetime.now().isoformat()
        )
        today = datetime.now().strftime("%Y-%m-%d")
        update_daily_stats(today, total_downloads=1, success_count=1, total_size=file_size)
        _ws_notify(task_id, {"status": "completed", "percent": 100, "filename": os.path.basename(filename)})


def _ws_notify(task_id: str, data: dict):
    """WebSocket 推送（静默失败）"""
    try:
        from backend.services.ws_manager import ws_manager
        import asyncio
        task = get_download_task(task_id)
        if task and task.get('user_id'):
            asyncio.run_coroutine_threadsafe(
                ws_manager.notify_download_progress(task_id, task['user_id'], data),
                asyncio.get_event_loop()
            )
    except Exception:
        pass


def _get_proxy(url: str) -> str:
    """获取代理地址"""
    proxy_enabled = get_setting('proxy_enabled', '0') == '1'
    proxy_cfg = get_proxy_config(APP_CONFIG)

    if not proxy_enabled:
        return ''

    http_proxy = get_setting('http_proxy') or proxy_cfg['http'] or os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY') or ''
    https_proxy = get_setting('https_proxy') or proxy_cfg['https'] or os.getenv('HTTPS_PROXY') or http_proxy or ''

    if proxy_cfg['mode'] == 'auto' and (http_proxy or https_proxy):
        hostname = urllib.parse.urlparse(url).hostname or ''
        if is_local_address(hostname, proxy_cfg['bypass_cidrs']):
            return ''

    return https_proxy or http_proxy or ''


def _build_ydl_opts(task_id: str, url: str, quality: str, cookies_file: Optional[str] = None) -> Dict:
    """构建 yt-dlp 配置"""
    platform = detect_platform(url)
    folder = DOWNLOAD_DIR / get_platform_folder(platform)
    folder.mkdir(parents=True, exist_ok=True)
    proxy = _get_proxy(url)

    # 基础配置
    ydl_opts = {
        'outtmpl': str(folder / '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: ytdl_progress_hook(d, task_id)],
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': COMMON_UA,
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        },
    }

    # 画质格式
    fmt_map = {
        "audio": ('bestaudio/best', None),
        "mp3": ('bestaudio/best', [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]),
        "m4a": ('bestaudio/best', [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}]),
        "1080p": ('bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best', 'mp4'),
        "720p": ('bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best', 'mp4'),
        "480p": ('bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best', 'mp4'),
        "360p": ('bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best', 'mp4'),
        "mp4": ('bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best', 'mp4'),
        "webm": ('bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo+bestaudio/best', 'webm'),
        "image": ('best', None),
    }

    fmt, merge_or_pp = fmt_map.get(quality, fmt_map["mp4"])
    ydl_opts['format'] = fmt
    if isinstance(merge_or_pp, str):
        ydl_opts['merge_output_format'] = merge_or_pp
    elif isinstance(merge_or_pp, list):
        ydl_opts['postprocessors'] = merge_or_pp

    # Cookies
    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    # ===== 平台专属配置 =====

    if platform == 'YouTube':
        ydl_opts = _apply_youtube_opts(ydl_opts, url, proxy)
    elif platform == 'Kuaishou':
        ydl_opts = _apply_kuaishou_opts(ydl_opts, url, proxy, cookies_file)
    elif platform == 'Bilibili':
        ydl_opts = _apply_bilibili_opts(ydl_opts, url, proxy)
    elif platform == 'Douyin':
        ydl_opts = _apply_douyin_opts(ydl_opts, url, proxy)
    elif platform == 'X':
        ydl_opts = _apply_twitter_opts(ydl_opts, url, proxy)
    else:
        # 通用：设置代理
        if proxy:
            ydl_opts['proxy'] = proxy

    return ydl_opts


def _apply_youtube_opts(ydl_opts: dict, url: str, proxy: str) -> dict:
    """YouTube 专属配置 - 应对 bot 检测"""
    # 使用 web_creator 客户端（更稳定，绕过 age-gate）
    ydl_opts['extractor_args'] = {
        'youtube': {
            'player_client': ['web_creator', 'mweb'],
        }
    }

    # YouTube 需要特殊 UA
    ydl_opts['http_headers'] = {
        'User-Agent': COMMON_UA,
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.youtube.com/',
    }

    # 代理
    if proxy:
        ydl_opts['proxy'] = proxy

    # PO Token 支持（从设置读取）
    po_token = get_setting('youtube_po_token', '')
    if po_token:
        ydl_opts['extractor_args']['youtube']['po_token'] = [po_token]

    # 访问者数据
    visitor_data = get_setting('youtube_visitor_data', '')
    if visitor_data:
        ydl_opts['extractor_args']['youtube']['visitor_data'] = [visitor_data]

    return ydl_opts


def _apply_kuaishou_opts(ydl_opts: dict, url: str, proxy: str, cookies_file: Optional[str]) -> dict:
    """快手专属配置"""
    ydl_opts['http_headers'] = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.kuaishou.com/',
        'Origin': 'https://www.kuaishou.com',
        'Cookie': '',
    }

    # 快手必须有 cookies 才能下载高清
    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file
    else:
        # 尝试从设置读取
        ks_cookies = get_setting('kuaishou_cookies', '')
        if ks_cookies:
            tmp_file = Path('/tmp/kuaishou_cookies.txt')
            tmp_file.write_text(ks_cookies)
            ydl_opts['cookiefile'] = str(tmp_file)

    # 快手使用移动端 UA 更稳定
    ydl_opts['extractor_args'] = {}

    # 代理
    if proxy:
        ydl_opts['proxy'] = proxy
    else:
        # 快手国内直连
        ydl_opts['proxy'] = ''

    return ydl_opts


def _apply_bilibili_opts(ydl_opts: dict, url: str, proxy: str) -> dict:
    """B站专属配置"""
    video_id = url.split('/')[-1].split('?')[0]
    ydl_opts['extractor_args'] = {'bilibili': {'ssr': ['yes']}}
    ydl_opts['http_headers'] = {
        'User-Agent': COMMON_UA,
        'Referer': f'https://www.bilibili.com/video/{video_id}',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    # B站国内直连
    ydl_opts['proxy'] = proxy if proxy else ''
    return ydl_opts


def _apply_douyin_opts(ydl_opts: dict, url: str, proxy: str) -> dict:
    """抖音专属配置"""
    ydl_opts['http_headers'] = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://www.douyin.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    ydl_opts['proxy'] = proxy if proxy else ''
    return ydl_opts


def _apply_twitter_opts(ydl_opts: dict, url: str, proxy: str) -> dict:
    """X/Twitter 专属配置"""
    ydl_opts['http_headers'] = {
        'User-Agent': COMMON_UA,
        'Referer': 'https://x.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    # 从设置读取 cookies
    x_cookies = get_setting('xtwitter_cookies', '')
    if x_cookies:
        tmp_file = Path('/tmp/xtwitter_cookies.txt')
        tmp_file.write_text(x_cookies)
        ydl_opts['cookiefile'] = str(tmp_file)

    if proxy:
        ydl_opts['proxy'] = proxy
    return ydl_opts


def run_download(task_id: str, url: str, quality: str, cookies_file: str = None):
    """执行下载"""
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

    # 第一次尝试
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            _extract_and_update(ydl, do_download=True)
        return  # 成功就返回
    except Exception as e:
        error_msg = str(e)
        _log_download_error(task_id, url, platform, error_msg, ydl_opts)

    # ===== 回退策略 =====
    _try_fallback_download(task_id, url, quality, ydl_opts, platform, error_msg)


def _log_download_error(task_id: str, url: str, platform: str, error: str, opts: dict):
    """记录下载错误日志"""
    import logging
    logger = logging.getLogger("bosco")
    logger.warning(f"[下载失败] platform={platform} url={url[:80]}")
    logger.warning(f"[下载失败] error={error[:300]}")
    if platform == 'YouTube':
        logger.info(f"[YouTube] player_client={opts.get('extractor_args', {}).get('youtube', {}).get('player_client', 'default')}")


def _try_fallback_download(task_id: str, url: str, quality: str, ydl_opts: dict, platform: str, original_error: str):
    """回退下载策略"""
    fallback_errors = [f"原始错误: {original_error[:200]}"]

    # 平台专属回退
    if platform == 'YouTube':
        fallback_formats = _youtube_fallback_formats()
    elif platform == 'Kuaishou':
        fallback_formats = ['best', 'bestvideo+bestaudio/best']
    else:
        fallback_formats = [
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'bestvideo+bestaudio/best',
            'best[ext=mp4]/best',
            'best'
        ]

    for fmt in fallback_formats:
        try:
            attempt_opts = dict(ydl_opts)
            attempt_opts['format'] = fmt
            if 'audio' not in fmt:
                attempt_opts['merge_output_format'] = 'mp4'
            # 移除可能干扰的 extractor_args
            if platform == 'YouTube':
                attempt_opts.setdefault('extractor_args', {})['youtube'] = {'player_client': ['web', 'mweb']}

            with yt_dlp.YoutubeDL(attempt_opts) as ydl_retry:
                info = ydl_retry.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                resource_type = 'audio' if info.get('acodec') or info.get('ext') in ('mp3', 'm4a') else 'video'
                update_download_task(task_id, title=title, platform=platform, resource_type=resource_type)
                return  # 成功
        except Exception as ee:
            fallback_errors.append(f"{fmt}: {str(ee)[:150]}")

    # 最终尝试：逐个 format_id
    try:
        probe_opts = dict(ydl_opts)
        probe_opts.update({'quiet': True, 'no_warnings': True, 'skip_download': True})
        with yt_dlp.YoutubeDL(probe_opts) as ydl_probe:
            info_probe = ydl_probe.extract_info(url, download=False)

        formats = info_probe.get('formats', []) if isinstance(info_probe, dict) else []
        sorted_formats = sorted(formats, key=lambda f: (int(f.get('height') or 0), int(f.get('tbr') or 0)), reverse=True)

        for fmt_info in sorted_formats:
            fmt_id = fmt_info.get('format_id')
            if not fmt_id:
                continue
            try:
                attempt_opts = dict(ydl_opts)
                attempt_opts['format'] = fmt_id
                if fmt_info.get('vcodec') not in (None, 'none'):
                    attempt_opts['merge_output_format'] = 'mp4'
                with yt_dlp.YoutubeDL(attempt_opts) as ydl_retry2:
                    info = ydl_retry2.extract_info(url, download=True)
                    update_download_task(task_id, title=info.get('title', 'Unknown'), platform=platform)
                    return
            except Exception as ee:
                fallback_errors.append(f"fmt_id={fmt_id}: {str(ee)[:100]}")
    except Exception as probe_exc:
        fallback_errors.append(f"探测失败: {str(probe_exc)[:150]}")

    # 全部失败
    err_msg = "下载失败（所有回退均失败）\n" + "\n".join(fallback_errors[-5:])
    DOWNLOAD_PROGRESS[task_id] = {"status": "failed", "error": err_msg}
    update_download_task(task_id, status="failed", error_message=err_msg)
    today = datetime.now().strftime("%Y-%m-%d")
    update_daily_stats(today, total_downloads=1, fail_count=1)
    _ws_notify(task_id, {"status": "failed", "error": err_msg[:200]})


def _youtube_fallback_formats():
    """YouTube 回退格式列表"""
    return [
        'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best',
        'bestvideo[height<=720]+bestaudio/best',
        'best[ext=mp4]/best',
        'best',
    ]


def start_download_task(url: str, quality: str, user_id: int) -> Dict:
    """创建并启动下载任务"""
    url_match = re.search(r'(https?://[^\s]+)', url)
    if not url_match:
        return {"error": "未识别到有效的网址链接"}

    clean_url = url_match.group(1).strip()
    platform = detect_platform(clean_url)
    task_id = str(uuid.uuid4())

    create_download_task(task_id, clean_url, user_id, platform=platform)
    cookies_file = get_cookies_file(platform)

    Thread(target=run_download, args=(task_id, clean_url, quality, cookies_file), daemon=True).start()

    return {"status": "started", "task_id": task_id, "platform": platform}
