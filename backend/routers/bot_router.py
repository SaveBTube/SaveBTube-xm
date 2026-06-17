"""
Bot Webhook 路由 - 接收外部平台消息
"""
from fastapi import APIRouter, Request, HTTPException

from backend.services.bot_gateway import bot_gateway
from backend.admin.qq_bot import QQBotAdapter
from backend.admin.wechat_bot import WeChatBotAdapter
from backend.admin.db import get_setting

router = APIRouter(prefix="/api/bot", tags=["Bot 网关"])

# 初始化适配器
qq_adapter = QQBotAdapter(bot_gateway)
wechat_adapter = WeChatBotAdapter(bot_gateway)


@router.post("/qq/webhook")
async def qq_webhook(request: Request):
    """QQ Bot Webhook - 接收 OneBot 事件

    配置方式：在 OneBot 实现（Lagrange/NapCat）中设置 HTTP POST 上报地址为：
    http://your-server:8080/api/bot/qq/webhook
    """
    try:
        data = await request.json()
        await qq_adapter.handle_event(data)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wechat/webhook")
async def wechat_webhook(request: Request):
    """微信 ClawBot Webhook - 接收微信消息

    配置方式：在 ClawBot 中设置回调地址为：
    http://your-server:8080/api/bot/wechat/webhook
    """
    try:
        data = await request.json()
        result = await wechat_adapter.handle_webhook(data)
        if result:
            return result
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def bot_status():
    """查看所有 Bot 状态"""
    return {
        "telegram": {
            "enabled": get_setting('telegram_login_enabled', '0') == '1',
            "bot_token_configured": bool(get_setting('telegram_bot_token', ''))
        },
        "qq": {
            "enabled": bool(get_setting('qq_bot_api_url', '')),
            "api_url": get_setting('qq_bot_api_url', '')
        },
        "wechat": {
            "enabled": bool(get_setting('wechat_clawbot_callback_url', '')),
            "callback_url": get_setting('wechat_clawbot_callback_url', '')
        }
    }


@router.post("/qq/start")
async def start_qq_bot():
    """手动启动 QQ Bot"""
    import asyncio
    if not qq_adapter.running:
        asyncio.create_task(qq_adapter.start())
        return {"status": "started"}
    return {"status": "already_running"}


@router.post("/qq/stop")
async def stop_qq_bot():
    """停止 QQ Bot"""
    await qq_adapter.stop()
    return {"status": "stopped"}


@router.post("/wechat/start")
async def start_wechat_bot():
    """手动启动微信 Bot"""
    import asyncio
    if not wechat_adapter.running:
        asyncio.create_task(wechat_adapter.start())
        return {"status": "started"}
    return {"status": "already_running"}


@router.post("/wechat/stop")
async def stop_wechat_bot():
    """停止微信 Bot"""
    await wechat_adapter.stop()
    return {"status": "stopped"}
