"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel
from typing import List, Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    invite_code: Optional[str] = None


class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "best"


class QuickDownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "best"


class ShortcutsDownloadRequest(BaseModel):
    """iOS 快捷指令下载请求"""
    url: str
    quality: Optional[str] = "best"


class RenameTaskRequest(BaseModel):
    new_title: str


class RenameFileRequest(BaseModel):
    old_name: str
    new_name: str


class BatchDeleteRequest(BaseModel):
    ids: List[int]


class SubscribeRequest(BaseModel):
    url: str
    platform: str
    channel_name: Optional[str] = None
    poll_interval: Optional[int] = 3600


class ApiKeyRequest(BaseModel):
    note: Optional[str] = None
    scopes: Optional[List[str]] = None
    expires_in_days: Optional[int] = None
    rate_limit: Optional[int] = 60


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[int] = None


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = 'user'
    is_active: Optional[int] = 1


class TelegramLoginRequest(BaseModel):
    """Telegram 登录请求"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class TelegramBindRequest(BaseModel):
    """绑定 Telegram 到系统账号"""
    telegram_id: int
    username: str
    password: str
