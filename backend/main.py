"""
Bosco Tsang - 全平台视频/音乐/图片下载系统
主入口（精简版，路由分发到 routers/）
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import logging
import os
import asyncio

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.admin.db import init_db, get_setting
from backend.admin.telegram_bot import bot_handler
from backend.config import load_config, apply_proxy_from_config

# ==================== 配置 ====================

BASE_DIR = Path(os.getenv("APP_BASE_DIR", "/app"))
DOWNLOAD_DIR = BASE_DIR / "downloads"
COOKIES_DIR = BASE_DIR / "cookies"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

for d in [DOWNLOAD_DIR, COOKIES_DIR, LOGS_DIR, DATA_DIR, STATIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 日志
class DailyFileHandler(logging.FileHandler):
    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        filename = self.logs_dir / f"app_{self.current_date}.log"
        super().__init__(str(filename), encoding="utf-8")

    def emit(self, record):
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            if self.stream:
                self.stream.close()
            self.baseFilename = str(self.logs_dir / f"app_{today}.log")
            self.stream = self._open()
        super().emit(record)

logger = logging.getLogger("bosco")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handler = DailyFileHandler(LOGS_DIR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# 配置加载
try:
    APP_CONFIG = load_config(BASE_DIR)
    apply_proxy_from_config(APP_CONFIG)
except Exception:
    APP_CONFIG = {}

# 数据库初始化
init_db()

# 速率限制器
limiter = Limiter(key_func=get_remote_address)

# ==================== 生命周期 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 应用启动中...")
    telegram_enabled = get_setting('telegram_login_enabled', '0')
    telegram_bot_token = get_setting('telegram_bot_token', '')
    if telegram_enabled == '1' and telegram_bot_token:
        logger.info("📱 启动 Telegram Bot 处理器...")
        asyncio.create_task(bot_handler.start())
    else:
        logger.info("📱 Telegram Bot 未启用")
    yield
    logger.info("🛑 应用关闭中...")
    if bot_handler.running:
        await bot_handler.stop()

# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Bosco Tsang",
    version="1.0.0",
    description="全平台视频/音乐/图片下载系统",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 白名单
cors_origins = APP_CONFIG.get('cors', {}).get('origins', [
    "http://localhost:8080", "http://127.0.0.1:8080",
    "http://localhost:3000", "http://127.0.0.1:3000"
])
app.add_middleware(CORSMiddleware, allow_origins=cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# 请求日志中间件
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    logger.info(f"REQUEST {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"RESPONSE {request.method} {request.url} -> {response.status_code}")
        return response
    except Exception as error:
        logger.exception(f"Unhandled exception: {request.method} {request.url}")
        raise

# ==================== 注册路由 ====================

from backend.routers.auth_router import router as auth_router
from backend.routers.download_router import router as download_router
from backend.routers.files_router import router as files_router
from backend.routers.users_router import router as users_router
from backend.routers.subscriptions_router import router as subscriptions_router
from backend.routers.settings_router import router as settings_router
from backend.routers.telegram_router import router as telegram_router
from backend.routers.bot_router import router as bot_router

app.include_router(auth_router)
app.include_router(download_router)
app.include_router(files_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(settings_router)
app.include_router(telegram_router)
app.include_router(bot_router)

# ==================== 静态文件 ====================

@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Bosco Tsang API", "version": "1.0.0", "docs": "/docs"}


@app.get("/shortcuts")
async def shortcuts_install_page():
    """iOS 快捷指令安装引导页"""
    page = STATIC_DIR / "shortcuts-install.html"
    if page.exists():
        return FileResponse(page)
    raise HTTPException(status_code=404, detail="安装页面不存在")

# 浏览器扩展下载
@app.get("/api/admin/plugin/info")
async def get_plugin_info():
    import json
    manifest_path = BASE_DIR / "extensions" / "quick-download" / "manifest.json"
    info = {"name": "Bosco Tsang 快速下载", "version": "1.2.0"}
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                m = json.load(f)
                info.update({"version": m.get("version", info["version"]), "name": m.get("name", info["name"])})
        except Exception:
            pass
    return info


@app.get("/api/admin/plugin/download")
async def download_plugin(authorization: str = Header(None)):
    import io, zipfile
    extensions_dir = BASE_DIR / "extensions" / "quick-download"
    if not extensions_dir.exists():
        raise HTTPException(status_code=404, detail="插件目录不存在")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(extensions_dir):
            dirs[:] = [d for d in dirs if d not in ('__pycache__', '.DS_Store')]
            for file in files:
                if file == 'README.md':
                    continue
                file_path = Path(root) / file
                zf.write(file_path, file_path.relative_to(extensions_dir))
    zip_buffer.seek(0)
    from fastapi.responses import Response
    return Response(
        content=zip_buffer.getvalue(), media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename*=UTF-8''bosco-tsang-plugin.zip"}
    )


@app.get("/api/admin/shortcuts/download")
async def download_shortcut():
    """下载 iOS 快捷指令文件"""
    shortcut_file = BASE_DIR / "static" / "BoscoTsang.shortcut"
    if not shortcut_file.exists():
        # 生成一个基础的快捷指令配置
        return {"status": "info", "message": "请通过 /shortcuts 页面引导安装", "install_url": "/shortcuts"}
    from fastapi.responses import Response
    content = shortcut_file.read_bytes()
    return Response(
        content=content,
        media_type="application/x-shortcut",
        headers={"Content-Disposition": "attachment; filename*=UTF-8''BoscoTsang.shortcut"}
    )
