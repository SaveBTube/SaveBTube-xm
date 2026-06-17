"""
X/Twitter 专用下载处理器
支持视频、GIF、图片下载
"""
import os
import re
import yt_dlp
from pathlib import Path
from typing import Optional, Dict, List
from backend.admin.db import get_setting

# X/Twitter URL 正则表达式
TWITTER_URL_PATTERN = re.compile(
    r'(https?://(?:twitter|x)\.com/[^\s]+)'
)

# 图片 URL 模式
IMAGE_URL_PATTERN = re.compile(
    r'(https?://pbs\.twimg\.com/media/[^\s]+)'
)


class TwitterDownloader:
    """X/Twitter 下载器"""
    
    def __init__(self):
        self.download_dir = Path('/app/downloads/x')
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cookies(self) -> Optional[str]:
        """获取 X/Twitter Cookies"""
        # 优先从设置中获取
        cookies_str = get_setting('xtwitter_cookies', '')
        if cookies_str:
            # 写入临时文件
            cookies_file = Path('/tmp/xtwitter_cookies.txt')
            cookies_file.write_text(cookies_str)
            return str(cookies_file)
        
        # 其次从 cookies 目录获取
        cookies_file = Path('/app/cookies/x.txt')
        if cookies_file.exists():
            return str(cookies_file)
        
        return None
    
    def get_download_options(self) -> Dict:
        """获取下载选项"""
        return {
            'download_video': get_setting('xtwitter_download_video', '1') == '1',
            'download_images': get_setting('xtwitter_download_images', '1') == '1',
            'best_quality': get_setting('xtwitter_best_quality', '1') == '1',
            'quality': get_setting('xtwitter_quality', 'best')
        }
    
    def download_tweet(self, url: str, progress_hook=None) -> List[str]:
        """下载推文内容（视频/图片）"""
        options = self.get_download_options()
        cookies_file = self.get_cookies()
        
        downloaded_files = []
        
        # 下载视频
        if options['download_video']:
            video_files = self.download_video(url, cookies_file, progress_hook)
            downloaded_files.extend(video_files)
        
        # 下载图片
        if options['download_images']:
            image_files = self.download_images(url, cookies_file)
            downloaded_files.extend(image_files)
        
        return downloaded_files
    
    def download_video(self, url: str, cookies_file: Optional[str], progress_hook=None) -> List[str]:
        """下载视频"""
        ydl_opts = {
            'outtmpl': str(self.download_dir / '%(title)s_%(id)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best' if self.get_download_options()['best_quality'] else 'best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        
        if progress_hook:
            ydl_opts['progress_hooks'] = [progress_hook]
        
        # 质量限制
        quality = self.get_download_options()['quality']
        if quality != 'best':
            ydl_opts['format'] = f'bestvideo[height<={quality.replace("p", "")}]+bestaudio/best[height<={quality.replace("p", "")}]'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    # 获取下载的文件路径
                    filename = ydl.prepare_filename(info)
                    if Path(filename).exists():
                        return [filename]
            return []
        except Exception as e:
            print(f"视频下载失败: {e}")
            return []
    
    def download_images(self, url: str, cookies_file: Optional[str]) -> List[str]:
        """下载图片"""
        downloaded_files = []
        
        try:
            # 使用 yt-dlp 提取图片 URL
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'simulate': True,  # 仅提取信息，不下载
            }
            
            if cookies_file:
                ydl_opts['cookiefile'] = cookies_file
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info and 'entries' in info:
                    # 处理多条推文
                    entries = info['entries']
                elif info:
                    # 单条推文
                    entries = [info]
                else:
                    return []
                
                for entry in entries:
                    if not entry:
                        continue
                    
                    # 提取图片 URL
                    if 'entries' in entry:
                        # 嵌套结构
                        for sub_entry in entry.get('entries', []):
                            if sub_entry:
                                images = self.extract_images_from_entry(sub_entry)
                                downloaded_files.extend(images)
                    else:
                        images = self.extract_images_from_entry(entry)
                        downloaded_files.extend(images)
        
        except Exception as e:
            print(f"图片提取失败: {e}")
        
        return downloaded_files
    
    def extract_images_from_entry(self, entry: Dict) -> List[str]:
        """从条目中提取图片并下载"""
        downloaded_files = []
        
        try:
            # 尝试从不同位置获取图片
            image_urls = []
            
            # 方式 1: 从 thumbnails 获取
            if 'thumbnails' in entry:
                for thumb in entry['thumbnails']:
                    if 'url' in thumb:
                        image_urls.append(thumb['url'])
            
            # 方式 2: 从 description 或 info 中提取
            description = entry.get('description', '') or entry.get('title', '')
            if description:
                # 查找图片 URL
                urls = IMAGE_URL_PATTERN.findall(description)
                image_urls.extend(urls)
            
            # 方式 3: 从 extended_entities 获取（Twitter API 结构）
            if 'extended_entities' in entry:
                media = entry['extended_entities'].get('media', [])
                for m in media:
                    if m.get('type') == 'photo':
                        image_urls.append(m.get('media_url_https') or m.get('media_url'))
            
            # 下载图片
            for idx, image_url in enumerate(set(image_urls)):  # 去重
                if image_url and ('twimg.com' in image_url or 'pbs.twimg.com' in image_url):
                    # 获取原始尺寸图片
                    original_url = image_url.replace(':small', ':orig').replace(':medium', ':orig').replace(':large', ':orig')
                    
                    # 下载图片
                    filename = self.download_single_image(original_url, idx)
                    if filename:
                        downloaded_files.append(filename)
        
        except Exception as e:
            print(f"提取图片失败: {e}")
        
        return downloaded_files
    
    def download_single_image(self, url: str, index: int) -> Optional[str]:
        """下载单张图片"""
        try:
            import httpx
            
            # 生成文件名
            filename = self.download_dir / f'image_{index}_{Path(url).name.split("?")[0]}'
            
            # 下载
            cookies_file = self.get_cookies()
            headers = {}
            
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                if cookies_file:
                    # 读取 cookies 并添加到 headers
                    cookies_text = Path(cookies_file).read_text()
                    # 简化的 cookies 处理
                    pass
                
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    # 保存图片
                    filename.write_bytes(response.content)
                    return str(filename)
            
            return None
        
        except Exception as e:
            print(f"下载图片失败: {e}")
            return None
    
    def is_twitter_url(self, url: str) -> bool:
        """检查是否为 X/Twitter URL"""
        return bool(TWITTER_URL_PATTERN.search(url))


# 全局下载器实例
twitter_downloader = TwitterDownloader()
