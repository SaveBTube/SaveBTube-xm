"""
Telegram Bot 下载处理器
处理 Telegram 消息和下载任务
"""
import asyncio
import httpx
import re
import uuid
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from backend.admin.db import (
    get_setting, 
    create_download_task, 
    get_telegram_user,
    create_telegram_user,
    update_download_task
)

# 日志记录器
logger = logging.getLogger("bosco")

def write_log(level: str, message: str):
    """写入日志"""
    if level == "ERROR":
        logger.error(message)
    elif level == "WARN":
        logger.warning(message)
    elif level == "DEBUG":
        logger.debug(message)
    else:
        logger.info(message)

# Telegram Bot API 基础 URL
TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"

# URL 正则表达式
URL_PATTERN = re.compile(r'(https?://[^\s<>"\']+|www\.[^\s<>"\']+)')


class TelegramBotHandler:
    """Telegram Bot 处理器"""
    
    def __init__(self):
        self.running = False
        self.offset = 0
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(
            connect=10.0,     # 连接超时 10 秒
            read=60.0,         # 读取超时 60 秒（需要大于长轮询 timeout）
            write=10.0,        # 写入超时 10 秒
            pool=10.0          # 连接池超时 10 秒
        ))
    
    async def start(self):
        """启动 Bot 轮询"""
        self.running = True
        write_log("INFO", "Telegram Bot 处理器已启动")
        
        while self.running:
            try:
                # 检查 Bot Token 是否配置
                bot_token = get_setting('telegram_bot_token', '')
                telegram_enabled = get_setting('telegram_login_enabled', '0')
                
                if not bot_token or telegram_enabled != '1':
                    await asyncio.sleep(10)
                    continue
                
                # 获取更新
                await self.get_updates(bot_token)
                await asyncio.sleep(3)  # 3 秒轮询间隔，避免 409 冲突
                
            except Exception as e:
                write_log("ERROR", f"Telegram Bot 轮询错误: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """停止 Bot 轮询"""
        self.running = False
        try:
            await self.client.aclose()
        except Exception:
            pass
        write_log("INFO", "Telegram Bot 处理器已停止")
    
    async def get_updates(self, bot_token: str):
        """获取 Telegram 更新"""
        url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/getUpdates"
        params = {
            'offset': self.offset,
            'timeout': 10,  # Telegram 长轮询 10 秒
            'allowed_updates': ['message']
        }
        
        write_log("DEBUG", f"请求 URL: {url}")
        write_log("DEBUG", f"请求参数: {params}")
        
        try:
            response = await self.client.get(url, params=params)
            
            # 记录 HTTP 状态码
            if response.status_code != 200:
                write_log("WARN", f"Telegram API 返回状态码: {response.status_code}")
                write_log("DEBUG", f"响应内容: {response.text[:200]}")
                
                # 处理常见错误
                if response.status_code == 401:
                    write_log("ERROR", "Telegram Bot Token 无效或已过期")
                elif response.status_code == 404:
                    write_log("ERROR", "Telegram API 端点不存在")
                elif response.status_code == 409:
                    write_log("WARN", "Telegram 409 冲突：存在其他 getUpdates 请求，等待重试...")
                    await asyncio.sleep(10)
                elif response.status_code == 429:
                    write_log("WARN", "Telegram API 请求过于频繁，等待中...")
                    await asyncio.sleep(30)
                return
            
            data = response.json()
            
            # 检查 API 响应
            if not data.get('ok'):
                error_msg = data.get('description', '未知错误')
                write_log("ERROR", f"Telegram API 错误: {error_msg}")
                return
            
            # 处理更新
            if data.get('result'):
                for update in data['result']:
                    await self.process_update(update, bot_token)
                self.offset = data['result'][-1]['update_id'] + 1
                
        except httpx.TimeoutException:
            write_log("WARN", "Telegram API 请求超时")
        except httpx.ConnectError as e:
            write_log("ERROR", f"无法连接到 Telegram API: {e}")
        except httpx.HTTPError as e:
            write_log("ERROR", f"Telegram HTTP 错误: {e}")
        except Exception as e:
            import traceback
            # 详细的错误信息
            error_type = type(e).__name__
            error_module = type(e).__module__
            error_str = str(e) if str(e) else "(空错误信息)"
            error_repr = repr(e)
            
            write_log("ERROR", f"获取 Telegram 更新失败: [{error_type}] {error_str}")
            write_log("DEBUG", f"异常类型: {error_module}.{error_type}")
            write_log("DEBUG", f"异常表示: {error_repr}")
            write_log("DEBUG", f"错误堆栈:\n{traceback.format_exc()}")
    
    async def process_update(self, update: dict, bot_token: str):
        """处理 Telegram 更新"""
        message = update.get('message')
        if not message:
            return
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        message_id = message.get('message_id')
        
        if not chat_id or not text:
            return
        
        # 检查用户权限
        allowed_user_ids = get_setting('telegram_allowed_user_ids', '')
        if allowed_user_ids:
            allowed_ids = [uid.strip() for uid in allowed_user_ids.split(',')]
            if str(chat_id) not in allowed_ids:
                await self.send_message(
                    bot_token, 
                    chat_id, 
                    "❌ 您没有权限使用此 Bot"
                )
                return
        
        # 处理命令
        if text.startswith('/'):
            await self.handle_command(bot_token, chat_id, text, message_id)
        else:
            # 处理普通消息（查找 URL）
            await self.handle_message(bot_token, chat_id, text, message_id)
    
    async def handle_command(self, bot_token: str, chat_id: int, text: str, message_id: int):
        """处理命令"""
        command = text.split()[0].lower()
        
        if command == '/start':
            await self.send_message(
                bot_token,
                chat_id,
                "👋 欢迎使用 Bosco Tsang 下载 Bot！\n\n"
                "📥 使用方法：\n"
                "• 直接发送视频/音频链接即可下载\n"
                "• 支持 YouTube、Bilibili、抖音等平台\n\n"
                "📝 可用命令：\n"
                "/start - 显示此帮助信息\n"
                "/help - 显示帮助\n"
                "/status - 查看下载状态"
            )
        
        elif command == '/help':
            await self.send_message(
                bot_token,
                chat_id,
                "📖 使用帮助\n\n"
                "✅ 支持的命令：\n"
                "/start - 开始使用\n"
                "/help - 显示帮助\n"
                "/status - 查看下载状态\n\n"
                "✅ 支持的链接：\n"
                "• YouTube: https://youtube.com/watch?v=...\n"
                "• Bilibili: https://bilibili.com/video/...\n"
                "• 抖音: https://douyin.com/video/...\n"
                "• 以及 3000+ 其他平台\n\n"
                "💡 提示：直接发送链接即可开始下载"
            )
        
        elif command == '/status':
            await self.send_message(
                bot_token,
                chat_id,
                "📊 下载状态\n\n"
                "当前没有活跃的下载任务。\n"
                "发送链接开始新的下载！"
            )
        
        else:
            await self.send_message(
                bot_token,
                chat_id,
                f"❓ 未知命令: {command}\n\n"
                "使用 /help 查看可用命令"
            )
    
    async def handle_message(self, bot_token: str, chat_id: int, text: str, message_id: int):
        """处理普通消息"""
        # 查找 URL
        urls = URL_PATTERN.findall(text)
        
        if not urls:
            await self.send_message(
                bot_token,
                chat_id,
                "❌ 未找到有效的链接\n\n"
                "请发送视频/音频链接，例如：\n"
                "https://youtube.com/watch?v=..."
            )
            return
        
        # 处理第一个 URL
        url = urls[0]
        if url.startswith('www.'):
            url = 'https://' + url
        
        await self.start_download(bot_token, chat_id, url)
    
    async def start_download(self, bot_token: str, chat_id: int, url: str):
        """开始下载"""
        # 发送开始消息
        start_msg = await self.send_message(
            bot_token,
            chat_id,
            f"📥 开始下载...\n\n"
            f"🔗 {url}\n\n"
            "⏳ 请稍候..."
        )
        
        # 创建下载任务
        task_id = str(uuid.uuid4())
        platform = self.detect_platform(url)
        
        create_download_task(task_id, url, platform=platform)
        
        # 更新消息
        await self.edit_message(
            bot_token,
            chat_id,
            start_msg['message_id'],
            f"📥 已创建下载任务\n\n"
            f"🔗 {url}\n"
            f"📱 平台: {platform}\n"
            f"🆔 任务ID: {task_id[:8]}...\n\n"
            "⏳ 正在下载中..."
        )
        
        # 启动下载线程
        import threading
        from backend.config import get_cookies_file
        
        def run_download():
            """在后台线程中运行下载"""
            try:
                import subprocess
                import yt_dlp
                
                cookies_file = get_cookies_file(platform)
                
                ydl_opts = {
                    'outtmpl': str(Path('/app/downloads') / f'{task_id}.%(ext)s'),
                    'progress_hooks': [lambda d: self.download_progress_hook(d, task_id, bot_token, chat_id)],
                }
                
                if cookies_file:
                    ydl_opts['cookiefile'] = str(cookies_file)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 下载完成
                asyncio.run(self.download_complete(
                    bot_token, 
                    chat_id, 
                    task_id, 
                    url, 
                    platform
                ))
                
            except Exception as e:
                write_log("ERROR", f"下载失败: {e}")
                asyncio.run(self.send_message(
                    bot_token,
                    chat_id,
                    f"❌ 下载失败\n\n"
                    f"🔗 {url}\n\n"
                    f"错误: {str(e)}"
                ))
        
        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()
    
    def download_progress_hook(self, d: dict, task_id: str, bot_token: str, chat_id: int):
        """下载进度回调"""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0) or 0
            percent = d.get('_percent_str', '0%')
            speed_str = d.get('_speed_str', 'N/A')
            
            if total > 0:
                progress = (downloaded / total) * 100
                # 每 10% 更新一次
                if int(progress) % 10 == 0:
                    asyncio.run(self.send_message(
                        bot_token,
                        chat_id,
                        f"📥 下载中...\n\n"
                        f"进度: {percent}\n"
                        f"速度: {speed_str}\n"
                        f"大小: {self.format_size(downloaded)} / {self.format_size(total)}",
                        disable_notification=True
                    ))
    
    async def download_complete(self, bot_token: str, chat_id: int, task_id: str, url: str, platform: str):
        """下载完成通知"""
        await self.send_message(
            bot_token,
            chat_id,
            f"✅ 下载完成！\n\n"
            f"🔗 {url}\n"
            f"📱 平台: {platform}\n"
            f"🆔 任务ID: {task_id[:8]}...\n\n"
            "📁 文件已保存到服务器\n"
            "请在 Web 界面的文件管理中查看"
        )
    
    async def send_message(self, bot_token: str, chat_id: int, text: str, disable_notification: bool = False, reply_markup: dict = None) -> dict:
        """发送消息"""
        url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_notification': disable_notification
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        try:
            response = await self.client.post(url, json=data)
            if response.status_code == 200:
                return response.json().get('result', {})
            else:
                write_log("ERROR", f"发送消息失败: {response.text}")
                return {}
        except Exception as e:
            write_log("ERROR", f"发送消息异常: {e}")
            return {}
    
    async def edit_message(self, bot_token: str, chat_id: int, message_id: int, text: str):
        """编辑消息"""
        url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/editMessageText"
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        try:
            response = await self.client.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            write_log("ERROR", f"编辑消息异常: {e}")
            return False
    
    def detect_platform(self, url: str) -> str:
        """检测平台"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'bilibili.com' in url:
            return 'bilibili'
        elif 'douyin.com' in url:
            return 'douyin'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'xtwitter'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'tiktok.com' in url:
            return 'tiktok'
        else:
            return 'unknown'
    
    def format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"


# 全局 Bot 处理器实例
bot_handler = TelegramBotHandler()
