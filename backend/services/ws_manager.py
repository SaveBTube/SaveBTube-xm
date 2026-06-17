"""
WebSocket 管理器 - 实时进度推送
"""
import json
import asyncio
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("bosco")


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # user_id -> set of websocket connections
        self._connections: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: int):
        """接受 WebSocket 连接"""
        await websocket.accept()
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(websocket)
        logger.info(f"WebSocket 连接: user_id={user_id}, 总连接数: {self.total_connections}")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """断开连接"""
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(websocket)
                if not self._connections[user_id]:
                    del self._connections[user_id]
        logger.info(f"WebSocket 断开: user_id={user_id}, 总连接数: {self.total_connections}")

    @property
    def total_connections(self) -> int:
        return sum(len(conns) for conns in self._connections.values())

    async def send_to_user(self, user_id: int, data: dict):
        """发送消息给指定用户的所有连接"""
        async with self._lock:
            connections = self._connections.get(user_id, set()).copy()

        if not connections:
            return

        message = json.dumps(data, ensure_ascii=False)
        dead = set()

        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        # 清理断开的连接
        if dead:
            async with self._lock:
                if user_id in self._connections:
                    self._connections[user_id] -= dead

    async def broadcast(self, data: dict):
        """广播消息给所有连接"""
        message = json.dumps(data, ensure_ascii=False)
        all_dead = []

        async with self._lock:
            all_connections = {uid: conns.copy() for uid, conns in self._connections.items()}

        for user_id, connections in all_connections.items():
            dead = set()
            for ws in connections:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.add(ws)
            if dead:
                all_dead.append((user_id, dead))

        for user_id, dead in all_dead:
            async with self._lock:
                if user_id in self._connections:
                    self._connections[user_id] -= dead

    async def notify_download_progress(self, task_id: str, user_id: int, progress: dict):
        """推送下载进度"""
        await self.send_to_user(user_id, {
            "type": "download_progress",
            "task_id": task_id,
            "data": progress
        })


# 全局实例
ws_manager = WebSocketManager()
