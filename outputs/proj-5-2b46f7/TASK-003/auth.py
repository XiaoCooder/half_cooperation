"""
JWT Token 认证模块
任务码: TASK-003
使用 PyJWT 实现 token 生成、验证和刷新
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production-min-32-characters"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    secret_key: str = SECRET_KEY
) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码的数据（通常是用户信息）
        expires_delta: 过期时间增量，默认使用 ACCESS_TOKEN_EXPIRE_MINUTES
        secret_key: JWT 签名密钥

    Returns:
        str: 编码后的 JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    secret_key: str = SECRET_KEY
) -> str:
    """
    创建刷新令牌

    Args:
        data: 要编码的数据（通常是用户 ID）
        expires_delta: 过期时间增量，默认使用 REFRESH_TOKEN_EXPIRE_DAYS
        secret_key: JWT 签名密钥

    Returns:
        str: 编码后的 JWT refresh token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(
    token: str,
    secret_key: str = SECRET_KEY,
    expected_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    解码并验证 JWT token

    Args:
        token: JWT token 字符串
        secret_key: JWT 签名密钥
        expected_type: 预期的 token 类型 ("access" 或 "refresh")

    Returns:
        Dict: 解码后的 payload

    Raises:
        HTTPException: token 无效、过期或类型不匹配
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])

        # 检查 token 类型
        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type, expected {expected_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str, secret_key: str = SECRET_KEY) -> Dict[str, Any]:
    """
    验证访问令牌

    Args:
        token: JWT access token
        secret_key: JWT 签名密钥

    Returns:
        Dict: 解码后的 payload
    """
    return decode_token(token, secret_key, expected_type="access")


def verify_refresh_token(token: str, secret_key: str = SECRET_KEY) -> Dict[str, Any]:
    """
    验证刷新令牌

    Args:
        token: JWT refresh token
        secret_key: JWT 签名密钥

    Returns:
        Dict: 解码后的 payload
    """
    return decode_token(token, secret_key, expected_type="refresh")


def get_token_expire_time(token: str, secret_key: str = SECRET_KEY) -> Optional[datetime]:
    """
    获取 token 的过期时间

    Args:
        token: JWT token
        secret_key: JWT 签名密钥

    Returns:
        datetime: 过期时间，如果无效则返回 None
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp, tz=timezone.utc)
        return None
    except JWTError:
        return None


class TokenPair:
    """Token 对象封装类"""

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        access_token_expires: datetime,
        refresh_token_expires: datetime
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": "bearer",
            "access_token_expires_in": int(
                (self.access_token_expires - datetime.now(timezone.utc)).total_seconds()
            ),
            "refresh_token_expires_in": int(
                (self.refresh_token_expires - datetime.now(timezone.utc)).total_seconds()
            ),
        }


def create_token_pair(user_id: int, username: str, secret_key: str = SECRET_KEY) -> TokenPair:
    """
    创建访问和刷新令牌对

    Args:
        user_id: 用户 ID
        username: 用户名
        secret_key: JWT 签名密钥

    Returns:
        TokenPair: 包含两个 token 的对象
    """
    access_data = {"sub": str(user_id), "username": username}
    refresh_data = {"sub": str(user_id)}

    access_token = create_access_token(access_data, secret_key=secret_key)
    refresh_token = create_refresh_token(refresh_data, secret_key=secret_key)

    access_expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires=access_expires,
        refresh_token_expires=refresh_expires
    )