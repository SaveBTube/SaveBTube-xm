"""
微信 ClawBot 适配器
通过 Webhook 与 OpenClaw/ClawBot 集成
"""

import httpx
import logging
import asyncio
from typing import Optional

from backend.services.bot_gateway import BotGateway, BotMessage, BotPlatform, BotResponse
from backend.admin.db import get_setting

logger = logging.getLogger("bosco")


class WeChatBotAdapter:
    """微信 ClawBot 适配器"""

    def __init__(self, gateway: BotGateway):
        self.gateway = gateway
        self.running = False
        self._client: Optional[httpx.AsyncClient] = None

    async def start(self):
        """启动微信 Bot"""
        self.running = True
        self._client = httpx.AsyncClient(timeout=30)
        self.gateway.register_adapter(BotPlatform.WECHAT, self)
        logger.info("微信 ClawBot 适配器已启动")

    async def stop(self):
        """停止"""
        self.running = False
        if self._client:
            await self._client.aclose()
        logger.info("微信 ClawBot 适配器已停止")

    async def handle_webhook(self, data: dict):
        """处理来自 ClawBot 的 Webhook 消息

        期望的消息格式：
        {
            "user_id": "wx_user_xxx",
            "username": "用户昵称",
            "text": "消息内容",
            "chat_id": "群聊ID或用户ID",
            "is_group": false,
            "message_id": "msg_xxx"
        }
        """
        msg = BotMessage(
            platform=BotPlatform.WECHAT,
            chat_id=data.get('chat_id', data.get('user_id', '')),
            user_id=data.get('user_id', ''),
            username=data.get('username', ''),
            text=data.get('text', ''),
            message_id=data.get('message_id', ''),
            is_group=data.get('is_group', False)
        )

        response = await self.gateway.handle_message(msg)
        if response:
            return {"text": response.text, "parse_mode": response.parse_mode}
        return None

    async def send_message(self, user_id: str, text: str):
        """主动发送消息到微信

        通过 ClawBot 的回调 URL 发送
        """
        callback_url = get_setting('wechat_clawbot_callback_url', '')
        if not callback_url or not self._client:
            logger.warning("微信 ClawBot 回调 URL 未配置")
            return

        try:
            payload = {
                "user_id": user_id,
                "text": text,
                "parse_mode": "html"
            }
            result = await self._client.post(callback_url, json=payload)
            if result.status_code != 200:
                logger.error(f"微信发送消息失败: {result.text}")
        except Exception as e:
            logger.error(f"微信发送消息异常: {e}")
