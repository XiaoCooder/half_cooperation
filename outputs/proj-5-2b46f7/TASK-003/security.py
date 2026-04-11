"""
密码安全工具模块
任务码: TASK-003
使用 passlib 和 bcrypt 进行密码哈希和验证
"""

from passlib.context import CryptContext

# 密码哈希上下文配置
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # bcrypt 工作因子，越高越安全但越慢
)


def hash_password(password: str) -> str:
    """
    对密码进行哈希处理

    Args:
        password: 原始密码字符串

    Returns:
        哈希后的密码字符串
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配

    Args:
        plain_password: 用户输入的原始密码
        hashed_password: 数据库存储的哈希密码

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    检查密码哈希是否需要更新（例如算法升级）

    Args:
        hashed_password: 当前存储的哈希密码

    Returns:
        bool: 是否需要重新哈希
    """
    return pwd_context.needs_update(hashed_password)