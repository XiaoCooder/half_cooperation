"""
认证相关的 Pydantic 模型
任务码: TASK-003
补充 authentication 专用的请求和响应模式
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ============== Token 相关模式 ==============

class TokenBase(BaseModel):
    """Token 基础模式"""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(TokenBase):
    """Token 响应模式"""
    refresh_token: str
    expires_in: int = Field(..., description="Access token 有效期（秒）")
    refresh_expires_in: int = Field(..., description="Refresh token 有效期（秒）")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(..., description="刷新令牌")


# ============== 登录/注册相关模式 ==============

class LoginRequest(BaseModel):
    """登录请求（JSON 格式）"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)


class RegisterResponse(BaseModel):
    """注册响应"""
    id: int
    username: str
    email: EmailStr
    nickname: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 密码相关模式 ==============

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class ResetPasswordRequest(BaseModel):
    """重置密码请求（需要额外验证机制）"""
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    """确认重置密码"""
    token: str = Field(..., description="重置密码验证 token")
    new_password: str = Field(..., min_length=6, max_length=100)


# ============== 用户信息模式 ==============

class UserMeResponse(BaseModel):
    """当前用户信息响应"""
    id: int
    username: str
    email: EmailStr
    nickname: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdateMe(BaseModel):
    """更新当前用户信息请求"""
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=255)


# ============== 通用响应模式 ==============

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: str
    status_code: int


# ============== Session 信息模式 ==============

class SessionInfo(BaseModel):
    """Session 信息"""
    user_id: int
    username: str
    token_type: str = "bearer"
    expires_at: datetime
    issued_at: datetime

    class Config:
        from_attributes = True


class AuthStatus(BaseModel):
    """认证状态"""
    authenticated: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    is_admin: Optional[bool] = None
    token_valid: Optional[bool] = None