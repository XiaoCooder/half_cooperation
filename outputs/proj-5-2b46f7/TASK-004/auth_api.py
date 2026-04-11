"""
认证 API 路由模块
任务码: TASK-004
实现 /api/auth/login, /api/auth/logout, /api/auth/me 接口

整合 TASK-002 数据库配置和 TASK-003 认证逻辑
"""

import sys
import os

# 添加前序任务模块路径
TASK002_PATH = os.path.abspath("../TASK-002")
TASK003_PATH = os.path.abspath("../TASK-003")
sys.path.insert(0, TASK002_PATH)
sys.path.insert(0, TASK003_PATH)

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

# 从 TASK-002 导入数据库配置
from database import get_db

# 从 TASK-003 导入认证模块
from security import hash_password, verify_password
from auth import verify_access_token, create_token_pair, TokenPair
from auth_service import AuthService
from models import User


# ============== 路由配置 ==============

router = APIRouter(prefix="/api/auth", tags=["auth"])

# OAuth2 scheme - 更新 tokenUrl 为正确路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============== 请求/响应模式 ==============

class LoginRequest(BaseModel):
    """登录请求（JSON 格式）"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="Access token 过期时间（秒）")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    is_active: bool = Field(..., description="是否活跃")
    is_admin: bool = Field(..., description="是否管理员")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class LogoutResponse(BaseModel):
    """登出响应"""
    message: str = Field(..., description="消息")
    success: bool = Field(default=True, description="是否成功")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误类型")
    detail: str = Field(..., description="错误详情")


# ============== 依赖函数 ==============

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户

    Args:
        token: OAuth2 bearer token
        db: 数据库会话

    Returns:
        User: 当前用户对象

    Raises:
        HTTPException: token 无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except HTTPException:
        raise credentials_exception

    # 获取用户
    auth_service = AuthService(db)
    user = auth_service.get_current_user(int(user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user


# ============== API 端点 ==============

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT token",
    responses={
        200: {"description": "登录成功，返回 token"},
        401: {"model": ErrorResponse, "description": "用户名或密码错误"},
    }
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口

    - **username**: 用户名（3-50字符）
    - **password**: 密码（6-100字符）

    返回 access_token 和 refresh_token
    """
    auth_service = AuthService(db)

    token_pair = auth_service.login(
        username=login_data.username,
        password=login_data.password
    )

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type="bearer",
        expires_in=int(
            (token_pair.access_token_expires - datetime.now(timezone.utc)).total_seconds()
        )
    )


@router.post(
    "/login/form",
    response_model=TokenResponse,
    summary="用户登录（OAuth2表单）",
    description="OAuth2 标准表单登录，用于 Swagger UI 测试",
    responses={
        200: {"description": "登录成功"},
        401: {"model": ErrorResponse, "description": "认证失败"},
    }
)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 表单登录接口

    用于 Swagger UI 和标准 OAuth2 客户端
    """
    auth_service = AuthService(db)

    token_pair = auth_service.login(
        username=form_data.username,
        password=form_data.password
    )

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type="bearer",
        expires_in=int(
            (token_pair.access_token_expires - datetime.now(timezone.utc)).total_seconds()
        )
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="用户登出",
    description="登出当前用户（客户端需删除本地 token）",
    responses={
        200: {"description": "登出成功"},
        401: {"model": ErrorResponse, "description": "未认证"},
    }
)
def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出接口

    注意：JWT token 在过期前仍然有效
    客户端应删除本地存储的 token
    如需服务器端登出控制，需要额外的 token 黑名单机制
    """
    return LogoutResponse(
        message=f"User '{current_user.username}' logged out successfully",
        success=True
    )


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="获取当前用户",
    description="获取当前认证用户的详细信息",
    responses={
        200: {"description": "返回用户信息"},
        401: {"model": ErrorResponse, "description": "未认证"},
        403: {"model": ErrorResponse, "description": "用户已禁用"},
    }
)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息接口

    需要在请求头携带有效的 Authorization: Bearer <token>
    """
    return UserInfoResponse.from_orm(current_user)


@router.patch(
    "/me",
    response_model=UserInfoResponse,
    summary="更新用户信息",
    description="更新当前用户的个人信息",
    responses={
        200: {"description": "更新成功"},
        401: {"model": ErrorResponse, "description": "未认证"},
    }
)
def update_current_user_info(
    nickname: Optional[str] = Field(None, max_length=50),
    bio: Optional[str] = Field(None, max_length=500),
    avatar: Optional[str] = Field(None, max_length=255),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息接口

    - **nickname**: 昵称（可选）
    - **bio**: 个人简介（可选）
    - **avatar**: 头像 URL（可选）
    """
    auth_service = AuthService(db)

    update_data = {}
    if nickname is not None:
        update_data["nickname"] = nickname
    if bio is not None:
        update_data["bio"] = bio
    if avatar is not None:
        update_data["avatar"] = avatar

    if update_data:
        user = auth_service.update_user(current_user.id, update_data)
        return UserInfoResponse.from_orm(user)

    return UserInfoResponse.from_orm(current_user)


# ============== 辅助接口 ==============

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新 Token",
    description="使用 refresh_token 获取新的 token",
    responses={
        200: {"description": "刷新成功"},
        401: {"model": ErrorResponse, "description": "refresh_token 无效"},
    }
)
def refresh_token(
    refresh_token: str = Body(..., embed=True, description="刷新令牌"),
    db: Session = Depends(get_db)
):
    """
    刷新 Token 接口

    使用 refresh_token 获取新的 access_token 和 refresh_token
    """
    try:
        payload = verify_access_token.__wrapped__(refresh_token) if hasattr(verify_access_token, '__wrapped__') else None
        # 直接使用 verify_refresh_token
        from auth import verify_refresh_token
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取新 token
    auth_service = AuthService(db)
    token_pair = auth_service.refresh_tokens(int(user_id))

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type="bearer",
        expires_in=int(
            (token_pair.access_token_expires - datetime.now(timezone.utc)).total_seconds()
        )
    )


@router.get(
    "/verify",
    response_model=LogoutResponse,
    summary="验证 Token",
    description="验证当前 token 是否有效",
    responses={
        200: {"description": "Token 有效"},
        401: {"model": ErrorResponse, "description": "Token 无效"},
    }
)
def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    验证 Token 有效性接口

    用于检查当前 token 状态
    """
    return LogoutResponse(
        message=f"Token is valid for user '{current_user.username}'",
        success=True
    )