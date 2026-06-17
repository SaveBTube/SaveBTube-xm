"""
Telegram Bot 处理器 - 支持 Webhook 和轮询双模式
"""
import asyncio
import httpx
import re
import uuid
import logging
import hashlib
import hmac
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
from fastapi import Request

from backend.admin.db import (
    get_setting, create_download_task, update_download_task,
    get_telegram_user, create_telegram_user
)
from backend.services.bot_gateway import bot_gateway, BotMessage, BotPlatform, BotResponse

logger = logging.getLogger("bosco")

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"
URL_PATTERN = re.compile(r'(https?://[^\s<>"\']+|www\.[^\s<>"\']+)')


class TelegramBotHandler:
    """Telegram Bot 处理器（Webhook + 轮询双模式）"""

    def __init__(self):
        self.running = False
        self.offset = 0
        self.mode = "polling"  # polling / webhook
        self._client: Optional[httpx.AsyncClient] = None
        self._webhook_url = ""
        self._last_update_ids: set = set()  # 去重

    async def start(self):
        """启动 Bot（自动选择模式）"""
        self.running = True
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(
            connect=10.0, read=60.0, write=10.0, pool=10.0
        ))

        # 检查是否配置了 Webhook URL
        self._webhook_url = get_setting('telegram_webhook_url', '')
        if self._webhook_url:
            self.mode = "webhook"
            await self._setup_webhook(self._webhook_url)
            logger.info(f"Telegram Bot 启动（Webhook 模式）: {self._webhook_url}")
        else:
            self.mode = "polling"
            logger.info("Telegram Bot 启动（轮询模式）")
            await self._polling_loop()

    async def stop(self):
        """停止 Bot"""
        self.running = False
        if self._client:
            await self._client.aclose()
        logger.info("Telegram Bot 已停止")

    # ==================== Webhook 模式 ====================

    async def _setup_webhook(self, url: str):
        """设置 Webhook"""
        bot_token = get_setting('telegram_bot_token', '')
        if not bot_token or not self._client:
            return

        api_url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/setWebhook"
        data = {
            "url": url,
            "allowed_updates": ["message", "callback_query"],
            "max_connections": 40
        }
        try:
            resp = await self._client.post(api_url, json=data)
            if resp.status_code == 200 and resp.json().get('ok'):
                logger.info(f"Telegram Webhook 设置成功: {url}")
            else:
                logger.error(f"Telegram Webhook 设置失败: {resp.text}")
        except Exception as e:
            logger.error(f"Telegram Webhook 设置异常: {e}")

    async def remove_webhook(self):
        """移除 Webhook"""
        bot_token = get_setting('telegram_bot_token', '')
        if not bot_token or not self._client:
            return
        api_url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/deleteWebhook"
        try:
            await self._client.post(api_url)
        except Exception:
            pass

    async def handle_webhook_update(self, update: dict):
        """处理 Webhook 推送的更新（由路由调用）"""
        update_id = update.get('update_id')
        if update_id in self._last_update_ids:
            return  # 去重
        self._last_update_ids.add(update_id)
        if len(self._last_update_ids) > 1000:
            self._last_update_ids = set(list(self._last_update_ids)[-500:])

        await self._process_update(update)

    # ==================== 轮询模式 ====================

    async def _polling_loop(self):
        """轮询主循环"""
        while self.running:
            try:
                bot_token = get_setting('telegram_bot_token', '')
                telegram_enabled = get_setting('telegram_login_enabled', '0')

                if not bot_token or telegram_enabled != '1':
                    await asyncio.sleep(10)
                    continue

                await self._get_updates(bot_token)
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Telegram 轮询错误: {e}")
                await asyncio.sleep(5)

    async def _get_updates(self, bot_token: str):
        """获取更新"""
        url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/getUpdates"
        params = {'offset': self.offset, 'timeout': 10, 'allowed_updates': ['message', 'callback_query']}

        try:
            response = await self._client.get(url, params=params)
            if response.status_code != 200:
                if response.status_code == 409:
                    await asyncio.sleep(10)
                return

            data = response.json()
            if not data.get('ok'):
                return

            for update in data.get('result', []):
                await self._process_update(update)
            if data.get('result'):
                self.offset = data['result'][-1]['update_id'] + 1
        except httpx.TimeoutException:
            pass
        except Exception as e:
            logger.error(f"Telegram 获取更新失败: {e}")

    # ==================== 通用处理 ====================

    async def _process_update(self, update: dict):
        """处理更新（消息 + 回调按钮）"""
        # 处理 Callback Query（Inline Keyboard 按钮）
        callback_query = update.get('callback_query')
        if callback_query:
            await self._handle_callback(callback_query)
            return

        # 处理消息
        message = update.get('message')
        if not message:
            return

        chat_id = str(message.get('chat', {}).get('id', ''))
        text = message.get('text', '').strip()
        user = message.get('from', {})
        user_id = str(user.get('id', ''))
        username = user.get('username', '')
        is_group = message.get('chat', {}).get('type') in ('group', 'supergroup')

        if not chat_id or not text:
            return

        # 检查权限
        allowed_user_ids = get_setting('telegram_allowed_user_ids', '')
        if allowed_user_ids:
            allowed_ids = [uid.strip() for uid in allowed_user_ids.split(',')]
            if user_id not in allowed_ids:
                await self._send(chat_id, "❌ 您没有权限使用此 Bot")
                return

        # 构建统一消息，交给网关处理
        msg = BotMessage(
            platform=BotPlatform.TELEGRAM,
            chat_id=chat_id,
            user_id=user_id,
            username=username,
            text=text,
            message_id=str(message.get('message_id', '')),
            is_group=is_group
        )

        response = await bot_gateway.handle_message(msg)
        if response:
            await self._send_response(chat_id, response)

    async def _handle_callback(self, callback_query: dict):
        """处理 Inline Keyboard 回调"""
        chat_id = str(callback_query.get('message', {}).get('chat', {}).get('id', ''))
        data = callback_query.get('data', '')
        user = callback_query.get('from', {})
        user_id = str(user.get('id', ''))
        username = user.get('username', '')

        # 确认回调
        bot_token = get_setting('telegram_bot_token', '')
        if bot_token and self._client:
            await self._client.post(
                f"{TELEGRAM_API_BASE.format(token=bot_token)}/answerCallbackQuery",
                json={"callback_query_id": callback_query['id']}
            )

        # 处理画质选择
        if data.startswith('dl:'):
            parts = data.split(':', 2)
            if len(parts) == 3:
                quality, url = parts[1], parts[2]
                msg = BotMessage(
                    platform=BotPlatform.TELEGRAM,
                    chat_id=chat_id, user_id=user_id,
                    username=username, text=f"/dl {url} {quality}"
                )
                response = await bot_gateway.handle_message(msg)
                if response:
                    await self._send_response(chat_id, response)

    async def _send(self, chat_id: str, text: str, reply_markup: dict = None):
        """发送消息"""
        bot_token = get_setting('telegram_bot_token', '')
        if not bot_token or not self._client:
            return

        url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/sendMessage"
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        if reply_markup:
            data['reply_markup'] = reply_markup

        try:
            await self._client.post(url, json=data)
        except Exception as e:
            logger.error(f"Telegram 发送消息失败: {e}")

    async def _send_response(self, chat_id: str, resp: BotResponse):
        """发送网关响应"""
        if resp.edit_message:
            bot_token = get_setting('telegram_bot_token', '')
            if bot_token and self._client:
                url = f"{TELEGRAM_API_BASE.format(token=bot_token)}/editMessageText"
                data = {
                    'chat_id': chat_id,
                    'message_id': int(resp.edit_message),
                    'text': resp.text,
                    'parse_mode': resp.parse_mode.upper()
                }
                if resp.keyboard:
                    data['reply_markup'] = resp.keyboard
                try:
                    await self._client.post(url, json=data)
                except Exception:
                    pass
        else:
            await self._send(chat_id, resp.text, resp.keyboard)

    async def send_message(self, user_id: str, text: str):
        """主动发送消息（网关调用）"""
        await self._send(user_id, text)

    async def send_download_options(self, chat_id: str, url: str):
        """发送画质选择 Inline Keyboard"""
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🎬 最佳", "callback_data": f"dl:best:{url}"},
                    {"text": "1080p", "callback_data": f"dl:1080p:{url}"},
                    {"text": "720p", "callback_data": f"dl:720p:{url}"}
                ],
                [
                    {"text": "🎵 MP3", "callback_data": f"dl:mp3:{url}"},
                    {"text": "🎵 M4A", "callback_data": f"dl:m4a:{url}"},
                    {"text": "🔊 音频", "callback_data": f"dl:audio:{url}"}
                ]
            ]
        }
        await self._send(chat_id, f"🎯 选择画质/格式：\n\n🔗 {url[:60]}...", reply_markup=keyboard)


# 全局实例
bot_handler = TelegramBotHandler()
