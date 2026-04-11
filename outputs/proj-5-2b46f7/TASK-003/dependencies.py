"""
FastAPI 认证依赖模块
任务码: TASK-003
提供获取当前用户、管理员验证等依赖函数
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import verify_access_token, verify_refresh_token
from auth_service import AuthService
from models import User

# OAuth2 密码模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(lambda: None)  # 需要替换为实际的 db 依赖
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


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（已验证 is_active）

    Args:
        current_user: 当前用户

    Returns:
        User: 当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户

    Args:
        current_user: 当前用户

    Returns:
        User: 当前管理员用户

    Raises:
        HTTPException: 用户不是管理员
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def get_optional_user(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)),
    db: Session = Depends(lambda: None)
) -> Optional[User]:
    """
    获取可选的当前用户（允许未认证访问）

    Args:
        token: OAuth2 bearer token（可选）
        db: 数据库会话

    Returns:
        Optional[User]: 当前用户，未认证返回 None
    """
    if token is None:
        return None

    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        auth_service = AuthService(db)
        user = auth_service.get_current_user(int(user_id))

        return user if user and user.is_active else None

    except HTTPException:
        return None


def get_user_id_from_refresh_token(
    token: str,
    db: Session = Depends(lambda: None)
) -> int:
    """
    从 refresh token 获取用户 ID

    Args:
        token: refresh token
        db: 数据库会话

    Returns:
        int: 用户 ID

    Raises:
        HTTPException: token 无效
    """
    try:
        payload = verify_refresh_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        return int(user_id)

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# 工具函数：创建带数据库依赖的版本
def create_auth_dependencies(get_db_func):
    """
    创建带实际数据库依赖的认证依赖函数

    Args:
        get_db_func: 获取数据库会话的函数

    Returns:
        dict: 包含所有认证依赖函数的字典
    """
    def _get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db_func)
    ) -> User:
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

    def _get_optional_user(
        token: Optional[str] = Depends(
            OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
        ),
        db: Session = Depends(get_db_func)
    ) -> Optional[User]:
        if token is None:
            return None

        try:
            payload = verify_access_token(token)
            user_id: str = payload.get("sub")

            if user_id is None:
                return None

            auth_service = AuthService(db)
            user = auth_service.get_current_user(int(user_id))

            return user if user and user.is_active else None

        except HTTPException:
            return None

    return {
        "get_current_user": _get_current_user,
        "get_current_active_user": lambda user=Depends(_get_current_user): user if user.is_active else HTTPException(status_code=403, detail="Inactive user"),
        "get_current_admin_user": lambda user=Depends(_get_current_user): user if user.is_admin else HTTPException(status_code=403, detail="Not admin"),
        "get_optional_user": _get_optional_user,
    }