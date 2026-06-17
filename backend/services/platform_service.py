"""
平台检测与 Cookies 管理服务
"""
import os
import urllib.parse
from pathlib import Path
from typing import Optional

COOKIES_DIR = Path(os.getenv("APP_BASE_DIR", "/app")) / "cookies"


def detect_platform(url: str) -> str:
    """检测URL平台"""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "YouTube"
    elif "bilibili.com" in url_lower or "b23.tv" in url_lower:
        return "Bilibili"
    elif "douyin.com" in url_lower:
        return "Douyin"
    elif "kuaishou.com" in url_lower or "ksurl.cn" in url_lower:
        return "Kuaishou"
    elif "xiaohongshu.com" in url_lower or "xhslink.com" in url_lower:
        return "Xiaohongshu"
    elif "weibo.com" in url_lower or "weibo.cn" in url_lower:
        return "Weibo"
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return "X"
    elif "tiktok.com" in url_lower:
        return "TikTok"
    elif "instagram.com" in url_lower:
        return "Instagram"
    elif "music.163.com" in url_lower or "y.music.163" in url_lower:
        return "NeteaseMusic"
    elif "qq.com" in url_lower or "y.qq.com" in url_lower:
        return "QQMusic"
    elif "apple.co" in url_lower:
        return "AppleMusic"
    elif "telegram.org" in url_lower or "t.me" in url_lower:
        return "Telegram"
    elif "toutiao.com" in url_lower or "365yg.com" in url_lower:
        return "Toutiao"
    elif "weixin.qq.com" in url_lower or "channels.weixin" in url_lower:
        return "WechatVideo"
    return "Unknown"


def get_cookies_file(platform: str) -> Optional[str]:
    """获取平台对应的 Cookies 文件"""
    platform_map = {
        "youtube": ["youtube.txt"],
        "bilibili": ["bilibili.txt"],
        "douyin": ["douyin.txt"],
        "kuaishou": ["kuaishou.txt"],
        "xiaohongshu": ["xiaohongshu.txt"],
        "x": ["x.txt", "twitter.txt"],
        "qqmusic": ["qqmusic.txt"],
        "neteasemusic": ["neteasemusic.txt"],
        "weibo": ["weibo.txt"],
        "instagram": ["instagram.txt"],
        "tiktok": ["tiktok.txt"],
    }
    filenames = platform_map.get(platform.lower(), [])
    for filename in filenames:
        cookie_path = COOKIES_DIR / filename
        if cookie_path.exists():
            return str(cookie_path)
    return None


def get_platform_folder(platform: str) -> str:
    """为平台返回独立下载目录名"""
    name = (platform or 'other').strip().lower()
    return name if name else 'other'


def format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"
