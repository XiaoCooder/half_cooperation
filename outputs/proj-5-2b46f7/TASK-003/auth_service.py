"""
用户认证服务层
任务码: TASK-003
处理用户注册、登录验证、用户管理等业务逻辑
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from security import hash_password, verify_password, needs_rehash
from auth import create_token_pair, TokenPair
from models import User


class AuthService:
    """用户认证服务类"""

    def __init__(self, db: Session, secret_key: str = None):
        """
        初始化认证服务

        Args:
            db: SQLAlchemy 数据库会话
            secret_key: JWT 签名密钥（可选）
        """
        self.db = db
        self.secret_key = secret_key or "your-secret-key-change-in-production-min-32-characters"

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        nickname: Optional[str] = None,
        is_admin: bool = False
    ) -> User:
        """
        注册新用户

        Args:
            username: 用户名
            email: 邮箱地址
            password: 原始密码
            nickname: 昵称（可选）
            is_admin: 是否为管理员

        Returns:
            User: 创建的用户对象

        Raises:
            HTTPException: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # 检查邮箱是否已存在
        existing_email = self.db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # 创建用户
        hashed_password = hash_password(password)

        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            nickname=nickname or username,
            is_active=True,
            is_admin=is_admin,
            created_at=datetime.now(timezone.utc)
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户登录

        Args:
            username: 用户名
            password: 原始密码

        Returns:
            User: 验证成功的用户对象，失败返回 None
        """
        user = self.db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # 检查是否需要更新密码哈希（算法升级等）
        if needs_rehash(user.hashed_password):
            user.hashed_password = hash_password(password)
            user.updated_at = datetime.now(timezone.utc)
            self.db.commit()

        return user

    def login(self, username: str, password: str) -> TokenPair:
        """
        用户登录，返回 token 对

        Args:
            username: 用户名
            password: 原始密码

        Returns:
            TokenPair: 包含 access_token 和 refresh_token

        Raises:
            HTTPException: 登录失败
        """
        user = self.authenticate_user(username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 更新最后登录时间
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return create_token_pair(user.id, user.username, self.secret_key)

    def get_current_user(self, user_id: int) -> Optional[User]:
        """
        根据 ID 获取当前用户

        Args:
            user_id: 用户 ID

        Returns:
            User: 用户对象，不存在返回 None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            User: 用户对象，不存在返回 None
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱地址

        Returns:
            User: 用户对象，不存在返回 None
        """
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户 ID
            update_data: 更新数据字典

        Returns:
            User: 更新后的用户对象

        Raises:
            HTTPException: 用户不存在
        """
        user = self.get_current_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 更新字段
        for field, value in update_data.items():
            if hasattr(user, field) and field not in ['id', 'hashed_password']:
                setattr(user, field, value)

        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)

        return user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码

        Args:
            user_id: 用户 ID
            old_password: 原密码
            new_password: 新密码

        Returns:
            bool: 修改是否成功

        Raises:
            HTTPException: 用户不存在或原密码错误
        """
        user = self.get_current_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 验证原密码
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )

        # 更新密码
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return True

    def deactivate_user(self, user_id: int) -> bool:
        """
        禁用用户

        Args:
            user_id: 用户 ID

        Returns:
            bool: 操作是否成功
        """
        user = self.get_current_user(user_id)

        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return True

    def activate_user(self, user_id: int) -> bool:
        """
        启用用户

        Args:
            user_id: 用户 ID

        Returns:
            bool: 操作是否成功
        """
        user = self.get_current_user(user_id)

        if not user:
            return False

        user.is_active = True
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return True

    def refresh_tokens(self, user_id: int) -> TokenPair:
        """
        使用 refresh token 刷新 access token

        Args:
            user_id: 用户 ID

        Returns:
            TokenPair: 新的 token 对

        Raises:
            HTTPException: 用户不存在或已禁用
        """
        user = self.get_current_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is deactivated"
            )

        return create_token_pair(user.id, user.username, self.secret_key)

    def validate_admin(self, user_id: int) -> bool:
        """
        验证用户是否为管理员

        Args:
            user_id: 用户 ID

        Returns:
            bool: 是否为管理员

        Raises:
            HTTPException: 用户不存在或不是管理员
        """
        user = self.get_current_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return True