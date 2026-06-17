"""
统一 Bot 网关 - 处理所有平台（Telegram/QQ/微信）的消息协议
提供统一的命令解析、任务分发、权限绑定、进度推送
"""

import re
import uuid
import logging
from typing import Dict, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from backend.admin.db import (
    get_setting, verify_user, create_download_task,
    get_download_tasks, get_download_task, get_download_history,
    get_subscriptions, get_statistics
)
from backend.services.download_service import start_download_task, DOWNLOAD_PROGRESS
from backend.services.platform_service import detect_platform

logger = logging.getLogger("bosco")


class BotPlatform(str, Enum):
    TELEGRAM = "telegram"
    QQ = "qq"
    WECHAT = "wechat"


@dataclass
class BotMessage:
    """统一的消息格式"""
    platform: BotPlatform
    chat_id: str            # 群组/私聊 ID
    user_id: str            # 平台用户 ID
    username: str           # 平台用户名
    text: str               # 消息内容
    message_id: str = ""    # 平台消息 ID（用于编辑/回复）
    is_group: bool = False  # 是否群组消息


@dataclass
class BotResponse:
    """统一的响应格式"""
    text: str = ""
    parse_mode: str = "html"  # html / markdown
    reply_to: str = ""        # 回复的消息 ID
    edit_message: str = ""    # 要编辑的消息 ID
    silent: bool = False      # 静音发送
    keyboard: Any = None      # InlineKeyboard 按钮


class BotGateway:
    """统一 Bot 网关"""

    def __init__(self):
        # 平台适配器注册表
        self._adapters: Dict[BotPlatform, Any] = {}
        # 用户绑定表：platform:user_id -> system_user_id
        self._user_bindings: Dict[str, int] = {}
        # 命令注册表
        self._commands: Dict[str, Callable] = {}
        # URL 正则
        self._url_pattern = re.compile(r'(https?://[^\s<>"\']+|www\.[^\s<>"\']+)')

        # 注册默认命令
        self._register_default_commands()

    def register_adapter(self, platform: BotPlatform, adapter: Any):
        """注册平台适配器"""
        self._adapters[platform] = adapter
        logger.info(f"Bot 网关注册平台适配器: {platform.value}")

    def _register_default_commands(self):
        """注册默认命令"""
        self._commands = {
            '/start': self._cmd_start,
            '/help': self._cmd_help,
            '/dl': self._cmd_download,
            '/download': self._cmd_download,
            '/list': self._cmd_list,
            '/status': self._cmd_status,
            '/history': self._cmd_history,
            '/stats': self._cmd_stats,
            '/bind': self._cmd_bind,
        }

    async def handle_message(self, msg: BotMessage) -> Optional[BotResponse]:
        """处理收到的消息"""
        logger.info(f"[Bot] 收到 {msg.platform.value} 消息: user={msg.user_id} text={msg.text[:50]}")

        # 群组消息需要 @ 机器人或以 / 开头
        if msg.is_group and not msg.text.startswith('/') and not self._has_url(msg.text):
            return None

        # 命令处理
        if msg.text.startswith('/'):
            parts = msg.text.strip().split(maxsplit=1)
            cmd = parts[0].lower().split('@')[0]  # 去掉 @botname
            args = parts[1] if len(parts) > 1 else ""

            handler = self._commands.get(cmd)
            if handler:
                return await handler(msg, args)
            return BotResponse(text=f"❓ 未知命令: {cmd}\n\n使用 /help 查看可用命令")

        # 非命令消息：检查是否有 URL
        urls = self._url_pattern.findall(msg.text)
        if urls:
            url = urls[0]
            if url.startswith('www.'):
                url = 'https://' + url
            return await self._do_download(msg, url, "best")

        return BotResponse(text="💡 发送链接即可下载，或使用 /help 查看命令")

    def _has_url(self, text: str) -> bool:
        return bool(self._url_pattern.search(text))

    # ==================== 命令实现 ====================

    async def _cmd_start(self, msg: BotMessage, args: str) -> BotResponse:
        return BotResponse(
            text="👋 <b>欢迎使用 Bosco Tsang 下载 Bot！</b>\n\n"
                 "📥 <b>使用方法：</b>\n"
                 "• 直接发送视频/音频链接即可下载\n"
                 "• 或使用 /dl <链接> [画质]\n\n"
                 "📝 <b>可用命令：</b>\n"
                 "/dl <链接> - 下载\n"
                 "/list - 查看任务列表\n"
                 "/history - 下载历史\n"
                 "/stats - 统计信息\n"
                 "/status - 系统状态\n"
                 "/bind <用户名> <密码> - 绑定账户\n"
                 "/help - 显示帮助"
        )

    async def _cmd_help(self, msg: BotMessage, args: str) -> BotResponse:
        return BotResponse(
            text="📖 <b>帮助信息</b>\n\n"
                 "✅ <b>下载命令：</b>\n"
                 "/dl <链接> [画质] - 下载视频/音频\n"
                 "  画质选项: best, 1080p, 720p, audio, mp3\n\n"
                 "✅ <b>查询命令：</b>\n"
                 "/list - 当前下载任务\n"
                 "/history - 下载历史\n"
                 "/stats - 下载统计\n"
                 "/status - 系统状态\n\n"
                 "✅ <b>账户命令：</b>\n"
                 "/bind <用户名> <密码> - 绑定系统账户\n\n"
                 "✅ <b>支持平台：</b>\n"
                 "YouTube, Bilibili, 抖音, Twitter/X,\n"
                 "Instagram, TikTok 等 3000+ 平台"
        )

    async def _cmd_download(self, msg: BotMessage, args: str) -> BotResponse:
        """下载命令：/dl <url> [quality]"""
        if not args:
            return BotResponse(text="❌ 请提供下载链接\n\n用法: /dl <链接> [画质]\n画质: best, 1080p, 720p, audio, mp3")

        parts = args.strip().split()
        url = parts[0]
        quality = parts[1] if len(parts) > 1 else "best"

        # 验证 URL
        if not self._url_pattern.search(url):
            return BotResponse(text="❌ 未识别到有效的网址链接")

        return await self._do_download(msg, url, quality)

    async def _do_download(self, msg: BotMessage, url: str, quality: str) -> BotResponse:
        """执行下载"""
        # 检查用户绑定
        system_user_id = self._get_bound_user(msg.platform, msg.user_id)
        if not system_user_id:
            return BotResponse(text="❌ 请先绑定系统账户\n\n使用 /bind <用户名> <密码> 进行绑定")

        # 发起下载
        result = start_download_task(url, quality, system_user_id)
        if "error" in result:
            return BotResponse(text=f"❌ {result['error']}")

        platform = detect_platform(url)
        return BotResponse(
            text=f"📥 <b>已创建下载任务</b>\n\n"
                 f"🔗 {url}\n"
                 f"📱 平台: {platform}\n"
                 f"🎯 画质: {quality}\n"
                 f"🆔 {result['task_id'][:8]}...\n\n"
                 f"⏳ 下载中，完成后自动通知"
        )

    async def _cmd_list(self, msg: BotMessage, args: str) -> BotResponse:
        """查看任务列表"""
        system_user_id = self._get_bound_user(msg.platform, msg.user_id)
        if not system_user_id:
            return BotResponse(text="❌ 请先绑定系统账户\n\n使用 /bind <用户名> <密码>")

        tasks = get_download_tasks(user_id=system_user_id, limit=10)
        if not tasks:
            return BotResponse(text="📋 暂无下载任务")

        lines = ["📋 <b>下载任务列表</b>\n"]
        for t in tasks:
            status_icon = {"completed": "✅", "downloading": "⏳", "failed": "❌", "pending": "⏸"}.get(t['status'], "❓")
            title = t.get('title') or t.get('url', '')[:40]
            progress = t.get('progress', 0)
            if t['status'] == 'downloading':
                lines.append(f"{status_icon} {title}\n   进度: {progress:.1f}%")
            else:
                lines.append(f"{status_icon} {title}")

        return BotResponse(text="\n".join(lines))

    async def _cmd_history(self, msg: BotMessage, args: str) -> BotResponse:
        """下载历史"""
        system_user_id = self._get_bound_user(msg.platform, msg.user_id)
        if not system_user_id:
            return BotResponse(text="❌ 请先绑定系统账户")

        history = get_download_history(user_id=system_user_id, limit=10)
        if not history:
            return BotResponse(text="📜 暂无下载历史")

        lines = ["📜 <b>下载历史</b>\n"]
        for h in history:
            status_icon = {"completed": "✅", "failed": "❌"}.get(h['status'], "❓")
            title = h.get('title') or h.get('url', '')[:40]
            lines.append(f"{status_icon} {title}")

        return BotResponse(text="\n".join(lines))

    async def _cmd_stats(self, msg: BotMessage, args: str) -> BotResponse:
        """统计信息"""
        stats = get_statistics(7)
        overview = stats.get('overview', {})
        return BotResponse(
            text="📊 <b>下载统计</b>\n\n"
                 f"📥 总任务: {overview.get('total_tasks', 0)}\n"
                 f"✅ 成功: {overview.get('success_count', 0)}\n"
                 f"❌ 失败: {overview.get('fail_count', 0)}\n"
                 f"🎬 视频: {overview.get('video_count', 0)}\n"
                 f"🎵 音频: {overview.get('audio_count', 0)}\n"
                 f"📷 图片: {overview.get('image_count', 0)}"
        )

    async def _cmd_status(self, msg: BotMessage, args: str) -> BotResponse:
        """系统状态"""
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return BotResponse(
            text="💻 <b>系统状态</b>\n\n"
                 f"🔲 CPU: {cpu}%\n"
                 f"💾 内存: {mem.percent}% ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)\n"
                 f"💿 磁盘: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
        )

    async def _cmd_bind(self, msg: BotMessage, args: str) -> BotResponse:
        """绑定系统账户"""
        if not args:
            return BotResponse(text="❌ 用法: /bind <用户名> <密码>")

        parts = args.strip().split(maxsplit=1)
        if len(parts) < 2:
            return BotResponse(text="❌ 用法: /bind <用户名> <密码>")

        username, password = parts[0], parts[1]
        user = verify_user(username, password)
        if not user:
            return BotResponse(text="❌ 用户名或密码错误")

        # 保存绑定
        binding_key = f"{msg.platform.value}:{msg.user_id}"
        self._user_bindings[binding_key] = user['id']

        # 也存到数据库
        from backend.admin.db import set_setting
        set_setting(f"bot_binding_{binding_key}", str(user['id']))

        return BotResponse(text=f"✅ 绑定成功！\n\n👤 用户: {user['username']}\n🎭 角色: {user['role']}")

    # ==================== 工具方法 ====================

    def _get_bound_user(self, platform: BotPlatform, platform_user_id: str) -> Optional[int]:
        """获取绑定的系统用户 ID"""
        binding_key = f"{platform.value}:{platform_user_id}"

        # 先查内存缓存
        if binding_key in self._user_bindings:
            return self._user_bindings[binding_key]

        # 再查数据库
        from backend.admin.db import get_setting
        user_id_str = get_setting(f"bot_binding_{binding_key}")
        if user_id_str:
            try:
                user_id = int(user_id_str)
                self._user_bindings[binding_key] = user_id
                return user_id
            except ValueError:
                pass
        return None

    async def send_progress_update(self, task_id: str):
        """推送下载进度到所有已绑定的平台（由下载钩子调用）"""
        progress = DOWNLOAD_PROGRESS.get(task_id)
        if not progress:
            return

        task = get_download_task(task_id)
        if not task:
            return

        user_id = task.get('user_id')
        if not user_id:
            return

        # 查找该用户绑定的所有 bot 平台
        for binding_key, bound_user_id in self._user_bindings.items():
            if bound_user_id != user_id:
                continue

            platform_str, platform_user_id = binding_key.split(':', 1)
            try:
                platform = BotPlatform(platform_str)
            except ValueError:
                continue

            adapter = self._adapters.get(platform)
            if not adapter or not hasattr(adapter, 'send_message'):
                continue

            if progress['status'] == 'completed':
                text = (f"✅ <b>下载完成！</b>\n\n"
                       f"📁 {progress.get('filename', '未知')}\n"
                       f"🔗 {task.get('url', '')[:60]}")
            elif progress['status'] == 'downloading':
                percent = progress.get('percent', 0)
                if int(percent) % 20 != 0:  # 每 20% 推送一次
                    continue
                text = (f"⏳ <b>下载中...</b>\n\n"
                       f"📊 进度: {percent:.1f}%\n"
                       f"🚀 速度: {progress.get('speed', 'N/A')}\n"
                       f"⏰ 剩余: {progress.get('eta', 'N/A')}")
            elif progress['status'] == 'failed':
                text = (f"❌ <b>下载失败</b>\n\n"
                       f"🔗 {task.get('url', '')[:60]}\n"
                       f"💬 {progress.get('error', '未知错误')[:200]}")
            else:
                continue

            try:
                await adapter.send_message(platform_user_id, text)
            except Exception as e:
                logger.error(f"推送进度失败 [{platform.value}]: {e}")


# 全局网关实例
bot_gateway = BotGateway()
