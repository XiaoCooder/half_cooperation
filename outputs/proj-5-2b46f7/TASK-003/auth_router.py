"""
认证路由模块
任务码: TASK-003
提供用户注册、登录、登出、刷新 token 等接口
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from auth_service import AuthService
from auth import verify_refresh_token, create_token_pair, TokenPair
from security import hash_password, verify_password
from models import User
from schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============== 扩展的请求/响应模式 ==============

class LoginRequest(BaseModel):
    """登录请求（JSON 格式）"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token 过期时间（秒）")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserMeResponse(BaseModel):
    """当前用户信息响应"""
    id: int
    username: str
    email: EmailStr
    nickname: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


# ============== 依赖函数 ==============

def get_db():
    """数据库会话依赖（示例实现，实际使用时需替换）"""
    # 这里需要从实际项目导入 get_db
    # from database import SessionLocal
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    pass


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户依赖"""
    from dependencies import get_current_user as _get_current_user
    return _get_current_user(token, db)


# ============== 路由端点 ==============

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（6-100字符）
    - **nickname**: 昵称（可选）
    """
    auth_service = AuthService(db)

    user = auth_service.register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        nickname=user_data.nickname
    )

    return UserResponse.from_orm(user)


@router.post("/login", response_model=TokenResponse)
def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录（JSON 格式）

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
        expires_in=token_pair.access_token_expires_in
    )


@router.post("/login/form", response_model=TokenResponse)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录（OAuth2 表单格式）

    用于 Swagger UI 测试和标准 OAuth2 客户端
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
        expires_in=token_pair.access_token_expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新 Token

    使用 refresh_token 获取新的 access_token 和 refresh_token
    """
    # 验证 refresh token
    try:
        payload = verify_refresh_token(refresh_data.refresh_token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # 获取新 token
    auth_service = AuthService(db)
    token_pair = auth_service.refresh_tokens(int(user_id))

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type="bearer",
        expires_in=token_pair.access_token_expires_in
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出

    注意：JWT token 在过期前仍然有效，客户端应删除本地存储的 token
    如需实现服务器端登出，需要额外的 token 存储机制（如 Redis 黑名单）
    """
    return MessageResponse(
        message=f"User {current_user.username} logged out successfully",
        success=True
    )


@router.get("/me", response_model=UserMeResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息

    需要认证
    """
    return UserMeResponse.from_orm(current_user)


@router.patch("/me", response_model=UserMeResponse)
def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息

    - **nickname**: 昵称
    - **bio**: 个人简介
    - **avatar**: 头像 URL
    """
    auth_service = AuthService(db)

    update_dict = update_data.dict(exclude_unset=True)
    user = auth_service.update_user(current_user.id, update_dict)

    return UserMeResponse.from_orm(user)


@router.post("/me/password", response_model=MessageResponse)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码

    - **old_password**: 原密码
    - **new_password**: 新密码
    """
    auth_service = AuthService(db)

    auth_service.change_password(
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )

    return MessageResponse(
        message="Password changed successfully",
        success=True
    )


@router.post("/verify-token", response_model=MessageResponse)
def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    验证当前 Token 是否有效

    用于检查 token 状态
    """
    return MessageResponse(
        message=f"Token is valid for user {current_user.username}",
        success=True
    )


# ============== 管理员专用接口 ==============

@router.get("/admin/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    列出所有用户（管理员）

    需要管理员权限
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(u) for u in users]


@router.patch("/admin/users/{user_id}/deactivate", response_model=MessageResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    禁用用户（管理员）

    需要管理员权限
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    auth_service = AuthService(db)
    auth_service.deactivate_user(user_id)

    return MessageResponse(
        message=f"User {user_id} deactivated",
        success=True
    )


@router.patch("/admin/users/{user_id}/activate", response_model=MessageResponse)
def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    启用用户（管理员）

    需要管理员权限
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    auth_service = AuthService(db)
    auth_service.activate_user(user_id)

    return MessageResponse(
        message=f"User {user_id} activated",
        success=True
    )