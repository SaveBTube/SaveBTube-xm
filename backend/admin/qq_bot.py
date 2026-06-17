"""
QQ 机器人适配器
支持 Lagrange / NapCat / go-cqhttp 等 OneBot 协议实现
通过 HTTP API 与 OneBot 后端通信
"""

import httpx
import logging
import asyncio
from typing import Optional

from backend.services.bot_gateway import BotGateway, BotMessage, BotPlatform, BotResponse
from backend.admin.db import get_setting

logger = logging.getLogger("bosco")


class QQBotAdapter:
    """QQ 机器人适配器（OneBot v11 协议）"""

    def __init__(self, gateway: BotGateway):
        self.gateway = gateway
        self.running = False
        self._client: Optional[httpx.AsyncClient] = None
        self._api_base = ""  # OneBot HTTP API 地址

    async def start(self):
        """启动 QQ Bot"""
        self.running = True
        self._api_base = get_setting('qq_bot_api_url', 'http://localhost:3000')
        self._client = httpx.AsyncClient(timeout=30)

        logger.info(f"QQ Bot 启动，API: {self._api_base}")

        # 注册到网关
        self.gateway.register_adapter(BotPlatform.QQ, self)

        # 轮询消息（如果使用 HTTP 轮询模式）
        while self.running:
            try:
                await self._poll_messages()
            except Exception as e:
                logger.error(f"QQ Bot 轮询错误: {e}")
            await asyncio.sleep(2)

    async def stop(self):
        """停止 QQ Bot"""
        self.running = False
        if self._client:
            await self._client.aclose()
        logger.info("QQ Bot 已停止")

    async def _poll_messages(self):
        """轮询获取消息（HTTP 方式）"""
        if not self._client or not self._api_base:
            return

        try:
            resp = await self._client.get(f"{self._api_base}/get_status")
            if resp.status_code != 200:
                return
        except httpx.ConnectError:
            return  # OneBot 后端未启动

    async def handle_event(self, event: dict):
        """处理 OneBot 事件（由 webhook 路由调用）"""
        post_type = event.get('post_type')
        if post_type != 'message':
            return

        message_type = event.get('message_type')
        raw_message = event.get('raw_message', '')
        user_id = str(event.get('user_id', ''))
        group_id = str(event.get('group_id', ''))
        message_id = str(event.get('message_id', ''))

        # 获取发送者信息
        sender = event.get('sender', {})
        username = sender.get('card') or sender.get('nickname') or user_id

        # 构建统一消息
        msg = BotMessage(
            platform=BotPlatform.QQ,
            chat_id=group_id if message_type == 'group' else user_id,
            user_id=user_id,
            username=username,
            text=raw_message,
            message_id=message_id,
            is_group=(message_type == 'group')
        )

        # 交给网关处理
        response = await self.gateway.handle_message(msg)
        if response:
            await self._send_response(msg, response)

    async def _send_response(self, msg: BotMessage, resp: BotResponse):
        """发送响应消息"""
        if not self._client or not self._api_base:
            return

        api_url = f"{self._api_base}/send_msg"

        if resp.edit_message:
            # 编辑消息
            data = {
                "message_id": int(resp.edit_message),
                "message": resp.text
            }
            await self._client.post(f"{self._api_base}/edit_msg", json=data)
        else:
            # 发送新消息
            data = {}
            if msg.is_group:
                data["message_type"] = "group"
                data["group_id"] = int(msg.chat_id)
            else:
                data["message_type"] = "private"
                data["user_id"] = int(msg.chat_id)

            data["message"] = resp.text
            if resp.reply_to:
                data["message"] = f"[CQ:reply,id={resp.reply_to}]{resp.text}"

            try:
                result = await self._client.post(api_url, json=data)
                if result.status_code != 200:
                    logger.error(f"QQ 发送消息失败: {result.text}")
            except Exception as e:
                logger.error(f"QQ 发送消息异常: {e}")

    async def send_message(self, user_id: str, text: str):
        """主动发送消息（网关调用）"""
        if not self._client or not self._api_base:
            return

        data = {
            "message_type": "private",
            "user_id": int(user_id),
            "message": text
        }
        try:
            await self._client.post(f"{self._api_base}/send_msg", json=data)
        except Exception as e:
            logger.error(f"QQ 主动发送消息失败: {e}")
